"""Original ideal-statevector teaching figures; basis order |ab>, left bit first.

All geometry and numbers are produced here. Angle units are radians. These are
the review's educational calculations, using the RZ/RX/RZZ conventions in IBM
Quantum's official gate definitions and the score-maximizing QAOA convention.
"""
from pathlib import Path
import cmath
import html
import json
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'
INK, MUTED, TEAL, ORANGE = '#183643', '#586e78', '#087b89', '#b9582f'
WASH, LINE, PAPER = '#edf3ef', '#c8d7d7', '#faf9f5'
TAU = 2 * math.pi


def qaoa(n, edges, gamma, beta):
    scores = [sum(((s >> (n-1-a)) & 1) != ((s >> (n-1-b)) & 1)
                  for a, b in edges) for s in range(2**n)]
    initial = [complex(1 / math.sqrt(2**n))] * (2**n)
    phased = [a * cmath.exp(-1j*gamma*c) for a, c in zip(initial, scores)]
    final = phased[:]
    for q in range(n):
        bit = 1 << (n - 1 - q)
        for s in range(2**n):
            if not s & bit:
                a, b = final[s], final[s | bit]
                final[s] = math.cos(beta)*a - 1j*math.sin(beta)*b
                final[s | bit] = -1j*math.sin(beta)*a + math.cos(beta)*b
    return scores, [initial, phased, final]


def text(x, y, value, size=24, color=INK, weight=400, anchor='start'):
    return f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(str(value))}</text>'


def lines(x, y, values, size=23, dy=32, **kwargs):
    return ''.join(text(x, y+i*dy, value, size, **kwargs) for i, value in enumerate(values))


def rect(x, y, w, h, color=WASH, radius=12, stroke='none'):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{radius}" fill="{color}" stroke="{stroke}"/>'


def line(x1, y1, x2, y2, color=LINE, width=2, arrow=False):
    return f'<path d="M{x1:g},{y1:g} L{x2:g},{y2:g}" fill="none" stroke="{color}" stroke-width="{width}"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>'


def complex_arrow(x, y, a, r=35, scale=1, color=TEAL, axes=True):
    s = ''
    if axes:
        s += line(x-r-4, y, x+r+4, y) + line(x, y+r+4, x, y-r-4)
        s += f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{LINE}" stroke-dasharray="3 4"/>'
    if abs(a) > 1e-12:
        s += line(x, y, x+r*a.real/scale, y-r*a.imag/scale, color, 5, True)
    else:
        s += f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>'
    return s


def bloch(x, y, vector, r=63):
    def project(v): return x+r*(v[0]-.50*v[1]), y+r*(.32*v[1]-v[2])
    s = f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" stroke="{LINE}"/><ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*.3}" fill="none" stroke="{LINE}"/>'
    for v, label in [((1,0,0),'x'),((0,1,0),'y'),((0,0,1),'z')]:
        xx, yy = project(v); s += line(x, y, xx, yy) + text(xx+6, yy-6, label, 19, MUTED)
    xx, yy = project(vector); s += line(x, y, xx, yy, ORANGE, 5, True)
    return s


def prob_bar(x, y, p, width=230, label='', color=TEAL):
    s = text(x, y+19, label, 22) + rect(x+58, y, width, 26, '#dfe8e5', 3)
    if p > 1e-12: s += rect(x+58, y, width*p, 26, color, 3)
    s += text(x+58+width+12, y+21, f'{p:.0%}', 22, color, 700)
    return s


def start(w, h, title, description, metadata):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(description)}</desc><metadata>{html.escape(json.dumps(metadata,ensure_ascii=False))}</metadata><defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="context-stroke"/></marker></defs><style>text{{font-family:ReviewFigure,sans-serif;letter-spacing:0}}path,circle,rect,ellipse{{vector-effect:non-scaling-stroke}}</style><rect width="{w}" height="{h}" rx="16" fill="{PAPER}"/>'''


def finish(stem, lang, mobile, w, h, title, description, metadata, body):
    name = f'{stem}{"_mobile" if mobile else ""}_{lang}.svg'
    (OUT/name).write_text(start(w,h,title,description,metadata)+body+'</svg>\n')


def phase_readout(lang, mobile):
    ko = lang == 'ko'; w,h = (720,1560) if mobile else (1200,920)
    title = '위상차를 확률로 읽는 한 큐비트' if ko else 'Reading a phase difference as probability'
    description = 'Ideal one-qubit H–Rz(pi)–H calculation. Complex amplitudes, Bloch vectors and Z-measurement probabilities are shown after each gate. The Bloch sphere is a state representation.'
    meta = {'calculation':'Review ideal statevector calculation','phi_rad':math.pi,'sources':['https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RZGate'],'stages':['H','Rz(phi)','H'],'amplitude_scale':'Arrow radius corresponds to amplitude magnitude 1; real right, imaginary up.'}
    s = text(32,48,title,31 if mobile else 35,weight=700)
    s += text(32,87,'|0⟩ → H → Rz(φ) → H     φ = π rad',25,TEAL,700)
    s += lines(32,126,['화살표: 복소 진폭  ·  막대: Z 측정 확률' if ko else 'Arrows: complex amplitudes  ·  Bars: Z probabilities'],21,color=MUTED)
    stage_names = ['첫 H 뒤','Rz 뒤','마지막 H 뒤'] if ko else ['After the first H','After Rz','After the final H']
    states = [[1/math.sqrt(2)]*2,[-1j/math.sqrt(2),1j/math.sqrt(2)],[0,-1j]]
    vectors = [(1,0,0),(-1,0,0),(0,0,-1)]
    amp_labels = [['1/√2','1/√2'],['−i/√2','+i/√2'],['0','−i']]
    for i,(state,vec) in enumerate(zip(states,vectors)):
        x,y,pw,ph = (24,170+i*420,672,396) if mobile else (24+i*394,185,370,590)
        s += rect(x,y,pw,ph)
        s += text(x+22,y+40,f'{i+1}  {stage_names[i]}',26,weight=700)
        if mobile:
            bx,by=x+115,y+165; ax=[x+340,x+525]; ay=y+140
            s += bloch(bx,by,vec,75)
            s += text(bx,y+275,'Bloch',21,MUTED,anchor='middle')
            for j,a in enumerate(state):
                s += complex_arrow(ax[j],ay,a,48,color=[TEAL,ORANGE][j])
                s += text(ax[j],ay+80,f'|{j}⟩: {amp_labels[i][j]}',23,anchor='middle')
            for j,a in enumerate(state): s += prob_bar(x+44,y+295+j*43,abs(a)**2,420,f'|{j}⟩',[TEAL,ORANGE][j])
        else:
            for j,a in enumerate(state):
                ax=x+95+j*176;ay=y+145
                s += complex_arrow(ax,ay,a,48,color=[TEAL,ORANGE][j])
                s += text(ax,ay+84,f'|{j}⟩: {amp_labels[i][j]}',23,anchor='middle')
            s += bloch(x+pw/2,y+350,vec,71)
            s += text(x+pw/2,y+449,'Bloch',21,MUTED,anchor='middle')
            for j,a in enumerate(state): s += prob_bar(x+20,y+485+j*43,abs(a)**2,205,f'|{j}⟩',[TEAL,ORANGE][j])
    yy=1453 if mobile else 823
    s += text(32,yy,'Re →   Im ↑   |진폭|² = 확률' if ko else 'Re →   Im ↑   |amplitude|² = probability',23,TEAL,700)
    s += lines(32,yy+35,(['Bloch 구: 양자 상태를 나타내는 공간','리뷰의 이상적 교육 계산 · 각도 단위 rad'] if ko else ['Bloch sphere: a representation of quantum state','Review ideal educational calculation · angles in rad']),20,color=MUTED)
    finish('phase_readout',lang,mobile,w,h,title,description,meta,s)


def parity_interaction(lang,mobile):
    ko=lang=='ko';w,h=(720,1120) if mobile else (1200,820)
    title='같고 다름에 위상을 남기는 세 연산' if ko else 'Three operations leave a parity-dependent phase'
    desc='Coherent basis-state tracking for CX(a to b), Rz(theta) on b, then CX(a to b), in |ab> basis order. The target stores a XOR b during the middle rotation; final basis bits are restored. The net phases are the RZZ(theta) diagonal entries.'
    meta={'basis_order':['00','01','10','11'],'control':'a','target':'b','theta_unit':'rad','phases':['-theta/2','+theta/2','+theta/2','-theta/2'],'source':'https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RZZGate'}
    s=text(32,48,title,30 if mobile else 34,weight=700)
    s+=text(32,91,'CX → Rz(θ) → CX  =  RZZ(θ)',28,TEAL,700)
    x0,x1=(130,665) if mobile else (290,1105);ya,yb=153,225
    s+=text(x0-67,ya+7,'a',25,weight=700)+text(x0-67,yb+7,'b',25,weight=700)
    s+=line(x0,ya,x1,ya,MUTED)+line(x0,yb,x1,yb,MUTED)
    positions=[x0+(x1-x0)*f for f in [.18,.5,.82]]
    for x in [positions[0],positions[2]]:
        s+=line(x,ya,x,yb,INK,2)+f'<circle cx="{x}" cy="{ya}" r="8" fill="{INK}"/><circle cx="{x}" cy="{yb}" r="16" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>'+line(x-12,yb,x+12,yb,INK)+line(x,yb-12,x,yb+12,INK)
    s+=rect(positions[1]-53,yb-28,106,56,'white',6,TEAL)+text(positions[1],yb+8,'Rz(θ)',25,TEAL,700,'middle')
    s+=text(32,292,'중첩의 각 성분에 적용하는 가역 패리티 계산' if ko else 'Reversible parity computation on every basis component',22,MUTED)
    rows=[('00','00','−θ/2','00',0),('01','01','+θ/2','01',1),('10','11','+θ/2','10',1),('11','10','−θ/2','11',0)]
    if mobile:
        for i,(inp,mid,phase,out,odd) in enumerate(rows):
            yy=328+i*151;color=ORANGE if odd else TEAL
            s+=rect(24,yy,672,133)
            s+=text(46,yy+37,('다른 비트' if odd else '같은 비트') if ko else ('Different bits' if odd else 'Equal bits'),23,color,700)
            s+=text(46,yy+86,f'|{inp}⟩ → |{mid}⟩',29,weight=700)+text(320,yy+86,phase,29,color,700)+text(502,yy+86,f'→ |{out}⟩',29,weight=700)
            s+=text(46,yy+116,'입력 → 첫 CX 뒤       위상각(rad)         최종 비트' if ko else 'Input → after CX      Phase angle(rad)      Final bits',18,MUTED)
    else:
        xs=[83,348,661,962]
        for xx,label in zip(xs,['입력 |ab⟩','첫 CX 뒤','Rz의 위상각 (rad)','마지막 CX 뒤'] if ko else ['Input |ab⟩','After first CX','Rz phase angle (rad)','After final CX']):s+=text(xx,350,label,24,weight=700)
        for i,(inp,mid,phase,out,odd) in enumerate(rows):
            yy=381+i*73;color=ORANGE if odd else TEAL
            s+=rect(30,yy,1140,61,WASH if odd else '#e5efec',5)
            for xx,label in zip(xs,[f'|{inp}⟩',f'|{mid}⟩',phase,f'|{out}⟩']):s+=text(xx,yy+41,label,29,color,700)
    yy=1000 if mobile else 731
    s+=text(32,yy,'같음: exp(−iθ/2)   다름: exp(+iθ/2)' if ko else 'Equal: exp(−iθ/2)   Different: exp(+iθ/2)',26,TEAL,700)
    s+=lines(32,yy+38,['비트 배열은 복원되고 상대위상은 남는다' if ko else 'Basis bits are restored; relative phases remain','RZZ(θ) = exp(−iθ ZaZb / 2)'],23,color=MUTED)
    finish('parity_interaction',lang,mobile,w,h,title,desc,meta,s)


def problem_to_probability(lang,mobile):
    ko=lang=='ko';w,h=(720,1660) if mobile else (1200,900)
    title='문제의 점수에서 답의 확률까지' if ko else 'From a problem score to answer probabilities'
    desc='Review ideal two-qubit, one-edge MaxCut statevector calculation. Basis order 00,01,10,11. Uniform initial state; cost phases exp(-i gamma C); local X mixers exp(-i beta (Xa+Xb)). gamma=pi/2 and beta=pi/8 radians yield probabilities 0,1/2,1/2,0. Arrows preserve the calculated common phase.'
    scores,states=qaoa(2,[(0,1)],math.pi/2,math.pi/8)
    meta={'calculation':'Review ideal statevector educational calculation','basis_order':['00','01','10','11'],'scores':scores,'gamma_rad':math.pi/2,'beta_rad':math.pi/8,'probabilities':[[abs(a)**2 for a in st] for st in states],'source':'https://arxiv.org/abs/1411.4028v1'}
    s=text(32,48,title,30 if mobile else 34,weight=700)
    s+=text(32,91,'γ = π/2 rad    β = π/8 rad',25,TEAL,700)
    s+=line(85,157,220,157,INK,3)
    for x,label in [(85,'a'),(220,'b')]:
        s+=f'<circle cx="{x}" cy="157" r="27" fill="white" stroke="{TEAL}" stroke-width="2"/>'+text(x,166,label,25,TEAL,700,'middle')
    s+=lines(284 if not mobile else 275,145,['다른 비트에 1점' if ko else 'Different bits earn 1','C = (I − ZaZb) / 2'],23,dy=36)
    s+=text(32,226,'화살표는 복소 진폭 · 막대는 측정 확률' if ko else 'Arrows show complex amplitudes; bars show probabilities',22,MUTED)
    headings=['처음 |++⟩','문제 위상층 뒤','X 혼합층 뒤'] if ko else ['Initial |++⟩','After cost phases','After X mixers']
    expected=[.5,.5,1]
    for stage,st in enumerate(states):
        x,y,pw,ph=(24,259+stage*420,672,395) if mobile else (24+394*stage,264,370,485)
        s+=rect(x,y,pw,ph)+text(x+21,y+40,f'{stage+1}  {headings[stage]}',25,weight=700)
        for j,a in enumerate(st):
            yy=y+101+j*70;p=abs(a)**2;color=ORANGE if scores[j] else TEAL
            s+=text(x+20,yy+8,f'|{j:02b}⟩',23,weight=700)
            ax=x+(146 if mobile else 112);s+=complex_arrow(ax,yy,a,24,1,color)
            bx=x+(223 if mobile else 157);bw=350 if mobile else 137
            s+=rect(bx,yy-13,bw,25,'#dce7e2',3)
            if p>1e-12:s+=rect(bx,yy-13,bw*p,25,color,3)
            s+=text(bx+bw+9,yy+7,f'{p:.0%}',22,color,700)
        yy=y+(365 if mobile else 440)
        s+=text(x+20,yy,f'기댓점수 = {expected[stage]:g}' if ko else f'Expected score = {expected[stage]:g}',25,TEAL,700)
    yy=1563 if mobile else 805
    s+=text(32,yy,'Re →   Im ↑    막대 길이 = |진폭|²' if ko else 'Re →   Im ↑    Bar length = |amplitude|²',22,TEAL,700)
    s+=lines(32,yy+34,['문제 위상은 방향을 바꾸고, 혼합 연산은 확률을 바꾼다' if ko else 'Cost phases change directions; mixing changes probabilities','리뷰의 이상적 교육 계산 · 2노드·1간선' if ko else 'Review ideal educational calculation · 2 nodes, 1 edge'],20,color=MUTED)
    finish('problem_to_probability',lang,mobile,w,h,title,desc,meta,s)


def main():
    OUT.mkdir(exist_ok=True)
    for lang in ['ko','en']:
        for mobile in [False,True]:
            phase_readout(lang,mobile);parity_interaction(lang,mobile);problem_to_probability(lang,mobile)
    record={'calculation':'Review ideal statevector educational calculations','angle_unit':'rad','sources_verified':'2026-11-05','basis_order':'left bit a, right bit b; |00>,|01>,|10>,|11>','single_qubit_phi':math.pi,'single_qubit_probabilities':[[.5,.5],[.5,.5],[0,1]],'two_qubit':{}}
    for name,n,edges,g,b in [('edge',2,[(0,1)],math.pi/2,math.pi/8),('triangle_same',3,[(0,1),(1,2),(0,2)],math.pi/2,math.pi/8),('triangle_retuned',3,[(0,1),(1,2),(0,2)],math.atan(1/math.sqrt(2)),math.atan(1/math.sqrt(2))/2)]:
        scores,states=qaoa(n,edges,g,b);probs=[abs(a)**2 for a in states[-1]]
        assert abs(sum(probs)-1)<1e-12
        record['two_qubit'][name]={'qubits':n,'edges':edges,'gamma_rad':g,'beta_rad':b,'scores':scores,'stages':[[[a.real,a.imag] for a in st] for st in states],'expected_score':sum(p*c for p,c in zip(probs,scores)),'optimal_probability':sum(p for p,c in zip(probs,scores) if c==max(scores))}
    assert abs(record['two_qubit']['edge']['expected_score']-1)<1e-12
    assert abs(record['two_qubit']['triangle_same']['expected_score']-.75)<1e-12
    assert abs(record['two_qubit']['triangle_retuned']['expected_score']-2)<1e-12
    (OUT/'figure-calculations.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print('Wrote 12 original bilingual desktop/mobile SVGs and exact statevector records.')


if __name__=='__main__':main()
