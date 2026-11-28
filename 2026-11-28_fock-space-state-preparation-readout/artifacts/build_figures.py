"""Deterministic teaching diagrams and CC BY 4.0 source-data plots.

No source artwork, experimental curve interpolation or fitted data are used.
"""
from pathlib import Path
import hashlib, html, json, math

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
OUT = ART / 'figures'
INK, TEAL, COPPER, MUTED, LINE, PAPER = '#18384a', '#267678', '#b65c35', '#566975', '#cbd8d8', '#faf8f1'

def esc(s): return html.escape(str(s), quote=True)
def txt(x,y,s,size=22,color=INK,anchor='start',weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>'
def line(x1,y1,x2,y2,color=LINE,width=1.5,dash=''):
    return f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'
def rect(x,y,w,h,color='white',stroke=LINE):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{color}" stroke="{stroke}"/>'
def save(name,w,h,parts,title):
    OUT.mkdir(exist_ok=True)
    text=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{esc(title)}</title><style>text{{font-family:ReviewSans,ReviewSymbols,ReviewMath,sans-serif}}</style><rect width="100%" height="100%" fill="{PAPER}"/>'+''.join(parts)+'</svg>'
    text=text.replace('T_F','T<tspan baseline-shift="sub" font-size="75%">F</tspan>')
    (OUT/name).write_text(text,encoding='utf-8')
def arrow(x,y,xx,yy):
    a=math.atan2(yy-y,xx-x); s=12
    return line(x,y,xx,yy,TEAL,3)+f'<path d="M{xx},{yy} L{xx-s*math.cos(a-.45)},{yy-s*math.sin(a-.45)} L{xx-s*math.cos(a+.45)},{yy-s*math.sin(a+.45)} Z" fill="{TEAL}"/>'

def protocol(en,mobile):
    w,h=(640,1300) if mobile else (1200,650)
    parts=[txt(30,42,'Two lenses: prepare → perturb → read' if en else '두 렌즈: 준비 → 작은 변위 → 판독',28,weight=700),txt(30,78,'One microwave mode + an ancilla qubit' if en else '한 마이크로파 저장 모드 + 보조 큐비트',21,MUTED)]
    labels=[('Coherent input','D(α) |0〉','Broad number distribution'),('Kerr waiting','Phase φ(n−N̄)²','Number probabilities unchanged'),('Coherent drive','Duration T_F','Number-focused probe'),('Signal at the focus','Small D(β)','Chosen signal quadrature'),('Second control','Drive T_F → Kerr waiting','Approximate return'),('Near-vacuum readout','D(−γ) → ancilla','Calibrated mean voltage → Pₑ')]
    if not en:labels=[('코히런트 입력','D(α) |0〉','넓은 광자수 분포'),('Kerr 대기','위상 φ(n−N̄)²','광자수 확률은 그대로'),('코히런트 구동','시간 T_F','광자수 집속 상태'),('집속점의 신호','작은 변위 D(β)','정렬한 신호 방향'),('두 번째 제어','구동 T_F → Kerr 대기','근사적으로 복귀'),('진공 근처 판독','D(−γ) → 보조 큐비트','평균 전압 보정 → Pₑ')]
    coords=[(30,110+i*184,580,155) for i in range(6)] if mobile else [(30,115,350,200),(425,115,350,200),(820,115,350,200),(820,365,350,200),(425,365,350,200),(30,365,350,200)]
    for i,((x,y,cw,ch),(a,b,c)) in enumerate(zip(coords,labels)):
        parts.extend([rect(x,y,cw,ch),txt(x+18,y+34,f'{i+1:02}',20,TEAL,weight=700),txt(x+63,y+34,a,24,weight=700),txt(x+22,y+77,b,23),txt(x+22,y+110,c,19,MUTED)])
        if not mobile:
            if i in (0,1,2):
                center=x+cw/2; sigma=17 if i==2 else 66
                for k in range(-7,8):
                    bh=44*math.exp(-((k*16)**2)/(2*sigma*sigma))
                    parts.append(f'<rect x="{center+k*16-5}" y="{y+181-bh:.2f}" width="10" height="{bh:.2f}" fill="{COPPER if i==1 else TEAL}"/>')
            else: parts.append(line(x+23,y+153,x+cw-23,y+153,LINE))
    for i in range(5):
        x,y,cw,ch=coords[i];xx,yy,ww,hh=coords[i+1]
        if mobile:parts.append(arrow(x+cw/2,y+ch+6,xx+ww/2,yy-6))
        elif i<2:parts.append(arrow(x+cw+6,y+ch/2,xx-6,yy+hh/2))
        elif i==2:parts.append(arrow(x+cw/2,y+ch+8,xx+ww/2,yy-8))
        else:parts.append(arrow(x-6,y+ch/2,xx+ww+6,yy+hh/2))
    parts += [txt(30,h-46,'Conceptual sequence; distributions are schematic, not data.' if en else '개념 순서도 · 분포는 설명용이며 실험 데이터가 아님',19,MUTED),txt(30,h-18,'Hua et al. (2026), SI I B & IV · DOI:10.1038/s41586-026-11353-2',17,MUTED)]
    save(f'fig1_{"mobile" if mobile else "desktop"}{"_en" if en else ""}.svg',w,h,parts,labels[0][0]+' to '+labels[-1][0])

def laguerre(n,x):
    if n==0:return 1.0
    a,b=1.0,1.0-x
    for k in range(2,n+1):a,b=b,((2*k-1-x)*b-(k-1)*a)/k
    return b
def survival(n,b): return math.exp(-b*b)*laguerre(n,b*b)**2

def axes(parts,box,xlim,ylim,xticks,yticks,xlabel,ylabel,fs=20):
    x,y,w,h=box
    X=lambda a:x+w*(a-xlim[0])/(xlim[1]-xlim[0]);Y=lambda a:y+h*(ylim[1]-a)/(ylim[1]-ylim[0])
    for v in yticks:
        parts.extend([line(x,Y(v),x+w,Y(v),LINE,1),txt(x-12,Y(v)+7,f'{v:g}',fs,MUTED,'end')])
    for v in xticks:parts.extend([line(X(v),y+h,X(v),y+h+7,INK),txt(X(v),y+h+31,f'{v:g}',fs,MUTED,'middle')])
    parts += [line(x,y,x,y+h,INK),line(x,y+h,x+w,y+h,INK),txt(x+w/2,y+h+65,xlabel,fs+1,INK,'middle'),txt(x,y-19,ylabel,fs+1,INK)]
    return X,Y

def return_plot(en,mobile):
    w,h=(640,640) if mobile else (1200,600);fs=22 if mobile else 21
    parts=[txt(30,43,'A narrow return response' if en else '광자수가 클수록 좁아지는 복귀 응답',27,weight=700),txt(30,78,'Ideal Fock states · teaching calculation' if en else '이상적 Fock 상태 · 리뷰 교육 계산',21,MUTED)]
    box=(80,135,w-125,h-330);X,Y=axes(parts,box,(-.5,.5),(0,1),[-.5,-.25,0,.25,.5],[0,.25,.5,.75,1],'Real displacement β' if en else '실수 변위 β','Return probability pₙ' if en else '복귀 확률 pₙ',fs)
    for n,col,dash in [(0,MUTED,''),(5,COPPER,'9 5'),(20,TEAL,'')]:
        pts=[(b/800-.5,survival(n,b/800-.5)) for b in range(801)]
        d=' '.join(('M' if i==0 else 'L')+f'{X(a):.3f},{Y(b):.3f}' for i,(a,b) in enumerate(pts))
        parts.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="3.2"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
    for j,(n,col) in enumerate([(0,MUTED),(5,COPPER),(20,TEAL)]):
        xx=100+j*(160 if mobile else 250);yy=h-91
        parts.extend([line(xx,yy,xx+36,yy,col,3,'9 5' if n==5 else ''),txt(xx+45,yy+7,f'n = {n}',23,col)])
    parts.extend([txt(30,h-40,'pₙ = exp(−β²) [Lₙ(β²)]² · no loss / control error' if en else 'pₙ = exp(−β²) [Lₙ(β²)]² · 손실·제어 오차 없음',18,MUTED),txt(30,h-14,'Not the measured N-focused probe response.' if en else '실제 N-focused 탐침의 측정 응답과 구별',18,MUTED)])
    save(f'fig2_{"mobile" if mobile else "desktop"}{"_en" if en else ""}.svg',w,h,parts,'Ideal Fock-state return probability')

def measured(en,mobile,data):
    w,h=(640,1100) if mobile else (1200,600)
    parts=[txt(30,43,'Preparation and sensing: different optima' if en else '상태 준비와 센싱: 서로 다른 최적 조건',27,weight=700),txt(30,80,'Published points ± supplied statistical SD' if en else '정식 원자료의 점 ± 제공된 통계 표준편차',21,MUTED)]
    boxes=[(87,166,500,290),(87,622,500,290)] if mobile else [(85,167,475,285),(690,167,475,285)]
    left=data['fig2d'];right=data['fig4e']
    X,Y=axes(parts,boxes[0],(25,525),(12,25),[100,200,300,400,500],[12,15,18,21,24],'Mean photon number N̄' if en else '평균 광자수 N̄','A · Variance compression (dB)' if en else 'A · 광자수 분산 압축 (dB)',21)
    for r in left:
        a=r['mean_photon_number'];v=r['compression_dB'];e=r['std_dB'];xx=X(a)
        parts += [line(xx,Y(v-e),xx,Y(v+e),TEAL,2),line(xx-5,Y(v-e),xx+5,Y(v-e),TEAL,2),line(xx-5,Y(v+e),xx+5,Y(v+e),TEAL,2),f'<circle cx="{xx}" cy="{Y(v)}" r="5.4" fill="{TEAL}"/>']
    parts.append(txt(boxes[0][0]+17,boxes[0][1]+30,'N̄=500: 21.5 dB',22,TEAL,weight=700))
    X,Y=axes(parts,boxes[1],(25,525),(.035,.125),[100,200,300,400,500],[.04,.06,.08,.10,.12],'Mean photon number N̄' if en else '평균 광자수 N̄','B · Displacement sensitivity δβ' if en else 'B · 변위 감도 δβ',21)
    for r in right:
        a=r['mean_photon_number'];v=r['delta_beta_experiment'];e=r['statistical_std'];m=r['delta_beta_lossless_model'];xx=X(a)
        parts += [line(xx,Y(v-e),xx,Y(v+e),TEAL,2),line(xx-5,Y(v-e),xx+5,Y(v-e),TEAL,2),line(xx-5,Y(v+e),xx+5,Y(v+e),TEAL,2),f'<circle cx="{xx}" cy="{Y(v)}" r="5.3" fill="{TEAL}"/>',f'<path d="M{xx},{Y(m)-5} l5,5 l-5,5 l-5,-5 Z" fill="white" stroke="{COPPER}" stroke-width="2"/>']
    parts += [txt(boxes[1][0]+boxes[1][2]-15,boxes[1][1]+30,'N̄=400: δβ≈0.0548',22,TEAL,'end',700),txt(boxes[1][0]+boxes[1][2]-15,boxes[1][1]+60,'SQL δβ=0.5 (not shown)' if en else 'SQL δβ=0.5 (범위 밖)',19,MUTED,'end')]
    ly=h-58
    parts += [f'<circle cx="45" cy="{ly-7}" r="5" fill="{TEAL}"/>',txt(60,ly,'Experiment' if en else '실험',19,TEAL),f'<path d="M225,{ly-12} l5,5 l-5,5 l-5,-5 Z" fill="white" stroke="{COPPER}" stroke-width="2"/>',txt(240,ly,'Author lossless model' if en else '저자 제공 손실 없는 모델',19,COPPER),txt(30,h-24,'Fig. 2d / 4e data · figshare 34329033.v1 · CC BY 4.0',18,MUTED)]
    save(f'fig3_{"mobile" if mobile else "desktop"}{"_en" if en else ""}.svg',w,h,parts,'Published preparation and sensing data')

def main():
    data=json.loads((ART/'measurement-data.json').read_text())
    assert len(data['fig2d'])==len(data['fig4e'])==10
    assert min(data['fig4e'],key=lambda r:r['delta_beta_experiment'])['mean_photon_number']==400
    for n in [0,5,20]:
        assert survival(n,0)==1
        for b in [.01,.1,.3]: assert abs(survival(n,b)-survival(n,-b))<1e-14
    for en in [False,True]:
        for mobile in [False,True]:
            protocol(en,mobile);return_plot(en,mobile);measured(en,mobile,data)
    manifest={'version':1,'created':'2026-11-28','source_data_doi':'10.6084/m9.figshare.34329033.v1','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*.svg'))},'notes':['Fig1 conceptual control sequence; no physical trajectories or experimental population curves.','Fig2 ideal Fock-state teaching calculation, independently checked against matrix exponentials.','Fig3 published table points and supplied SDs; no interpolation or new fits; original artwork not reused.']}
    (ART/'figure-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'figures':len(manifest['files']),'status':'built'},ensure_ascii=False))

if __name__=='__main__':main()
