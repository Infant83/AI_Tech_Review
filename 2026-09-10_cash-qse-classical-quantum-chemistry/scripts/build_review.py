from pathlib import Path
import re, shutil, json, csv, html
import markdown
from bs4 import BeautifulSoup
from PIL import Image

TOPIC = Path(__file__).resolve().parents[1]
ROOT = TOPIC.parent
SLUG = TOPIC.name
BASE = 'https://infant83.github.io/AI_Tech_Review/'
TITLES = {'ko':'분자 계산의 일을 나누는 법: CASH-QSE로 이해하는 고전·양자 협업', 'en':'Sharing the work of molecular calculation: classical–quantum collaboration through CASH-QSE'}
DESCS = {'ko':'전자상관과 활성공간에서 출발해 고전 기준상태·양자 보정·측정비용을 설명하는 CASH-QSE 심층 리뷰', 'en':'An in-depth explanation of electron correlation, active spaces, classical references, quantum corrections and measurement costs.'}

CSS = '''
:root{--paper:#fbfaf7;--ink:#17211d;--muted:#5f6b65;--line:#d8d5cb;--teal:#0f766e;--blue:#25456f}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Sans KR","Segoe UI",Arial,sans-serif;text-rendering:optimizeLegibility}a{color:var(--teal);text-underline-offset:3px}a:hover{color:var(--blue)}.topline{background:white;border-bottom:1px solid var(--line)}.topline-inner{max-width:1180px;margin:auto;padding:16px 24px;display:flex;justify-content:space-between;gap:20px;font-size:14px}.topline-actions{display:flex;flex-wrap:wrap;gap:18px}.brand{font-weight:700;letter-spacing:.03em}.hero-inner{max-width:1180px;margin:auto;padding:52px 24px 34px}.hero h1{max-width:950px;font-size:clamp(28px,4.3vw,48px);line-height:1.32;letter-spacing:-.045em;word-break:keep-all;margin:0}.content-grid{max-width:1180px;margin:0 auto;display:grid;grid-template-columns:minmax(0,800px) minmax(180px,240px);gap:60px;padding:32px 24px 60px}.final-article{min-width:0;font-size:17px;line-height:1.95;word-break:keep-all;overflow-wrap:break-word}.final-article p{margin:0 0 24px}.final-article h2{font-size:26px;line-height:1.5;margin:62px 0 22px;letter-spacing:-.035em;padding-top:22px;border-top:1px solid var(--line)}.final-article h2:first-of-type{margin-top:45px}.final-article strong{font-weight:750}.final-article img{display:block;width:100%;height:auto}.final-article p:has(>img){margin:30px 0 10px}.final-article p:has(>em:only-child){font-size:14px;color:var(--muted);line-height:1.7}.final-article em{font-style:normal}.sidebar{align-self:start;position:sticky;top:25px;font-size:14px;line-height:1.75;color:var(--muted)}.sidebar h2{font-size:15px;color:var(--ink);margin:0 0 15px}.sidebar a{display:block;color:var(--muted);margin-bottom:12px;text-decoration:none}.sidebar a:hover{text-decoration:underline}.sidebar hr{border:0;border-top:1px solid var(--line);margin:25px 0}.table-wrap{width:100%;overflow:auto;margin:28px 0 18px;outline-offset:4px}table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.65;word-break:normal}th,td{padding:12px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}th{background:#eaf0ee;font-weight:700;white-space:normal}td:nth-child(n+3){font-variant-numeric:tabular-nums}tbody tr:nth-child(even){background:#f4f4ef}figure{margin:32px 0}figcaption{font-size:14px;color:var(--muted);line-height:1.65;margin-top:10px}.matrix-figure img{background:#fff;border:1px solid var(--line)}.math{overflow-x:auto;max-width:100%}.display-math{display:block;text-align:center;margin:25px 0;padding:10px 0;font-size:1rem;overflow-x:auto}.toy{border-top:3px solid var(--teal);border-bottom:1px solid var(--line);padding:24px;background:#f1f5f2;margin:28px 0}.toy h3{margin:0 0 8px;font-size:20px}.toy p{font-size:14px;line-height:1.65;margin-bottom:18px}.toy-controls{display:grid;grid-template-columns:1fr 1fr;gap:20px}.toy label{display:block;font-size:14px;font-weight:650}.toy input{display:block;width:100%;padding:9px 12px;margin:7px 0 0;border:1px solid #899b94;border-radius:3px;font:inherit;font-size:16px;background:#fff;color:var(--ink)}.toy button{margin:18px 10px 18px 0;padding:8px 14px;font:inherit;font-size:14px;cursor:pointer;border:1px solid var(--teal);background:white;color:var(--teal);border-radius:3px}.toy-results{display:grid;grid-template-columns:1fr 1fr;gap:15px}.toy-results div{padding-top:12px;border-top:1px solid #bbc8c1;font-size:14px}.toy-results output{display:block;font-size:24px;font-weight:700;color:var(--blue);font-variant-numeric:tabular-nums}.weight-track{margin:18px 0 8px;background:#0f766e;height:18px;display:flex}.classical-weight{background:#25456f;width:96.42383454%}.quantum-weight{background:#0f766e;flex:1}.weight-legend{display:flex;justify-content:space-between;font-size:13px}.weight-legend span:first-child{color:var(--blue)}.weight-legend span:last-child{color:var(--teal)}.toy .error{color:#922f2f;margin:8px 0}.toy small{font-size:12px;color:var(--muted)}.final-article ol{padding-left:22px;font-size:14px;line-height:1.8}.final-article li{margin-bottom:14px}.publication-note{border-top:1px solid var(--line);margin-top:45px;padding-top:18px;color:var(--muted);font-size:13px;line-height:1.8}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #bc6414;outline-offset:3px}
@media(max-width:1000px){.content-grid{grid-template-columns:1fr;gap:35px;max-width:848px}.sidebar{position:static;grid-row:1;font-size:13px;border-bottom:1px solid var(--line);padding-bottom:15px}.sidebar nav{display:flex;flex-wrap:wrap;gap:4px 16px}.sidebar nav a{margin:0}.sidebar .side-extra{display:none}.hero-inner{max-width:848px}.final-article{font-size:16px}}
@media(max-width:560px){.topline-inner{padding:14px 18px;display:block}.topline-actions{margin-top:10px;font-size:13px}.hero-inner{padding:34px 18px 24px}.content-grid{padding:22px 18px 50px}.final-article h2{font-size:22px;margin-top:42px}.final-article{line-height:1.9;word-break:normal}table{min-width:620px}.toy{padding:18px}.toy-controls,.toy-results{gap:12px}.toy-results output{font-size:21px}.matrix-figure{overflow-x:auto}.matrix-figure img{min-width:590px}.display-math{font-size:13px}.sidebar h2{margin-bottom:8px}}
@media print{body{background:white}.topline,.sidebar,.toy-controls,.toy button{display:none}.content-grid{display:block;padding:0;max-width:none}.hero-inner{padding:0 0 20px}.final-article{font-size:11pt}.final-article h2{break-after:avoid;font-size:16pt}.table-wrap{overflow:visible}table{min-width:0!important}.toy,figure{break-inside:avoid}a{color:inherit}.display-math{overflow:visible}}
'''

def matrix_svg(lang):
    ko=lang=='ko'
    txt=['고전적으로 아는 블록','양자 측정이 필요한 부분','내적은 0이어도 Hamiltonian 결합은 남습니다','고전 행렬 대각화로 혼합 계수와 에너지 계산'] if ko else ['Classically known block','Quantum-measured entries','Zero overlap does not mean zero Hamiltonian coupling','Classical diagonalization gives coefficients and energies']
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="400" viewBox="0 0 760 400" role="img"><title>Classical and quantum Hamiltonian blocks</title><rect width="760" height="400" fill="#fff"/><g font-family="Arial, Noto Sans KR, sans-serif" fill="#17211d">']
    for i,label in enumerate(['C','q₁','q₂']):
        out.append(f'<text x="{204+i*88}" y="47" text-anchor="middle" font-size="22">{label}</text><text x="125" y="{102+i*70}" text-anchor="middle" font-size="22">{label}</text>')
    vals=[['E꜀','V₁','V₂'],['V₁*','H₁₁','H₁₂'],['V₂*','H₂₁','H₂₂']]
    for i in range(3):
        for j in range(3):
            out.append(f'<rect x="{162+j*88}" y="{61+i*70}" width="84" height="66" fill="{("#25456f" if i==j==0 else "#dceee7")}"/><text x="{204+j*88}" y="{103+i*70}" font-size="23" text-anchor="middle" fill="{("white" if i==j==0 else "#0f5d55")}">{vals[i][j]}</text>')
    out.append(f'<rect x="466" y="88" width="15" height="15" fill="#25456f"/><text x="493" y="101" font-size="16">{txt[0]}</text><rect x="466" y="150" width="15" height="15" fill="#dceee7" stroke="#0f766e"/><text x="493" y="163" font-size="16">{txt[1]}</text><text x="466" y="221" font-size="18">⟨C|qᵢ⟩ = 0;  ⟨qᵢ|qⱼ⟩ = δᵢⱼ</text><line x1="48" y1="297" x2="712" y2="297" stroke="#d8d5cb"/><text x="380" y="331" text-anchor="middle" font-size="18">{txt[2]}</text><text x="380" y="367" text-anchor="middle" fill="#5f6b65" font-size="16">{txt[3]}</text></g></svg>')
    return ''.join(out)

def toy(lang):
    ko=lang=='ko'
    labels=['두 상태를 섞어보기','설명용 2×2 모델 · 실제 분자 데이터 아님','보정 상태 에너지 Δ (eV)','결합 V (eV)','초기값','결합을 더 크게','낮은 고유값 E₋','보정 성분 비중','고전 성분','보정 성분','입력 범위: Δ = 0.1–2 eV, V = 0–0.5 eV. E꜀ = 0.','오차 민감도 |∂E₋/∂V|'] if ko else ['Mix two states','Educational 2×2 model · not molecular data','Correction energy Δ (eV)','Coupling V (eV)','Reset','Stronger coupling','Lower eigenvalue E₋','Correction weight','Classical component','Correction component','Input range: Δ = 0.1–2 eV, V = 0–0.5 eV. E꜀ = 0.','Sensitivity |∂E₋/∂V|']
    return f'''<section class="toy" id="two-state-model" data-language="{lang}" aria-labelledby="toy-heading"><h3 id="toy-heading">{labels[0]}</h3><p>{labels[1]}</p><div class="toy-controls"><label>{labels[2]}<input id="delta" type="number" min="0.1" max="2" step="0.1" value="1"></label><label>{labels[3]}<input id="coupling" type="number" min="0" max="0.5" step="0.05" value="0.2"></label></div><button type="button" id="toy-reset">{labels[4]}</button><button type="button" id="toy-strong">{labels[5]}</button><div class="toy-results" aria-live="polite"><div>{labels[6]}<output id="energy">−0.03852 eV</output></div><div>{labels[7]}<output id="weight">3.58%</output></div></div><div class="weight-track" aria-hidden="true"><span class="classical-weight" id="classical-bar"></span><span class="quantum-weight"></span></div><div class="weight-legend"><span>{labels[8]}</span><span>{labels[9]}</span></div><p>{labels[11]}: <output id="sensitivity">0.37139</output></p><p class="error" id="toy-error" role="status"></p><small>{labels[10]}</small></section>'''

JS='''export function solveTwoState(delta, v) {
  if (!Number.isFinite(delta) || !Number.isFinite(v) || delta <= 0) throw new RangeError('Finite inputs and positive gap required');
  const gapNorm = Math.hypot(delta, 2*v);
  return {energy: -2*v*v/(delta+gapNorm), weight:(1-delta/gapNorm)/2, sensitivity:2*Math.abs(v)/gapNorm};
}
if (typeof document !== 'undefined' && document.getElementById('two-state-model')) {
 const panel=document.getElementById('two-state-model'), d=document.getElementById('delta'), v=document.getElementById('coupling');
 const ko=panel.dataset.language==='ko';
 function update(){
  const gap=d.valueAsNumber, coupling=v.valueAsNumber;
  const valid=Number.isFinite(gap)&&Number.isFinite(coupling)&&gap>=.1&&gap<=2&&coupling>=0&&coupling<=.5;
  document.getElementById('toy-error').textContent=valid?'':(ko?'표시된 입력 범위 안의 숫자를 넣어 주세요. 마지막 유효 결과를 표시합니다.':'Enter numbers within the displayed ranges. The last valid result remains visible.');
  if(!valid) return;
  const r=solveTwoState(gap,coupling);
  document.getElementById('energy').textContent=r.energy.toFixed(5)+' eV';
  document.getElementById('weight').textContent=(100*r.weight).toFixed(2)+'%';
  document.getElementById('sensitivity').textContent=r.sensitivity.toFixed(5);
  document.getElementById('classical-bar').style.width=(100*(1-r.weight))+'%';
 }
 for(const input of [d,v]) input.addEventListener('input',update);
 document.getElementById('toy-reset').addEventListener('click',()=>{d.value='1';v.value='.2';update();});
 document.getElementById('toy-strong').addEventListener('click',()=>{d.value='.2';v.value='.4';update();});
 update();
}
'''

def render_md(source):
    protected=[]
    def save(m):
        raw=m.group(0); display=raw.startswith('\\[')
        protected.append('<span class="'+('display-math' if display else 'math')+'">'+html.escape(raw)+'</span>')
        return f'MATHBLOCKTOKEN{len(protected)-1}END'
    source=re.sub(r'\\\[.*?\\\]|\\\(.*?\\\)',save,source,flags=re.S)
    text=markdown.markdown(source,extensions=['tables','fenced_code','sane_lists'])
    for i,value in enumerate(protected):text=text.replace(f'MATHBLOCKTOKEN{i}END',value)
    return text

def main():
    hero=TOPIC/'artifacts/final_review/figures/cash_qse_hero.webp'
    if not hero.exists(): raise FileNotFoundError('Copy the selected project hero before building')
    rows=[['molecule','basis_window','bond_angstrom','reference','cash_continuous_shots','adapt_continuous_shots','reported_adapt_cash_ratio','cash_full_cnot','cash_floor_shots','reported_floor_ratio','source'],
      ['N2','STO-3G',1.8,'HF',1100000,2400000,2.1,342,'','','https://arxiv.org/html/2609.08170v1#S8'],
      ['N2','STO-3G',1.8,'CAS(4,4)',160000,2400000,15,333,'','','https://arxiv.org/html/2609.08170v1#S8'],
      ['N2','STO-3G',1.8,'CAS(6,6)',850,2400000,2800,328,'','','https://arxiv.org/html/2609.08170v1#S8'],
      ['N2','STO-3G',3.0,'HF',2300000,770000,.33,338,'','','https://arxiv.org/html/2609.08170v1#S8'],
      ['N2','STO-3G',3.0,'CAS(4,4)',810000,770000,.94,328,'','','https://arxiv.org/html/2609.08170v1#S8'],
      ['N2','STO-3G',3.0,'CAS(6,6)','classical stop','','','','','','https://arxiv.org/html/2609.08170v1#S8'],
      ['H2O','restricted cc-pVDZ 14 spatial orbitals',.96,'CAS(4,4)',21000,'','',383,51800,560,'https://arxiv.org/html/2609.08170v1#A3'],
      ['H2O','restricted cc-pVDZ 14 spatial orbitals',1.75,'CAS(4,4)',12000,'','',375,32800,630,'https://arxiv.org/html/2609.08170v1#A3'],
      ['H2O','restricted cc-pVDZ 14 spatial orbitals',3.0,'CAS(4,4)',510,'','',350,941,4400,'https://arxiv.org/html/2609.08170v1#A3']]
    for lang in ['ko','en']:
        dist=TOPIC/'dist'/('en' if lang=='en' else '')
        dist.mkdir(parents=True,exist_ok=True)
        shutil.copy2(hero,dist/hero.name)
        (dist/'matrix.svg').write_text(matrix_svg(lang))
        (dist/'two_state.js').write_text(JS)
        with (dist/'benchmarks.csv').open('w',newline='',encoding='utf-8-sig') as f:csv.writer(f).writerows(rows)
        src=(TOPIC/'reports'/('final_review_en.md' if lang=='en' else 'final_review.md')).read_text()
        src=src.split('\n',1)[1].lstrip()
        mdout='# '+TITLES[lang]+'\n\n'+src.replace('<!-- MATRIX -->','![Hamiltonian blocks](matrix.svg)').replace('<!-- INTERACTIVE -->',('조작 예제는 HTML 페이지에서 사용할 수 있습니다.' if lang=='ko' else 'The interactive model is available in the HTML article.'))
        (dist/'review.md').write_text(mdout)
        caption='고전 블록은 재사용하고, 나머지 행렬원소와의 결합으로 전체 상태를 구합니다.' if lang=='ko' else 'Reuse the classical block and combine it with measured correction and coupling entries.'
        body=render_md(src.replace('(benchmarks.csv)', '(https://github.com/infant83/AI_Tech_Review/blob/main/'+SLUG+'/dist/benchmarks.csv)')).replace('<!-- MATRIX -->',f'<figure class="matrix-figure"><img src="matrix.svg" alt="Classical and quantum Hamiltonian blocks" loading="lazy" width="760" height="400"><figcaption>{caption}</figcaption></figure>').replace('<!-- INTERACTIVE -->',toy(lang))
        soup=BeautifulSoup(body,'html.parser')
        links=[]
        for i,h in enumerate(soup.find_all('h2'),1):
            h['id']=f'section-{i}'
            links.append(f'<a href="#section-{i}">{html.escape(h.get_text())}</a>')
        for table in soup.find_all('table'):
            wrap=soup.new_tag('div',attrs={'class':'table-wrap','tabindex':'0','role':'region','aria-label':'Research comparison table'})
            table.wrap(wrap)
        for image in soup.find_all('img'):
            if image.get('src')=='cash_qse_hero.webp':image['width']='1536';image['height']='1024';image['fetchpriority']='high'
        url=BASE+'reviews/'+SLUG+('/en/' if lang=='en' else '/')
        other=BASE+'reviews/'+SLUG+('/' if lang=='en' else '/en/')
        full=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(TITLES[lang])}</title><meta name="description" content="{html.escape(DESCS[lang])}"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ko" href="{BASE}reviews/{SLUG}/"><link rel="alternate" hreflang="en" href="{BASE}reviews/{SLUG}/en/"><link rel="alternate" hreflang="x-default" href="{BASE}reviews/{SLUG}/"><meta property="og:type" content="article"><meta property="og:title" content="{html.escape(TITLES[lang])}"><meta property="og:description" content="{html.escape(DESCS[lang])}"><meta property="og:url" content="{url}"><meta property="og:image" content="{url}cash_qse_hero.webp"><meta name="twitter:card" content="summary_large_image"><meta name="author" content="김현중"><meta property="article:published_time" content="2026-09-10"><meta property="article:modified_time" content="2026-09-10"><style>{CSS}</style>
<script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']],displayMath:[['\\\\[','\\\\]']]}},options:{{skipHtmlTags:['script','noscript','style','textarea','pre','code']}}}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js" integrity="sha384-AHAnt9ZhGeHIrydA1Kp1L7FN+2UosbF7RQg6C+9Is/a7kDpQ1684C2iH2VWil6r4" crossorigin="anonymous"></script></head><body><div class="topline"><div class="topline-inner"><span class="brand">AI Tech Review Letters</span><div class="topline-actions"><a class="hub-link" href="{BASE}">{'리뷰 허브' if lang=='ko' else 'Review hub'}</a><span lang="{lang}" aria-current="page">{"한국어" if lang=="ko" else "English"}</span><a href="{other}" hreflang="{'en' if lang=='ko' else 'ko'}">{'English' if lang=='ko' else '한국어'}</a><a href="https://github.com/infant83/AI_Tech_Review/blob/main/{SLUG}/dist/{"en/" if lang=="en" else ""}review.md">Markdown</a></div></div></div><header class="hero"><div class="hero-inner"><h1>{html.escape(TITLES[lang])}</h1></div></header><main class="content-grid"><article class="final-article">{soup}<div class="publication-note">{'도식과 두 상태 모델은 이 글의 설명용 구성입니다. 도입 일러스트는 OpenAI 이미지 생성 도구로 제작했습니다.' if lang=='ko' else 'The matrix diagram and two-state model are educational constructions for this article. The opening illustration was made with OpenAI image generation.'}</div></article><aside class="sidebar"><h2>{'이 글의 순서' if lang=='ko' else 'In this article'}</h2><nav aria-label="{'목차' if lang=='ko' else 'Contents'}">{''.join(links)}</nav><div class="side-extra"><hr><a href="https://arxiv.org/abs/2609.08170v1">CASH-QSE · arXiv v1</a><a href="https://github.com/infant83/AI_Tech_Review/blob/main/{SLUG}/dist/benchmarks.csv">{'표 데이터 CSV' if lang=='ko' else 'Table data CSV'}</a><p>{'프리프린트 · 고전 수치·자원 분석' if lang=='ko' else 'Preprint · classical numerical and resource analysis'}</p></div></aside></main><script type="module" src="two_state.js"></script></body></html>'''
        (dist/'index.html').write_text(full)
        print(lang,len(src.split()),'words',len(src),'characters')

if __name__=='__main__':main()
