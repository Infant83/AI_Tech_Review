"""Rebuild original explanatory SVGs and the pre-publication coverage inventory."""
from pathlib import Path
import json
import html
from bs4 import BeautifulSoup

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent
ASSETS = PACKAGE / "artifacts"
ASSETS.mkdir(exist_ok=True)

LABELS = {
    "ko": ["빠른 실행은 규칙으로, 느린 판단은 제한적으로", "리뷰 제안 · Avatar의 구현 재현이 아님",
           "빠른 실행", "의존관계 · 자원 제어 · 작업 실행", "관측 이력", "실패 · 재시도 · 탐색 진전", "느린 검토", "LLM 진단과 행동 제안",
           "행동 수용 검사", "상태 버전 · 권한 · 비용 · 과학 조건", "허용된 행동만 실행", "재시도 · 다음 묶음 · 종료", "제안이 낡았거나 불충분하면", "폐기 · 규칙 유지 · 사람 검토",
           "상태와 결과 기록", "예외만 전달", "제안", "통과", "보류", "빠른 루프는 느린 검토를 기다리지 않는다"],
    "en": ["Fast execution, bounded slower judgment", "Reviewer proposal · not an Avatar implementation diagram",
           "Fast execution", "Dependencies · resources · task execution", "Execution history", "Failures · retries · learning progress", "Slower review", "LLM diagnosis and action proposal",
           "Acceptance checks", "State version · authority · cost · science", "Execute permitted action", "Retry · next batch · stop", "Stale or unsupported proposal", "Discard · retain rules · human review",
           "Record state and outcomes", "Escalate exceptions", "Propose", "Pass", "Defer", "Fast control does not wait for slower deliberation"],
}

for lang, s in LABELS.items():
    def text(x, y, value, size=18, fill="#182e36", weight=400):
        return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" font-weight="{weight}" fill="{fill}">{html.escape(value)}</text>'
    def box(x,y,w,h,title,detail,color):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{color}" stroke="#adbab9"/>'+text(x+w/2,y+33,title,21,weight=700)+text(x+w/2,y+65,detail,15)
    def arrow(d):
        return f'<path d="{d}" fill="none" stroke="#557477" stroke-width="2.5" marker-end="url(#arrow)"/>'
    def label(x,y,value,width):
        return f'<rect x="{x-width/2}" y="{y-17}" width="{width}" height="24" rx="4" fill="#f8f6ef"/>'+text(x,y,value,16)
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="960" height="700" viewBox="0 0 960 700" role="img" aria-labelledby="title desc">'
    svg+=f'<title id="title">{html.escape(s[0])}</title><desc id="desc">{html.escape(s[1]+". "+s[-1])}</desc>'
    svg+='<metadata>Proposed / reviewer-constructed; inspired by arXiv:2609.10509v1; no measured data; CC BY-NC-SA 4.0</metadata>'
    svg+='<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="#557477"/></marker></defs>'
    svg+='<rect width="960" height="700" fill="#f8f6ef"/><g font-family="Noto Sans CJK KR, Arial, sans-serif">'
    svg+=text(480,45,s[0],28,weight=700)+text(480,76,s[1],16,fill="#637579")
    svg+=box(55,120,390,96,s[2],s[3],"#dcedea")+box(515,120,390,96,s[4],s[5],"#e9eeee")
    svg+=arrow('M445 168 H507')+text(480,108,s[14],14)
    svg+=box(515,300,390,96,s[6],s[7],"#f7e6be")+arrow('M710 216 V291')+label(710,262,s[15],174)
    svg+=box(55,300,390,96,s[8],s[9],"#e0e9ef")+arrow('M515 348 H453')+text(480,290,s[16],15)
    svg+=box(55,495,390,96,s[10],s[11],"#dcedea")+arrow('M250 396 V487')+text(218,451,s[17],16)
    svg+=box(515,495,390,96,s[12],s[13],"#f0e5df")+arrow('M445 370 H478 V541 H507')+label(478,451,s[18],58)
    svg+=arrow('M55 544 H25 V168 H47')+text(480,653,s[19],21,weight=700)
    svg+='</g></svg>\n'
    (ASSETS/f"control_boundary_{lang}.svg").write_text(svg,encoding="utf-8")

manifest=json.loads((ROOT/"site/manifest.json").read_text())
inventory=[]
for item in manifest:
    if item['folder']==PACKAGE.name:
        continue
    p=ROOT/'site'/item['href']
    soup=BeautifulSoup(p.read_text(),"html.parser")
    article=soup.find("article") or soup.find("main") or soup
    for el in article.select('script,style'):
        el.decompose()
    refs=sorted({a['href'] for a in article.select('a[href]') if a['href'].startswith('http')})
    inventory.append({"folder":item['folder'],"date":item['date'],"updated":item.get('updated'),"category":item['category'],
        "title":item['title'],"summary":item['summary'],"headings":[h.get_text(' ',strip=True) for h in article.select('h2,h3')],
        "claims":[p.get_text(' ',strip=True) for p in article.select('p') if p.get_text(strip=True)],"references":refs})
(PACKAGE/'notes/coverage_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f"SVGs: 2; audited public articles: {len(inventory)}; skipped new article")
