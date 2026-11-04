"""Prepare the reviewed 114-page lecture manuscript and self-contained HTML.

Inputs remain private. Only the original course text, illustrations and public
references are retained; collection context and a conversation reference are
removed. This command does not register documents or deploy the website.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import fitz
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_ID = '2026-11-04-quantum-computing-applications-lecture-notes-ko'
SOURCE_HASH = 'a47a036ea1a2d55b61ef93ef1e854d036b3f967e243d6ba7ecee6ceb64f5bff5'
INTRO = '시즌 1의 01–08회차를 한 권으로 묶은 한국어 학습 자료다. 01·02회차의 원문과 후속 회차를 연결했으며, 각 회차의 가정·계산 범위와 학습 과제를 함께 수록했다.'
SYNTHETIC = '교육용 예제는 12개 검증분자를 가정한다. 큰 활성공간의 충분히 검증된 고전 다중참조 계산을 문제 안의 참조로 사용한다. 그 참조도 모델 계산이며, 실험적 진실과 동일하다는 뜻은 아니다.'
EDITION = ('공개 보관본 · 2026-11-04 · 책임 편집자 김현중 · AI 보조 OpenAI Codex. '
           '원판의 학습 내용·수식·출처를 보존하며 내부 편집 경위와 대화 자료는 제외했다. '
           '일괄 재사용 라이선스를 추가하지 않으며, 문헌의 원문 그림·표를 복제한 자료가 아니다.')
PUBLIC_NOTE = ('S1 · 교육용 합성 입력과 공개판 안내\n'
              '첫 TADF 사례의 12개 가상 검증분자와 오차·시간 수치는 교육용 합성 입력이다. 실제 분자 관측이나 성능 벤치마크로 해석하지 않는다.\n\n'
              '책임 편집자 김현중 · AI 보조 OpenAI Codex. 원 작성 세션의 정확한 모델·에이전트 식별자는 미보존이다. '
              '이번 공개 등록에서 root가 정제·게재를, public_pdf_qa가 별도의 본문·출처·출력 검수와 대표 식 부분검산을 수행했다.\n\n'
              '원판의 오프라인 예제 검증 기록과 이번 공개 검수를 구분한다. 원판의 소스 ZIP 전체와 188개 조건을 이번 등록에서 독립 재실행한 것은 아니다. '
              '실제 QPU·분자 실험이나 사람의 문장별 전체 감수도 수행하지 않았다.\n\n'
              '원판의 회차별 작성일·초안 표기는 그 판본의 제작 이력으로 보존했다. 공개 보관본의 등록일은 2026-11-04다. '
              'AI Tech Review Editorial Harness 2026.08 · 과학 설명 준칙 1.0.')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--font', type=Path, required=True)
    args = parser.parse_args()
    pdf = args.source_dir / 'quantum-computing-lecture-series.pdf'
    assert digest(pdf) == SOURCE_HASH
    original = fitz.open(pdf)
    doc = fitz.open(pdf)
    assert len(doc) == 114
    operations = {
        0: [((47, 294, 548, 347), INTRO, 10.3)],
        1: [((47, 620, 548, 654), EDITION, 8.8),
            ((47, 264, 548, 316), '통합 HTML은 CSS·수식·그림을 포함한 단일 파일이며 인터넷 없이 읽을 수 있다. PDF는 같은 HTML에서 생성한 인쇄본이다. 아래 생성 명령은 원판의 소스 묶음을 위한 안내다. 소스 ZIP이 이 공개본에 포함되거나 그 전체 검증을 이번 등록에서 재실행했다는 뜻은 아니다.', 9.4)],
        4: [((47, 500.5, 548, 535), SYNTHETIC, 9.4)],
        12: [((76, 148, 548, 165), '문제의 가상 입력: 이 노트의 교육용 합성 예제.', 9.4)],
        101: [((47, 187.5, 548, 239), '아래 기록에는 원판에서 열람한 1차 논문·공식 문서의 서지 정보, 접근일과 지원하는 주장이 있다. 각 회차의 직접 유도·합성 입력·실행 결과는 별도로 구분한다.', 10.3),
              ((47, 403.5, 548, 420), '자체 교육용 예제와 설명·계산을 작성했으며 문헌의 원문 그림·표·문장을 복제하지 않았다.', 9.2),
              ((47, 466, 548, 687), PUBLIC_NOTE, 9.2)],
    }
    for number, ops in operations.items():
        page = doc[number]
        for rect, _, _ in ops:
            page.add_redact_annot(rect, fill=(1, 1, 1))
        page.apply_redactions(images=0, graphics=0)
        page.insert_font(fontname='PublicNanum', fontfile=str(args.font))
        for rect, text, size in ops:
            rest = page.insert_textbox(rect, text, fontname='PublicNanum', fontsize=size,
                                       lineheight=1.45, color=(.09, .18, .23))
            assert rest >= 0, (number + 1, rest)
    # Remove any remaining annotation to the excluded conversation source.
    for page in doc:
        for link in page.get_links():
            if link.get('uri', '').startswith('https://chatgpt.com/share/'):
                page.delete_link(link)
    doc.set_metadata({'title': '양자컴퓨팅 응용 렉처노트 · 시즌 1 완결본 · 공개 보관본',
                      'author': '김현중', 'creator': 'AI Tech Review; OpenAI Codex-assisted public archive',
                      'subject': 'Eight Korean lectures; educational synthetic examples; public edition 2026-11-04'})
    doc.del_xml_metadata()
    doc.subset_fonts()
    dist = ROOT / 'dist'
    dist.mkdir(parents=True, exist_ok=True)
    output = ROOT / 'output/pdf' / (DOCUMENT_ID + '.pdf')
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output, garbage=4, deflate=True, clean=True)
    (dist / 'notes.pdf').write_bytes(output.read_bytes())
    final = fitz.open(output)
    final_text = '\n'.join(p.get_text() for p in final)
    assert 'chatgpt.com/share/' not in final_text and '공유 대화' not in final_text
    original_uris = [l['uri'] for p in original for l in p.get_links() if 'uri' in l and not l['uri'].startswith('https://chatgpt.com/share/')]
    assert [l['uri'] for p in final for l in p.get_links() if 'uri' in l] == original_uris
    for i in range(114):
        def image(page):
            p = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            return Image.frombytes('RGB', (p.width, p.height), p.samples)
        delta = ImageChops.difference(image(original[i]), image(final[i]))
        draw = ImageDraw.Draw(delta)
        for rect, _, _ in operations.get(i, []):
            x0, y0, x1, y1 = rect
            draw.rectangle((math.floor(x0*1.5)-3, math.floor(y0*1.5)-3,
                            math.ceil(x1*1.5)+3, math.ceil(y1*1.5)+3), fill='black')
        assert delta.getbbox() is None, ('Unexpected change outside edited regions', i+1, delta.getbbox())
    html = (args.source_dir / 'quantum-computing-lecture-series.html').read_text()
    html, n = re.subn(r'<p>원래 주간 연재로 시작했지만,.*?</p>', '<p>'+INTRO+'</p>', html, count=1, flags=re.S)
    assert n == 1
    html = html.replace('공유 대화는 <strong>12개 검증분자</strong>를 가정한다.', '교육용 예제는 <strong>12개 검증분자</strong>를 가정한다.')
    html = re.sub(r'<li>문제의 의도·가상 입력: <a href="https://chatgpt.com/share/[^\"]+">.*?</a>\.</li>', '<li>문제의 가상 입력: 이 노트의 교육용 합성 예제.</li>', html)
    html = re.sub(r'<p>작성에는 AI 보조를 사용했다\..*?</p>', '<p>'+EDITION+'</p>', html, count=1, flags=re.S)
    html = re.sub(r'<p>2026-11-04 사용자의 요청으로 예정된.*?</p>', '<p>아래 기록에는 원판에서 열람한 1차 논문·공식 문서의 서지 정보, 접근일과 지원하는 주장이 있다. 각 회차의 직접 유도·합성 입력·실행 결과는 별도로 구분한다.</p>', html, count=1, flags=re.S)
    html = html.replace('공유 대화는 편집 의도와 가상 입력의 출처다. ', '')
    html, n = re.subn(r'<h2 id="source-index-s1-[^\"]+">.*?</ul>', '<h2 id="source-index-s1-사용자-제공-공유-대화">S1 · 교육용 합성 입력과 공개판 안내</h2><p>'+PUBLIC_NOTE.replace('\n\n', '</p><p>').replace('\n', '<br>')+'</p>', html, count=1, flags=re.S)
    assert n == 1
    html = html.replace('인터넷 없이 읽을 수 있다. 외부 인용 링크를 여는 경우에만 네트워크가 필요하다.', '인터넷 없이 읽을 수 있다. 외부 인용 링크를 여는 경우에만 네트워크가 필요하다. 이 공개본에는 PDF와 HTML을 제공하며 원판의 소스 ZIP은 포함하지 않는다. 아래 명령은 그 소스 묶음 전용 안내다.')
    assert 'chatgpt.com/share/' not in html and not re.search(r'<script\b|\son\w+=|<iframe\b', html, re.I)
    # Preserve fragment identity while replacing the displayed collection label.
    html = html.replace('<body>', '<body><nav class="publication-navigation" aria-label="강의 자료"><a href="../">렉처 노트</a> · <a href="../reader/?id='+DOCUMENT_ID+'">필기하며 읽기</a> · <a href="notes.pdf">PDF 읽기</a></nav>')
    html = html.replace('</style>', '.publication-navigation{max-width:950px;margin:20px auto;padding:0 22px;font-size:14px}.publication-navigation a{color:#236b72}@media print{.publication-navigation{display:none}}</style>', 1)
    (dist / 'index.html').write_text(html)
    notes = ROOT / 'notes'
    notes.mkdir(exist_ok=True)
    (notes / 'production-qa.json').write_text(json.dumps({'pages': 114, 'source_sha256': SOURCE_HASH,
        'public_sha256': digest(output), 'html_sha256': digest(dist/'index.html'),
        'unchanged_pixels_outside_edit_regions': True, 'official_external_links_preserved': len(original_uris),
        'edit_regions': {str(i+1): [list(x[0]) for x in ops] for i, ops in operations.items()},
        'source_examples_complete_rerun': False, 'final_visual_review': 'pending'}, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'pdf': output.name, 'sha256': digest(output), 'pages': 114}))


if __name__ == '__main__':
    main()
