from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent

def start(title, description):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="580" viewBox="0 0 1080 580" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
        '<rect width="1080" height="580" rx="16" fill="#f4f6f3"/>',
        '<style>text{font-family:"Noto Sans KR","Noto Sans CJK KR",Arial,sans-serif;fill:#172a39} .muted{fill:#5a6d77} .large{font-size:32px;font-weight:700} .body{font-size:23px} .small{font-size:20px}</style>']

def txt(a,x,y,t,cls='body',extra=''):
    a.append(f'<text x="{x}" y="{y}" class="{cls}" {extra}>{escape(t)}</text>')

for lang in ['ko','en']:
    ko=lang=='ko'
    title='공항 SAR: 같은 조건의 최대 F1 비교' if ko else 'Airport SAR: maximized filtered F1'
    a=start(title,'NLCD 0.16, classical copula 0.24, QCBM full QPU 0.32. Zero-based axis from 0 to 0.40. Selected Miramar configuration; after filtering and threshold adjustment.')
    txt(a,48,62,title,'large')
    txt(a,48,102,'Miramar · 필터 및 임계값 조정 후 최대값' if ko else 'Miramar · maximum after filtering and threshold adjustment','small')
    for i in range(5):
        x=280+i*155
        a.append(f'<line x1="{x}" y1="150" x2="{x}" y2="386" stroke="#d7dfdf"/>')
        txt(a,x,422,f'{i/10:.1f}','small','text-anchor="middle"')
    for i,(lab,val,col) in enumerate([('NLCD',.16,'#708691'),('Copula',.24,'#398896'),('QCBM · QPU',.32,'#116d59')]):
        y=175+i*78
        txt(a,52,y+28,lab)
        a.append(f'<rect x="280" y="{y}" width="{val/.4*620}" height="40" rx="4" fill="{col}"/>')
        txt(a,295+val/.4*620,y+29,f'{val:.2f}')
    txt(a,48,485,'20 qubits · 300 iterations · 5,000 shots/evaluation · 100,000 inference shots','small')
    txt(a,48,528,'실제 QPU 실행 · 전체 시간 가속은 미입증' if ko else 'Actual QPU execution · no end-to-end speedup established','small')
    a.append('</svg>'); (OUT/f'sar_f1_{lang}.svg').write_text('\n'.join(a))

    title='Cyclobutadiene: 기준 상태를 함께 유지한 효과' if ko else 'Cyclobutadiene: retaining the reference space'
    a=start(title,'Active space 4 electrons in 4 orbitals, cc-pVDZ. Reference barrier 8.96, NOQE 7.70, DS-NOCI 8.62 kcal/mol. Absolute errors 1.26 and 0.34. Classical numerical study, no actual QPU.')
    txt(a,48,62,title,'large')
    txt(a,48,102,'cc-pVDZ · 활성공간 (4e, 4o) · 단위 kcal/mol' if ko else 'cc-pVDZ · active space (4e, 4o) · values in kcal/mol','small')
    for i in range(6):
        x=280+i*112
        a.append(f'<line x1="{x}" y1="150" x2="{x}" y2="386" stroke="#d7dfdf"/>')
        txt(a,x,422,str(i*2),'small','text-anchor="middle"')
    for i,(lab,val,col) in enumerate([('CASCI/FCI',8.96,'#708691'),('NOQE',7.70,'#b37b38'),('DS-NOCI',8.62,'#116d59')]):
        y=175+i*78
        txt(a,48,y+28,lab)
        a.append(f'<rect x="280" y="{y}" width="{val/10*560}" height="40" rx="4" fill="{col}"/>')
        txt(a,294+val/10*560,y+29,f'{val:.2f}')
    txt(a,48,485,'절대 장벽 오차: NOQE 1.26 → DS-NOCI 0.34 kcal/mol' if ko else 'Absolute barrier error: NOQE 1.26 → DS-NOCI 0.34 kcal/mol','body')
    txt(a,48,528,'소형 분자 수치실험 · 실제 QPU 실행 없음' if ko else 'Small-molecule numerical study · no actual QPU execution','small')
    a.append('</svg>'); (OUT/f'chemistry_barrier_{lang}.svg').write_text('\n'.join(a))
