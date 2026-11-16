#!/usr/bin/env python3
"""Original charts of explicitly reported values; no source artwork or curves."""
from pathlib import Path
import argparse, json, math
from PIL import Image, ImageDraw, ImageFont

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--font',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    im=Image.new('RGB',(2000,1060),'white');d=ImageDraw.Draw(im)
    navy='#17364b';teal='#247b83';muted='#62737c';line='#cfdce2'
    def font(size):return ImageFont.truetype(str(a.font),size)
    def text(x,y,s,size=31,fill=navy):d.text((x,y),s,font=font(size),fill=fill)
    text(65,35,'A  입력선에서 추가된 탈위상률',42)
    text(65,96,'같은 냉각 회차의 기준선과 MUX를 약 12시간 교대로 측정',27,muted)
    x0,x1,y0,y1=200,925,200,650
    def xx(v):return x0+(x1-x0)*v/7
    for i in range(8):
        x=xx(i);d.line((x,y0,x,y1),fill=line,width=2);text(x-10,y1+14,str(i),27,muted)
    for i,(v,e) in enumerate([(2.3,.4),(5.6,.4),(2.4,.7)]):
        y=245+145*i
        text(65,y-20,'큐비트 '+str(i+1),30)
        d.rectangle((x0,y-30,xx(v),y+30),fill=teal)
        d.line((xx(v-e),y,xx(v+e),y),fill=navy,width=5)
        for z in [v-e,v+e]:d.line((xx(z),y-15,xx(z),y+15),fill=navy,width=4)
        text(xx(v)+20,y+39,f'{v:.1f} ± {e:.1f}',29)
    text(415,710,'추가 탈위상률 (kHz)',32)
    text(65,783,'오차막대: 논문 Table 1의 평균 표준오차(SE).',27,muted)
    text(65,828,'0.55 V, 10 mK; 입력선 실험의 세 큐비트.',27,muted)
    d.line((1010,25,1010,925),fill=line,width=3)
    text(1070,35,'B  쓰임에 따라 달라지는 발열',42)
    text(1070,96,'서로 다른 운용 조건; 전력의 합계나 동시 실험이 아님',26,muted)
    x0b,x1b,y0b,y1b=1380,1890,210,700
    def xb(v):return x0b+(x1b-x0b)*(math.log10(v)-2)/4
    for e in range(2,7):
        x=xb(10**e);d.line((x,y0b,x,y1b),fill=line,width=2)
        text(x-20,y1b+15,str(10**e),22,muted)
    rows=[('정적 대기',200,'200 pW','보고값'),
          ('2,000회/초 전환',216,'216 pW','산술: 108 fJ/회 × 전환율'),
          ('1,000,000회/초',108000,'108 nW','산술: 동적 성분만'),
          ('0.23 mA 바이어스',280000,'약 0.28 µW','논문 추정: I²R, 저항 약 5.3옴')]
    for i,(label,v,value,note) in enumerate(rows):
        y=245+125*i;text(1065,y-30,label,27)
        x=xb(v);d.ellipse((x-12,y-12,x+12,y+12),fill=teal if i in [0,3] else navy)
        text(1400,y+18,value,31);text(1065,y+63,note,23,muted)
    text(1450,760,'전력 (pW, 로그 축)',30)
    text(1070,828,'전환율은 events/s. AWG 구형파 1주기는 전환 2회.',26,muted)
    text(65,945,'리뷰 재구성 | Fallik et al., DOI: 10.1038/s41534-026-01424-7',29)
    text(65,991,'A: Table 1. B: 본문·보충자료의 정적 전력, 전환 에너지와 바이어스 추정. 원 그림·곡선은 사용하지 않음.',26,muted)
    a.output.parent.mkdir(parents=True,exist_ok=True);im.save(a.output)
    a.output.with_suffix('.json').write_text(json.dumps({'source_doi':'10.1038/s41534-026-01424-7','source_version':'Publisher Article in Press, online 2026-11-14','original_artwork_used':False,'reported_added_dephasing_kHz':[[2.3,.4],[5.6,.4],[2.4,.7]],'uncertainty':'reported mean standard error, Table 1','static_power_pW':200,'switch_energy_fJ':108,'derived_event_rates_per_second':[2000,1000000],'derived_dynamic_power_pW':[216,108000],'reported_bias_estimate_uW':.28,'bias_current_mA':.23,'simulated_on_resistance_ohm':5.3,'scope':'Different operating conditions, not total power or simultaneous measurement. Square-wave frequency is half the event rate.'},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
