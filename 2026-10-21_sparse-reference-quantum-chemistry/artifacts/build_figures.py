"""Original bilingual seminar figures and independently checked teaching values.

Figures are explanatory redrawings, not source-paper plots or circuit layouts.
The two-level example is synthetic and uses mHa throughout. Outlined SVG text
avoids a dependency on fonts in the public figure files.
"""
from pathlib import Path
import argparse, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc

OUT=Path(__file__).resolve().parent
BG='#fbf9f3'; INK='#18313c'; MUTED='#536971'; TEAL='#11666d'; GOLD='#b77b30'; RED='#aa5148'; LINE='#cfdbd5'; WASH='#eaf1ec'; BLUE='#456b9d'
FONT=None
def tx(ax,x,y,s,size=15,color=INK,ha='left',va='center',weight='normal'):
    s=s.replace('EΦ',r'$E_\Phi$')
    return ax.text(x,y,s,fontsize=size,color=color,ha=ha,va=va,fontproperties=FONT,weight=weight)
def box(ax,x,y,w,h,fill=WASH,edge=LINE):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008,rounding_size=.016',facecolor=fill,edgecolor=edge,lw=1.2))
def arrow(ax,x,y,u,v,color=TEAL,lw=2,style='-|>'):
    ax.add_patch(FancyArrowPatch((x,y),(u,v),arrowstyle=style,mutation_scale=18,color=color,lw=lw))
def canvas(mobile,h=7.5,mh=12):
    f=plt.figure(figsize=(6,mh) if mobile else (12,h),facecolor=BG);a=f.add_axes([0,0,1,1]);a.set(xlim=(0,1),ylim=(0,1));a.axis('off');return f,a
def save(f,name,lang,mobile):
    target=OUT/f'{name}{"_mobile" if mobile else ""}_{lang}.svg'
    f.canvas.draw();renderer=f.canvas.get_renderer();bounds=f.bbox
    for text in f.findobj(matplotlib.text.Text):
        if not text.get_visible() or not text.get_text():continue
        b=text.get_window_extent(renderer)
        if b.width and b.height and (b.x0 < -1 or b.y0 < -1 or b.x1>bounds.width+1 or b.y1>bounds.height+1):
            raise ValueError(f'Text exceeds {target.name}: {text.get_text()}')
    f.savefig(target,format='svg',metadata={'Date':None,'Creator':'Original AI Tech Review seminar diagram; matplotlib'})
    qa=OUT.parent/'tmp'/'figures';qa.mkdir(parents=True,exist_ok=True)
    f.savefig(qa/(target.stem+'.png'),dpi=110);plt.close(f)

def projection(lang,m):
    ko=lang=='ko';f,a=canvas(m,7.6,12)
    tx(a,.055,.957,('참조 상태와 잔차: 한 방향을 더 읽는다' if ko else ('Reference and residual:\nread one more direction' if m else 'Reference and residual: read one more direction')),20 if m else 23,weight='bold',va='top')
    tx(a,.055,.87 if m else .895,('해밀토니안이 기준상태를 보내는 방향을 분해한다.' if ko else ('Resolve the direction in which H sends\nthe reference state.' if m else 'Resolve the direction in which H sends the reference state.')),13 if m else 14,color=MUTED,va='top')
    # Coordinates in the orthonormal (Phi,Lambda) basis. Direction lengths are illustrative.
    x,y=(.16,.45) if m else (.14,.38);sx,sy=(.63,.29) if m else (.34,.36)
    arrow(a,x-.045,y,x+sx*1.08,y,color=LINE,lw=1.3);arrow(a,x,y-.10,x,y+sy*1.12,color=LINE,lw=1.3)
    arrow(a,x,y,x+sx*.83,y,color=TEAL,lw=3);arrow(a,x,y,x,y+sy*.72,color=BLUE,lw=3)
    arrow(a,x,y,x+sx*.66,y+sy*.63,color=GOLD,lw=3)
    a.plot([x+sx*.66,x+sx*.66],[y,y+sy*.63],color=BLUE,lw=1.7,ls=(0,(4,3)))
    a.plot([x,x+sx*.66],[y+sy*.63,y+sy*.63],color=TEAL,lw=1.7,ls=(0,(4,3)))
    tx(a,x+sx*.85,y-.045,r'$|\Phi\rangle$',19,color=TEAL,ha='center')
    tx(a,x-.018,y+sy*.82,r'$|\Lambda\rangle$',19,color=BLUE,ha='right')
    tx(a,x+sx*.68,y+sy*.68,r'$H|\Phi\rangle$',18,color=GOLD)
    tx(a,x+sx*.34,y-.03,r'$E_\Phi|\Phi\rangle$',15,color=TEAL,ha='center')
    tx(a,x+sx*.68,y+sy*.28,r'$r|\Lambda\rangle$',15,color=BLUE)
    arrow(a,x,y,x+sx*.55,y-sy*.31,color=RED,lw=2.3)
    tx(a,x+sx*.57,y-sy*.33,r'$|\Psi\rangle$',18,color=RED)
    tx(a,x+.02,y+.02,'0',12,color=MUTED)
    if m: x2,y2,w,h=.07,.11,.86,.22
    else:x2,y2,w,h=.57,.29,.365,.47
    box(a,x2,y2,w,h)
    rows=[r'$H|\Phi\rangle=E_\Phi|\Phi\rangle+r|\Lambda\rangle$',r'$\langle\Phi|\Lambda\rangle=0,\quad r=\|(H-E_\Phi)|\Phi\rangle\|$',r'$E_\Psi=E_\Phi+r\,\frac{\langle\Lambda|\Psi\rangle}{\langle\Phi|\Psi\rangle}$']
    for i,s in enumerate(rows):tx(a,x2+w/2,y2+h*(.80-i*.25),s,14 if m else 15,ha='center')
    tx(a,.055,.065,('정규화한 실수 고유상태, 참조 중첩 ≠ 0일 때의 항등식.' if ko else ('Identity for a normalized real eigenstate\nwith nonzero reference overlap.' if m else 'Identity for a normalized real eigenstate with nonzero reference overlap.')),11.5 if m else 12,color=MUTED,va='top')
    tx(a,.055,.025,('기하·길이는 설명용이며 실제 분자나 회로가 아니다.' if ko else ('Illustrative geometry; not a molecular structure or circuit.')),11 if m else 12,color=MUTED,va='top')
    save(f,'projection_residual',lang,m)

def evidence(lang,m):
    ko=lang=='ko';f,a=canvas(m,7.6,13)
    tx(a,.055,.957,('400회와 10,000회: 조건부터 읽는다' if ko else ('400 and 10,000 shots:\nread the conditions first' if m else '400 and 10,000 shots: read the conditions first')),20 if m else 23,weight='bold',va='top')
    tx(a,.055,.87 if m else .89,('서로 다른 활성공간과 실행 조건의 측정 횟수다.' if ko else ('These counts use different active spaces\nand execution conditions.' if m else 'These counts use different active spaces and execution conditions.')),13 if m else 14,color=MUTED,va='top')
    panels=[(.07,.53,.86,.29),(.07,.19,.86,.29)] if m else [(.055,.37,.425,.43),(.52,.37,.425,.43)]
    labels=[
        [('이상적 분산 추정' if ko else 'Noiseless variance estimate'),'~400',('CU shots / geometry'),('활성공간 (6,6) · Rx · 8개 기준 행렬식' if ko else 'Active space (6,6) · Rx · 8 determinants'),('목표 표준오차 1.6 mHa · 최적 측정 배분' if ko else 'Target SE 1.6 mHa · optimal allocation'),('Fig. 6d · Discussion')],
        [('실제 Helios-1 QPU 측정' if ko else 'Physical Helios-1 QPU measurement'),'10,000',('CU submitted shots / geometry'),('활성공간 (10,10) · AI-sMCS' if ko else 'Active space (10,10) · AI-sMCS'),('기준 2,000 + 잔차 8,000 · 누설 후선택' if ko else 'Reference 2,000 + residual 8,000 · postselection'),('Table 1 · Fig. 8 · Supplement S8')]]
    for (x,y,w,h),L in zip(panels,labels):
        box(a,x,y,w,h)
        tx(a,x+w/2,y+h*.88,L[0],15 if m else 15,color=TEAL,ha='center',weight='bold')
        tx(a,x+w/2,y+h*.65,L[1],33 if m else 36,ha='center',weight='bold')
        tx(a,x+w/2,y+h*.48,L[2],12 if m else 13,color=MUTED,ha='center')
        tx(a,x+w/2,y+h*.31,L[3],11.7 if m else 12,ha='center')
        tx(a,x+w/2,y+h*.19,L[4],11 if m else 11.3,ha='center')
        tx(a,x+w/2,y+h*.07,L[5],10.7 if m else 11,color=MUTED,ha='center')
    if m:xx,yy=.07,.135
    else:xx,yy=.055,.25
    tx(a,xx,yy,('정밀도(SE) 1.66-1.73 mHa  ≠  CASCI 기준 정확도 보장' if ko else ('SE 1.66-1.73 mHa does not guarantee\naccuracy against CASCI.')),12 if m else 14,color=RED,va='top')
    tx(a,.055,.095,('원 논문 보고값을 재도식화했다. 비율·성능 곡선이 아니다.' if ko else ('Redrawn reported values, not a speedup ratio\nor a reproduced performance curve.')),11.5 if m else 12,color=MUTED,va='top')
    tx(a,.055,.025,'Source: arXiv:2610.26689v1 · 21 October 2026',11,color=MUTED,va='top')
    save(f,'evidence_conditions',lang,m)

def cost(lang,m):
    ko=lang=='ko';f,a=canvas(m,7.2,12.7)
    tx(a,.055,.957,('측정 절감에서 전체 계산비용까지' if ko else ('From fewer measurements\nto total computational cost' if m else 'From fewer measurements to total computational cost')),20 if m else 23,weight='bold',va='top')
    tx(a,.055,.87 if m else .895,('한 단계가 빨라져도 다른 단계의 비용은 남는다.' if ko else ('Improving one stage leaves the costs\nof the other stages.' if m else 'Improving one stage leaves the costs of the other stages.')),13 if m else 14,color=MUTED,va='top')
    stages=[('고전 기준상태' if ko else 'Classical reference','selected CI / sparse state'),('잔차 계산·준비' if ko else 'Residual and preparation','H, EΦ, r, support, circuits'),('QPU 측정' if ko else 'QPU measurements','reference + residual shots'),('후선택·보정' if ko else 'Selection and correction','acceptance, mitigation'),('추정·비교' if ko else 'Estimate and compare','SE, bias, wall time')]
    rects=[(.08,.718-i*.132,.84,.096) for i in range(5)] if m else [(.045+i*.19,.49,.15,.29) for i in range(5)]
    for i,((x,y,w,h),(title,sub)) in enumerate(zip(rects,stages)):
        box(a,x,y,w,h,edge=TEAL if i==2 else LINE)
        if m:
            tx(a,x+.025,y+h*.69,f'{i+1:02}  '+title,16,color=TEAL,weight='bold');tx(a,x+.025,y+h*.25,sub,12,color=MUTED)
        else:
            tx(a,x+w/2,y+h*.77,f'{i+1:02}',17,color=GOLD,ha='center');tx(a,x+w/2,y+h*.53,title,12,ha='center',weight='bold')
            # Short annotation lines deliberately avoid tiny compressed text.
            subs=[['selected CI','sparse state'],['H, EΦ, r,','support, circuits'],['reference +','residual shots'],['acceptance,','mitigation'],['SE, bias,','wall time']][i]
            tx(a,x+w/2,y+h*.22,'\n'.join(subs),11,color=MUTED,ha='center')
        if i<4:
            u,v,ww,hh=rects[i+1]
            if m:arrow(a,.5,y-.004,.5,v+hh+.008)
            else:arrow(a,x+w+.003,y+h*.5,u-.005,v+hh*.5)
    y=.10 if m else .28
    tx(a,.055,y,('총시간 = 고전 전처리 + 회로 준비·실행 + 후처리' if ko else ('Total time = classical preparation +\ncircuit preparation/execution + postprocessing')),12 if m else 16,color=TEAL,va='top')
    tx(a,.055,.045 if m else .16,('설명용 비용 분해: 실제 전체 속도 향상은 측정하지 않았다.' if ko else ('Teaching decomposition; end-to-end speedup\nwas not measured here.')),11.5 if m else 13,color=MUTED,va='top')
    save(f,'cost_chain',lang,m)

def two_level(lang,m):
    ko=lang=='ko';f,a=canvas(m,7.8,12.5)
    tx(a,.055,.957,('2준위 실습: 기준 오차를 상쇄하는 항' if ko else ('Two-level lab:\nthe term that cancels reference error' if m else 'Two-level lab: the term that cancels reference error')),20 if m else 23,weight='bold',va='top')
    tx(a,.055,.87 if m else .895,('리뷰의 합성 모형 · 논문 분자나 QPU 데이터가 아니다.' if ko else ('Synthetic teaching model, not molecular\nor QPU data from the paper.')),13 if m else 14,color=MUTED,va='top')
    p=f.add_axes([.15,.49,.78,.29] if m else [.10,.26,.47,.51]);theta=np.linspace(1,89,250);s=np.sin(np.deg2rad(theta));c=np.cos(np.deg2rad(theta))
    p.plot(theta,100*s*s,color=TEAL,lw=2.5,label=r'$E_\Phi$');p.plot(theta,-100*s*s,color=GOLD,lw=2.5,label=r'$-r\sqrt{p_\Lambda/p_\Phi}$');p.axhline(0,color=RED,lw=2,label=r'$E_{\rm ME}=E_0=0$')
    p.axvline(30,color=LINE,ls='--');p.scatter([30,30,30],[25,-25,0],c=[TEAL,GOLD,RED],s=45,zorder=3)
    p.set(xlim=(0,90),ylim=(-105,105),xticks=[0,30,60,90],yticks=[-100,-50,0,50,100]);p.set_xlabel(r'$\theta\ (\mathrm{degrees})$',fontsize=12);p.set_ylabel('Energy (mHa)',fontsize=12);p.set_facecolor(BG);p.grid(color=LINE,lw=.7);p.spines[['top','right']].set_visible(False);p.tick_params(labelsize=11);p.legend(fontsize=11,loc='upper left')
    if m:x,y,w,h=.075,.13,.85,.275
    else:x,y,w,h=.64,.25,.30,.53
    box(a,x,y,w,h)
    values=[r'$H=\mathrm{diag}(0,100)\ \mathrm{mHa}$',r'$\theta=30^\circ:\ E_\Phi=25\ \mathrm{mHa}$',r'$r=43.3013\ \mathrm{mHa}$',r'$p_\Phi=0.75,\quad p_\Lambda=0.25$',r'$N_\Phi=2500,\quad N_\Lambda=7500$',r'$\mathrm{SE}_{\rm opt}\approx0.2887\ \mathrm{mHa}$']
    for i,v in enumerate(values):tx(a,x+w/2,y+h*(.89-i*.15),v,14.5 if m else 13.3,ha='center')
    tx(a,.055,.095,('독립 Bernoulli 투영 측정 · 채택된 측정 10,000회 · 1차 분산 근사' if ko else ('Independent Bernoulli projector measurements;\n10,000 accepted shots; first-order variance approximation.')),11 if m else 12,color=MUTED,va='top')
    tx(a,.055,.035,('0°에서는 잔차 불필요, 90°에서는 참조 중첩이 0이다.' if ko else ('At 0° the residual is unnecessary; at 90°\nthe reference overlap vanishes.' if m else 'At 0° the residual is unnecessary; at 90° the reference overlap vanishes.')),11 if m else 12,color=MUTED,va='top')
    save(f,'two_level_model',lang,m)

def validate():
    delta=100.;H=np.diag([0.,delta]);psi=np.array([1.,0.]);maximum=0.
    for deg in np.linspace(1,89,177):
        th=np.deg2rad(deg);phi=np.array([np.cos(th),np.sin(th)]);lam=np.array([-np.sin(th),np.cos(th)]);E=float(phi@H@phi);res=(H-E*np.eye(2))@phi;r=np.linalg.norm(res);q=float((phi@psi)**2);p=float((lam@psi)**2)
        assert np.allclose(res,r*lam,atol=1e-11)
        eme=E-r*np.sqrt(p/q);maximum=max(maximum,abs(eme));assert abs(eme)<1e-10
        dp=-r/(2*np.sqrt(p*q));dq=r*np.sqrt(p)/(2*q**1.5)
        A=dp*dp*p*(1-p);B=dq*dq*q*(1-q)
        assert np.isclose(A,r*r*(1-p)/(4*q));assert np.isclose(B,r*r*p*(1-q)/(4*q*q))
    p=.25;q=.75;r=100*np.sqrt(p*q);A=r*r*(1-p)/(4*q);B=r*r*p*(1-q)/(4*q*q);N=10000;frac=np.sqrt(A)/(np.sqrt(A)+np.sqrt(B))
    # Independent finite-difference gradient check at the pedagogical default.
    energy=lambda pp,qq:25-r*np.sqrt(pp/qq)
    step=1e-6;g_numeric=[(energy(p+step,q)-energy(p-step,q))/(2*step),(energy(p,q+step)-energy(p,q-step))/(2*step)];g_exact=[-r/(2*np.sqrt(p*q)),r*np.sqrt(p)/(2*q**1.5)]
    assert np.allclose(g_numeric,g_exact,atol=1e-7)
    assert np.isclose(frac,.75)
    var_opt=A/(N*frac)+B/(N*(1-frac));var_equal=2*(A+B)/N
    grid=np.linspace(.001,.999,999);assert var_opt<=np.min(A/(N*grid)+B/(N*(1-grid)))+1e-10
    theta=np.deg2rad(30);eta=np.deg2rad(-5);phi=np.array([np.cos(theta),np.sin(theta)]);approx=np.array([np.cos(eta),np.sin(eta)])
    approximate_mixed=float(approx@H@phi/(approx@phi));approximate_variational=float(approx@H@approx)
    assert np.isclose(approximate_mixed,-5.319875800548582,rtol=0,atol=1e-10)
    assert np.isclose(approximate_variational,.759612349389597,rtol=0,atol=1e-10)
    excited=np.array([0.,1.]);excited_signed=float(excited@H@phi/(excited@phi));wrong_negative=25-r*np.sqrt(.75/.25)
    assert np.isclose(excited_signed,100);assert np.isclose(wrong_negative,-50)
    # 2022 CODATA Hartree energy and exact SI Boltzmann constant, as cited in the article.
    hartree_J=4.3597447222060e-18;kB_J_per_K=1.380649e-23
    thermal_factor=math.exp(1.6e-3*hartree_J/(kB_J_per_K*300))
    assert np.isclose(thermal_factor,5.3877802,atol=1e-7)
    casci=np.array([-2404.524315,-2404.524434]);reported=[('Leakage',[-2404.517851,-2404.514175],[.001724,.001658]),('CPC',[-2404.518388,-2404.511333],[.001734,.001691]),('MBPC',[-2404.517853,-2404.513668],[.001734,.001687])]
    contrasts=[]
    for name,energies,se in reported:
        e=np.array(energies);point_diff=float((e[0]-e[1])*1000);casci_diff=float((casci[0]-casci[1])*1000)
        contrasts.append({'source':'arXiv:2610.26689v1 Tables S8 and S6; recalculation from printed rounded values','detection':name,'geometry_deviations_mHa':((e-casci)*1000).tolist(),'energy_difference_mHa':point_diff,'independent_difference_SE_mHa':float(np.linalg.norm(se)*1000),'CASCI_difference_mHa':casci_diff,'difference_deviation_mHa':point_diff-casci_diff})
    record={'basis':'Independent synthetic two-level teaching model, not paper data. Exact normalized target |0>, H=diag(0,100) mHa. Independent Bernoulli projector samples and first-order delta-method variance; no hardware noise, leakage, correction, state-preparation or runtime costs.','theta_degrees':30,'delta_mHa':delta,'reference_energy_mHa':25,'residual_norm_mHa':r,'p_residual':p,'p_reference':q,'accepted_shots':N,'variance_coefficient_residual_mHa2':A,'variance_coefficient_reference_mHa2':B,'optimal_residual_shots':7500,'optimal_reference_shots':2500,'optimal_SE_mHa':np.sqrt(var_opt),'equal_allocation_SE_mHa':np.sqrt(var_equal),'sweep_points':177,'maximum_exact_identity_error_mHa':maximum,'finite_difference_gradients':g_numeric,'analytic_gradients':g_exact}
    record.update({'approximate_target_eta_degrees':-5,'approximate_target_mixed_energy_mHa':approximate_mixed,'approximate_target_variational_energy_mHa':approximate_variational,'excited_target_signed_energy_mHa':excited_signed,'excited_target_wrong_negative_branch_mHa':wrong_negative,'thermal_sensitivity':{'basis':'Independent Arrhenius sensitivity calculation using 2022 CODATA Hartree energy, exact SI kB, fixed prefactors. Not a Ru model rate prediction.','energy_difference_mHa':1.6,'temperature_K':300,'rate_ratio':thermal_factor},'reported_energy_recalculations':contrasts})
    (OUT/'two_level_teaching_values.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))

def main():
    global FONT
    p=argparse.ArgumentParser();p.add_argument('--font',type=Path,required=True);args=p.parse_args();FONT=FontProperties(fname=str(args.font))
    plt.rcParams.update({'svg.fonttype':'path','svg.hashsalt':'sparse-reference-seminar-2026-10-21','mathtext.fontset':'dejavusans','axes.unicode_minus':False})
    validate()
    for lang in ['ko','en']:
        for mobile in [False,True]:
            projection(lang,mobile);evidence(lang,mobile);cost(lang,mobile);two_level(lang,mobile)
    print('Created 16 outlined bilingual responsive SVG diagrams.')
if __name__=='__main__':main()
