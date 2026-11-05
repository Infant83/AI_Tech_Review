"""Create reviewed public PDFs; source messages and originals stay private.

No source ZIP is available. This script preserves the original educational
pages, removes two personalized phrases, replaces file-launch links with public
HTTPS references, and adds a distinct public-edition disclosure page.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

import fitz
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://infant83.io/AI_Tech_Review/'
UNITS = [
    ('001', '2026-11-01', 24, '5905a3c673dba3195074ab31a34a35407303702ea470b92803d9bf5ae7de7563', '고객의 질문을 계산 가능한 문제로'),
    ('002', '2026-11-03', 19, '0f285f71871eb1a0e596e366fb8dd84e23daf6ce3501188847df3454c1e9de1f', '복소 벡터에서 두 큐비트까지'),
    ('003', '2026-11-05', 18, '1336d9fed2c843342760b50205aa71a9c142406ee10779673692ec4966454117', '에너지를 재는 행렬은 어떻게 게이트가 되는가'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def document_id(unit, date):
    return f'{date}-classiq-qae-l{unit}-notes-ko'


def raster(page, scale=1.5):
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--font', required=True, type=Path)
    args = parser.parse_args()
    output_dir = ROOT/'output/pdf'
    dist = ROOT/'dist'
    qa = args.source_dir/'qa/public'
    for folder in [output_dir, dist, qa]:
        folder.mkdir(parents=True, exist_ok=True)
    names = {f'{date}_Classiq_QAE_Lecture{int(unit):02d}_KO_v1.pdf': document_id(unit, date)+'.pdf' for unit, date, *_ in UNITS}
    records = []
    for unit, date, pages, source_hash, title in UNITS:
        source = args.source_dir/f'{date}_Classiq_QAE_Lecture{int(unit):02d}_KO_v1.pdf'
        assert sha(source) == source_hash
        original, doc = fitz.open(source), fitz.open(source)
        assert len(doc) == pages
        regions = {i: [] for i in range(pages)}
        if unit == '001':
            rect = fitz.Rect(59, 119, 144, 134)
            doc[13].add_redact_annot(rect, fill=(1, 1, 1)); doc[13].apply_redactions(images=0, graphics=0)
            doc[13].insert_font(fontname='PublicNanum', fontfile=str(args.font))
            doc[13].insert_text((59.528, 129.629), '여기서 다루는', fontname='PublicNanum', fontsize=10.5, color=(.086,.209,.29))
            regions[13].append(list(rect))
        if unit == '003':
            rect = fitz.Rect(58, 775, 537, 791)
            doc[0].add_redact_annot(rect, fill=(1, 1, 1)); doc[0].apply_redactions(images=0, graphics=0)
            doc[0].insert_font(fontname='PublicNanum', fontfile=str(args.font))
            doc[0].insert_text((59.528, 785.197), 'SCM은 이 과정에서 계산화학 소프트웨어 회사와 AMS/ADF를 뜻한다.', fontname='PublicNanum', fontsize=9.5, color=(.32,.41,.45))
            regions[0].append(list(rect))
        cover = fitz.Rect(59, 536, 536, 630)
        doc[0].insert_font(fontname='PublicNanum', fontfile=str(args.font))
        note = ('공개 보관본 · 2026-11-05\n'
                'Classiq 공식 강의가 아닌 독립 학습 과정이다.\n'
                '원판의 소스 ZIP은 이 공개본에 포함되지 않는다.\n'
                '원판 검산 기록과 이번 공개 검수의 범위는 마지막 쪽에서 구분한다.')
        assert doc[0].insert_textbox(cover, note, fontname='PublicNanum', fontsize=9.5, lineheight=1.5, color=(.10,.30,.35)) >= 0
        regions[0].append(list(cover))
        rewritten = []
        original_uris = [l['uri'] for p in original for l in p.get_links() if 'uri' in l]
        for number, page in enumerate(doc):
            for link in page.get_links():
                if link['kind'] in (fitz.LINK_LAUNCH, fitz.LINK_GOTOR):
                    filename, sep, fragment = link.get('file', '').partition('#')
                    assert filename in names, ('Unreviewed external file action', filename)
                    uri = BASE+'archive/files/'+names[filename]+('#'+fragment if sep else '')
                    page.delete_link(link)
                    page.insert_link({'kind':fitz.LINK_URI,'from':link['from'],'uri':uri})
                    rewritten.append(dict(page=number+1, uri=uri))
        appendix = doc.new_page(width=595.276, height=841.89)
        appendix.insert_font(fontname='PublicNanum', fontfile=str(args.font))
        assert appendix.insert_textbox(fitz.Rect(55,60,540,115), 'L'+unit+' · 공개판 안내와 확인 범위', fontname='PublicNanum', fontsize=19, color=(.08,.21,.29)) >= 0
        disclosure = (
            '책임 편집자 김현중 · AI 보조 OpenAI Codex · 공개판 기준일 2026-11-05\n\n'
            '자료 성격\n'
            '공개 1차 교재·논문과 공식 Classiq 문서에 근거해 자체 집필한 한국어 학습 과정이다. '
            '공식 Classiq 교육·자격 인증이나 강사의 감수를 받은 자료로 표시하지 않는다. '
            'QAE는 Quantum Application Engineer이며 진폭 추정 알고리즘 AE/IQAE와 구별한다.\n\n'
            '원판과 공개본\n'
            f'원판 {pages}쪽의 수식·도표·문제·해설·용어색인·출처와 원래 쪽번호를 보존했다. '
            '개인화된 배경 표현은 일반 독자용 표현으로 정리하고 메타데이터를 정제했다. '
            '회차 간 파일 실행 동작을 공개 HTTPS PDF 링크로 바꾸었다. '
            '개인 메일·전달 경위·운영 시각과 원문 수집 파일은 수록하지 않았다.\n\n'
            '재현과 실행 범위\n'
            '본문의 numerical_checks.py·첨부 ZIP·32개 또는 41개 검산 등은 원판 제작 기록이다. '
            '원판 소스 ZIP은 이번 공개 묶음에 포함하지 않으며 그 검사 전체를 독립 재실행하지 않았다. '
            '공개 웹 입구의 reference_checks.py는 PDF에 보이는 작은 행렬·식에 대해 별도로 작성한 '
            'Python 표준 라이브러리 재계산이며 원판 소스의 대체본이 아니다. '
            'Classiq 합성·SDK·QPU 실행, 실제 분자·DFT·고객 데이터 계산은 이번 공개 작업에서도 하지 않았다.\n\n'
            '작성·검수 공개\n'
            '원 작성 세션의 정확한 실행 모델·에이전트 식별자는 미보존이다. '
            '이번 작업의 public_pdf_qa/auth_audit는 자료 확인·공개판 정제·부분검산·웹 학습 입구를 담당했다. '
            'root는 최종 통합·게시를 담당한다. 사람의 문장별 전체 감수나 Classiq의 승인을 받았다고 주장하지 않는다. '
            '원판 참고문헌의 실제 읽은 위치와 판본 기록은 원판 제작자의 기록으로 보존하며 '
            '이번 확인은 웹 입구의 별도 출처·검수 기록과 구분한다.\n\n'
            'AI Tech Review Editorial Harness 2026.08 · 과학 설명 준칙 1.0\n'
            '웹 학습 입구: infant83.io/AI_Tech_Review/lectures/classiq-qae-onboarding/'
        )
        assert appendix.insert_textbox(fitz.Rect(55,125,540,755), disclosure, fontname='PublicNanum', fontsize=10.1, lineheight=1.5, color=(.12,.20,.25)) >= 0
        web_line=appendix.search_for('infant83.io/AI_Tech_Review/lectures/classiq-qae-onboarding/')[0]
        appendix.insert_link({'kind':fitz.LINK_URI,'from':web_line,'uri':BASE+'lectures/classiq-qae-onboarding/'})
        doc.set_metadata(dict(title='Classiq QAE L'+unit+' · '+title+' · 공개 보관본',author='김현중',creator='AI Tech Review; OpenAI Codex-assisted public archive',subject='Independent Korean study notes; public edition 2026-11-05'))
        doc.del_xml_metadata(); doc.xref_set_key(doc.pdf_catalog(),'OpenAction','null'); doc.subset_fonts()
        doc.update_object(doc.pdf_catalog(),re.sub(r'\s*/OpenAction\s+null\b','',doc.xref_object(doc.pdf_catalog())))
        target = output_dir/(document_id(unit,date)+'.pdf')
        doc.save(target, garbage=4, deflate=True, clean=True)
        final = fitz.open(target)
        assert len(final) == pages+1
        for i in range(pages):
            diff = ImageChops.difference(raster(original[i]), raster(final[i])); draw=ImageDraw.Draw(diff)
            for x0,y0,x1,y1 in regions[i]:
                draw.rectangle((math.floor(x0*1.5)-3,math.floor(y0*1.5)-3,math.ceil(x1*1.5)+3,math.ceil(y1*1.5)+3), fill='black')
            assert diff.getbbox() is None, ('Unexpected rendering change',unit,i+1,diff.getbbox())
        links = [l['uri'] for p in final for l in p.get_links() if 'uri' in l]
        assert all(uri in links for uri in original_uris)
        objects='\n'.join(final.xref_object(i) for i in range(1,final.xref_length()))
        text='\n'.join(p.get_text() for p in final)
        assert not re.search(r'/S\s*/(?:Launch|JavaScript)|/OpenAction\b|/EmbeddedFile\b|/(?:Users|home|private)/|mailto:|chatgpt\.com/share/',objects)
        assert not re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',text+objects)
        assert '사용자가익숙한' not in text and '사용자배경의' not in text
        assert final.embfile_count()==0
        for i,page in enumerate(final):
            raster(page,.75).save(qa/f'L{unit}-page-{i+1:02d}.png')
        (dist/target.name).write_bytes(target.read_bytes())
        if unit=='003':(dist/'notes.pdf').write_bytes(target.read_bytes())
        records.append(dict(unit='L'+unit,date=date,title=title,source_pages=pages,public_pages=len(final),
                            source_sha256=source_hash,public_sha256=sha(target),file=target.name,
                            redaction_and_added_regions={str(k+1):v for k,v in regions.items() if v},
                            rewritten_links=rewritten,unchanged_original_page_regions_pixel_equal=True,
                            embedded_files=0,launch_or_script_actions=0))
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports/pdf-production-qa.json').write_text(json.dumps(dict(date='2026-11-05',units=records,source_zip_retrieved=False,original_validation_suite_rerun=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Prepared',len(records),'public PDFs;',sum(r['public_pages'] for r in records),'pages')


if __name__=='__main__':main()
