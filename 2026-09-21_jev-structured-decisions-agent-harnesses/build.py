"""Build bilingual pages and reproducible figures. No model or network calls."""
from pathlib import Path
from html import escape
import csv
import re
import shutil

P = Path(__file__).resolve().parent
BASE = 'https://infant83.github.io/AI_Tech_Review/'
META = {
 'ko': {'title':'에이전트의 작은 판단을 빠르게: Jev의 구조화된 결정과 적용 한계', 'subtitle':'System One 모델의 인터페이스·확률 보정·초기 평가를 읽고 연구 하네스의 적용 조건을 살피다', 'description':'TypeSafe Jev의 Choice·Score·Noul, RLCD와 확률 보정, LangChain의 5개 사례 반복 평가를 분석합니다. 형식 보장과 정확성을 구분하고 연구·코딩 하네스의 적용 조건을 제안합니다.', 'alt':'비정형 자료가 분류 장치를 지나 서로 다른 형태로 정돈되는 판단 모델의 개념 일러스트', 'caption':'그림 1. 자료를 정해진 형태의 판단으로 바꾸는 과정을 표현한 생성 일러스트입니다. 실제 장치·신경망 구조·측정 데이터가 아닙니다. OpenAI imagegen 제작.', 'label':'번외 심층 리뷰 · 에이전트 시스템 · 초기 실험 분석'},
 'en': {'title':'Fast Decisions Inside Agents: Jev’s Structured Outputs and Practical Limits', 'subtitle':'Examining System One interfaces, calibration and early evaluations for research harnesses', 'description':'A review of TypeSafe Jev, its decision primitives and calibration claims, a five-case repeated-judge experiment, and practical limits for research and coding harnesses.', 'alt':'Conceptual illustration of unstructured material passing through a sorting apparatus into distinct organized forms', 'caption':'Figure 1. AI-generated metaphor for turning material into bounded decisions. It depicts no real apparatus, neural architecture or measured data. Created with OpenAI imagegen.', 'label':'Special review · Agent systems · Early experiment analysis'}
}

def diagram(lang):
 labels = {
 'ko':['검토에 필요한 자료','관련 문단 · 실행 기록 · 적용 기준','Jev: 짧고 명확한 질문','Choice · Score · Noul','프로그램의 검사와 정책','형식 · 수치 · 권한 · 보류 기준','자동 처리','추가 추론','사람 검토','리뷰 제안 · 내부 신경망 구조 아님'],
 'en':['Relevant evidence','Passages · execution records · criteria','Jev: focused questions','Choice · Score · Noul','Program checks and policy','Types · numbers · permissions · abstention','Process','Reason further','Human review','Reviewer proposal · not a neural architecture']
 }[lang]
 def t(x,y,s,size=23):
  return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}">{escape(s)}</text>'
 s='<svg xmlns="http://www.w3.org/2000/svg" width="800" height="650" viewBox="0 0 800 650" role="img" aria-labelledby="title desc"><title id="title">Decision composition</title><desc id="desc">Evidence is evaluated through focused questions. Code checks the results before routing to processing, reasoning or review.</desc><rect width="800" height="650" fill="#f0f3ed"/><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#58726a"/></marker></defs><g font-family="Arial,Noto Sans KR,sans-serif" fill="#182c31">'
 for i in range(3):
  y=40+i*152
  s+=f'<rect x="95" y="{y}" width="610" height="108" rx="8" fill="'+['#dde9e3','#d5e9e6','#f2dfbd'][i]+'"/>'+t(400,y+40,labels[i*2],27)+t(400,y+78,labels[i*2+1],21)
  if i<2:s+=f'<path d="M400 {y+108}V{y+143}" stroke="#58726a" stroke-width="2" marker-end="url(#arrow)"/>'
 s+='<path d="M400 452V484H145V513M400 484V513M400 484H655V513" fill="none" stroke="#58726a" stroke-width="2"/>'
 for x,l in zip([145,400,655],labels[6:9]):
  s+=f'<rect x="{x-113}" y="513" width="226" height="60" rx="7" fill="#dde9e3"/>'+t(x,551,l,22)
 return s+t(400,617,labels[9],18)+'</g></svg>'

def chart():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 rows=list(csv.DictReader((P/'benchmark_summary.csv').open()))
 plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','font.size':12})
 fig,ax=plt.subplots(figsize=(8,4.4),layout='constrained')
 fig.patch.set_facecolor('#f0f3ed');ax.set_facecolor('#f0f3ed')
 names=[r['model'] for r in rows];v=[float(r['latency_seconds']) for r in rows]
 ax.barh(names,v,color=['#16746b','#94aaa3','#94aaa3','#94aaa3'],height=.57)
 ax.invert_yaxis();ax.set_xlim(0,3.3);ax.set_xlabel('Mean latency per evaluator call (s)')
 ax.set_title('Five frozen cases, repeated judgments',loc='left',pad=20,fontweight='bold')
 for i,x in enumerate(v):ax.text(x+.06,i,f'{x:.2f} s',va='center')
 ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0)
 ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
 fig.savefig(P/'artifacts'/'benchmark.svg',metadata={'Date':None,'Creator':'AI Tech Review','Description':'Reconstruction of reported mean latency values. Source: danielgshea/jev-as-a-judge, pinned in README. No new API measurements.'})
 plt.close(fig)

def build():
 chart()
 for lang,m in META.items():
  dist=P/'dist'/('en' if lang=='en' else '')
  dist.mkdir(parents=True,exist_ok=True)
  (P/'artifacts'/f'decision_flow_{lang}.svg').write_text(diagram(lang))
  for f in ['jev_hero.webp','review.css','benchmark.svg',f'decision_flow_{lang}.svg']:
   shutil.copy2(P/'artifacts'/f,dist/f)
  body=(P/'reports'/f'review_{lang}.html').read_text()
  toc=''.join(f'<li><a href="#{i}">{t}</a></li>' for i,t in re.findall(r'<section id="([^"]+)"><h2>(.*?)</h2>',body))
  canonical=f'{BASE}reviews/{P.name}/'+('en/' if lang=='en' else '')
  alternates=''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE}reviews/{P.name}/{s}">' for l,s in [('ko',''),('en','en/'),('x-default','')])
  links=' · '.join(f'<a lang="{l}" hreflang="{l}" href="{BASE}reviews/{P.name}/{s}" '+('aria-current="page" ' if lang==l else '')+f'>{label}</a>' for l,s,label in [('ko','','한국어'),('en','en/','English')])
  date='김현중 책임 편집 · AI 보조 · 근거 기준일 2026-09-21' if lang=='ko' else 'Responsible editor: Hyun-Jung Kim · AI-assisted · Evidence cutoff 2026-09-21'
  html=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(m['title'])}</title><meta name="description" content="{escape(m['description'],quote=True)}"><meta name="author" content="Hyun-Jung Kim"><link rel="canonical" href="{canonical}">{alternates}<meta property="og:title" content="{escape(m['title'],quote=True)}"><meta property="og:description" content="{escape(m['description'],quote=True)}"><meta property="og:type" content="article"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{canonical}jev_hero.webp"><meta property="og:image:alt" content="{m['alt']}"><meta name="twitter:card" content="summary_large_image"><meta property="article:published_time" content="2026-09-21"><meta property="article:modified_time" content="2026-09-21"><link rel="stylesheet" href="review.css"></head><body><nav class="top"><a href="{BASE}">AI Tech Review Letters</a><span>{links}</span></nav><div class="wrap"><header><div class="kicker">{m['label']}</div><h1>{m['title']}</h1><p class="subtitle">{m['subtitle']}</p><p class="date">{date}</p></header><figure class="hero"><img src="jev_hero.webp" width="1672" height="941" alt="{m['alt']}" fetchpriority="high"><figcaption>{m['caption']}</figcaption></figure><main><nav class="toc" aria-label="Contents"><ul>{toc}</ul></nav><article>{body}</article></main><footer><a href="{BASE}">AI Tech Review Letters</a> · <a href="{BASE}methods/">{'작성·검증 원칙' if lang=='ko' else 'Editorial methods'}</a></footer></div></body></html>'''
  (dist/'index.html').write_text(html)

if __name__=='__main__':build()
