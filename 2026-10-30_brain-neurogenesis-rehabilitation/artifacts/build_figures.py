"""Original, outlined explanatory figures; data are adjacent public JSON files."""
from pathlib import Path
import argparse
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
PREVIEW = ROOT / 'tmp' / 'figures'
INK = '#253b40'
TEAL = '#177c79'
PURPLE = '#765783'
OCHRE = '#ab6a3b'
MUTED = '#637570'
GRID = '#d8e0db'
PAPER = '#faf8f2'


def canvas(width, height):
    fig = plt.figure(figsize=(width / 72, height / 72), facecolor=PAPER)
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, width), ylim=(0, height))
    ax.axis('off')
    return fig, ax


def text(ax, x, y, content, size=13, color=INK, weight='normal', **kwargs):
    return ax.text(x, y, content, fontsize=size, color=color, fontweight=weight,
                   va=kwargs.pop('va', 'top'), linespacing=1.35, **kwargs)


def rect(ax, x, y, width, height, color=TEAL, fill='white', lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), width, height,
                 boxstyle='round,pad=0,rounding_size=6', facecolor=fill,
                 edgecolor=color, linewidth=lw))


def arrow(ax, start, end, color=MUTED, dashed=False):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=10,
                 linewidth=1.2, color=color, linestyle=(0, (3, 3)) if dashed else '-'))


def save(fig, stem, lang, mobile):
    name = f'{stem}{"_mobile" if mobile else ""}_{lang}'
    fig.savefig(ART / f'{name}.svg', metadata={
        'Date': None, 'Creator': 'AI Tech Review original figure builder',
        'Description': 'Original explanatory geometry; source data and scope are recorded separately.'})
    svg_path = ART / f'{name}.svg'
    svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text().splitlines()) + '\n')
    fig.savefig(PREVIEW / f'{name}.png', dpi=140)
    plt.close(fig)


def evidence_steps(lang, mobile, data):
    ko = lang == 'ko'
    assert len(data['evidence_steps']['questions']) == 4
    if ko:
        title = '세포 연구는 서로 다른 질문에 답한다'
        cards = [
            ('언제 만들어졌나', 'BrdU + 뉴런 표지: 표지 뒤 생존 단서\n탄소-14 DNA: 집단의 출생·교체 모형\n개별 세포의 회로 기능은 따로 확인'),
            ('어떤 계열이 증식하나', 'Ki67 농축 + 단일핵 RNA + 공간 위치\n증식하는 전구체의 정체성을 함께 조사\nKi67 하나만으로 뉴런의 운명은 판정 못함'),
            ('어떤 세포 상태인가', '표지 조합·RNA·염색질 접근성\n미성숙·분화·조절 상태를 비교\n상태의 유사성이 출생 날짜는 아님'),
            ('회로와 기능에 어떻게 기여하나', '연결·생리·행동 기여를 추가로 조사\n임상 기능·일상 수행은 별도 평가\n세포 상태와 회복 점수를 동일시하지 않음')]
        sub = '관찰법은 상보적이다. 위아래 순위나 하나의 확정 계보를 뜻하지 않는다.'
        process = '생물학적 과정: 탄생 · 생존 · 분화 · 회로 통합'
        foot = '발달 순서·변화 방향은 계산상 추정이다. 실제 시간·세포 계보 추적과 구분한다.\nDCX·PSA-NCAM 같은 표지 하나만으로 새로 태어난 뉴런을 단정하지 않는다.'
    else:
        title = 'Cell studies answer different questions'
        cards = [
            ('When was a cell born?', 'BrdU + neuronal phenotype: survival clues\nCarbon-14 DNA: population turnover model\nCircuit function requires other observations'),
            ('Which lineage is proliferating?', 'Ki67 enrichment + single-nucleus RNA + location\nIdentify proliferating progenitors jointly\nKi67 alone does not establish neuronal fate'),
            ('What cellular state is present?', 'Markers, RNA and chromatin accessibility\nCompare immaturity and regulatory states\nSimilar states do not establish birth dates'),
            ('How does it contribute to function?', 'Study connections, physiology and behavior\nClinical function / daily activity are separate\nCell states and recovery scores differ')]
        sub = 'Complementary observations, not a ranking of assays or an observed lineage.'
        process = 'Biological processes: birth · survival · differentiation · circuit integration'
        foot = 'Inferred developmental order and direction are not direct time or lineage tracking.\nA single marker such as DCX or PSA-NCAM does not establish that a neuron was newly born.'
    if mobile:
        fig, ax = canvas(342, 820)
        text(ax, 20, 798, '세포 연구의 네 질문' if ko else 'Four questions for cell studies', 17, weight='bold')
        text(ax, 20, 759, '방법을 서로 보완해 읽는다.' if ko else 'Read methods as complementary.', 12, MUTED)
        for i, (heading, body) in enumerate(cards):
            y = 584 - i * 145
            rect(ax, 20, y, 302, 126, TEAL if i < 3 else OCHRE)
            text(ax, 33, y + 109, heading, 13.7, TEAL if i < 3 else OCHRE, weight='bold')
            if not ko:
                wraps = [
                    'BrdU + neuronal phenotype:\nsurvival clues after labeling\nCarbon-14 DNA: population turnover\nCircuit function needs other observations',
                    'Ki67 enrichment + single-nucleus RNA\n+ spatial location: identify progenitors\nKi67 alone does not establish\nneuronal fate',
                    'Markers, RNA and chromatin accessibility\nCompare immaturity / regulatory states\nSimilar states do not establish\nbirth dates',
                    'Connections, physiology and behavior\nClinical function and daily activity\nneed separate outcome measures']
                body = wraps[i]
            text(ax, 33, y + 78, body, 12 if not ko else 12.1)
        text(ax, 20, 128, '탄생 · 생존 · 분화 · 회로 통합\n기능 기여에는 추가 관찰이 필요하다.' if ko else
             'Birth · survival · differentiation\n· integration: functional contribution\nrequires further observations.', 11.5, weight='bold')
        text(ax, 20, 66, '발달 순서·변화 방향은 계산상 추정.\n실제 시간·계보 추적과 구분한다.\n한 가지 표지로 세포 탄생을 단정하지 않는다.' if ko else
             'Developmental order / direction are inferred.\nThey do not directly track time or lineage.\nOne marker does not establish cell birth.', 10.7, MUTED)
    else:
        fig, ax = canvas(864, 468)
        text(ax, 30, 446, title, 22, weight='bold')
        text(ax, 30, 409, sub, 13, MUTED)
        for i, (heading, body) in enumerate(cards):
            x = 30 + (i % 2) * 410
            y = 249 if i < 2 else 107
            color = TEAL if i < 3 else OCHRE
            rect(ax, x, y, 394, 126, color)
            text(ax, x + 16, y + 108, heading, 15, color, weight='bold')
            text(ax, x + 16, y + 75, body, 13 if ko else 12.4)
        text(ax, 30, 88, process, 12, weight='bold')
        text(ax, 30, 59, foot, 11.3, MUTED)
    save(fig, 'evidence_steps', lang, mobile)


def circuit(ax, x, y, width):
    for cy, strong in [(y + 64, False), (y, True)]:
        nodes = [(x + 24, cy), (x + width / 2, cy + 17), (x + width - 24, cy)]
        for a, b in zip(nodes[:-1], nodes[1:]):
            ax.plot([a[0], b[0]], [a[1], b[1]], color=TEAL,
                    linewidth=3 if strong else 1.2, linestyle='-' if strong else '--')
        for px, py in nodes:
            ax.add_patch(Circle((px, py), 8, edgecolor=TEAL, facecolor='white', linewidth=1.3))
    arrow(ax, (x + width / 2, y + 48), (x + width / 2, y + 30), TEAL)


def mechanism_card(ax, x, y, width, height, index, lang):
    ko = lang == 'ko'
    color = [PURPLE, TEAL, OCHRE][index]
    headings = ['새 뉴런 생성·통합', '기존 회로 조정·재학습', '과제·환경의 보상'] if ko else [
        'New neurons and integration', 'Existing circuits and relearning', 'Task / environmental compensation']
    rect(ax, x, y, width, height, color)
    text(ax, x + width / 2, y + height - 18, headings[index], 14 if ko else 12.9, color,
         weight='bold', ha='center')
    if index == 0:
        layers = [('안쪽 측두엽', 'Medial temporal lobe', 18, 104, height - 172),
                  ('해마 형성체', 'Hippocampal formation', 34, 112, height - 214),
                  ('치아이랑 (DG)', 'Dentate gyrus (DG)', 50, 120, height - 248)]
        # Nested containment only; no anatomical surface or MRI is simulated.
        for a, b, inset, base, h in layers:
            rect(ax, x + inset, y + base, width - 2 * inset, h, color, PAPER, .9)
            text(ax, x + width / 2, y + base + h - 12, a if ko else b,
                 11.8 if ko else 10.8, color, ha='center')
        text(ax, x + 16, y + 59, '구조적 신경가소성의 일부\n위치 포함 관계만 표시' if ko else
             'Part of structural neuroplasticity\nContainment only, not an MRI', 12 if width > 280 else 11.3 if ko else 10.8)
    elif index == 1:
        text(ax, x + width / 2, y + height - 60,
             '같은 뉴런, 달라지는 연결·활동' if ko else 'Existing neurons, changed connections',
             11.3 if ko else 10.8, ha='center')
        circuit(ax, x + 16, y + height - 190, width - 32)
        text(ax, x + 16, y + 59, '연습·피드백을 통한 재학습\n세포 탄생을 뜻하지 않음' if ko else
             'Practice and feedback support relearning\nThis does not imply cell birth', 12 if width > 280 else 11.3 if ko else 10.7)
    else:
        text(ax, x + width / 2, y + height - 60,
             '같은 목표, 달라지는 수행 방식' if ko else 'Same goal, different ways to act',
             11.3 if ko else 10.8, ha='center')
        for offset, label in [(112, '전략 조정' if ko else 'Adjust strategy'),
                              (173, '보조도구·환경 조정' if ko else 'Adapt tools / environment')]:
            rect(ax, x + 24, y + height - offset - 30, width - 48, 42, color, PAPER, .9)
            text(ax, x + width / 2, y + height - offset - 10, label, 12, color, ha='center', va='center')
        text(ax, x + width / 2, y + height - 147, '또는 함께' if ko else 'or together',
             10.2, color, ha='center')
        text(ax, x + 16, y + 59, '수행을 돕는 보상·적응\n기전들은 함께 작용할 수 있음' if ko else
             'Compensation and adaptation aid tasks\nMechanisms can operate together', 12 if width > 280 else 11.3 if ko else 10.7)


def recovery_mechanisms(lang, mobile, data):
    ko = lang == 'ko'
    assert data['recovery_mechanisms']['neurogenesis_is_part_of_structural_neuroplasticity']
    if mobile:
        fig, ax = canvas(342, 1110)
        text(ax, 20, 1088, '회복에 기여하는 서로 다른 변화' if ko else
             'Different changes can\ncontribute to recovery', 17, weight='bold')
        text(ax, 20, 1029, '서로 배타적인 세 갈래가 아니다.' if ko else
             'These are not mutually exclusive routes.', 11.5, MUTED)
        for i in range(3):
            mechanism_card(ax, 20, 700 - i * 302, 302, 280, i, lang)
        text(ax, 20, 75, '치아이랑의 세포 연구를 뇌손상 전반의\n복구로 확대하지 않는다. 수행 향상만으로\n세포 수준의 기전을 특정할 수 없다.' if ko else
             'Dentate-gyrus evidence does not establish\nrepair throughout an injured brain.\nTask gains alone do not identify cell mechanisms.', 10.7, MUTED)
    else:
        fig, ax = canvas(864, 468)
        text(ax, 30, 446, '기능의 향상과 세포의 변화는 다른 질문이다' if ko else
             'Functional gains and cellular changes are different questions', 21, weight='bold')
        text(ax, 30, 410, '새 뉴런 생성도 구조적 신경가소성에 포함된다. 여러 변화가 함께 작용할 수 있다.' if ko else
             'Neurogenesis is part of structural neuroplasticity. Several mechanisms can act together.', 12.6, MUTED)
        for i in range(3):
            mechanism_card(ax, 30 + i * 274, 86, 256, 292, i, lang)
        text(ax, 30, 61, '위치의 포함 관계를 단순화한 개념도이며 실제 해부 단면·축척이 아니다.\n치아이랑의 관찰을 뇌손상 전반의 재생으로 확대하거나 수행 향상에서 세포 기전을 단정하지 않는다.' if ko else
             'Original containment and mechanism schematic, not an anatomical section or scale drawing.\nDentate-gyrus observations do not establish whole-brain repair; task gains alone do not identify cell mechanisms.', 11.3, MUTED)
    save(fig, 'recovery_mechanisms', lang, mobile)


def style_plot(ax, ylabel=None, size=12):
    ax.set_facecolor(PAPER)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color(GRID)
    ax.tick_params(colors=INK, labelsize=size, length=3, color=MUTED)
    ax.yaxis.grid(True, color=GRID, linewidth=.7)
    ax.set_axisbelow(True)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=size, color=INK)


def stemtra_results(lang, mobile, data):
    ko = lang == 'ko'
    assert data['cell_n'] + data['sham_n'] == data['operated_modified_intention_to_treat_n'] == 61
    assert data['randomized_n'] == 63
    assert math.isclose(data['ls_mean_cell'] - data['ls_mean_sham'], data['between_group_difference'], abs_tol=1e-10)
    assert data['between_group_95ci'] == [.3, 11.8]
    fig, ax = canvas(342, 850) if mobile else canvas(864, 510)
    width, height = (342, 850) if mobile else (864, 510)
    title = ('STEMTRA: 6개월 운동 점수' if ko else 'STEMTRA: motor scores at 6 months')
    text(ax, 20 if mobile else 30, height - 22, title, 17 if mobile else 22, weight='bold')
    text(ax, 20 if mobile else 30, height - (65 if mobile else 59),
         '만성 외상성 뇌손상 성인 · 2상 무작위 시험\n63명 무작위 배정 → 수술한 61명 분석' if ko else
         'Adults with chronic TBI · randomized phase 2\n63 randomized; 61 operated and analyzed',
         11.3 if mobile else 12.6, MUTED)
    text(ax, 20 if mobile else 30, 741 if mobile else 409,
         ('FMMS 0–100점: 높을수록 양호\nSB623 46명은 3개 용량군 통합' if ko else
          'FMMS: 0–100; higher is better\nSB623: 46 patients across 3 dose groups') if mobile else
         ('FMMS 0–100점: 높을수록 양호 · SB623 46명은 3개 용량군 통합' if ko else
          'FMMS: 0–100; higher is better · SB623: 46 patients across 3 dose groups'),
         10.7 if mobile else 11.3, MUTED)
    group_rect = [.18, .51, .76, .275] if mobile else [.10, .35, .37, .37]
    groups = fig.add_axes(group_rect)
    means = [data['ls_mean_cell'], data['ls_mean_sham']]
    groups.bar([0, 1], means, color=[TEAL, '#aab8b1'], width=.53, zorder=3)
    groups.set_ylim(0, 10.5)
    groups.set_yticks([0, 2, 4, 6, 8, 10])
    groups.set_xticks([0, 1], [f'SB623\nn = {data["cell_n"]}', f'{"모의수술" if ko else "Sham surgery"}\nn = {data["sham_n"]}'])
    style_plot(groups, 'FMMS 변화 (점)' if ko else 'FMMS change (points)', 11 if mobile else 13)
    groups.set_title('기준점 대비 LS 평균 변화' if ko else 'LS mean change from baseline', fontsize=12 if mobile else 14, color=INK, pad=14)
    for i, mean in enumerate(means):
        groups.text(i, mean + .3, f'+{mean:.1f}', ha='center', fontsize=18, color=INK, fontweight='bold')
    if mobile:
        text(ax, 20, 373, '두 군 차이와 불확실성' if ko else 'Between-group difference and uncertainty', 13.1, weight='bold')
        ci_rect = [.11, .30, .84, .105]
    else:
        text(ax, 480, 386, '군간 차이: SB623 - 모의수술' if ko else 'Between-group difference: SB623 - sham', 14, weight='bold')
        ci_rect = [.57, .43, .36, .20]
    ci = fig.add_axes(ci_rect)
    low, high = data['between_group_95ci']
    estimate = data['between_group_difference']
    ci.axvline(0, color=MUTED, linestyle='--', linewidth=1)
    ci.errorbar(estimate, 0, xerr=[[estimate - low], [high - estimate]], fmt='o', color=TEAL,
                capsize=6, markersize=7, linewidth=2)
    ci.set_xlim(-1.5, 13)
    ci.set_ylim(-.6, .9)
    ci.set_xticks([0, 3, 6, 9, 12])
    ci.set_yticks([])
    ci.set_xlabel('FMMS 차이 (점), 95% 신뢰구간' if ko else 'FMMS points, 95% confidence interval', fontsize=10.7 if mobile else 12, color=INK)
    ci.spines[['top', 'left', 'right']].set_visible(False)
    ci.spines['bottom'].set_color(GRID)
    ci.set_facecolor(PAPER)
    ci.tick_params(axis='x', colors=INK, labelsize=11)
    ci.text(estimate, .45, f'+{estimate:.1f} [{low:.1f}, {high:.1f}]', ha='center', fontsize=13.5, color=TEAL, fontweight='bold')
    ci.text(estimate, -.32, f'p = {data["p"]:.3f}', ha='center', fontsize=11, color=MUTED)
    if mobile:
        notes = ('막대는 LS 평균만 표시. 95% 구간은\n개별 군이 아니라 두 군 차이의 구간이다.\n\n장애·활동 등 이차 지표는\n군간 통계적으로 유의한 차이 없음.\n6개월 중대한 이상사건 경험자:\nSB623 4/46명, 모의수술 2/15명.\n\n세포 이식 시험의 운동 평가이며\n해마 뉴런 탄생·기억 회복의 측정이 아니다.\n저자 보고값 · SanBio 지원 · 6개월 중간 분석' if ko else
                 'Bars show LS means only. The 95% interval\nis for the difference, not each group.\n\nSecondary disability / activity outcomes\nwere not significantly different.\nAt 6 months: serious adverse events\nin 4/46 (SB623) vs 2/15 (sham).\n\nMotor outcomes after cell implantation,\nnot hippocampal neuron birth or memory recovery.\nAuthor-reported · SanBio-funded · interim analysis')
        text(ax, 20, 208, notes, 10.7, MUTED)
    else:
        notes = ('막대는 LS 평균만 표시하며 95% 신뢰구간은 두 군 차이의 구간이다. 이차 장애·활동 지표는 군간 유의한 차이 없음.\n6개월 중대한 이상사건 경험자: SB623 4/46명, 모의수술 2/15명. 세포 이식의 운동 평가이며 해마 뉴런 탄생·기억 회복의 측정이 아니다.\nKawabori 외, Neurology (2021) 보고값의 새 도표 · SanBio 지원 · 6개월 중간 분석 · 환자 원자료 재분석 없음.' if ko else
                 'Bars show LS means only; the 95% interval is for the difference. Secondary disability / activity outcomes were not significantly different.\nPatients with serious adverse events at 6 months: SB623 4/46, sham 2/15. Motor outcomes do not measure hippocampal neuron birth or memory recovery.\nNew chart of Kawabori et al., Neurology (2021) reported values · SanBio-funded · 6-month interim analysis · no patient-data reanalysis.')
        text(ax, 30, 125, notes, 11.1, MUTED)
    save(fig, 'stemtra_results', lang, mobile)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--bold', type=Path, required=True)
    args = parser.parse_args()
    for font in [args.font, args.bold]:
        font_manager.fontManager.addfont(str(font))
    family = font_manager.FontProperties(fname=args.font).get_name()
    plt.rcParams.update({'font.family':family, 'font.size':13, 'text.color':INK,
                         'svg.fonttype':'path', 'svg.hashsalt':'brain-review-2026-10-30',
                         'axes.unicode_minus':False})
    PREVIEW.mkdir(parents=True, exist_ok=True)
    data = json.loads((ART / 'figure_data.json').read_text())
    clinical = json.loads((ART / 'stemtra_reported.json').read_text())
    for lang in ['ko', 'en']:
        for mobile in [False, True]:
            evidence_steps(lang, mobile, data)
            recovery_mechanisms(lang, mobile, data)
            stemtra_results(lang, mobile, clinical)
    print('Created 12 original outlined SVGs and local PNG previews.')


if __name__ == '__main__':
    main()
