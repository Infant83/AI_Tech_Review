# coding: utf-8
"""Make the narrowly corrected public copy of the historical four-page DQB.

Supply the private original, Korean fonts and private QA directory. Only declared
text regions and metadata change. The original four-page layout and all eleven
public URI annotations remain. No research code, archive registration or deploy
is performed. Requires PyMuPDF, Pillow, fontTools and pypdf. Use Korean TrueType
fonts; CID-keyed OpenType/CFF fonts are unsuitable for these text insertions.
Rebuilds reset visual review.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from io import BytesIO
import math
from pathlib import Path
import re

import fitz
from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image, ImageChops, ImageDraw
from pypdf import PdfReader
from pypdf.generic import IndirectObject, StreamObject

TOPIC = Path(__file__).resolve().parents[1]
REPOSITORY = TOPIC.parent
SOURCE_SHA256 = '58c1ad01380c076a9543fffedfc6b5da8b183fa35956f20b88c7c2b8b47e0861'
DEFAULT_REPORT = REPOSITORY / '.automation/writing-reviews/legacy-refresh/2026-11-12-thermal/briefing-publication-qa.json'
# Zero-based pages; coordinates are PDF points. Unlisted text and graphics stay.
EDITS = [
    dict(id='cover-date', page=0, rect=(59.4,148.8,538.8,164.0), x=59.85827, y=159.22368, size=11.2, color=5858681,
         find='2026년 8월 31일 · 최근 24시간 우선',
         lines=['2026년 8월 31일 · 유한온도 상태와 엑시톤의 검증']),
    dict(id='exciton-summary-width', page=0, rect=(210.0,361.9,538.8,389.0), x=210.34650, y=370.42368, size=9.2, leading=14.2, color=1911097,
         find='α-sexithiophene에서 엑시톤이 약 3개 분자에 퍼지고',
         lines=['α-sexithiophene의 엑시톤은 약 3개 분자에 퍼진다. 400 fs 안에',
                '가우스 진폭의 공간폭(FWHM_x)이 약 25% 줄어드는 과정을 실험으로 복원했다.']),
    dict(id='revision-heading', page=0, rect=(59.4,495.0,538.8,510.0), x=59.85827, y=505.62369, size=11.6, color=1057599, bold=True,
         find='메일 점검', lines=['수정 이력 · Agentic Tech Review Letters(ATRL)']),
    dict(id='revision-record', page=0, rect=(59.4,514.7,538.8,542.0), x=59.85827, y=523.22369, size=9.2, leading=14.2, color=1911097,
         find='지난 실행 이후 D-Wave 기술 뉴스레터는 없었다.',
         lines=['원발행·근거 기준일은 2026-08-31이다. 2026-11-12 원문·보충자료 대조로 공간폭과 제어 조건을 정정했다.',
                '수집·실행 메모를 덜고 과학 본문과 출처를 보존했다. 코드·실험은 재실행하지 않았다.']),
    dict(id='classification-without-collection-note', page=0, rect=(59.4,568.1,538.8,595.0), x=59.85827, y=576.62366, size=9.2, leading=14.2, color=1911097,
         find='실제 실험, 아날로그 양자 시뮬레이터, 고전 수치 시뮬레이션, 하드웨어 제안을',
         lines=['실제 실험, 아날로그 양자 시뮬레이터, 고전 수치 시뮬레이션, 하드웨어 제안을 서로 다른 증거 층으로 구분했다.']),
    dict(id='gibbs-perturbative-scope', page=1, rect=(63.8,137.7,535.0,164.8), x=64.27559, y=146.22366, size=9.2, leading=14.2, color=1911097,
         find='고정점의 Gibbs 상태 오차는 약결합에서 결합 세기 θ에 대해 O(θ²)로 줄어든다.',
         lines=['Lloyd와 Abanin은 보조 bath를 반복 초기화하고 system-bath 결합을 시간에 따라 변조해 detailed balance를',
                '근사적으로 만족하는 채널을 구성했다. 고정점 오차의 O(θ²) 스케일링을 섭동적으로 논의하고 혼합시간 의존성을 분석했다.']),
    dict(id='exciton-body-width', page=1, rect=(63.8,340.7,535.0,367.8), x=64.27559, y=349.22369, size=9.2, leading=14.2, color=1911097,
         find='coherent하게 delocalize되며, 400 fs 안에 반경이 약 25% 수축했다.',
         lines=['coherent하게 delocalize되며, 400 fs 안에 가우스 진폭의 공간폭(FWHM_x)이 약 25% 수축했다.',
                '이는 exciton-phonon 결합에 따른 self-trapping과 일치한다.']),
    dict(id='exciton-application-width', page=1, rect=(94.4,399.7,535.0,410.3), x=94.75019, y=407.02368, size=7.8, color=5858681,
         find='OLED 계산에서는 S1 에너지 하나보다 엑시톤 반경,',
         lines=['OLED 계산에서는 S1 에너지 하나보다 엑시톤 공간폭, 위상 패턴, phonon에 의한 국소화 시간까지 검증 목표로 삼을 수 있다.']),
    dict(id='closed-system-includes-leakage', page=2, rect=(63.8,199.3,535.0,222.0), x=64.27559, y=206.62367, size=7.8, leading=11.4, color=5858681, bold_prefix='검증 경계 · ',
         find='closed-system infidelity는 재료 결함, 제어 전자장치, leakage, calibration drift를 포함한',
         lines=['검증 경계 · 폐쇄계 gate infidelity는 모델 안의 leakage와 위상 오차를 포함한다. decoherence는 별도 추정이며, 칩 제작·QPU 실험,',
                '제어 전자장치와 calibration drift의 장치 검증은 남아 있다.']),
    dict(id='single-parameter-ode-scope', page=2, rect=(63.8,340.7,535.0,367.8), x=64.27559, y=349.22366, size=9.2, leading=14.2, color=1911097,
         find='최적화가 1차 ODE 풀이로 줄어들며, spin-based state initialization과 qubit state transfer',
         lines=['metric과 지수를 정하면 펄스 생성이 1차 ODE 풀이로 줄어든다. spin-based state initialization과 qubit state transfer',
                '예제로 adiabatic·diabatic 오류 사이의 절충을 보였다.']),
    dict(id='noise-and-grape-analysis', page=2, rect=(63.8,373.9,535.0,396.6), x=64.27559, y=381.22369, size=7.8, leading=11.4, color=5858681, bold_prefix='검증 경계 · ',
         find='이론·수치 예제이며 실제 장치의 noise와 calibration 비용은 검증하지 않았다.',
         lines=['검증 경계 · 보충자료는 전하·스핀 dephasing의 Lindblad 분석과 특정 DQD 조건의 GRAPE 실행시간 비교를 제시했다. 실제 장치의',
                'calibration 비용은 검증하지 않았다. Classiq·AshN과는 서로 다른 제어 층을 다룬다.']),
    dict(id='source6-study-type', page=3, rect=(144.0,601.0,390.9,611.0), x=144.69807, y=607.92371, size=7.3, color=1911097,
         find='검토했으나 실제 실험이 아닌 제안·시뮬레이션이므로 핵심 5건에는 포함하지 않음.',
         lines=['제안·시뮬레이션 연구.']),
    dict(id='bibliographic-correction-heading', page=3, rect=(59.4,628.3,538.8,644.0), x=59.85827, y=639.02368, size=11.6, color=1057599, bold=True,
         find='조사 범위와 한계', lines=['참고문헌 표기 보완 · 2026-11-12']),
    dict(id='bibliographic-correction-record', page=3, rect=(59.4,647.9,538.8,788.0), x=59.85827, y=655.22363, size=7.8, leading=11.4, color=5858681,
         find='공개 웹과 연결된 Gmail을 기준으로 확인했다.',
         lines=['[2] M. Theilen, S. Kaidisch, M. Stettner, S. Zajusch, E. Fackelman, A. Adamkiewicz, R. Wallauer, A. Windischbacher,',
                'C. S. Kern, M. G. Ramsey, F. C. Bocquet, S. Soubatch, F. S. Tautz, U. Höfer, and P. Puschnig.',
                '[3] E. Fitzner, B. Lee, J. Hur, M. Kim, B. Schneider, J.-y. Choi, and B. Sbierski.',
                '[4] L. Heunisch, L. Huang, T. Eckstein, S. Tasler, J. Schirk, F. Wallner, V. Feulner, B. Sarma, K. Liegener,',
                'C. M. F. Schneider, S. Filipp, and M. J. Hartmann.',
                '[5] C. Ventura-Meinersen, E. Valvo, S. Bosco, and M. Rimbach-Russ.',
                '정식 출판본 제목: [4] Scalable fluxonium-transmon architecture for error-corrected quantum processors;',
                '[5] Multilevel spectral navigation with geometric diabatic-adiabatic control.',
                '위 논문의 발행일은 2026-08-28이다. 본문은 2026-08-31의 근거 범위를 유지하며 출판본·보충자료와 대조했다.',
                '원저자 보고 수치는 재계산하지 않았다.'])
]
FORBIDDEN_ACTION = re.compile(rb'/(?:OpenAction|AA|JavaScript|JS|Launch|GoToR|SubmitForm|ImportData|EmbeddedFiles|RichMedia|XFA)\b')
PRIVATE_TEXT = re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|/(?:Users|home|tmp)/|[A-Za-z]:\\(?:Users|Temp)\\|(?:access_token|refresh_token|api_key)\s*[:=]', re.I)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bitmap(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def outside_words(page, regions):
    return Counter(tuple(round(v, 3) for v in word[:4]) + (word[4],)
                   for word in page.get_text('words')
                   if not any(fitz.Rect(word[:4]).intersects(fitz.Rect(r)) for r in regions))


def links(page):
    return sorted((a.get('kind'), a.get('uri', ''), tuple(round(v, 3) for v in a['from'])) for a in page.get_links())


def rgb(color):
    return tuple(((color >> shift) & 255) / 255 for shift in (16, 8, 0))


def text_font_buffer(path, text):
    # Subset before PDF insertion so the generated ToUnicode map contains only
    # the actual document characters, including no unrelated non-BMP mappings.
    font = TTFont(path, recalcTimestamp=False)
    if 'glyf' not in font:
        raise ValueError('Use a Korean TrueType font with glyf outlines')
    options = subset.Options()
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text=text)
    subsetter.subset(font)
    data = BytesIO()
    font.save(data)
    return data.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, default=TOPIC / 'artifacts/daily_quantum_brief_2026-08-31.pdf')
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--qa-dir', type=Path, required=True)
    parser.add_argument('--font-regular', type=Path, required=True)
    parser.add_argument('--font-bold', type=Path, required=True)
    args = parser.parse_args()
    if any(p.resolve().is_relative_to(REPOSITORY.resolve()) for p in (args.source, args.qa_dir)):
        raise ValueError('Source and QA must remain outside the public repository')
    raw = args.source.read_bytes()
    if sha(raw) != SOURCE_SHA256:
        raise ValueError('Unexpected historical source PDF')
    source, public = fitz.open(stream=raw, filetype='pdf'), fitz.open(stream=raw, filetype='pdf')
    if len(source) != 4:
        raise ValueError('Expected four historical pages')
    required_text = ''.join(line for item in EDITS for line in item['lines'])
    buffers = {kind: text_font_buffer(path, required_text) for kind, path in [('regular', args.font_regular), ('bold', args.font_bold)]}
    fonts = {kind: fitz.Font(fontbuffer=data) for kind, data in buffers.items()}
    for kind, font in fonts.items():
        if any(not font.has_glyph(ord(c)) for c in required_text if not c.isspace()):
            raise ValueError(f'Missing document glyph in {kind} font')
    regions = {i: [] for i in range(4)}
    removed = []
    for item in EDITS:
        page = source[item['page']]
        if item['find'] not in page.get_text():
            raise ValueError(f"Historical anchor missing: {item['id']}")
        regions[item['page']].append(item['rect'])
        removed.append({'id': item['id'], 'page': item['page'] + 1, 'original': page.get_textbox(fitz.Rect(item['rect']))})
        public[item['page']].add_redact_annot(fitz.Rect(item['rect']), fill=None)
    for page in public:
        page.apply_redactions(images=0, graphics=0, text=0)
    for item in EDITS:
        page = public[item['page']]
        for kind, data in buffers.items():
            page.insert_font(fontname='Public' + kind.title(), fontbuffer=data)
        for index, line in enumerate(item['lines']):
            x, y = item['x'], item['y'] + index * item.get('leading', item['size'] * 1.4)
            runs = [('bold' if item.get('bold') else 'regular', line)]
            if index == 0 and item.get('bold_prefix'):
                prefix = item['bold_prefix']
                if not line.startswith(prefix):
                    raise ValueError('Expected styled prefix')
                runs = [('bold', prefix), ('regular', line[len(prefix):])]
            total = sum(fonts[k].text_length(t, fontsize=item['size']) for k, t in runs)
            if x + total > item['rect'][2] or y + 0.35 * item['size'] > item['rect'][3]:
                raise ValueError(f"Replacement exceeds declared area: {item['id']} line {index + 1}")
            for kind, text in runs:
                page.insert_text((x, y), text, fontname='Public' + kind.title(), fontsize=item['size'], color=rgb(item['color']))
                x += fonts[kind].text_length(text, fontsize=item['size'])
    public.set_metadata({'title': source.metadata.get('title', ''), 'author': 'AI Tech Review',
                         'subject': 'Original publication 2026-08-31; source-comparison corrections 2026-11-12',
                         'keywords': '', 'creator': '', 'producer': '', 'creationDate': '', 'modDate': ''})
    public.del_xml_metadata()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    public.subset_fonts()
    identifier = sha((SOURCE_SHA256 + ':narrow-source-corrections-2026-11-12-v1').encode())[:32]
    public.xref_set_key(-1, 'ID', f'[<{identifier}><{identifier}>]')
    public.save(args.output, garbage=4, deflate=True, clean=True, no_new_id=True)
    public.close()
    public = fitz.open(args.output)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    checks = []
    for number, (before, after) in enumerate(zip(source, public)):
        a, b = bitmap(before), bitmap(after)
        a.save(args.qa_dir / f'original-{number + 1}.png')
        b.save(args.qa_dir / f'public-{number + 1}.png')
        for r in regions[number]:
            pixels = (math.floor(r[0]*2), math.floor(r[1]*2), math.ceil(r[2]*2), math.ceil(r[3]*2))
            ImageDraw.Draw(a).rectangle(pixels, fill='white')
            ImageDraw.Draw(b).rectangle(pixels, fill='white')
        difference = ImageChops.difference(a, b)
        if difference.getbbox():
            difference.save(args.qa_dir / f'outside-edit-difference-{number + 1}.png')
        check = {'page': number + 1, 'declared_edit_rectangles_pt': regions[number],
                 'pixels_identical_outside_edits_144dpi': difference.getbbox() is None,
                 'text_and_positions_identical_outside_edits': outside_words(before, regions[number]) == outside_words(after, regions[number]),
                 'all_uri_annotations_and_positions_preserved': links(before) == links(after),
                 'page_geometry_preserved': before.rect == after.rect}
        if not all(v for k, v in check.items() if k not in ('page', 'declared_edit_rectangles_pt')):
            raise ValueError(f'Unexpected change: {check}')
        checks.append(check)
    text = '\n'.join(p.get_text() for p in public)
    normalized = text.replace('\xa0', ' ').replace('‑', '-')
    forbidden = ('메일', 'Gmail', 'LinkedIn', '지난 실행', '최근 24시간', '소셜 신호', '계정 활성화', '반경')
    active, object_count, stream_count = [], 0, 0
    for xref in range(1, public.xref_length()):
        data = public.xref_object(xref, compressed=False).encode()
        object_count += 1
        if public.xref_is_stream(xref):
            data += b'\n' + public.xref_stream(xref)
            stream_count += 1
        if FORBIDDEN_ACTION.search(data):
            active.append(xref)
    uris = [a['uri'] for p in public for a in p.get_links()]
    inspection = {'all4pages_retained': len(public) == 4,
                  'public_journal_author_preserved': public.metadata.get('author') == source.metadata.get('author') == 'AI Tech Review',
                  'exact_production_timestamps_removed': not public.metadata.get('creationDate') and not public.metadata.get('modDate'),
                  'no_collection_or_run_status_text': not any(t in text for t in forbidden),
                  'no_private_text_or_paths': not PRIVATE_TEXT.search(text + json.dumps(public.metadata, ensure_ascii=False)),
                  'no_xml_metadata': public.xref_xml_metadata() == 0,
                  'no_embedded_files': public.embfile_count() == 0,
                  'no_widgets': all(not list(p.widgets() or ()) for p in public),
                  'no_active_actions_in_objects_or_decoded_streams': not active,
                  'no_null_or_replacement_glyphs': '\x00' not in text and '\ufffd' not in text,
                  'all11public_https_links_retained': len(uris) == 11 and all(u.startswith('https://') for u in uris),
                  'original_and_revision_dates_distinct': all(t in normalized for t in ('원발행·근거 기준일은 2026-08-31', '2026-11-12')),
                  'gibbs_perturbative_scope_corrected': '섭동적으로 논의하고 혼합시간 의존성을 분석했다' in normalized,
                  'exciton_width_corrected': text.count('FWHM_x') == 2,
                  'diad_noise_and_baseline_recorded': all(t in text for t in ('dephasing', 'Lindblad', 'GRAPE')),
                  'closed_infidelity_includes_leakage': '모델 안의 leakage와 위상 오차를 포함한다' in normalized,
                  'scientific_checklist_preserved': all(t in text for t in ('한계·검증 체크리스트', 'Pareto front', 'finite-size', 'Gibbs-state fidelity')),
                  'source_citations_preserved': all(t in text for t in ('[1]', '[2]', '[3]', '[4]', '[5]', '[6]'))}
    if not all(inspection.values()):
        raise ValueError(inspection)
    strict = PdfReader(args.output, strict=True)
    if len(strict.pages) != 4 or any(not p.extract_text().strip() for p in strict.pages):
        raise ValueError('Strict PDF parsing failed')
    refs = {(n, g) for g, objects in strict.xref.items() for n in objects if n != 0}
    refs |= {(n, 0) for n in strict.xref_objStm}
    strict_objects, strict_streams = 0, 0
    for n, g in sorted(refs):
        obj = strict.get_object(IndirectObject(n, g, strict))
        strict_objects += 1
        if isinstance(obj, StreamObject):
            obj.get_data()
            strict_streams += 1
    report = {'date': '2026-11-12', 'operation': 'Narrow privacy and source-comparison corrections to historical 2026-08-31 DQB',
              'original_publication_date': '2026-08-31', 'evidence_cutoff_retained': '2026-08-31',
              'source_sha256': SOURCE_SHA256, 'public_sha256': sha(args.output.read_bytes()),
              'font_subset_sha256': {kind: sha(data) for kind, data in buffers.items()},
              'source_pages': 4, 'public_pages': len(public), 'public_bytes': args.output.stat().st_size,
              'declared_edit_ids': [e['id'] for e in EDITS], 'page_checks': checks,
              'uri_annotation_count': len(uris), 'unique_source_urls': sorted(set(uris)),
              'all_content_outside_declared_edits_preserved': True, 'whole_body_rewritten': False,
              'scientific_claims_narrowly_corrected': ['Gibbs fixed-point error scaling discussed perturbatively together with mixing-time dependence', 'Exciton Gaussian amplitude spatial width FWHM_x',
                'Closed-system gate infidelity includes modeled leakage and phase error; decoherence separately estimated',
                'Single-control ODE constructs a pulse after metric/exponent selection',
                'Published SI contains Lindblad noise and specific GRAPE runtime comparisons'],
              'collection_context_removed': True, 'public_AI_Tech_Review_author_preserved': True,
              'bibliographic_supplement': 'Full author lists for references 2–5 and published titles for references 4–5 supplement historical abbreviated entries; original reference positions and links retained',
              'exact_production_timestamps_removed': True, 'inspection': inspection,
              'strict_reader': {'library': 'pypdf', 'strict': True, 'all4pages_readable': True,
                'all_indirect_objects_resolved': strict_objects, 'all_streams_decoded': strict_streams},
              'pdf_structure': {'objects_inspected': object_count, 'decoded_streams_inspected': stream_count},
              'visual_qa': {'status': 'pending_root_review', 'editor_read_all_original4pages': True,
                'all_public4pages_rendered': True, 'human_reader_test': False},
              'independent_reproduction': False, 'research_code_or_experiment_executed': False}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (args.qa_dir / 'public.txt').write_text(text)
    (args.qa_dir / 'removed-lines-private.json').write_text(json.dumps(removed, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'public_sha256': report['public_sha256'], 'pages': 4, 'bytes': report['public_bytes'], 'uri_annotations': 11, 'checks_passed': True}))


if __name__ == '__main__':
    main()
