"""Build a bilingual static review with deterministic original SVG figures."""
from pathlib import Path
import ast, csv, html, math, re, shutil
import markdown
from bs4 import BeautifulSoup

TOPIC = Path(__file__).resolve().parents[1]
ROOT = TOPIC.parent
SLUG = TOPIC.name
BASE = 'https://infant83.github.io/AI_Tech_Review/'
PAPER = 'https://advanced.onlinelibrary.wiley.com/doi/10.1002/advs.77225'
TITLES = {'ko':'빛의 세기에서 광자 수 분포로: 다광자 저장소 계산을 읽다','en':'From light intensity to photon-count distributions: reading multiphoton reservoir computing'}
DESCS = {'ko':'고전광·편광·OAM·광자 계수의 원리에서 861개 특징, 함수 복원 성능, 32분 취득비용과 고전 시뮬레이션 조건까지 검토합니다.','en':'Classical light, polarization, OAM and photon counting: 861 features, regression evidence, 32-minute acquisition and classical simulation conditions.'}
# Reuse the established editorial layout without executing another package.
template=ast.parse((ROOT/'2026-09-10_cash-qse-classical-quantum-chemistry/scripts/build_review.py').read_text())
CSS=next(ast.literal_eval(node.value) for node in template.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CSS' for t in node.targets))
CSS+='\n.final-article img{border-radius:4px}.final-article ul{padding-left:24px}.final-article li{font-size:15px}.kicker{font-size:13px;letter-spacing:.1em;color:#5f6b65;margin-bottom:18px}.standfirst{max-width:780px;font-size:18px;line-height:1.8;color:#5f6b65;margin:22px 0 0}.final-article p:has(>img[src="pipeline.svg"]),.final-article p:has(>img[src="poisson_features.svg"]){border:1px solid #d8d5cb;background:white}.math{display:inline-block;vertical-align:middle}.final-article li .math{display:inline}\n'

def svg_start(w,h,title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{html.escape(title)}</title><rect width="100%" height="100%" fill="#ffffff"/><g font-family="Arial, Noto Sans KR, sans-serif" fill="#17211d">']

def text(out,x,y,value,size=17,color='#17211d',anchor='start'):
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{html.escape(value)}</text>')

def pipeline(lang):
    ko=lang=='ko'; out=svg_start(760,510,'Optical feature acquisition and trained readout')
    text(out,32,39,'무엇을 고정하고 무엇을 학습하나' if ko else 'What stays fixed, and what is trained',22)
    labels=[('입력 · 편광','91개 입력 상태','INPUT') if ko else ('Input · polarization','91 input settings','INPUT'),('고정 · 광학 모드 혼합','파장판 + q-plate','FIXED') if ko else ('Fixed · optical mixing','Wave plates + q-plates','FIXED'),('측정 · 계수 분포','21 OAM × 41 항목 = 861','MEASURE') if ko else ('Measured · count features','21 OAM × 41 entries = 861','MEASURE'),('학습 · 고전 선형 읽기층','가중치 + ridge 정규화','TRAINED') if ko else ('Trained · classical readout','Weights + ridge penalty','TRAINED')]
    positions=[(32,65),(402,65),(32,248),(402,248)]
    for (x,y),(a,b,c) in zip(positions,labels):
        out.append(f'<rect x="{x}" y="{y}" width="326" height="132" rx="7" fill="{("#e8f2ed" if c=="TRAINED" else "#f2f5f6")}" stroke="#cad4d1"/>')
        text(out,x+20,y+29,c,12,'#0f766e');text(out,x+20,y+65,a,19);text(out,x+20,y+99,b,16,'#5f6b65')
    out.append('<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#0f766e"/></marker></defs><path d="M365 130H394 M565 203V222H195V240 M365 315H394" fill="none" stroke="#0f766e" stroke-width="2" marker-end="url(#a)"/>')
    text(out,32,427,'측정 시간은 빛의 전파 시간과 별도로 필요합니다.' if ko else 'Acquisition is a separate cost from optical propagation.',18)
    text(out,32,460,'1초 / 입력·OAM 설정 → 전체 1,911초 ≈ 32분' if ko else '1 s / input–OAM setting → 1,911 s ≈ 32 min total',17,'#25456f')
    text(out,32,488,'구성 변경·교정·데이터 이동 시간 제외' if ko else 'Excludes switching, calibration and data transfer',14,'#5f6b65')
    return ''.join(out)+ '</g></svg>'

def poisson(lang):
    ko=lang=='ko';out=svg_start(760,490,'Illustrative ideal Poisson feature map')
    text(out,32,37,'광량 하나에서 서로 다른 비선형 특징으로' if ko else 'Different nonlinear features from one intensity',22)
    text(out,32,67,'이상적 코히런트 모드 · 실험 데이터가 아닌 수식 예제' if ko else 'Ideal coherent mode · mathematical illustration, not measured data',14,'#5f6b65')
    x0,y0,w,h=80,110,610,285
    for p in [0,.25,.5,.75,1]:
        y=y0+h*(1-p);out.append(f'<path d="M{x0} {y}H{x0+w}" stroke="#e0e5e3"/>');text(out,x0-12,y+5,f'{p:g}',13,'#5f6b65','end')
    for lam in range(9):
        x=x0+w*lam/8;text(out,x,y0+h+24,str(lam),13,'#5f6b65','middle')
    for n,color in [(0,'#25456f'),(1,'#0f766e'),(2,'#bc6414'),(4,'#925681')]:
        points=[]
        for i in range(401):
            lam=8*i/400;p=math.exp(-lam)*lam**n/math.factorial(n)
            points.append(f'{x0+w*lam/8:.2f},{y0+h*(1-p):.2f}')
        out.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="3"/>')
    for i,(n,color) in enumerate([(0,'#25456f'),(1,'#0f766e'),(2,'#bc6414'),(4,'#925681')]):
        x=150+i*142;out.append(f'<path d="M{x} 91h22" stroke="{color}" stroke-width="3"/>');text(out,x+30,96,f'n = {n}',14)
    text(out,385,450,'평균 검출 광자 수 λ' if ko else 'Mean detected photon number λ',16,'#17211d','middle')
    text(out,385,480,'Pₙ(λ) = exp(−λ) λⁿ / n!     ·     n = 0, 1, 2, 4',15,'#5f6b65','middle')
    text(out,32,99,'확률' if ko else 'Probability',13,'#5f6b65')
    return ''.join(out)+'</g></svg>'

def render_md(source):
    saved=[]
    def protect(m):
        raw=m.group(0);display=raw.startswith('\\[')
        saved.append('<span class="'+('display-math' if display else 'math')+'">'+html.escape(raw)+'</span>')
        return f'MATHBLOCKTOKEN{len(saved)-1}END'
    body=markdown.markdown(re.sub(r'\\\[.*?\\\]|\\\(.*?\\\)',protect,source,flags=re.S),extensions=['tables','fenced_code','sane_lists'])
    for i,v in enumerate(saved):body=body.replace(f'MATHBLOCKTOKEN{i}END',v)
    return body

def main():
    hero=TOPIC/'artifacts/photon_reservoir_hero.webp'
    if not hero.exists():raise FileNotFoundError(hero)
    rows=[['target','mean_intensity_R2','count_distribution_R2','source'],*[ [f,a,b,'Hong et al. 2026 SI Table S2'] for f,a,b in [('quadratic',.92,.94),('cubic',.89,.93),('quartic',.90,.94),('exponential',.96,.97),('logarithmic',.97,.97),('damped_sinusoid',.69,.94),('reported_mean',.89,.95)]]]
    for lang in ['ko','en']:
        ko=lang=='ko';dist=TOPIC/'dist'/('' if ko else 'en');dist.mkdir(parents=True,exist_ok=True)
        shutil.copy2(hero,dist/hero.name)
        (dist/'pipeline.svg').write_text(pipeline(lang));(dist/'poisson_features.svg').write_text(poisson(lang))
        with (dist/'benchmarks.csv').open('w',newline='',encoding='utf-8') as f:csv.writer(f,lineterminator='\n').writerows(rows)
        source=(TOPIC/'reports'/('final_review.md' if ko else 'final_review_en.md')).read_text()
        (dist/'review.md').write_text(source)
        csvurl=f'https://github.com/Infant83/AI_Tech_Review/blob/main/{SLUG}/dist/{"" if ko else "en/"}benchmarks.csv'
        soup=BeautifulSoup(render_md(source.split('\n',1)[1].replace('(benchmarks.csv)',f'({csvurl})')),'html.parser')
        toc=[]
        for i,h in enumerate(soup.find_all('h2'),1):
            h['id']=f'section-{i}';toc.append(f'<a href="#section-{i}">{html.escape(h.get_text())}</a>')
        for table in soup.find_all('table'):
            table.wrap(soup.new_tag('div',attrs={'class':'table-wrap','tabindex':'0','role':'region','aria-label':'연구 비교 표' if ko else 'Research comparison table'}))
        for im in soup.find_all('img'):
            name=im['src'];im['width']='1536' if name==hero.name else '760';im['height']='1024' if name==hero.name else ('510' if name=='pipeline.svg' else '490')
            im['fetchpriority']='high' if name==hero.name else 'auto'
            if name!=hero.name:im['loading']='lazy'
        url=BASE+'reviews/'+SLUG+('/' if ko else '/en/');other=BASE+'reviews/'+SLUG+('/en/' if ko else '/')
        title=html.escape(TITLES[lang]);desc=html.escape(DESCS[lang]);mdurl=f'https://github.com/Infant83/AI_Tech_Review/blob/main/{SLUG}/dist/{"" if ko else "en/"}review.md'
        full=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ko" href="{BASE}reviews/{SLUG}/"><link rel="alternate" hreflang="en" href="{BASE}reviews/{SLUG}/en/"><link rel="alternate" hreflang="x-default" href="{BASE}reviews/{SLUG}/"><meta property="og:type" content="article"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}"><meta property="og:image" content="{url}{hero.name}"><meta name="twitter:card" content="summary_large_image"><meta name="author" content="김현중"><meta property="article:published_time" content="2026-09-13"><meta property="article:modified_time" content="2026-09-13"><style>{CSS}</style>
<script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']],displayMath:[['\\\\[','\\\\]']]}},options:{{skipHtmlTags:['script','noscript','style','textarea','pre','code']}}}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js" integrity="sha384-AHAnt9ZhGeHIrydA1Kp1L7FN+2UosbF7RQg6C+9Is/a7kDpQ1684C2iH2VWil6r4" crossorigin="anonymous"></script></head><body><div class="topline"><div class="topline-inner"><span class="brand">AI Tech Review Letters</span><div class="topline-actions"><a href="{BASE}">{'리뷰 허브' if ko else 'Review hub'}</a><span aria-current="page">{'한국어' if ko else 'English'}</span><a href="{other}" hreflang="{'en' if ko else 'ko'}">{'English' if ko else '한국어'}</a><a href="{mdurl}">Markdown</a></div></div></div><header class="hero"><div class="hero-inner"><div class="kicker">PHOTONIC COMPUTING · 2026.09.13</div><h1>{title}</h1><p class="standfirst">{desc}</p></div></header><main class="content-grid"><article class="final-article">{soup}<div class="publication-note">{'생성 표지는 개념 일러스트입니다. 두 SVG 도표는 논문의 측정 흐름과 이상적 Poisson 식을 설명하기 위해 제작했습니다.' if ko else 'The generated hero is conceptual. Two original SVG figures explain the measurement workflow and ideal Poisson equation.'}</div></article><aside class="sidebar"><h2>{'이 글의 순서' if ko else 'In this article'}</h2><nav aria-label="{'목차' if ko else 'Contents'}">{''.join(toc)}</nav><div class="side-extra"><hr><a href="{PAPER}">Advanced Science · e77225</a><a href="{csvurl}">{'표 데이터 CSV' if ko else 'Table data CSV'}</a><p>{'동료평가 논문 · 상온 광학 실험' if ko else 'Peer-reviewed · room-temperature optics'}</p></div></aside></main></body></html>'''
        full=full.replace('<span aria-current="page">',f'<span lang="{lang}" aria-current="page">')
        (dist/'index.html').write_text(full)
        print(lang,len(source.split()),'words',len(source),'characters')

if __name__=='__main__':main()
