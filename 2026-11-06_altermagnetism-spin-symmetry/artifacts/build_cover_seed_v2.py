"""CrSb structure and g-wave sign geometry for a watercolor cover reference.

Original geometry, not a reproduction of a paper figure or a Fermi surface.
"""
from pathlib import Path
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUT=Path(__file__).resolve().parent
A=np.array([[1.,-.5,0.],[0.,math.sqrt(3)/2,0.],[0.,0.,1.324]])
CR=np.array([[0.,0.,0.],[0.,0.,.5]])
SB=np.array([[1/3,2/3,.25],[2/3,1/3,.75]])
BLUE='#376b98';RED='#ba674e';OCHRE='#bd995b';INK='#7b776b'

def cart(p): return A@np.array(p)
def screw(p):
    u,v,z=p
    return np.mod([u-v,u,z+.5],1.)
def periodic_match(p,group):
    return any(np.linalg.norm((p-q+.5)%1.-.5)<1e-12 for q in group)
assert all(periodic_match(screw(p),CR) for p in CR)
assert all(periodic_match(screw(p),SB) for p in SB)
assert not all(periodic_match(np.mod(p+[0,0,.5],1),SB) for p in SB)

def cage(frac):
    candidates=[]
    for i in range(-3,4):
        for j in range(-3,4):
            for k in range(-2,4):
                for sb in SB:
                    p=cart(sb+[i,j,k]);candidates.append((np.linalg.norm(p-cart(frac)),p))
    candidates.sort(key=lambda x:x[0])
    return np.array([x[1] for x in candidates[:6]])
c0=cage([0,0,0]);c1=cage([0,0,.5])-cart([0,0,.5])
rot=np.array([[.5,-math.sqrt(3)/2,0],[math.sqrt(3)/2,.5,0],[0,0,1]])
cage_residual=max(min(np.linalg.norm(rot@p-q) for q in c1) for p in c0)
assert cage_residual<1e-12

fig=plt.figure(figsize=(16,9),dpi=130,facecolor='#faf6ed')
ax=fig.add_axes([-.035,-.10,.76,1.15],projection='3d',computed_zorder=False)
ax.patch.set_alpha(0);ax.set_axis_off();ax.view_init(elev=23,azim=-65)
sites=[]
for u in range(-1,2):
    for v in range(-1,2):
        if np.linalg.norm(cart([u,v,0])[:2])<1.5:
            for z in [0,.5,1,1.5]:sites.append(np.array([u,v,z]))
sbcoords={}
for site in sites:
    for p in cage(site):sbcoords[tuple(np.round(p,8))]=p
for p in sbcoords.values(): ax.scatter(*p,s=28,c=OCHRE,alpha=.42,depthshade=False,edgecolors='#fffaf1',linewidths=.4)
for frac in sites:
    p=cart(frac);sgn=1 if int(round(2*frac[2]))%2==0 else -1;color=BLUE if sgn>0 else RED
    ax.scatter(*p,s=70,c=color,alpha=.68,depthshade=False,edgecolors='#fffaf1',linewidths=.6)
    ax.quiver(*p,0,0,sgn*.28,color=color,arrow_length_ratio=.34,linewidth=1.5,alpha=.7)
    for q in cage(frac):ax.plot(*np.array([p,q]).T,color=INK,lw=.45,alpha=.25)

# Two neighboring foreground cages are emphasized, sharing the actual ligand plane.
for frac in [np.array([0.,-1.,0.]),np.array([0.,-1.,.5])]:
    p=cart(frac);sgn=1 if frac[2]==0 else -1;color=BLUE if sgn>0 else RED
    cagepoints=cage(frac)
    for q in cagepoints:
        ax.plot(*np.array([p,q]).T,color=INK,lw=1.25,alpha=.82)
        ax.scatter(*q,s=100,c=OCHRE,depthshade=False,edgecolors='#fffaf1',linewidths=1)
    for tri in [cagepoints[cagepoints[:,2]>p[2]],cagepoints[cagepoints[:,2]<p[2]]]:
        center=tri.mean(axis=0);order=np.argsort(np.arctan2(tri[:,1]-center[1],tri[:,0]-center[0]));tri=tri[order]
        ax.add_collection3d(Poly3DCollection([tri],facecolors=color,edgecolors=color,linewidths=1,alpha=.11))
    ax.scatter(*p,s=200,c=color,depthshade=False,edgecolors='#fffaf1',linewidths=1.5)
    ax.quiver(*p,0,0,sgn*.24,color=color,arrow_length_ratio=.38,linewidth=3)
ax.set_box_aspect([1.3,1.3,1.05]);ax.set_xlim(-1.5,1.5);ax.set_ylim(-1.65,1.4);ax.set_zlim(-.4,2.45)

ag=fig.add_axes([.49,.21,.56,.78],projection='3d');ag.patch.set_alpha(0);ag.set_axis_off();ag.view_init(elev=23,azim=-57)
th=np.linspace(.005,math.pi-.005,151);ph=np.linspace(0,2*math.pi,241)
TH,PH=np.meshgrid(th,ph)
X=np.sin(TH)*np.cos(PH);Y=np.sin(TH)*np.sin(PH);Z=np.cos(TH)
G=Z*Y*(3*X*X-Y*Y);norm=np.max(np.abs(G));rad=.77+.55*np.abs(G)/norm
from matplotlib.colors import to_rgba
colors=np.zeros(G.shape+(4,));colors[G>=0]=to_rgba(BLUE,.68);colors[G<0]=to_rgba(RED,.68)
colors[np.abs(G)<.008]=to_rgba('#faf6ed',.55)
ag.plot_surface(rad*X,rad*Y,rad*Z,facecolors=colors,rcount=151,ccount=241,shade=True,linewidth=0,antialiased=True)
# Four nodal-plane traces are geometric guides, not field lines.
tt=np.linspace(0,2*math.pi,400)
ag.plot(.775*np.cos(tt),.775*np.sin(tt),np.zeros_like(tt),c=INK,lw=.7,alpha=.55)
for phi in [0,math.pi/3,2*math.pi/3]:ag.plot(.775*np.cos(tt)*math.cos(phi),.775*np.cos(tt)*math.sin(phi),.775*np.sin(tt),c=INK,lw=.65,alpha=.5)
ag.set_xlim(-1.4,1.4);ag.set_ylim(-1.4,1.4);ag.set_zlim(-1.4,1.4);ag.set_box_aspect([1,1,1])
fig.savefig(OUT/'cover-geometry-v2.png',dpi=130,facecolor=fig.get_facecolor())
plt.close(fig)

def g(p):x,y,z=p;return z*y*(3*x*x-y*y)
rng=np.random.default_rng(20261106);p=rng.normal(size=(200,3))
inv=max(abs(g(-v)-g(v)) for v in p);r60=max(abs(g(rot@v)+g(v)) for v in p)
assert inv<1e-10 and r60<1e-10
(OUT/'cover-geometry-v2-checks.json').write_text(json.dumps({'crystal':'CrSb NiAs-type P63/mmc','basis_columns':A.tolist(),'Cr_fractional':CR.tolist(),'Sb_fractional':SB.tolist(),'cage_rotation_residual':float(cage_residual),'screw_maps_Cr_and_Sb':True,'pure_half_c_translation_maps_Sb':False,'displayed_Cr_count':len(sites),'equal_up_down_layers':True,'g_wave_harmonic':'kz*ky*(3*kx^2-ky^2)','g_inversion_residual':float(inv),'g_60_degree_sign_flip_residual':float(r60),'momentum_surface':'Signed harmonic illustration; radial deformation is an artistic amplitude convention, not a calculated material Fermi surface.'},indent=2)+'\n')
print('CrSb screw/cage and g-wave relations verified; cover reference generated.')
