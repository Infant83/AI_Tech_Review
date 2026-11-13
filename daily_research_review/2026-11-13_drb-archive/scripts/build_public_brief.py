#!/usr/bin/env python3
"""Build the November 13 DRB public edition from reviewed prose and figure data.

Requires reportlab. Supply licensed Unicode fonts with --font and --font-bold.
No original article image, email, or private report is an input to this builder.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

TOPIC = Path(__file__).resolve().parents[1]
NAVY = colors.HexColor('#193b4b')
TEAL = colors.HexColor('#217b76')
ORANGE = colors.HexColor('#a05a24')
INK = colors.HexColor('#243b43')
MUTED = colors.HexColor('#586c72')
PALE = colors.HexColor('#eef5f4')
LINE = colors.HexColor('#ccdcd9')
W, H = A4
M = 48
CW = W - 2*M


def normalized(value):
    return str(value).replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, default=TOPIC/'reports_data.json')
    ap.add_argument('--output', type=Path, default=TOPIC/'artifacts/daily_research_brief_2026-11-13.pdf')
    ap.add_argument('--font', type=Path, required=True)
    ap.add_argument('--font-bold', type=Path, required=True)
    ap.add_argument('--qa-dir', type=Path)
    args = ap.parse_args()
    r = json.loads(args.source.read_text())
    assert len(r['papers']) == 6 and [x['id'] for x in r['papers']] == list(range(1, 7))
    pdfmetrics.registerFont(TTFont('BriefBody', str(args.font)))
    pdfmetrics.registerFont(TTFont('BriefBold', str(args.font_bold)))
    pdfmetrics.registerFontFamily('BriefBody', normal='BriefBody', bold='BriefBold', italic='BriefBody', boldItalic='BriefBold')
    styles = {
        'title': ParagraphStyle('title', fontName='BriefBold', fontSize=22, leading=29, textColor=NAVY, wordWrap='CJK'),
        'heading': ParagraphStyle('heading', fontName='BriefBold', fontSize=16, leading=23, textColor=NAVY, wordWrap='CJK'),
        'body': ParagraphStyle('body', fontName='BriefBody', fontSize=10.2, leading=16.2, textColor=INK, wordWrap='CJK'),
        'small': ParagraphStyle('small', fontName='BriefBody', fontSize=8.2, leading=12, textColor=MUTED, wordWrap='CJK'),
        'ref': ParagraphStyle('ref', fontName='BriefBody', fontSize=9.1, leading=13, textColor=INK, wordWrap='CJK'),
        'figure': ParagraphStyle('figure', fontName='BriefBody', fontSize=9, leading=13, textColor=INK, wordWrap='CJK'),
        'figurebold': ParagraphStyle('figurebold', fontName='BriefBold', fontSize=10.4, leading=15, textColor=NAVY, wordWrap='CJK'),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # A reproducible document timestamp uses the stated edition date, not a
    # misleading library-default epoch or a claim about the exact writing time.
    edition_epoch = str(int(datetime.fromisoformat(r['public_edition_date']).replace(tzinfo=timezone.utc).timestamp()))
    previous_epoch = os.environ.get('SOURCE_DATE_EPOCH')
    os.environ['SOURCE_DATE_EPOCH'] = edition_epoch
    c = canvas.Canvas(str(args.output), pagesize=A4, pageCompression=1, invariant=1)
    if previous_epoch is None:
        os.environ.pop('SOURCE_DATE_EPOCH', None)
    else:
        os.environ['SOURCE_DATE_EPOCH'] = previous_epoch
    c.setTitle('Daily Research Brief | 2026-11-13 | '+r['title'])
    c.setAuthor('Agentic Tech Review Letters / AEDAUT')
    c.setSubject('Public edition: research models, observables and computational costs')
    c.setCreator('ATRL deterministic public DRB builder')
    positions = []
    page = 0

    def para(text, x, y, width=CW, style='body', gap=9, raw=False):
        value = normalized(text)
        p = Paragraph(value if raw else html.escape(value).replace('\n', '<br/>'), styles[style])
        _, height = p.wrap(width, H)
        if y-height < 44:
            raise ValueError(f'Page {page} overflows: {text[:65]}')
        p.drawOn(c, x, y-height)
        positions.append({'page':page,'x':round(x,2),'top':round(y,2),'bottom':round(y-height,2),'width':round(width,2),'style':style})
        return y-height-gap

    def start(label):
        nonlocal page
        if page: c.showPage()
        page += 1
        c.setFillColor(TEAL);c.setFont('BriefBold',8)
        c.drawString(M,H-30,'AGENTIC TECH REVIEW LETTERS')
        c.setFont('BriefBody',8);c.drawRightString(W-M,H-30,'Daily Research Brief | 2026-11-13')
        c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(M,H-38,W-M,H-38)
        c.setFillColor(MUTED);c.setFont('BriefBody',7.3)
        c.drawString(M,25,label+' | Public edition · 2026-11-13')
        c.drawRightString(W-M,25,str(page))
        return H-61

    def text_box(x,y,width,height,title,body):
        c.setFillColor(PALE);c.setStrokeColor(LINE);c.roundRect(x,y,width,height,8,stroke=1,fill=1)
        para(title,x+11,y+height-11,width-22,'figurebold',gap=4)
        para(body,x+11,y+height-35,width-22,'figure',gap=0)

    def arrow(x1,y1,x2,y2):
        c.setStrokeColor(TEAL);c.setFillColor(TEAL);c.setLineWidth(1.4);c.line(x1,y1,x2,y2)
        path=c.beginPath();path.moveTo(x2,y2);path.lineTo(x2-6,y2+3);path.lineTo(x2-6,y2-3);path.close();c.drawPath(path,fill=1,stroke=0)

    def chart(kind, y):
        """Original diagrams or plots of selected reported scalar values, never traced curves."""
        height=165
        low=y-height
        c.setFillColor(colors.white);c.setStrokeColor(LINE);c.roundRect(M,low,CW,height,8,stroke=1,fill=1)
        if kind == 'inverse':
            bw=(CW-58)/3;by=low+70
            text_box(M+10,by,bw,78,'측정 자료','자화 36점\n1.4 K')
            text_box(M+29+bw,by,bw,78,'고전 모형 탐색','24 sites / ED\n500평가 × 5회')
            text_box(M+48+2*bw,by,bw,78,'남은 제약 검사','비열 · 구조인자\n감수율')
            arrow(M+12+bw,by+39,M+26+bw,by+39);arrow(M+31+2*bw,by+39,M+45+2*bw,by+39)
            para('최저 자화 비용: K=-6.0, Γ=7.5, Γ′=-0.3, J=-1.75 meV; g_c=2.3',M+14,low+54,CW-28,'figure',gap=4)
            para('자화의 둔감한 방향을 다른 관측량이 얼마나 좁히는가?',M+14,low+30,CW-28,'figurebold',gap=0)
        elif kind == 'moire':
            text_box(M+12,low+105,CW-24,47,'DFT 유래 continuum Hamiltonian','')
            para('고전 transformer 파동함수 + 변분 에너지 최소화',M+16,low+95,CW-32,'figurebold',gap=0)
            bw=(CW-38)/2
            text_box(M+12,low+13,bw,65,'강자성 예제','28전자 / 21단위격자\n총스핀·운동량 점유수')
            text_box(M+26+bw,low+13,bw,65,'반강자성 예제','최대54전자 / 27단위격자\n스핀 구조인자')
        elif kind == 'deepqmc':
            axis_x=M+136;axis_end=W-M-28;axis_y=low+28;scale=(axis_end-axis_x)/35
            c.setStrokeColor(MUTED);c.line(axis_x,axis_y,axis_end,axis_y)
            for val in [0,10,20,30]:
                x=axis_x+val*scale;c.line(x,axis_y,x,axis_y-4);c.setFont('BriefBody',8);c.setFillColor(MUTED);c.drawCentredString(x,axis_y-14,str(val))
            data=r['figures']['deepqmc']
            for i,(label,val,err) in enumerate(zip(data['labels'],data['values'],data['uncertainty'])):
                yy=low+115-i*48;c.setFillColor(INK);c.setFont('BriefBody',9);c.drawString(M+14,yy-3,label)
                xx=axis_x+val*scale;c.setFillColor(TEAL);c.circle(xx,yy,4,fill=1,stroke=0)
                c.setStrokeColor(TEAL);c.line(xx-err*scale,yy,xx+err*scale,yy);c.line(xx-err*scale,yy-5,xx-err*scale,yy+5);c.line(xx+err*scale,yy-5,xx+err*scale,yy+5)
                c.setFillColor(NAVY);c.drawString(min(xx+10,axis_end-20),yy+9,f'{val:g}({int(round(err*10))})')
            para('Relative energy MAE vs NES-VMC (meV)',axis_x,low+158,axis_end-axis_x,'figurebold',gap=0)
        elif kind == 'vdbf':
            bw=(CW-38)/2
            text_box(M+12,low+24,bw,126,'Table I: 10 × 10 / OBC','cutoff 10^-3 / 100회 반복\n에너지 오차 0.158%\n단일 스레드 2.5분\nDMRG: 64스레드 / 3213.9분')
            text_box(M+26+bw,low+24,bw,126,'Fig.3: 1 × 100 체인','cutoff 10^-4\n연결 스핀 상관 C(r)\nvDBF: 빠른 감쇠\nDMRG: 더 먼 거리의 교대 상관')
        elif kind == 'prethermal':
            para('180원자 2D 실험: 관측 범위',M+14,low+151,CW-28,'figurebold',gap=0)
            x1=M+44;x2=W-M-44;yy=low+93;c.setStrokeColor(TEAL);c.setLineWidth(2);c.line(x1,yy,x2,yy)
            for i in range(5):
                xx=x1+(x2-x1)*i/4;c.line(xx,yy-5,xx,yy+5);c.setFillColor(INK);c.setFont('BriefBody',9);c.drawCentredString(xx,yy-21,f'{i} μs')
            para('시간점당 100샷 · 공개 v1에 적힌 관측 범위',M+14,low+61,CW-28,'figure',gap=0)
            para('Fig.4(b)의 크기 비교: 9 / 16 / 64 / 180원자',M+14,low+32,CW-28,'figurebold',gap=0)
        elif kind == 'air':
            x1=M+142;x2=W-M-30;ay=low+28;scale=(x2-x1)/100
            c.setStrokeColor(MUTED);c.setLineWidth(.7);c.line(x1,ay,x2,ay)
            for value in [0,25,50,75,100]:
                xx=x1+value*scale;c.line(xx,ay,xx,ay-4);c.setFillColor(MUTED);c.setFont('BriefBody',8);c.drawCentredString(xx,ay-13,str(value))
            data=r['figures']['air']
            for i,(label,value,std) in enumerate(zip(data['labels'],data['values'],data['std'])):
                yy=low+125-i*35;xx=x1+value*scale;c.setFillColor(INK);c.setFont('BriefBody',8.7);c.drawString(M+13,yy-3,label)
                c.setFillColor(TEAL if std is not None else ORANGE)
                if std is not None:
                    c.circle(xx,yy,3.5,stroke=0,fill=1);c.setStrokeColor(TEAL);c.line(xx-std*scale,yy,xx+std*scale,yy);c.line(xx-std*scale,yy-4,xx-std*scale,yy+4);c.line(xx+std*scale,yy-4,xx+std*scale,yy+4)
                else:
                    p=c.beginPath();p.moveTo(xx,yy+4);p.lineTo(xx+4,yy);p.lineTo(xx,yy-4);p.lineTo(xx-4,yy);p.close();c.drawPath(p,stroke=0,fill=1)
                c.setFillColor(NAVY);c.drawString(xx-30,yy+10,f'{value:g}%')
            para('Test accuracy (%)',x1,low+159,x2-x1,'figurebold',gap=0)
        else: raise ValueError(kind)
        return low-12

    y=start('Brief')
    y=para(r['title'],M,y,style='title',gap=12)
    y=para(r['subtitle'],M,y,style='small',gap=16)
    for item in r['intro']: y=para(item,M,y)
    y=para('이번에 읽는 여섯 자료',M,y-7,style='heading',gap=10)
    for item in r['papers']:
        y=para(f"[{item['id']}] {item['heading']} · {item['published']}",M,y,style='body',gap=7)
    y=para('공개 파생판',M,y-8,style='heading',gap=8)
    y=para(r['revision_note'],M,y,style='small',gap=8)
    para('원호·근거 기준일 2026-11-13 / 공개판 작성일 2026-11-13. 읽기 범위와 작성·검증 이력은 마지막 쪽에 기록했다.',M,y,style='small',gap=0)

    for item in r['papers']:
        y=start(f"Study {item['id']}")
        y=para(f"{item['id']}. {item['heading']}",M,y,style='heading',gap=9)
        y=para(f"<link href='{item['url']}' color='#217b76'>[{item['id']}] DOI {item['doi']} · Published {item['published']}</link>",M,y,style='small',gap=11,raw=True)
        if item.get('read_url'):
            version = item['read_url'].rsplit('/',1)[-1]
            y=para(f"<link href='{item['read_url']}' color='#217b76'>대조한 공개판: arXiv:{version}</link>",M,y,style='small',gap=9,raw=True)
        for text in item['paragraphs_before']: y=para(text,M,y)
        y=chart(item['figure_kind'],y-2)
        y=para(item['figure_caption'],M,y,style='small',gap=12)
        for text in item['paragraphs_after']: y=para(text,M,y)

    y=start('References and authoring')
    y=para('References',M,y,style='heading',gap=12)
    for item in r['papers']:
        value=f"<link href='{item['url']}' color='#217b76'>[{item['id']}] {html.escape(item['citation'])}</link>"
        y=para(value,M,y,style='ref',gap=8,raw=True)
    y=para('작성·검증과 공개판 이력',M,y-7,style='heading',gap=9)
    y=para('편집·저술: 에이전틱 편집·저술팀(Agentic Editorial and Authoring Team, AEDAUT). 원호의 자료 선별·과학 감수 기록과 이번 공개 파생판의 조판·그림 생성 검수를 구분했다. 정확한 모델 식별자는 보존되지 않았다.',M,y,style='small',gap=8)
    y=para(r['verification_note'],M,y,style='small',gap=8)
    y=para(r['read_scope_note'],M,y,style='small',gap=0)
    c.save()
    result={'pages':page,'output_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),'original_edition_sha256':r['original_edition_sha256'],'all_figures_original_review_reconstructions':True,'copied_original_paper_images':0,'layout_blocks':positions}
    if args.qa_dir:
        args.qa_dir.mkdir(parents=True,exist_ok=True)
        (args.qa_dir/'builder-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='layout_blocks'},ensure_ascii=False))


if __name__ == '__main__':
    main()
