#!/usr/bin/env python3
"""Build a reviewed DRB from its public prose/data and licensed figure inputs."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,html,os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,PageBreak,Image,KeepTogether
from reportlab.graphics.shapes import Drawing,Line,String,Rect,Polygon
TOPIC=Path(__file__).resolve().parents[1]
NAVY=colors.HexColor('#17364b');TEAL=colors.HexColor('#247b83');INK=colors.HexColor('#263640');MUTED=colors.HexColor('#62737c');LINE=colors.HexColor('#cfdae0');PALE=colors.HexColor('#e9f2f6')
W,H=A4;M=54;CW=W-2*M

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=TOPIC/'reports_data.json');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--font',type=Path,required=True);ap.add_argument('--font-heading',type=Path,required=True);args=ap.parse_args()
 r=json.loads(args.source.read_text());day=r['date'];assets=TOPIC/'artifacts'
 pdfmetrics.registerFont(TTFont('Body',str(args.font)));pdfmetrics.registerFont(TTFont('Heading',str(args.font_heading)));pdfmetrics.registerFontFamily('Body',normal='Body',bold='Body',italic='Body',boldItalic='Body')
 S={key:ParagraphStyle(key,fontName=face,fontSize=size,leading=leading,textColor=color,spaceAfter=after,wordWrap='CJK',keepWithNext=key in ['h1','h2']) for key,face,size,leading,color,after in [('title','Heading',23,30,NAVY,14),('h1','Heading',16,22,NAVY,10),('h2','Heading',12,17,TEAL,7),('body','Body',10.1,15.2,INK,7),('small','Body',8.4,12,MUTED,5),('cell','Body',8.8,12.8,INK,0),('ref','Body',9.1,13,TEAL,5)]}
 def norm(s):return str(s).replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')
 def p(s,style='body'):return Paragraph(html.escape(norm(s)).replace('\n','<br/>'),S[style])
 story=[]
 def add(s,style='body'):story.append(p(s,style))
 def link(label,url,style='small'):story.append(Paragraph('<link href="'+html.escape(url,quote=True)+'" color="#247b83">'+html.escape(norm(label))+'</link>',S[style]))
 def sub(s):add(s,'h2')
 def page(s):story.append(PageBreak());add(s,'h1')
 def point(label,text):add(label+'  '+text)
 def table(head,rows,widths):
  t=Table([[p(x,'cell') for x in head]]+[[p(x,'cell') for x in row] for row in rows],colWidths=widths,repeatRows=1)
  t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('GRID',(0,0),(-1,-1),.35,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));story.extend([t,Spacer(1,8)])
 def boundary(text):
  t=Table([[p(text,'cell')]],colWidths=[CW]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#fff3e3')),('BOX',(0,0),(-1,-1),.4,colors.HexColor('#e8d8bd')),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]));story.extend([t,Spacer(1,7)])
 def label(x,y,s,size=10,color=INK):return String(x,y,norm(s),fontName='Body',fontSize=size,fillColor=color)
 def schematic(kind):
  if kind=='noise_bound':
   d=Drawing(CW,175);x0=90;x1=CW-25;y=63;scale=(x1-x0)
   d.add(Line(x0,y,x1,y,strokeColor=MUTED,strokeWidth=1))
   for value in [0,.2,.4,.6,.8,1]:
    x=x0+value*scale;d.add(Line(x,y-4,x,y+4,strokeColor=MUTED));d.add(label(x-7,y-19,str(value),8,MUTED))
   x=x0+.7*scale;d.add(Line(x,y+12,x,y+59,strokeColor=TEAL,strokeWidth=2));d.add(Line(x,y+36,x-110,y+36,strokeColor=TEAL,strokeWidth=2));d.add(Polygon([x-110,y+36,x-101,y+40,x-101,y+32],fillColor=TEAL,strokeColor=TEAL))
   d.add(label(x-41,y+69,'0.70 × 10³',11,TEAL));d.add(label(4,y+31,'508 MHz',11));d.add(label(x0+30,15,'Sδω  [10³ rad²/s]',10));d.add(label(12,154,'68% Bayesian 上限'.replace('上限','상한')+' · 60,000회',11,NAVY));d.add(label(x0+15,131,'화살표는 상한의 방향이며 확률분포가 아니다.',9,MUTED))
   return d
  if kind=='inverse':
   d=Drawing(CW,174);bw=(CW-36)/3
   for i,(title,text) in enumerate([('전달 스펙트럼','수치적으로 만든 수송 자료'),('비지도 표현 학습','물리 decoder + autoencoder'),('Hamiltonian 추정','매개변수와 비유일성 확인')]):
    x=i*(bw+18);d.add(Rect(x,65,bw,83,rx=5,ry=5,fillColor=PALE,strokeColor=LINE));d.add(label(x+9,123,title,10,TEAL));d.add(label(x+9,99,text,8.5))
    if i<2:
     d.add(Line(x+bw+2,105,x+bw+15,105,strokeColor=TEAL));d.add(Polygon([x+bw+15,105,x+bw+10,108,x+bw+10,102],fillColor=TEAL,strokeColor=TEAL))
   d.add(label(10,35,'리뷰 재구성 | 원문 방법의 관계도; 새로운 수송 데이터·성능 곡선 없음',9,MUTED));return d
  raise ValueError(kind)
 add('AGENTIC TECH REVIEW LETTERS  /  DAILY RESEARCH BRIEF 02','small');add(r['title'],'title');add(day+' | 새 온라인 논문 범위: 11월 13-14일 | 자료 확인: '+day,'small')
 sub('Executive summary')
 for text in r['summary']:add(text)
 table(['논문·핵심 질문','보고 결과·실행 수준','선정 판단·한계'],[[q['table_title'],q['table_result'],q['table_assessment']] for q in r['papers']],[CW*.29,CW*.36,CW*.35])
 add('선정 논문 4건. Nature와 Artificial Intelligence Review도 별도로 재확인했으며, 확인한 최신 목록에서 11월13-14일 새 항목은 보이지 않았다. 후보 수를 채우기 위해 이전 연구를 새 소식으로 넣지 않았다.','small')
 boundary('이 보고서의 수치와 실험은 원문 보고다. 계산·실험·학습을 독립 재현하지 않았다. DOI와 읽은 판본·범위를 마지막에 기록했다.')
 for q in r['papers']:
  page(str(q['id'])+'. '+q['heading']);link('['+str(q['id'])+'] '+q['journal']+' | 온라인 '+q['published']+' | DOI '+q['doi'],q['url'])
  point('핵심 주장',q['claim']);point('핵심 결과·조건',q['result'])
  if q.get('operating_rows'):table(['측정','조건','보고 결과'],q['operating_rows'],[CW*.24,CW*.41,CW*.35])
  f=q['figure'];story.append(Spacer(1,4))
  if f.get('kind'):story.append(schematic(f['kind']))
  else:
   im=Image(str(assets/f['asset']));scale=min(CW/im.imageWidth,f.get('height',255)/im.imageHeight);im.drawWidth=im.imageWidth*scale;im.drawHeight=im.imageHeight*scale;im.hAlign='CENTER';story.append(im)
  story.append(Spacer(1,5));add(f['caption'],'small');link(f['credit'],f['url'])
  if f.get('license'):link('그림 재사용 라이선스',f['license'])
  point('그림 읽기',f['reading']);point('의미·리뷰 해석',q['meaning']);point('인사이트·후속 제안',q['insight']);boundary(q['limit'])
 page('5. 리뷰 기획과 이어 볼 질문')
 for plan in r['plans']:
  sub(plan['title']);point('독자·범위',plan['audience']);point('중심 논지',plan['thesis'])
  for i,text in enumerate(plan['outline'],1):add(str(i)+'. '+text)
  add('확인할 근거: '+plan['checks'],'small');add('기존 기획과의 관계: '+plan['relation'],'small')
 page('6. 외부 공유 문안과 다음 조사')
 sub(r['external_title'])
 for text in r['external_brief']:add(text)
 sub('Watchlist')
 for text in r['watchlist']:add('- '+text)
 sub('조사 범위·접근 상태')
 for text in r['coverage']:add(text,'small')
 page('7. 원문·판본·작성과 검증')
 for q in r['papers']:
  add('['+str(q['id'])+'] '+q['citation'],'ref')
  ref_links='<link href="'+html.escape(q['url'],quote=True)+'" color="#247b83">DOI '+html.escape(q['doi'])+'</link>'
  if q.get('read_url'):ref_links+=' | <link href="'+html.escape(q['read_url'],quote=True)+'" color="#247b83">확인한 공개 전문·판본</link>'
  story.append(Paragraph(ref_links,S['small']))
  add('확인 범위: '+q['read_scope'],'small');add('공식 데이터·코드: '+q['availability'],'small')
 add('[5] '+r['air_citation'],'ref');link('Artificial Intelligence Review | 기존 리뷰의 후속 판본 점검',r['air_url']);add(r['air_scope'],'small')
 sub('작성·검증')
 add('책임 편집자: 김현중. 편집부(AEDAUT; Agentic Editorial and Authoring Team)가 조사·집필·감수했다. AI 보조: OpenAI Codex. 정확한 실행 모델 식별자는 미보존이다. 사람의 문장별 감수·독자 이해도 평가는 수행하지 않았다.','small')
 add('역할: root(통합·Nature·PDF·공개), aps_condensed_survey(PRL·PRB), aps_quantum_survey(PRX·PRX Quantum), brief_format(AIR·한영 글). 별도 담당자들이 주장·수치·서지·한영·렌더를 교차 확인했다. 원문 실험·학습·코드·증명을 독립 재현하지 않았다.','small')
 add('편집 방법: ATRL 작성 방법2026.08, 과학 설명 준칙2026-10-22, APS 인용 기준·문체 감사 하네스2026-11-11. 그림1·4는 출판 원그림의 CC BY4.0, 그림3은 공개 arXiv v3 원그림의 CC BY-SA4.0 재사용이다. 세 그림은 크기 조절 외 변경이 없으며 원 출처·권리를 유지한다. 그림2는 보고된 단일 잡음 상한을 자체 도식화한 리뷰 재구성이다. 수송·잡음·학습 곡선을 임의 복원하지 않았다.','small')
 class Numbered(canvas.Canvas):
  def __init__(self,*a,**kw):super().__init__(*a,**kw);self.states=[]
  def showPage(self):self.states.append(dict(self.__dict__));self._startPage()
  def save(self):
   total=len(self.states)
   for state in self.states:
    self.__dict__.update(state);self.saveState();self.setStrokeColor(LINE);self.line(M,42,W-M,42);self.setFont('Body',8);self.setFillColor(MUTED);self.drawString(M,28,'ATRL | Daily Research Brief | '+day);self.drawRightString(W-M,28,str(self._pageNumber)+' / '+str(total));self.restoreState();super().showPage()
   super().save()
 def header(c,doc):
  c.saveState();c.setFont('Body',8);c.setFillColor(MUTED)
  if doc.page>1:c.drawString(M,H-30,'DRB | '+r['short_title'])
  c.restoreState()
 args.output.parent.mkdir(parents=True,exist_ok=True);old=os.environ.get('SOURCE_DATE_EPOCH');os.environ['SOURCE_DATE_EPOCH']=str(int(datetime.fromisoformat(day).replace(tzinfo=timezone.utc).timestamp()))
 doc=SimpleDocTemplate(str(args.output),pagesize=A4,leftMargin=M,rightMargin=M,topMargin=68,bottomMargin=59,title='Daily Research Brief | '+day+' | '+r['short_title'],author='Agentic Tech Review Letters / AEDAUT',subject='Quantum materials, memories, inverse models and simulation',pageCompression=1)
 doc.build(story,onFirstPage=header,onLaterPages=header,canvasmaker=Numbered)
 if old is None:os.environ.pop('SOURCE_DATE_EPOCH',None)
 else:os.environ['SOURCE_DATE_EPOCH']=old
 print(json.dumps({'pdf':str(args.output),'bytes':args.output.stat().st_size},ensure_ascii=False))
if __name__=='__main__':main()
