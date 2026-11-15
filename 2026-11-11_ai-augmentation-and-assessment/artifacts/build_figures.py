"""Replot published coefficients; draw an explicitly proposed assessment comparison."""
from pathlib import Path
import json
import argparse
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import font_manager
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts' / 'figures'
DATA = {
    'source': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12232635/',
    'location': 'Table 1, Bastani et al., PNAS 122 e2422633122 (2025)',
    'quantity': 'Treatment regression coefficient relative to no-AI control; score normalized 0-1',
    'uncertainty': 'Plus or minus one classroom-clustered HC1 robust standard error; not a confidence interval',
    'practice': {'base': [0.137, 0.031], 'tutor': [0.361, 0.032]},
    'unassisted_exam': {'base': [-0.054, 0.022], 'tutor': [-0.004, 0.013]},
    'control_mean': {'practice': 0.284, 'unassisted_exam': 0.321},
    'reported_significance': {'practice_base': 'p<0.01', 'practice_tutor': 'p<0.01', 'exam_base': 'p<0.05', 'exam_tutor': 'not significant'},
    'reproduction_scope': 'Replotting published coefficients only; no individual-level statistical reanalysis'
}

COLORS = ['#a85836', '#14737b']
INK = '#19323a'
MUTED = '#586a71'

def plot_study(lang, mobile=False):
    ko = lang == 'ko'
    size = (5.15, 7.7) if mobile else (10.8, 6.4)
    fig, axes = plt.subplots(2, 1, figsize=size)
    fig.patch.set_facecolor('#fffefa')
    title = '연습의 성과와 이후 독립시험은 다른 결과다' if ko else 'Practice performance and later learning are different outcomes'
    if mobile:
        title = '연습 성과와 이후 독립시험' if ko else 'Practice and the later unassisted exam'
    fig.suptitle(title, x=0.075 if mobile else 0.14, y=0.975, ha='left', color=INK,
                 fontsize=16 if mobile else 17, fontweight='bold')
    labels = ['일반 보조', '힌트형 튜터'] if ko else ['General assistant', 'Hint-based tutor']
    if mobile and not ko:
        labels = ['General\nassistant', 'Hint-based\ntutor']
    panel_titles = ['AI와 함께 푼 연습', '이후 자료 없는 독립시험'] if ko else ['Practice with AI available', 'Later unassisted exam']
    for idx, (key, ax) in enumerate(zip(['practice', 'unassisted_exam'], axes)):
        ax.set_facecolor('#fffefa')
        ax.set_title(panel_titles[idx], loc='left', pad=16, fontsize=14 if mobile else 13, fontweight='bold', color=INK)
        for j, condition in enumerate(['base', 'tutor']):
            val, se = DATA[key][condition]
            y = 1-j
            ax.errorbar(val, y, xerr=se, fmt='o', markersize=8, color=COLORS[j],
                        ecolor=COLORS[j], capsize=5, linewidth=2.2, zorder=3)
            ax.text(max(val+se+0.023,0.045), y, f'{val:+.3f}', va='center', color=COLORS[j],
                    fontsize=13.5 if mobile else 12, fontweight='bold')
        ax.axvline(0, color=INK, lw=1)
        ax.set_xlim(-0.12, 0.52)
        ax.set_ylim(-0.55, 1.55)
        ax.set_yticks([1, 0], labels=labels, fontsize=13.5 if mobile else 11.5, color=INK)
        ax.set_xticks(np.arange(-0.1, 0.5, 0.1))
        ax.tick_params(axis='x', labelsize=11.5 if mobile else 10.5, colors=MUTED)
        ax.tick_params(axis='y', length=0, pad=12)
        ax.grid(axis='x', color='#e0e6e0', lw=.8)
        ax.set_axisbelow(True)
        for spine in ax.spines.values():
            spine.set_visible(False)
        xlabel = '대조군 대비 정규화 점수 차이 (0-1)' if ko else 'Difference from no-AI control (score normalized 0-1)'
        if mobile:
            xlabel = '대조군 대비 정규화 점수 차이\n(0-1)' if ko else 'Difference from no-AI control\n(score normalized 0-1)'
        ax.set_xlabel(xlabel, fontsize=11.5 if mobile else 11, color=MUTED, labelpad=10)
    if mobile:
        fig.subplots_adjust(left=.30, right=.96, top=.88, bottom=.20, hspace=1.02)
        footer = '점: 회귀 추정치 · 막대: ±1 표준오차\n학급 군집 HC1 · 원자료 재분석 아님' if ko else 'Dots: regression estimates; bars: ±1 SE\nClassroom-clustered HC1; no raw-data reanalysis'
    else:
        fig.subplots_adjust(left=.18, right=.95, top=.86, bottom=.17, hspace=.93)
        footer = '점: 회귀 추정치 · 막대: ±1 표준오차 (학급 군집 HC1). 두 패널은 서로 다른 과제다.' if ko else 'Dots: regression estimates; bars: ±1 classroom-clustered HC1 SE. The panels are different tasks.'
    fig.text(.075 if mobile else .14, .035, footer, fontsize=11 if mobile else 10, color=MUTED, linespacing=1.8)
    name = f'practice-and-learning{"-mobile" if mobile else ""}-{lang}.svg'
    target = OUT / name
    fig.savefig(target, format='svg', metadata={'Date': None, 'Creator': 'AI Tech Review; Matplotlib', 'Title': title})
    plt.close(fig)
    s = target.read_text()
    s = s.replace('<svg ', '<svg role="img" ', 1)
    target.write_text(s)

def conceptual_diagram(lang):
    ko = lang == 'ko'
    ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', ns)
    root = ET.Element(f'{{{ns}}}svg', {'width':'760','height':'650','viewBox':'0 0 760 650','role':'img'})
    def tag(name, attrs=None, txt=None):
        e=ET.SubElement(root, f'{{{ns}}}{name}',attrs or {})
        if txt is not None:e.text=txt
        return e
    title = '하나의 판단 과제, 세 가지 관찰' if ko else 'One decision task, three observations'
    tag('title',txt=title)
    tag('desc',txt='A proposal by this review, not a validated universal competence model.')
    tag('rect',{'width':'760','height':'650','fill':'#fffefa'})
    def text(x,y,txt,size=25,bold=False,color=INK):
        tag('text',{'x':str(x),'y':str(y),'font-family':'ReviewFigure,sans-serif','font-size':str(size),'font-weight':'700' if bold else '400','fill':color},txt)
    text(34,50,title,30,True)
    text(34,89,'“방법 A가 B보다 낫다”는 주장을 검토한다' if ko else 'Evaluate a claim that method A outperforms B',21,color=MUTED)
    contents = [
        ('기초 이해','분모·단위·비교 조건을 읽는다','무엇을 이해하고, 무엇을 더 알아야 하는가?',COLORS[0]),
        ('AI를 활용한 수행','더 큰 자료를 분석하고 대안을 비교한다','어떤 결과를 시간·비용 안에서 만드는가?',COLORS[1]),
        ('위임과 검증의 판단','맡길 일을 정하고, 확인하고, 수정한다','결과를 채택·보류·추가 확인할 이유는?', '#6c5683')
    ] if ko else [
        ('Foundational understanding','Read denominators, units and comparison conditions','What is understood? What is still unknown?',COLORS[0]),
        ('Performance with AI','Analyze more data and compare alternatives','What can be delivered within time and cost limits?',COLORS[1]),
        ('Delegation and verification','Decide what to delegate, check and revise','Why accept, defer or investigate the result?', '#6c5683')
    ]
    for i,(a,b,c,col) in enumerate(contents):
        y=119+154*i
        tag('rect',{'x':'34','y':str(y),'width':'692','height':'132','rx':'10','fill':'#f1f4ef','stroke':'#d8e0d9'})
        tag('rect',{'x':'34','y':str(y),'width':'7','height':'132','rx':'3','fill':col})
        text(60,y+36,a,27,True,col)
        text(60,y+76,b,22)
        text(60,y+110,c,20,color=MUTED)
    text(34,610,'함께 관찰하되 임의의 총점으로 합치지 않는다' if ko else 'Observe together; do not invent an aggregate score',21,True)
    text(34,638,'리뷰의 교육 설계 제안 · 보편적으로 검증된 척도가 아님' if ko else 'A review proposal, not a universally validated scale',17,color=MUTED)
    (OUT/f'competence-and-tools-{lang}.svg').write_text(ET.tostring(root,encoding='unicode')+'\n')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--font-regular',type=Path,required=True)
    parser.add_argument('--font-bold',type=Path,required=True)
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    for font in [args.font_regular,args.font_bold]:
        font_manager.fontManager.addfont(font)
    plt.rcParams.update({'font.family':'Noto Sans KR','svg.fonttype':'path','svg.hashsalt':'ai-augmentation-assessment-2026-11-11','axes.unicode_minus':False})
    for lang in ['ko','en']:
        plot_study(lang)
        plot_study(lang,mobile=True)
        conceptual_diagram(lang)
    # Arithmetic checks validate the redraw only, not the study's analysis.
    assert DATA['practice']['base']==[.137,.031]
    assert DATA['unassisted_exam']['tutor']==[-.004,.013]
    assert abs(DATA['unassisted_exam']['base'][0]/DATA['control_mean']['unassisted_exam']+.168224299)<1e-8
    (ROOT/'artifacts/study-figure-data.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'svg_count':len(list(OUT.glob('*.svg'))),'coefficient_points':4,'uncertainty':'±1 SE','reanalysis':False}))

if __name__=='__main__':
    main()
