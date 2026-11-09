"""Original explanatory SVG: learned properties, explicit energies, total force.

Relationships follow SO3LR Tauri arXiv:2611.06237v1 II.1/S1.
This is a conceptual architecture diagram, not measured or simulated data.
"""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parent
COLORS = ['#bd8542', '#426a79', '#638776', '#a96678']

def build(lang):
    ko = lang == 'ko'
    title = '무엇을 배우고, 무엇을 식으로 계산하는가' if ko else 'What is learned, and what is evaluated explicitly?'
    subtitle = 'SO3LR Tauri의 에너지 구성과 힘의 계산' if ko else 'Energy construction and force evaluation in SO3LR Tauri'
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1420" height="910" viewBox="0 0 1420 910" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">Four differentiable energy terms sum to total energy. Fixed NLH repulsion is distinct from network-predicted energy, charge and dispersion properties; forces include their coordinate dependence.</desc>',
             '<style>text{font-family:ReviewFigure,sans-serif;fill:#253b42}.label{font-size:25px;font-weight:700}.body{font-size:22px}.small{font-size:20px}.wire{fill:none;stroke:#748c91;stroke-width:2.5;stroke-linejoin:round}</style>',
             '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6.5" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="none" stroke="#748c91" stroke-width="1.4"/></marker></defs>',
             '<rect width="1420" height="910" fill="#fbfaf6"/>']
    def text(x,y,s,css='body',anchor='start'):
        parts.append(f'<text x="{x}" y="{y}" class="{css}" text-anchor="{anchor}">{escape(s)}</text>')
    def box(x,y,w,h,fill='#fff',stroke='#b5c5c3'):
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    def line(points):
        parts.append(f'<path d="{points}" class="wire" marker-end="url(#arrow)"/>')
    text(48,49,title,'label');text(48,82,subtitle,'small')
    box(48,111,1324,96,'#edf2ee')
    text(710,148,'입력: 원자 좌표 R · 원소 Z · 총전하 Q · 스핀 다중도 S' if ko else 'Inputs: atomic positions R · elements Z · total charge Q · spin multiplicity S','label','middle')
    text(710,182,'좌표를 미분할 때 Z, Q, S는 고정한다' if ko else 'Z, Q and S are held fixed when differentiating positions','small','middle')
    line('M198 207 V250');line('M886 207 V250')
    box(48,253,300,142,'#f6eee1',COLORS[0]);box(392,253,980,142,'#eaf0f3',COLORS[1])
    text(198,297,'고정 NLH 반발표' if ko else 'Fixed NLH repulsion','label','middle')
    text(198,332,'별도 DFT로 정한 원자쌍 항' if ko else 'Pair terms fitted to DFT','small','middle')
    text(198,366,'ML 학습 중 고정' if ko else 'Fixed during ML training','small','middle')
    text(882,298,'SO3krates 신경망' if ko else 'SO3krates neural network','label','middle')
    text(882,334,'학습 출력: 원자 에너지 · 전하 q · 분극률 α · 분산 계수 C₆' if ko else 'Learned outputs: atomic energy · charges q · polarizability α · dispersion C₆','body','middle')
    text(882,368,'현재 원자 환경에 따라 출력값도 변한다' if ko else 'The predicted values change with the atomic environment','small','middle')
    centers=[198,542,886,1222]
    for x in centers:line(f'M{x} 395 V450')
    labels_ko=[('Erep','단거리 반발','가까운 접촉의 급한 반발'),('ESO3k','반국소 에너지','신경망이 학습한 에너지'),('Eelec','정전기 에너지','예측 q를 쿨롱식에 대입'),('Edisp','분산 에너지','예측 α, C₆로 쌍 항 구성')]
    labels_en=[('Erep','Short-range repulsion','Steep close-contact repulsion'),('ESO3k','Semi-local energy','Energy learned by the network'),('Eelec','Electrostatic energy','Predicted q in Coulomb terms'),('Edisp','Dispersion energy','Pair terms from predicted α, C₆')]
    for x,color,labels in zip(centers,COLORS,labels_ko if ko else labels_en):
        box(x-150,454,300,135,'#fff',color)
        text(x,490,labels[0],'label','middle');text(x,526,labels[1],'body','middle');text(x,562,labels[2],'small','middle')
        parts.append(f'<path d="M{x} 589 V631" class="wire"/>')
    parts.append('<path d="M198 631 H1222" class="wire"/>');line('M710 631 V664')
    box(266,668,888,78,'#edf2ee','#638776');text(710,714,'Etotal = Erep + ESO3k + Eelec + Edisp','label','middle')
    line('M710 746 V789')
    text(710,825,'힘 F = −∇R Etotal' if ko else 'Forces F = −∇R Etotal','label','middle')
    text(710,862,'거리의 변화와 예측 물리량의 변화를 함께 미분한다' if ko else 'Differentiate both distances and the predicted properties','body','middle')
    text(48,894,'개념도 · 길이·색은 정량 값을 뜻하지 않음' if ko else 'Conceptual diagram · lengths and colors do not encode data','small')
    parts.append('</svg>')
    out=ROOT/f'tauri_energy_model_{lang}.svg';out.write_text('\n'.join(parts)+'\n')
    return {'language':lang,'file':out.name,'energy_terms':4,'network_outputs':['atomic_energy','charge','polarizability','C6'],'fixed_during_ML':'NLH repulsion parameters','coordinate_derivative':'total energy including property dependence; fixed Z/Q/S','kind':'original conceptual diagram; no numerical benchmark'}

if __name__ == '__main__':
    result=[build(lang) for lang in ['ko','en']]
    (ROOT/'tauri_energy_model.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
