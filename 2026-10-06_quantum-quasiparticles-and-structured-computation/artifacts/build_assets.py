"""Original explanatory diagram, mathematical SVGs and a subset embedded font."""
from pathlib import Path
import base64
import html
import json
import re
import sys
import subprocess
from PIL import Image, ImageOps
from fontTools import subset
from matplotlib.mathtext import math_to_image

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
ART.mkdir(parents=True, exist_ok=True)

def diagram(lang):
    ko = lang == 'ko'
    labels = (
        [('전자계의 배경', '분극·상관을 유효량에 담는다'),
         ('GW / BSE 유효모형', '소수 전자–정공을 명시한다'),
         ('논리 회로와 출력', '모형의 고유값을 계산한다')]
        if ko else
        [('Electronic background', 'Encode response in effective quantities'),
         ('GW / BSE effective model', 'Keep a few electrons and holes explicit'),
         ('Logical circuit and output', 'Estimate eigenvalues of the model')]
    )
    checks = (
        [('모형의 물리오차', 'GW·차폐·TDA의 타당성'),
         ('입력의 준비비용', '상태의 겹침·대칭·인코딩'),
         ('총 계산비용', '회로·오류정정·반복·후처리')]
        if ko else
        [('Model error', 'Validity of GW, screening and TDA'),
         ('Preparation cost', 'Overlap, symmetry and encoding'),
         ('Total computational cost', 'Circuit, QEC, repetitions and readout')]
    )
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="510" viewBox="0 0 960 510" role="img">',
           '<title>Effective-model quantum computation: three separate checks</title>',
           '<rect width="960" height="510" fill="#f7faf8"/>',
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#116f79"/></marker></defs>',
           '<g font-family="Noto Sans KR,Arial,sans-serif" fill="#18313c">']
    def text(x, y, value, size=22, color='#18313c'):
        out.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{html.escape(value)}</text>')
    text(32, 47, '같은 계산 안에서도 검증은 세 갈래다' if ko else 'One computation, three distinct validation tasks', 29)
    for i, (a, b) in enumerate(labels):
        y = 76 + i * 134
        out.append(f'<rect x="32" y="{y}" width="455" height="111" rx="9" fill="#e5efeb" stroke="#a3c2ba"/>')
        text(53, y + 40, a, 26)
        text(53, y + 78, b, 21, '#58656d')
        if i < 2:
            out.append(f'<path d="M260 {y+115}V{y+132}" stroke="#116f79" stroke-width="2" marker-end="url(#arrow)"/>')
        c, d = checks[i]
        out.append(f'<path d="M496 {y+54}H530" stroke="#99aaa8" stroke-width="2"/>')
        text(550, y + 41, c, 25, '#116f79')
        text(550, y + 77, d, 20, '#58656d')
    text(32, 493, '설명용 도표 · 논문의 자원추정이나 새 실험 결과를 재현한 그림이 아니다.' if ko else 'Teaching diagram · not a reproduced resource estimate or new experiment.', 18, '#58656d')
    return ''.join(out) + '</g></svg>'

def main():
    if len(sys.argv) > 1:
        hero = Image.open(sys.argv[1]).convert('RGB')
        ImageOps.fit(hero, (1600, 900)).save(ART / 'hero.webp', quality=90, method=6)
    texts = ''.join(p.read_text() for p in (ROOT / 'reports').glob('review_*.md'))
    font_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    if font_path:
        options = subset.Options()
        font = subset.load_font(str(font_path), options)
        sub = subset.Subsetter(options=options)
        sub.populate(text=texts + '김현중 책임편집 검증 범위 AI 보조 공개 게시 요청 문장 단위 사람 검토 없음 한영 번역 연구 도표 참고 링크 과학 감수 독립 재현 아님 물리 모형 전전자 배경 분극 상관을 유효량에 담는다 소수 전자 정공을 명시한다 논리 회로와 출력 모형의 고유값을 계산한다 물리오차 차폐 타당성 입력의 준비비용 상태의 겹침 대칭 인코딩 총 계산비용 오류정정 반복 후처리 설명용 도표 논문의 자원추정이나 새 실험 결과를 재현한 그림이 아니다 같은 계산 안에서도 검증은 세 갈래다 ' + ''.join(chr(i) for i in range(32,127)))
        sub.subset(font)
        subset.save_font(font, str(ART / 'review-font.ttf'), options)
        font_data = base64.b64encode((ART / 'review-font.ttf').read_bytes()).decode()
        (ART / 'font.css').write_text('@font-face{font-family:"Review Sans";src:url(data:font/ttf;base64,' + font_data + ') format("truetype");font-weight:100 900;font-display:swap;}')
    expressions = {}
    for lang in ['ko', 'en']:
        (ART / f'model_{lang}.svg').write_text(diagram(lang))
        # Outline text so external SVG images do not depend on the viewer's fonts.
        outlined=ART/f'model_{lang}_outlined.svg'
        subprocess.run(['inkscape',str(ART/f'model_{lang}.svg'),'--export-text-to-path','--export-plain-svg',f'--export-filename={outlined}'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        outlined.replace(ART/f'model_{lang}.svg')
        source = (ROOT / 'reports' / f'review_{lang}.md').read_text()
        vals = re.findall(r'\$\$([\s\S]*?)\$\$|\\\(([\s\S]*?)\\\)', source)
        for a,b in vals:
            tex = (a or b).strip()
            if tex in expressions:
                continue
            name = f'math_{len(expressions):02}.svg'
            rendered = re.sub(r'\s+', ' ', tex).replace(r'\lVert',r'\Vert').replace(r'\rVert',r'\Vert')
            rendered = re.sub(r'\\mathcal\s+([A-Za-z])',r'\\mathcal{\1}',rendered)
            math_to_image('$'+rendered+'$', ART / name, format='svg', dpi=150, color='#18313c')
            expressions[tex] = name
    (ART / 'math_map.json').write_text(json.dumps(expressions, ensure_ascii=False, indent=2))
    print(f'Original diagrams and {len(expressions)} equation SVGs created.')

if __name__ == '__main__':
    main()
