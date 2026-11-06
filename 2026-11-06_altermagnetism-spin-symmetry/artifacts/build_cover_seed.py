"""Deterministic geometric reference for the conceptual cover."""
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parent
W,H = 1600,900
def contour(phase):
    points=[]
    for i in range(721):
        th=2*math.pi*i/720
        r=275*(1+0.24*math.cos(2*(th-phase)))
        points.append((1000+r*math.cos(th),420+r*math.sin(th)))
    return 'M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in points)+' Z'

parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
'<rect width="1600" height="900" fill="#211c35"/>']
for j in range(4):
    for i in range(6):
        x=120+i*100+j*20;y=380+j*100-i*15
        rot=0 if (i+j)%2==0 else 90
        color='#8bd5c2' if rot==0 else '#ed9b9f'
        parts.append(f'<g transform="translate({x} {y}) rotate({rot})"><path d="M-43 0 L0-23 L43 0 L0 23 Z" fill="none" stroke="{color}" stroke-width="4"/><ellipse rx="8" ry="8" fill="{color}"/></g>')
for phase,color in [(0,'#8bd5c2'),(math.pi/2,'#ed9b9f')]:
    parts.append(f'<path d="{contour(phase)}" fill="{color}" fill-opacity="0.16" stroke="{color}" stroke-width="14"/>')
for i in range(4):
    th=math.pi/4+i*math.pi/2
    x=1000+275*math.cos(th);y=420+275*math.sin(th)
    parts.append(f'<circle cx="{x}" cy="{y}" r="10" fill="#fff3de"/>')
parts.append('</svg>')
(ROOT/'cover-geometry.svg').write_text('\n'.join(parts))
# Exact radial relation: r_up(theta+pi/2)=r_down(theta).
assert max(abs((1+.24*math.cos(2*(i/100+math.pi/2)))-(1-.24*math.cos(2*i/100))) for i in range(1000)) < 1e-14
print('Cover geometry written; rotation relation verified.')
