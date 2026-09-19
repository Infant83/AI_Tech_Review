"""Build bilingual review pages and original diagrams without external dependencies."""
from pathlib import Path
from html import escape
import math
import shutil

P = Path(__file__).resolve().parent
SLUG = P.name
BASE = 'https://infant83.github.io/AI_Tech_Review/'
SOURCE = 'https://github.com/chimie-paristech-CTM/TL-ChemBO/tree/a35276cdbf8b8c6dde4d71c224b918e04ddf52c2'
META = {
 'ko': {
  'title':'과거 실험을 재사용하는 화학 베이지안 최적화: 전이학습의 이점과 한계',
  'subtitle':'Digital Discovery 게재 연구의 공개 초록·코드와 차원에 맞춘 GP 사전 설정을 읽다',
  'description':'화학 반응 최적화에서 과거 데이터를 재사용하는 두 단계 전이학습을 해설합니다. 고차원 분자 표현과 GP 하이퍼프라이어, 공개 코드의 단계 구분, 음의 전이와 OLED 적용 조건을 검토합니다.',
  'label':'번외 리뷰 · 방법 해설 · 공개 코드 검토',
  'alt':'과거 실험판과 새로운 실험판 사이의 정보 공유를 빛으로 표현한 화학 최적화 개념 그림',
  'caption':'그림 1. 과거 실험의 정보를 새 화학 후보의 탐색에 활용하는 개념 그림입니다. 실제 실험 장치나 측정 결과를 묘사하지 않습니다. OpenAI imagegen으로 제작했습니다.',
  'contents':'이 글의 내용',
 },
 'en': {
  'title':'Reusing Chemical Experiments: Benefits and Limits of Transfer in Bayesian Optimization',
  'subtitle':'Reading the published study through its public abstract, code and dimension-aware GP priors',
  'description':'A source-bounded review of two-phase transfer learning for chemical Bayesian optimization: molecular representations, GP hyperpriors, implementation details, negative transfer and implications for OLED discovery.',
  'label':'Special review · Methods explainer · Public code analysis',
  'alt':'Conceptual chemistry illustration linking an earlier experiment plate to a new plate through threads of light',
  'caption':'Figure 1. Conceptual illustration of reusing past experimental information in the exploration of new chemical options. It does not depict an actual apparatus or measured results. Created with OpenAI imagegen.',
  'contents':'In this review',
 }
}
CSS='''
:root{--ink:#182c31;--muted:#576b70;--paper:#fcfaf5;--teal:#146b69;--line:#d7ded8;--amber:#a96820}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:30px}body{margin:0;background:var(--paper);color:var(--ink);font:18px/1.9 "Noto Sans KR","Segoe UI",Arial,sans-serif;overflow-wrap:break-word}a{color:var(--teal);text-underline-offset:4px}a:focus-visible{outline:3px solid var(--amber);outline-offset:4px}nav.top{border-bottom:1px solid var(--line);padding:16px max(22px,calc((100% - 1100px)/2));display:flex;gap:18px;flex-wrap:wrap;justify-content:space-between;font-size:14px}nav.top a{text-decoration:none}.wrap{max-width:1100px;padding:0 24px;margin:auto}header{padding:55px 0 24px}.kicker{color:var(--teal);font-size:13px;font-weight:700;letter-spacing:.07em}h1{font-size:clamp(30px,4.4vw,48px);line-height:1.38;letter-spacing:-.04em;max-width:960px;margin:18px 0}.subtitle{color:var(--muted);font-size:20px;max-width:920px;margin:0 0 20px}.date{font-size:14px;color:var(--muted)}.hero{margin:20px 0 46px}.hero img{width:100%;aspect-ratio:1672/941;object-fit:cover;border-radius:4px}figcaption{font-size:13px;line-height:1.8;color:var(--muted);margin-top:10px}main{max-width:790px;margin:auto;padding-bottom:70px}p{margin:0 0 22px}.lead{font-size:21px;line-height:1.85}section{margin-top:55px}h2{font-size:27px;line-height:1.5;letter-spacing:-.025em;margin:0 0 22px}h3{font-size:21px}.scope{border-left:4px solid var(--amber);padding:22px 25px;background:#f3ede0;margin:32px 0;font-size:15px;line-height:1.85}.scope p{margin:8px 0 0}.toc{background:#edf3ee;padding:20px 25px;margin:34px 0}.toc strong{font-size:15px}.toc ul{list-style:none;padding:0;margin:9px 0 0}.toc li{font-size:15px;margin:4px 0}.table-wrap{max-width:100%;overflow:auto;margin:25px 0 30px;border:1px solid var(--line)}table{border-collapse:collapse;width:100%;font-size:15px;line-height:1.8}th,td{padding:14px 16px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;min-width:120px}th{background:#e8efea;color:#224941}tr:last-child td{border-bottom:0}code{font:0.85em/1.7 ui-monospace,monospace;background:#eaf0ec;padding:2px 5px;border-radius:3px;overflow-wrap:anywhere}.equation{font:26px/1.7 Georgia,serif;text-align:center;padding:20px 8px;margin:25px 0;background:#f0f3ef;border-radius:4px}figure{margin:32px 0}figure img{max-width:100%;height:auto;display:block}.references{padding-left:23px;font-size:15px;line-height:1.85}.references li{padding:0 0 20px 5px}footer{border-top:1px solid var(--line);padding:25px 0;color:var(--muted);font-size:14px}.byline-disclosure{font-size:14px}.authoring-disclosure{font-size:14px}.authoring-disclosure h2{font-size:24px}@media(max-width:600px){body{font-size:17px}.wrap{padding:0 20px}header{padding-top:32px}h1{font-size:31px}.subtitle{font-size:18px}.lead{font-size:19px}h2{font-size:24px}section{margin-top:42px}.scope{padding:18px 20px}.hero{margin-bottom:32px}th,td{padding:10px 12px;min-width:108px}.toc{padding:17px 20px}.equation{font-size:23px}}
'''

def svg_open(title,desc,w,h):
 return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc><metadata>Original reviewer reconstruction; source: {SOURCE}; not measured performance.</metadata><rect width="100%" height="100%" fill="#f0f3ed"/><g font-family="Arial, Noto Sans KR, sans-serif" fill="#182c31">'
def text(x,y,s,size=22,color='#182c31',anchor='start',weight=400):
 return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{escape(s)}</text>'
def build_prior(lang):
 labels= ('차원에 따라 달라지는 사전평균','공개 구현식 · 성능 측정값 아님','입력 차원 d','길이척도 사전평균') if lang=='ko' else ('A prior mean that grows with dimension','Implementation formula · not performance data','Feature dimension d','Length-scale prior mean')
 s=svg_open(labels[0],labels[1],740,420)
 s+=text(35,46,labels[0],27,weight=700)+text(35,79,labels[1],18,'#576b70')
 s+=text(690,124,'μℓ = 0.4√d + 4',23,anchor='end')
 for i,d in enumerate([32,128,512,2048]):
  y=167+i*53;v=.4*math.sqrt(d)+4
  s+=text(93,y+7,str(d),22,anchor='end')
  s+=f'<rect x="120" y="{y-16}" width="{v*20:.3f}" height="30" rx="3" fill="#287e76"/>'
  s+=text(133+v*20,y+7,f'{v:.3f}',22)
 s+=text(90,395,labels[2],18,anchor='middle')+text(430,395,labels[3],19,anchor='middle')+'</g></svg>'
 return s
def build_phases(lang):
 if lang=='ko':
  title='직접 공유 후, 탐색 단계를 구분합니다';desc='고정 코드의 A–B–C 구성 · 전환 시점 P는 사전 설정'
  rows=[('A  과거 탐색','이전 화학 후보의 관측 기록'),('B  새 후보의 초기 탐색','A를 재사용 · task parameter 없음 · P회'),('C  새 후보의 나머지 탐색','A+B 이력: training · 이후 관측: test')]
  note='B도 C의 시작 시점에는 training 이력으로 들어갑니다.'
 else:
  title='Pool first, distinguish stages later';desc='Pinned A–B–C implementation · P is preset'
  rows=[('A  Historical campaign','Observations on previous chemical options'),('B  Initial target exploration','Reuse A · no task parameter · P iterations'),('C  Remaining target exploration','A+B history: training · new observations: test')]
  note='B is also labeled training when campaign C begins.'
 s=svg_open(title,desc,740,595)+text(35,46,title,27,weight=700)+text(35,80,desc,18,'#576b70')
 for i,(a,b) in enumerate(rows):
  y=114+145*i;fill=['#dde9e3','#f2dfbd','#d9e9ea'][i]
  s+=f'<rect x="40" y="{y}" width="660" height="107" rx="8" fill="{fill}" stroke="#b3c4bd"/>'
  s+=text(64,y+39,a,25,weight=700)+text(64,y+76,b,21)
  if i<2:s+=f'<path d="M370 {y+107} V{y+133} m-6 -8 l6 8 l6 -8" fill="none" stroke="#577b76" stroke-width="2.5"/>'
 s+=text(370,559,note,20,anchor='middle')+'</g></svg>'
 return s

def build():
 import re
 for lang,m in META.items():
  dist=P/'dist'/('en' if lang=='en' else '')
  dist.mkdir(parents=True,exist_ok=True)
  for name,fn in [('prior_scale',build_prior),('two_phase',build_phases)]:
   filename=f'{name}_{lang}.svg';(P/'artifacts'/filename).write_text(fn(lang),encoding='utf-8');shutil.copy2(P/'artifacts'/filename,dist/filename)
  shutil.copy2(P/'artifacts'/'transfer_hero.webp',dist/'transfer_hero.webp')
  body=(P/'reports'/f'review_{lang}.html').read_text()
  toc=''.join(f'<li><a href="#{i}">{t}</a></li>' for i,t in re.findall(r'<section id="([^"]+)"><h2>(.*?)</h2>',body))
  canonical=f'{BASE}reviews/{SLUG}/'+('en/' if lang=='en' else '')
  alternates=''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE}reviews/{SLUG}/{s}">' for l,s in [('ko',''),('en','en/'),('x-default','')])
  nav=f'<a href="{BASE}">AI Tech Review Letters</a><span><a lang="ko" href="../" '+('aria-current="page"' if lang=='ko' else '')+'>한국어</a> · <a lang="en" href="en/" '+('aria-current="page"' if lang=='en' else '')+'>English</a></span>'
  # Explicit canonical language destinations; publication renderer also validates these.
  nav=nav.replace('lang="ko" href="../"',f'lang="ko" hreflang="ko" href="{BASE}reviews/{SLUG}/"').replace('lang="en" href="en/"',f'lang="en" hreflang="en" href="{BASE}reviews/{SLUG}/en/"')
  doc=f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(m['title'])}</title><meta name="description" content="{escape(m['description'],quote=True)}"><meta name="author" content="Hyun-Jung Kim">
<link rel="canonical" href="{canonical}">{alternates}<meta property="og:title" content="{escape(m['title'],quote=True)}"><meta property="og:description" content="{escape(m['description'],quote=True)}"><meta property="og:type" content="article"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{canonical}transfer_hero.webp"><meta property="og:image:alt" content="{escape(m['alt'],quote=True)}"><meta name="twitter:card" content="summary_large_image"><meta property="article:published_time" content="2026-09-19"><meta property="article:modified_time" content="2026-09-19"><style>{CSS}</style></head>
<body><nav class="top">{nav}</nav><div class="wrap"><header><div class="kicker">{m['label']}</div><h1>{m['title']}</h1><p class="subtitle">{m['subtitle']}</p><p class="date">2026-09-19 · {'김현중 책임 편집 · AI 보조' if lang=='ko' else 'Responsible editor: Hyun-Jung Kim · AI-assisted'}</p></header><figure class="hero"><img src="transfer_hero.webp" alt="{m['alt']}" width="1672" height="941" fetchpriority="high"><figcaption>{m['caption']}</figcaption></figure><main><nav class="toc" aria-label="{m['contents']}"><strong>{m['contents']}</strong><ul>{toc}</ul></nav><article>{body}</article></main><footer><a href="{BASE}">AI Tech Review Letters</a> · <a href="{BASE}methods/">{'작성·검증 원칙' if lang=='ko' else 'Editorial methods'}</a></footer></div></body></html>'''
  (dist/'index.html').write_text(doc,encoding='utf-8')
 print('Built Korean and English HTML, four original SVGs and two web image copies.')
if __name__=='__main__':build()
