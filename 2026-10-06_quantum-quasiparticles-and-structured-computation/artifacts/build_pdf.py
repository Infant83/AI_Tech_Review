"""Typeset the complete bilingual review, with embedded Hangul and equation images."""
from pathlib import Path
from html.parser import HTMLParser
import html
import re
import subprocess
import sys
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle, HRFlowable, KeepTogether, PageBreak

ROOT = Path(__file__).resolve().parents[1]
TEMP = Path(sys.argv[3])
TEMP.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont('Review',sys.argv[1]))
pdfmetrics.registerFont(TTFont('ReviewBold',sys.argv[2]))
pdfmetrics.registerFontFamily('Review',normal='Review',bold='ReviewBold',italic='Review',boldItalic='ReviewBold')
INK=colors.HexColor('#18313c'); TEAL=colors.HexColor('#116f79'); MUTED=colors.HexColor('#58656d'); LINE=colors.HexColor('#d9dfdb')
WIDTH=A4[0]-102
STYLES={
 'body':ParagraphStyle('body',fontName='Review',fontSize=10,leading=16,textColor=INK,spaceAfter=10,wordWrap='CJK',allowWidows=0,allowOrphans=0),
 'title':ParagraphStyle('title',fontName='ReviewBold',fontSize=25,leading=33,textColor=INK,spaceAfter=14,wordWrap='CJK',keepWithNext=True),
 'h2':ParagraphStyle('h2',fontName='ReviewBold',fontSize=15.5,leading=22,textColor=TEAL,spaceBefore=18,spaceAfter=12,wordWrap='CJK',keepWithNext=True),
 'h3':ParagraphStyle('h3',fontName='ReviewBold',fontSize=12,leading=18,textColor=INK,spaceBefore=13,spaceAfter=8,wordWrap='CJK',keepWithNext=True),
 'dek':ParagraphStyle('dek',fontName='Review',fontSize=12,leading=18,textColor=MUTED,spaceAfter=10,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='Review',fontSize=8,leading=12,textColor=MUTED,spaceAfter=8,wordWrap='CJK'),
 'cell':ParagraphStyle('cell',fontName='Review',fontSize=8.6,leading=13,textColor=INK,wordWrap='CJK'),
 'note':ParagraphStyle('note',fontName='Review',fontSize=9.3,leading=15,textColor=INK,spaceAfter=10,wordWrap='CJK',borderColor=LINE,borderWidth=.5,borderPadding=12,backColor=colors.HexColor('#eef1ea')),
}
for style in STYLES.values():
    # Standard word wrapping supports inline equation images. CJK frag splitting
    # in this ReportLab version does not support those image fragments reliably.
    style.wordWrap = None

class Node:
    def __init__(self,tag='',attrs=None):
        self.tag=tag;self.attrs=dict(attrs or []);self.children=[]
    def get_text(self):
        return ''.join(c if isinstance(c,str) else c.get_text() for c in self.children)
    def find_all(self,tag):
        result=[]
        for c in self.children:
            if isinstance(c,Node):
                if c.tag==tag:result.append(c)
                result.extend(c.find_all(tag))
        return result

class DOM(HTMLParser):
    def __init__(self):super().__init__();self.root=Node();self.stack=[self.root]
    def handle_starttag(self,tag,attrs):
        n=Node(tag,attrs);self.stack[-1].children.append(n)
        if tag not in ['img','meta','link','br','hr','input']:self.stack.append(n)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:self.stack=self.stack[:i];break
    def handle_data(self,data):self.stack[-1].children.append(data)

def png(src):
    p=ROOT/'artifacts'/src
    if p.suffix!='.svg':return p
    out=TEMP/(p.stem+'.png')
    if not out.exists() or out.stat().st_mtime < p.stat().st_mtime:
        subprocess.run(['inkscape',str(p),'--export-type=png',f'--export-filename={out}','--export-dpi=220'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def inline(node):
    if isinstance(node,str):return html.escape(node)
    text=''.join(inline(c) for c in node.children)
    if node.tag=='img':
        p=png(node.attrs['src']);w,h=PILImage.open(p).size
        height=10.5;width=height*w/h
        return f'<img src="{p}" width="{width:.2f}" height="{height}" valign="-2"/>'
    if node.tag in ['strong','b']:return '<b>'+text+'</b>'
    if node.tag in ['em','i']:return '<i>'+text+'</i>'
    if node.tag=='a':return '<link href="'+html.escape(node.attrs.get('href',''),quote=True)+'" color="#116f79"><u>'+text+'</u></link>'
    if node.tag=='br':return '<br/>'
    return text

def image_flow(src,max_width=WIDTH,max_height=None):
    p=png(src);w,h=PILImage.open(p).size
    scale=max_width/w
    if max_height:scale=min(scale,max_height/h)
    return Image(str(p),width=w*scale,height=h*scale)

def table_flow(n):
    rows=n.find_all('tr');matrix=[]
    for row in rows:
        cells=[c for c in row.children if isinstance(c,Node) and c.tag in ['th','td']]
        matrix.append([Paragraph(inline(c),STYLES['cell']) for c in cells])
    widths=[WIDTH*.48,WIDTH*.22,WIDTH*.30] if len(matrix[0])==3 else [WIDTH/len(matrix[0])]*len(matrix[0])
    tab=Table(matrix,colWidths=widths,repeatRows=1,hAlign='LEFT')
    tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5efeb')),('LINEBELOW',(0,0),(-1,-1),.4,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    return tab

def flow(node,lang):
    if isinstance(node,str):return []
    cls=node.attrs.get('class','')
    if node.tag in ['details','script','header'] or cls in ['downloads','reading']:return []
    if node.tag in ['h1','h2','h3']:
        if node.tag=='h2' and (node.get_text().startswith('참고문헌') or node.get_text().startswith('References')):
            return [PageBreak(),Paragraph(inline(node),STYLES['h2'])]
        return [Paragraph(inline(node),STYLES['title' if node.tag=='h1' else node.tag])]
    if node.tag=='p':
        style='dek' if cls=='dek' else ('small' if cls in ['caption','kicker'] else 'body')
        return [Paragraph(inline(node),STYLES[style])]
    if node.tag=='figure':
        imgs=node.find_all('img');captions=node.find_all('figcaption')
        if not imgs:return []
        im=image_flow(imgs[0].attrs['src'],max_height=255 if cls=='hero' else 270)
        result=[im,Spacer(1,7)]
        if captions:result.append(Paragraph(inline(captions[0]),STYLES['small']))
        return [KeepTogether(result)]
    if node.tag=='aside':return [Spacer(1,8),Paragraph(inline(node),STYLES['note']),Spacer(1,5)]
    if cls=='math-block':
        src=node.find_all('img')[0].attrs['src']
        im=image_flow(src,max_width=WIDTH*.94,max_height=45)
        return [Spacer(1,5),im,Spacer(1,12)]
    if node.tag=='table':return [Spacer(1,5),table_flow(node),Spacer(1,9)]
    if node.tag=='ol':
        result=[]
        for i,c in enumerate((c for c in node.children if isinstance(c,Node) and c.tag=='li'),1):
            result.append(Paragraph(str(i)+'. '+inline(c),STYLES['small']))
        return result
    if node.tag=='div' and cls=='footer':return []
    result=[]
    for c in node.children:result.extend(flow(c,lang))
    return result

def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(LINE);canvas.line(51,40,A4[0]-51,40)
    canvas.setFont('Review',7.2);canvas.setFillColor(MUTED)
    canvas.drawString(51,28,'AI Tech Review Letters · 2026-10-06')
    canvas.drawRightString(A4[0]-51,28,str(doc.page));canvas.restoreState()

def main():
    for lang in ['ko','en']:
        d=ROOT/'dist'/('en' if lang=='en' else '')
        parser=DOM();parser.feed((d/'index.html').read_text())
        main=parser.root.find_all('main')[0]
        story=flow(main,lang)
        story.extend([Spacer(1,18),HRFlowable(width='100%',color=LINE),Spacer(1,10)])
        note=('책임편집: 김현중 · AI 보조 작성: OpenAI Codex Work Mode. 출처 검증, 한영 작성, 과학 감수와 도표·PDF 검수를 수행했다. 사람의 주제·게시 요청은 확인했으며 문장 단위 사람 검토나 논문의 독립 실험 재현은 수행하지 않았다. 핵심 5편은 동료평가 전이며 OLED 연결은 리뷰어 해석이다. 근거 확인일: 2026-10-06.' if lang=='ko' else 'Responsible editor: Hyun-Jung Kim. AI-assisted production: OpenAI Codex Work Mode. Primary-source checking, bilingual writing, scientific copyediting, and figure/PDF verification were performed. Topic and publication were requested by the editor; no line-by-line human approval or independent experimental reproduction was performed. The five core papers are preprints. OLED applications are reviewer interpretations. Evidence cutoff: 2026-10-06.')
        story.append(Paragraph(note,STYLES['small']))
        out=d/f'review_{lang}.pdf'
        doc=SimpleDocTemplate(str(out),pagesize=A4,leftMargin=51,rightMargin=51,topMargin=48,bottomMargin=55,title=main.find_all('h1')[0].get_text(),author='Hyun-Jung Kim / AI Tech Review Letters')
        doc.build(story,onFirstPage=footer,onLaterPages=footer)
        print(out.name,'created')

if __name__=='__main__':main()
