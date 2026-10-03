from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
plt.rcParams.update({'font.size': 17, 'svg.fonttype': 'none', 'font.family': 'DejaVu Sans'})
g = np.linspace(0, 2, 401)
fig, ax = plt.subplots(figsize=(11, 6.5))
fig.patch.set_facecolor('#faf8f2')
ax.set_facecolor('#faf8f2')
ax.plot(g, -np.sqrt(1+4*g*g), lw=3.8, color='#116f79', label='Exact / entangled ansatz')
ax.plot(g, np.where(g<=1, -1-g*g, -2*g), lw=3.3, color='#b44e3a', label='Best product state')
ax.axhline(-1, lw=2, ls='--', color='#777', label='Subspace: |00>, |11>')
ax.scatter([.5,.5], [-1.25,-np.sqrt(2)], color=['#b44e3a','#116f79'], zorder=4)
ax.set(xlabel='Transverse field g (J = 1)', ylabel='Energy / J', xlim=(0,2))
ax.set_title('Two spins: expressive states and missing configurations', fontsize=19, pad=18)
ax.spines[['top','right']].set_visible(False)
ax.grid(alpha=.15)
ax.legend(fontsize=14, loc='lower left')
fig.tight_layout()
fig.savefig(ART/'entanglement.svg')
plt.close(fig)

def diagram(lang):
    ko = lang=='ko'
    title = '에너지 측정과 전자배치 선택의 분업' if ko else 'Energy measurement vs configuration selection'
    rows = [
      ('VQE', ['상태 준비','Pauli 기대값 측정','에너지 합산','회로 갱신'] if ko else ['Prepare state','Measure Pauli terms','Combine energies','Update circuit'], ['QPU','QPU','CPU','CPU'], '#116f79'),
      ('HI-VQE / SQD', ['상태 준비','전자배치 샘플링','부분공간 H 구성','고전 대각화'] if ko else ['Prepare state','Sample occupations','Project Hamiltonian','Diagonalize'], ['QPU','QPU','CPU','CPU'], '#b44e3a')]
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 490" role="img"><title>{title}</title><rect width="1000" height="490" fill="#faf8f2"/><g font-family="Arial, Noto Sans KR, sans-serif"><text x="40" y="48" font-size="28" fill="#142b39">{title}</text>']
    for row,(label,boxes,chips,color) in enumerate(rows):
        y=100+row*180
        s.append(f'<text x="40" y="{y}" font-size="22" font-weight="bold" fill="{color}">{label}</text>')
        for i,(txt,chip) in enumerate(zip(boxes,chips)):
            x=40+i*235
            s.append(f'<rect x="{x}" y="{y+25}" width="208" height="102" rx="12" fill="white" stroke="{color}" stroke-width="2"/><text x="{x+104}" y="{y+57}" text-anchor="middle" font-size="16" fill="{color}">{chip}</text><text x="{x+104}" y="{y+96}" text-anchor="middle" font-size="20" fill="#142b39">{txt}</text>')
            if i<3:
                s.append(f'<path d="M{x+210} {y+78} h20 m-8 -6 l8 6 -8 6" fill="none" stroke="#5c6770" stroke-width="2"/>')
    note='HI-VQE는 샘플 기반 에너지에 따라 회로를 반복 갱신할 수 있습니다.' if ko else 'HI-VQE can train the circuit using sampled-subspace energies.'
    s.append(f'<text x="40" y="458" font-size="19" fill="#5c6770">{note}</text></g></svg>')
    (ART/f'division_{lang}.svg').write_text(''.join(s),encoding='utf-8')
diagram('ko'); diagram('en')

generated = ROOT.parent.parent / 'generated_images' / 'exec-9d698aa7-ccf4-44a1-aa5d-0cd1ff433e74.png'
if generated.exists():
    Image.open(generated).convert('RGB').save(ART/'hero.webp', quality=85, method=4)
elif not (ART/'hero.webp').is_file():
    raise FileNotFoundError('Use the published hero.webp or provide the original generated image.')
print('Figures built:', ', '.join(p.name for p in ART.glob('*.svg')))
