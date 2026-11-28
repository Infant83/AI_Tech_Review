"""Typeset the reviewed Korean T-gate explainer from its preserved manuscript.

Supply licensed source fonts explicitly; no private font path is stored here.
The identical HTML is the source for the screen proof and printed PDF.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import html
import json
import re
import shutil
import unicodedata

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
DIST = ROOT / 'dist'
TITLE = '양자컴퓨터는 왜 T 게이트를 아끼려 할까'
SUBTITLE = '45도의 위상 변화에서 양자화학의 계산 비용까지'
DATE = '2026-11-28'
URLS = [
    'https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.TGate',
    'https://arxiv.org/abs/quant-ph/9807006',
    'https://doi.org/10.1103/PhysRevA.71.022316',
    'https://arxiv.org/abs/1403.2975v3',
    'https://arxiv.org/abs/2611.33509v1',
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def esc(text):
    return html.escape(text, quote=True)


def model_sentence():
    settings = []
    for filename, label in [
        ('ai-model-provenance-authoring.json', '저술'),
        ('ai-model-provenance-source-review.json', '원문 대조·과학 감수'),
        ('ai-model-provenance-pdf-final.json', 'PDF 조판·검수'),
    ]:
        path = ART / filename
        if filename == 'ai-model-provenance-pdf-final.json' and not path.exists():
            path = ART / 'ai-model-provenance-pdf-start.json'
        data = json.loads(path.read_text())
        assert len(data['roles']) == 1
        record = data['roles'][0]
        assert record['evidence_kind'] == 'turn_context'
        settings.append(f"{label}: {record['model_id']}, 추론 강도 {record['reasoning_effort']}")
    return ' / '.join(settings) + '. 각 역할의 대화 설정 기록으로 확인했다.'


def inline(text):
    text = esc(text.replace('–', '-').replace('—', ' - '))
    text = re.sub(r'e\^\(iπ/4\)', 'e<sup>iπ/4</sup>', text)
    links = {
        'T 게이트의 정의': 1,
        '안정자 연산에 대한 Gottesman의 해설': 2,
        '마법 상태와 보편적 양자계산': 3,
        '회전의 Clifford+T 합성': 4,
        'ELOTE 원논문': 5,
    }
    for label, n in links.items():
        text = re.sub(r'\[' + re.escape(label) + r'\]\([^)]+\)',
                      f'<a class="cite" href="#ref-{n}" role="doc-biblioref">[{n}]</a>', text)
    # Keep mathematical labels together while leaving the Korean prose flexible.
    text = text.replace('T₉₅', '<span class="nowrap">T<sub>95</sub></span>')
    for term in ['85.35%', '85.4%', '14.6%', 'Clifford+T', '1kcal/mol', '1.6mHa']:
        text = text.replace(term, '<span class="nowrap">' + term + '</span>')
    return text


def document():
    source = (ROOT / 'reports' / 'review_ko.md').read_text()
    prose, bibliography = source.split('\n참고문헌\n', 1)
    paragraphs = prose.strip().split('\n\n')
    assert paragraphs[0] == '# ' + TITLE and paragraphs[1] == SUBTITLE
    headings = {
        '큐비트는 0과 1을': '45도의 차이가 간섭을 바꾼다',
        '이 작은 위상 변화는': 'T가 더해지면 가능한 연산이 넓어진다',
        '이 작은 회전의 구현 비용은': '오류정정이 붙이는 구현 비용',
        '양자화학에서 이 비용이': '분자의 에너지를 회전으로 계산한다',
        '이제 ELOTE의 질문이': '필요한 정확도에 맞추어 T를 아낀다',
    }
    body = []
    for paragraph in paragraphs[2:]:
        for prefix, heading in headings.items():
            if paragraph.startswith(prefix):
                body.append('<h2>' + heading + '</h2>')
        if paragraph.startswith('(|0⟩'):
            body.append('<div class="equation" aria-label="T 게이트가 두 성분의 크기를 유지하며 1 성분의 상대위상을 45도 바꾼다">'
                        '<span class="frac"><span>|0⟩ + |1⟩</span><span>√2</span></span>'
                        '<span class="eq-arrow"> →<small>T</small> </span>'
                        '<span class="frac"><span>|0⟩ + e<sup>iπ/4</sup>|1⟩</span><span>√2</span></span></div>')
        else:
            body.append('<p>' + inline(paragraph) + '</p>')
        if paragraph.startswith('이 작은 위상 변화는'):
            body.append('<figure id="figure-1"><img src="t-gate-interference.png" alt="H-위상-H 회로에서 위상은 45도 변하고, 마지막 H 뒤에 0을 측정할 확률은 약 85.4퍼센트가 된다. 가운데 위상을 0도에서 180도까지 바꾼 교육 계산.">'
                        '<figcaption><b>그림 1.</b> H-위상-H 회로에서 상대위상이 측정 확률로 이어지는 과정. 왼쪽 원은 두 진폭의 상대위상을 나타내며, 오른쪽은 '
                        'P(0)=[1+cosφ]/2다. 이상적인 한 큐비트의 자체 교육 계산으로, 게이트 행렬의 곱과 해석식을 대조했다.</figcaption></figure>')
    refs = []
    for line in bibliography.strip().splitlines():
        n = int(re.match(r'\[(\d+)\]', line)[1])
        content = re.sub(r'^\[\d+\]\s*', '', line)
        if n == 3:
            content = content.replace('Phys. Rev. A 71, 022316 (2005).', '<a href="' + URLS[n-1] + '">Phys. Rev. A <b>71</b>, 022316 (2005)</a>.')
        elif n == 4:
            content = content.replace('Quantum Information and Computation 16, 901 (2016).', '<a href="' + URLS[n-1] + '">Quantum Information and Computation <b>16</b>, 901 (2016)</a>.')
        else:
            content = '<a href="' + URLS[n-1] + '">' + esc(content) + '</a>'
        refs.append(f'<p id="ref-{n}"><span class="ref-n">[{n}]</span>{content}</p>')
    related = '<aside class="related"><h2>함께 읽을 글</h2><p><a href="https://infant83.io/AI_Tech_Review/reviews/2026-11-04_quantum-gates-phase-and-interaction/">양자 게이트·위상·큐비트 상호작용 해설</a>에서 회로의 작동을 더 살펴보고, '
    related += '<a href="https://infant83.io/AI_Tech_Review/reviews/2026-11-24_quantum-algorithms-principles-applications/">양자 알고리즘의 원리와 활용</a>에서 이 연산들이 어떤 문제에 쓰이는지 이어 읽을 수 있다.</p></aside>'
    disclosure = '<aside class="production"><h2>작성·검증 정보</h2><p><b>책임 편집</b> 김현중 · <b>AI 보조</b> OpenAI Codex · <b>제1판</b> 2026-11-28</p><p>'
    disclosure += esc(model_sentence()) + '</p><p>편집자의 주제·집필·PDF 제작·게시 요청에 따라 작성했다. 원문 대조 담당은 원논문과 공식 코드의 조건·지표를 확인했고, 저술 담당은 쉬운 설명과 자체 교육 그림을 구성했다. 제작 담당은 수식·서체·전 페이지 조판과 링크를 검수했다. 그림의 확률은 게이트 행렬 계산과 해석식을 대조했으며, ELOTE 수치는 원저자의 고전 검증·논리 자원 추정 결과다. ELOTE 벤치마크를 독립 재실행하거나 별도 사람의 문장별 감수를 수행한 기록은 없다.</p></aside>'
    return ''.join(body), ''.join(refs), related, disclosure

def main():
    parser = argparse.ArgumentParser()
    for name in ['regular', 'bold', 'symbols', 'math']:
        parser.add_argument('--' + name + '-font', type=Path, required=True)
    args = parser.parse_args()
    source = (ROOT / 'reports' / 'review_ko.md').read_text()
    # HTML is assembled here so prose remains a reviewable, separate source.
    code = Path(__file__).read_text()
    all_text = source + code + model_sentence()
    codepoints = {ord(c) for c in all_text if not unicodedata.category(c).startswith('C')}
    codepoints |= {n for n in range(32, 256) if not unicodedata.category(chr(n)).startswith('C')}
    paths = {name: getattr(args, name + '_font') for name in ['regular', 'bold', 'symbols', 'math']}
    coverage = {name: set(TTFont(p).getBestCmap()) for name, p in paths.items()}
    missing = codepoints - coverage['regular']
    symbol_needed = missing & coverage['symbols']
    math_needed = missing - symbol_needed
    assert not math_needed - coverage['math'], sorted(math_needed - coverage['math'])
    css_fonts = []
    records = []
    for name in ['regular', 'bold', 'symbols', 'math']:
        font = TTFont(paths[name]); font.recalcTimestamp = False
        needed = codepoints & coverage[name] if name in ['regular', 'bold'] else (symbol_needed if name == 'symbols' else math_needed)
        worker = subset.Subsetter(options=subset.Options(recalc_timestamp=False))
        worker.populate(unicodes=needed | {32}); worker.subset(font); font.flavor = 'woff2'
        family = 'TGateSans' if name in ['regular', 'bold'] else 'TGateSymbols' if name == 'symbols' else 'TGateMath'
        weight = 700 if name == 'bold' else 400
        family_name = 'ATRL TGate Sans Subset' if name in ['regular', 'bold'] else 'ATRL TGate Symbols Subset' if name == 'symbols' else 'ATRL TGate Math Subset'
        style_name = 'Bold' if name == 'bold' else 'Regular'
        names = {1: family_name, 2: style_name, 3: family_name.replace(' ', '') + '-' + style_name,
                 4: family_name + ' ' + style_name, 6: family_name.replace(' ', '') + '-' + style_name,
                 16: family_name, 17: style_name}
        for record in font['name'].names:
            if record.nameID in names:
                record.string = names[record.nameID].encode(record.getEncoding())
        path = ART / ('font-' + name + '.woff2'); font.save(path)
        data = path.read_bytes()
        records.append({'kind': name, 'source_filename': paths[name].name, 'source_sha256': sha(paths[name].read_bytes()), 'subset_sha256': sha(data), 'codepoints': sorted(needed)})
        css_fonts.append(f'@font-face{{font-family:{family};font-weight:{weight};src:url(data:font/woff2;base64,{base64.b64encode(data).decode()}) format("woff2");font-display:block}}')
    body, refs, related, disclosure = document()
    css = '''*{box-sizing:border-box}html{color:#193f45;background:#faf9f3}body{margin:0;font-family:TGateSans,TGateSymbols,TGateMath,sans-serif;font-size:17px;line-height:1.85}.paper{max-width:850px;margin:auto;padding:44px 38px}.series{font-size:10px;letter-spacing:.12em;color:#397473;margin-bottom:17px}.title{font-size:34px;line-height:1.3;letter-spacing:-.035em;margin:0 0 12px}.dek{font-size:19px;color:#397473;margin:0 0 14px}.byline{font-size:11px;color:#5e706e;border-bottom:1px solid #ccd8d2;padding-bottom:15px;margin:0 0 25px}p{margin:0 0 17px;word-break:keep-all;overflow-wrap:break-word}h2{font-size:22px;line-height:1.4;margin:33px 0 13px;letter-spacing:-.02em;break-after:avoid}a{color:#236f73;text-decoration-thickness:.6px;text-underline-offset:3px}.cite{font-size:.78em;vertical-align:super;white-space:nowrap;text-decoration:none}figure{margin:24px 0 30px;break-inside:avoid}figure img{width:100%;height:auto;display:block}figcaption{font-size:11px;line-height:1.65;color:#5a6e6b;padding-top:10px}.equation{display:flex;justify-content:center;align-items:center;gap:22px;padding:19px 10px;margin:23px 0 24px;background:#eef2eb;border-top:1px solid #d1ddd4;border-bottom:1px solid #d1ddd4;font-size:21px;break-inside:avoid}.frac{display:inline-flex;flex-direction:column;align-items:center}.frac>span:first-child{border-bottom:1px solid #193f45;padding:0 7px 5px}.frac>span:last-child{padding-top:4px}.eq-arrow{position:relative}.eq-arrow small{position:absolute;left:.35em;top:-1.1em;font-size:.65em}sup{font-size:.72em}sub{font-size:.7em}.nowrap{white-space:nowrap}.references{font-size:12px;line-height:1.7}.references p{position:relative;padding-left:32px;margin-bottom:11px;break-inside:avoid}.ref-n{position:absolute;left:0;top:0}.references a{overflow-wrap:anywhere}.related{border-top:1px solid #ccd8d2;margin-top:26px;padding-top:12px;font-size:12px;line-height:1.7}.related h2{font-size:16px;margin:0 0 8px}.production{background:#eef2eb;margin-top:24px;padding:15px 18px;font-size:11px;line-height:1.65;break-inside:avoid}.production h2{font-size:15px;margin:0 0 8px}.production p{margin-bottom:7px}.production p:last-child{margin:0}
@media(max-width:600px){.paper{padding:30px 21px}.title{font-size:29px}.dek{font-size:18px}.equation{font-size:17px;gap:14px}.references{font-size:11px}}
@media print{@page{size:A4;margin:16mm 17mm 19mm}html,body{background:#fff}body{font-size:10pt;line-height:1.68}.paper{max-width:none;margin:0;padding:0}.series{font-size:7pt;margin-bottom:10pt}.title{font-size:25pt;line-height:1.3;margin-bottom:10pt}.dek{font-size:12pt;line-height:1.5;margin-bottom:10pt}.byline{font-size:7pt;line-height:1.6;padding-bottom:10pt;margin-bottom:17pt}p{margin-bottom:9pt;orphans:3;widows:3}h2{font-size:14.5pt;margin:18pt 0 9pt}h2+p{break-inside:avoid}.equation{font-size:15pt;padding:10pt;margin:13pt 0 16pt}.equation .frac>span:first-child{padding-bottom:2pt}.equation .frac>span:last-child{padding-top:2pt}figure{margin:12pt 0 16pt}figcaption{font-size:7.5pt;line-height:1.6;padding-top:6pt}.references{font-size:8pt;line-height:1.65}.references p{margin-bottom:7pt;padding-left:24pt}.related{font-size:8pt;line-height:1.65;margin-top:14pt;padding-top:9pt}.related h2{font-size:10pt}.production{font-size:7.4pt;line-height:1.55;margin-top:13pt;padding:10pt 12pt}.production h2{font-size:10pt}.production p{margin-bottom:5pt}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
'''
    result = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + TITLE + '</title><meta name="author" content="김현중"><style>' + '\n'.join(css_fonts) + css + '</style></head><body><main class="paper"><div class="series">AGENTIC TECH REVIEW LETTERS · LECTURE NOTES · 2026-11-28</div><h1 class="title">' + TITLE + '</h1><p class="dek">' + SUBTITLE + '</p><p class="byline">책임 편집 김현중 · AI 보조 OpenAI Codex · 원문·계산 대조 2026-11-28</p>' + body + '<h2 id="references">참고문헌</h2><div class="references">' + refs + '</div>' + related + disclosure + '</main></body></html>'
    assert '/Users/' not in result and 'file://' not in result
    (DIST / 'index.html').write_text(result)
    (ART / 'font-coverage.json').write_text(json.dumps({'source_sha256': sha(source.encode()), 'missing_codepoints': [], 'fonts': records}, ensure_ascii=False, indent=2) + '\n')
    (ART / 'production-html-manifest.json').write_text(json.dumps({'title': TITLE, 'language': 'ko', 'date': DATE, 'html_sha256': sha(result.encode()), 'figure_count': 1, 'references': 5}, ensure_ascii=False, indent=2) + '\n')
    print('Built Korean print/source HTML with complete font coverage.')


if __name__ == '__main__':
    main()
