#!/usr/bin/env python3
"""Render this issue from reviewed prose, factual tables and attributed figures."""
from pathlib import Path
import argparse, html, json, os
from datetime import datetime, timezone
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak, Image, KeepTogether

TOPIC = Path(__file__).resolve().parents[1]
NAVY=colors.HexColor('#17364b');TEAL=colors.HexColor('#247b83')
INK=colors.HexColor('#263640');MUTED=colors.HexColor('#62737c')
LINE=colors.HexColor('#cfdae0');PALE=colors.HexColor('#e9f2f6')
W,H=A4;M=48;CW=W-2*M

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=TOPIC/'reports_data.json')
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--font',type=Path,required=True)
    ap.add_argument('--font-heading',type=Path,required=True)
    ap.add_argument('--font-fallback',type=Path,required=True)
    a=ap.parse_args();r=json.loads(a.source.read_text());day=r['date']
    pdfmetrics.registerFont(TTFont('Body',str(a.font)))
    pdfmetrics.registerFont(TTFont('Heading',str(a.font_heading)))
    pdfmetrics.registerFont(TTFont('Fallback',str(a.font_fallback)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Heading',italic='Body',boldItalic='Heading')
    S={}
    for k,font,size,leading,color,after in [
        ('title','Heading',22,29,NAVY,13),('h1','Heading',16,22,NAVY,11),
        ('h2','Heading',12,18,TEAL,7),('body','Body',9.8,14.7,INK,8),
        ('small','Body',8.1,11.6,MUTED,5),('cell','Body',8.5,12.1,INK,0),
        ('ref','Body',8.5,12.2,TEAL,5)]:
        S[k]=ParagraphStyle(k,fontName=font,fontSize=size,leading=leading,textColor=color,
                           spaceAfter=after,wordWrap='CJK',keepWithNext=k in ['h1','h2'])
    def norm(s):return str(s).replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')
    common=set(pdfmetrics.getFont('Body').face.charToGlyph)&set(pdfmetrics.getFont('Heading').face.charToGlyph)
    fallback=set(pdfmetrics.getFont('Fallback').face.charToGlyph)
    def rich(s):
        out=[];run=[];mode=None
        def flush():
            if run:
                value=html.escape(''.join(run)).replace('\n','<br/>')
                out.append('<font name="Fallback">'+value+'</font>' if mode else value)
                run.clear()
        for c in norm(s):
            use=ord(c) not in common and c!='\n'
            if use and ord(c) not in fallback:raise ValueError('Missing glyph '+repr(c))
            if mode is not None and use!=mode:flush()
            mode=use;run.append(c)
        flush();return ''.join(out)
    def p(s,k='body'):return Paragraph(rich(s),S[k])
    st=[]
    def add(s,k='body'):st.append(p(s,k))
    def link(label,url,k='small'):
        st.append(Paragraph('<link href="'+html.escape(url,quote=True)+'" color="#247b83">'+rich(label)+'</link>',S[k]))
    def page(title):
        st.append(PageBreak());add(title,'h1')
    def table(headers,rows,widths):
        t=Table([[p(v,'cell') for v in headers]]+[[p(v,'cell') for v in row] for row in rows],colWidths=widths,repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('GRID',(0,0),(-1,-1),.35,LINE),
           ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),
           ('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
        st.extend([t,Spacer(1,9)])
    add('AGENTIC TECH REVIEW LETTERS  /  DAILY RESEARCH BRIEF '+r['issue'],'small')
    add(r['title'],'title');add(r['tagline'],'small');add('Executive summary','h2')
    for s in r['summary']:add(s)
    table(['연구·질문','실제 결과·실행 수준','선정 의미와 조건'],r['comparison'],[CW*.29,CW*.35,CW*.36])
    add('조사일과 논문의 온라인 공개일을 구별했다. 논문 보고·편집 해석·수치 대조의 범위와 읽은 판본은 마지막에 기록한다.','small')
    for q in r['papers']:
        page(str(q['id'])+'. '+q['heading'])
        link(q['journal']+' | 온라인 '+q['published']+' | DOI '+q['doi'],q['url'])
        for s in q['paragraphs']:add(s)
        for f in q['figures']:
            im=Image(str(TOPIC/'artifacts'/f['asset']))
            scale=min(CW/im.imageWidth,f.get('height',230)/im.imageHeight)
            im.drawWidth=im.imageWidth*scale;im.drawHeight=im.imageHeight*scale;im.hAlign='CENTER'
            st.extend([Spacer(1,3),im,Spacer(1,6),p(f['caption'],'small')])
            link('그림 근거·원 판본',f['url'])
            if f.get('license'):link('CC BY 4.0',f['license'])
        for s in q['after']:add(s)
    page('리뷰로 이어 볼 두 질문')
    for plan in r['plans']:
        add(plan['title'],'h2');add(plan['audience'],'small');add(plan['thesis'])
        for i,s in enumerate(plan['outline'],1):add(str(i)+'. '+s)
        add('확인할 근거: '+plan['checks'],'small');add(plan['relation'],'small');st.append(Spacer(1,12))
    page('외부 공유 문안과 다음 조사')
    add(r['external_title'],'h2')
    for s in r['external']:add(s)
    add('Watchlist','h2')
    for s in r['watchlist']:add('• '+s)
    add('조사 범위와 접근 상태','h2')
    for s in r['coverage']:add(s,'small')
    page('직접 출처와 실제로 읽은 판본')
    for q in r['papers']:
        start=len(st)
        add('['+str(q['id'])+'] '+q['citation'],'ref')
        link('DOI '+q['doi'],q['url']);link('확인한 본문·판본',q['read_url'])
        add(q['read_scope'],'small');add(q['availability'],'small')
        block=st[start:];del st[start:];st.append(KeepTogether(block))
    for c in r['context_refs']:
        start=len(st)
        add('['+str(c['n'])+'] '+c['citation'],'ref');link('직접 출처',c['url'])
        add(c['scope'],'small')
        block=st[start:];del st[start:];st.append(KeepTogether(block))
    add('작성·검증과 그림 출처','h2')
    for s in r['disclosure']:add(s,'small')
    class Numbered(canvas.Canvas):
        def __init__(self,*args,**kw):super().__init__(*args,**kw);self.states=[]
        def showPage(self):self.states.append(dict(self.__dict__));self._startPage()
        def save(self):
            total=len(self.states)
            for state in self.states:
                self.__dict__.update(state);self.saveState();self.setStrokeColor(LINE);self.line(M,42,W-M,42)
                self.setFont('Body',8);self.setFillColor(MUTED)
                self.drawString(M,28,'ATRL | Daily Research Brief | '+day)
                self.drawRightString(W-M,28,str(self._pageNumber)+' / '+str(total));self.restoreState();super().showPage()
            super().save()
    def header(c,doc):
        if doc.page>1:
            c.saveState();c.setFont('Body',8);c.setFillColor(MUTED);c.drawString(M,H-30,'DRB | '+r['short_title']);c.restoreState()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    os.environ['SOURCE_DATE_EPOCH']=str(int(datetime.fromisoformat(day).replace(tzinfo=timezone.utc).timestamp()))
    doc=SimpleDocTemplate(str(a.output),pagesize=A4,leftMargin=M,rightMargin=M,topMargin=63,bottomMargin=59,
        title='Daily Research Brief | '+day+' | '+r['short_title'],author='Agentic Tech Review Letters / AEDAUT',
        subject='Cryogenic multiplexing, cavity-coupled Rydberg arrays and vibronic structure of spin defects',pageCompression=1)
    doc.build(st,onFirstPage=header,onLaterPages=header,canvasmaker=Numbered)
    print(json.dumps({'pdf':str(a.output),'bytes':a.output.stat().st_size},ensure_ascii=False))
if __name__=='__main__':main()
