"""Original, bilingual figures from explicitly supplied review data.

All chart values come from the adjacent JSON files. SVG text is outlined for
portable rendering. Supply openly licensed font files through CLI arguments.
"""
from pathlib import Path
import argparse
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
PREVIEW = ROOT / 'tmp' / 'figures'
INK = '#17343e'
TEAL = '#087c83'
BLUE = '#4e6dac'
OCHRE = '#ba6b35'
MUTED = '#63756f'
GRID = '#d8e1dc'
PAPER = '#faf8f2'


def canvas(width, height):
    fig = plt.figure(figsize=(width / 72, height / 72), facecolor=PAPER)
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, width), ylim=(0, height))
    ax.axis('off')
    return fig, ax


def text(ax, x, y, value, size=13, color=INK, weight='normal', **kwargs):
    return ax.text(x, y, value, fontsize=size, color=color, fontweight=weight,
                   va=kwargs.pop('va', 'top'), linespacing=1.35, **kwargs)


def box(ax, x, y, width, height, title, body='', color=TEAL,
        title_size=14, body_size=12.5):
    ax.add_patch(FancyBboxPatch((x, y), width, height,
                 boxstyle='round,pad=0,rounding_size=6', facecolor='white',
                 edgecolor=color, linewidth=1.25))
    text(ax, x + width / 2, y + height - 13, title, title_size, color,
         ha='center', weight='bold')
    if body:
        text(ax, x + width / 2, y + height - 39, body, body_size, ha='center')


def arrow(ax, points, color=MUTED, dashed=False, lw=1.15):
    if len(points) > 2:
        ax.plot([p[0] for p in points[:-1]], [p[1] for p in points[:-1]],
                color=color, linewidth=lw, linestyle=(0, (3, 3)) if dashed else '-')
    ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle='-|>',
                 mutation_scale=9, linewidth=lw, color=color,
                 linestyle=(0, (3, 3)) if dashed else '-'))


def save(fig, stem, lang, mobile):
    name = f'{stem}{"_mobile" if mobile else ""}_{lang}'
    fig.savefig(ART / f'{name}.svg', metadata={
        'Date': None, 'Creator': 'AI Tech Review deterministic figure builder',
        'Description': 'Original explanatory figure; evidence scope is stated in the figure and caption.'})
    svg_file = ART / f'{name}.svg'
    svg_file.write_text('\n'.join(line.rstrip() for line in svg_file.read_text().splitlines()) + '\n')
    fig.savefig(PREVIEW / f'{name}.png', dpi=140)
    plt.close(fig)


def program_paths(lang, mobile):
    ko = lang == 'ko'
    if ko:
        title = '두 접근은 어디에서 선택을 미루는가'
        sub = '실선: 프로그램 변환   점선: 도구 호출·검사 피드백'
        agent = ('AI 에이전트', '양쪽 경로의 도구를 선택·호출')
        checks = ('명세·출력 검사', '검사 결과를 받아 수정\n의도에 맞는지는 별도 확인')
        rows = [
            ('Classiq / Qmod', [
                ('의도 + 자원 제약', 'Qmod 명세\n예: 최대 회로 폭'),
                ('합성', '구현 후보를 선택·조합\n제약 안에서 자원 탐색'),
                ('고수준 양자 프로그램', '선택한 구현·자원 배치\n함수 계층·상징 제어 유지'),
                ('하위 변환·실행', '설정한 하위 변환\n기저·배치·라우팅')]),
            ('Qiskit', [
                ('고수준 블록·회로', '연산 객체와 회로\n보조 큐비트 정보'),
                ('HLS + Target', '고수준 합성·pass 선택\n타깃 연산·연결 정보'),
                ('하위 회로 변환', '기저 변환·배치·라우팅\nTarget에 맞춤'),
                ('실행', '시뮬레이터·백엔드\n결과와 제약을 확인')])]
        foot = '설명 도식. 닫힌 진영이 아니며 연동·혼합이 가능하다. 전역 최적성·사용자 의도를 자동 보장하지 않는다.\n하위 변환은 설정한 변환·실행 단계를 요약한다. 기본 export가 항상 회로 변환을 수행하는 것은 아니다.'
    else:
        title = 'Where do the two approaches defer choices?'
        sub = 'Solid: program transformations   Dashed: tool calls and check feedback'
        agent = ('AI agent', 'Selects and calls tools in either approach')
        checks = ('Specification and output checks', 'Feedback supports revision;\nuser intent still needs checking')
        rows = [
            ('Classiq / Qmod', [
                ('Intent + limits', 'Qmod specification\ne.g. maximum circuit width'),
                ('Synthesis', 'Choose and combine\nimplementation options'),
                ('High-level program', 'Selected implementation\nResources allocated; hierarchy\nand symbolic control retained'),
                ('Lowering + execution', 'Configured transforms\nBasis, layout and routing')]),
            ('Qiskit', [
                ('High-level blocks', 'Operations and circuit\nAncilla information'),
                ('HLS + Target', 'Synthesis / passes\nTarget ops / connectivity'),
                ('Circuit transforms', 'Basis, layout, routing\nfor the selected Target'),
                ('Execution', 'Simulator or backend\nCheck results and limits')])]
        foot = 'Explanatory diagram. Open, interoperable approaches; no global optimum or intent-correctness guarantee.\nLowering summarizes configured transforms and execution; plain export does not always transpile.'
    if not mobile:
        fig, ax = canvas(864, 540)
        text(ax, 30, 518, title, 22, weight='bold')
        text(ax, 30, 483, sub, 12, MUTED)
        box(ax, 228, 404, 408, 54, agent[0], agent[1], title_size=14, body_size=12.5)
        xs = [46, 241, 436, 631]
        for index, (name, cards) in enumerate(rows):
            y = 270 if index == 0 else 128
            text(ax, 46, y + 123, name, 15, weight='bold')
            for column, (heading, body) in enumerate(cards):
                box(ax, xs[column], y, 173, 96, heading, body,
                    TEAL if index == 0 else BLUE, title_size=12.4,
                    body_size=11.2 if not ko and index == 0 and column == 2 else 12.1)
                if column < 3:
                    arrow(ax, [(xs[column] + 175, y + 48), (xs[column + 1] - 3, y + 48)])
            arrow(ax, [(228, 431), (18, 431), (18, y + 48), (44, y + 48)], BLUE, True)
            arrow(ax, [(806, y + 48), (839, y + 48), (839, 61), (637, 61)], OCHRE, True)
        box(ax, 228, 35, 408, 54, checks[0], checks[1].replace('\n', ' · ') if ko else
            'Check results drive revision; intent needs tests',
            OCHRE, title_size=14, body_size=11.3)
        arrow(ax, [(228, 61), (4, 61), (4, 449), (226, 449)], OCHRE, True)
        text(ax, 30, 28, foot, 10.8, MUTED)
    else:
        fig, ax = canvas(342, 1122)
        mobile_title = '두 접근의 프로그램 변환' if ko else 'Two routes for program\ntransformation'
        text(ax, 20, 1101, mobile_title, 17, weight='bold')
        text(ax, 20, 1049, '실선: 변환  /  점선: 호출·검사' if ko else 'Solid: transforms / dashed: calls, checks', 10.8, MUTED)
        box(ax, 36, 946, 270, 74, agent[0],
            '양쪽 도구 호출 · 검사 뒤 수정' if ko else 'Calls tools in either approach;\nrevises using check feedback',
            title_size=14, body_size=12)
        for index, (name, cards) in enumerate(rows):
            top = 830 if index == 0 else 434
            text(ax, 36, top + 108, name, 15, weight='bold')
            for i, (heading, body) in enumerate(cards):
                y = top - i * 86 - (16 if index == 0 and i >= 2 else 0)
                heading = heading.replace(' + ', ' +\n') if len(heading) > 26 else heading
                height = 88 if index == 0 and i == 2 else 72
                box(ax, 36, y, 270, height, heading, body,
                    TEAL if index == 0 else BLUE, title_size=12.4, body_size=12)
                if i < 3:
                    arrow(ax, [(171, y - 1), (171, y - 12)])
            arrow(ax, [(306, 982), (329, 982), (329, top + 36), (308, top + 36)], BLUE, True)
        box(ax, 36, 60, 270, 70, checks[0], checks[1], OCHRE,
            title_size=12.5, body_size=11.7)
        for y in [592, 212]:
            arrow(ax, [(36, y), (20, y), (20, 95), (34, 95)], OCHRE, True)
        arrow(ax, [(36, 95), (5, 95), (5, 982), (34, 982)], OCHRE, True)
        text(ax, 20, 44, '연동 가능. 전역 최적·의도 정확 보장 아님.\n하위 변환: 설정한 변환·실행 단계.\n기본 export가 항상 변환을 수행하진 않음.' if ko else
             'Interoperable; no global or intent guarantee.\nLowering: configured transforms / execution.\nPlain export does not always transpile.', 10.2, MUTED)
        ax.set_ylim(-24, 1122)
    save(fig, 'program_paths', lang, mobile)


def style_plot(ax, ylabel, size=12):
    ax.set_facecolor(PAPER)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color(GRID)
    ax.tick_params(colors=INK, labelsize=size, length=3, color=MUTED)
    ax.yaxis.grid(True, color=GRID, linewidth=.7)
    ax.set_axisbelow(True)
    ax.set_ylabel(ylabel, fontsize=size, color=INK)


def oracle_semantics(lang, mobile, data):
    ko = lang == 'ko'
    title = '같이 유니터리여도 같은 문제를 풀지는 않는다' if ko else 'Unitary does not mean the intended problem'
    cases = data['cases']
    assert data['intended_answer'] == '101' and data['iterations'] == 1
    for case in cases:
        assert math.isclose(sum(case['after_one_iteration_probabilities']), 1, abs_tol=1e-12)
        assert all(math.isclose(p, 1 / 8, abs_tol=1e-12) for p in case['after_oracle_probabilities'])
        expected = [25 / 32 if x == case['marked_basis'] else 1 / 32 for x in case['basis']]
        assert all(math.isclose(x, y, abs_tol=1e-12) for x, y in zip(expected, case['after_one_iteration_probabilities']))
        assert case['oracle_unitarity_error'] == 0
    if not mobile:
        fig, ax = canvas(864, 468)
        text(ax, 30, 446, title, 21, weight='bold')
        text(ax, 30, 410, '의도한 정답 101 · 3큐비트 · 균등 중첩 입력 · 이상적 무잡음 계산' if ko else
             'Intended answer 101 · 3 qubits · uniform-superposition input · ideal noiseless calculation', 13, MUTED)
        box(ax, 30, 328, 804, 55,
            '두 위상 오라클 모두 U†U = I' if ko else 'Both phase oracles satisfy U†U = I',
            '오라클 직후 바로 측정하면 두 경우 모두 모든 비트열이 1/8' if ko else
            'Measure immediately after the oracle: every bit string has probability 1/8 in both cases',
            title_size=14, body_size=12.5)
        plot_rects = [[.085, .21, .37, .34], [.57, .21, .37, .34]]
        head_y = 310
    else:
        fig, ax = canvas(342, 990)
        text(ax, 20, 968, '유니터리 검사만으로는\n의도한 답을 확인할 수 없다' if ko else
             'Unitarity alone cannot\ncheck the intended answer', 17, weight='bold')
        text(ax, 20, 910, '의도한 답 101 · 3큐비트 · 균등 입력' if ko else
             'Intended answer 101 · 3 qubits\nUniform-superposition input', 11.7, MUTED)
        box(ax, 20, 778, 302, 86,
            '두 오라클 모두 유니터리' if ko else 'Both oracles are unitary',
            '위상만 바꾼 직후 측정:\n두 경우 모두 모든 비트열이 1/8' if ko else
            'Measure just after the phase flip:\nall bit strings have probability 1/8\nin both cases',
            title_size=13, body_size=11.5)
        plot_rects = [[.16, .475, .78, .205], [.16, .16, .78, .205]]
        head_y = 742
    for index, (case, rect) in enumerate(zip(cases, plot_rects)):
        color = TEAL if index == 0 else OCHRE
        mark = case['marked_basis']
        x_heading = 75 if not mobile and index == 0 else 494 if not mobile else 20
        y_heading = head_y if not mobile else head_y - index * 312
        label = ('명세 101: 101의 위상 반전' if ko else 'Mark 101: intended specification') if index == 0 else (
                 '명세 오류: 111의 위상 반전' if ko else 'Mark 111: wrong specification')
        text(ax, x_heading, y_heading, label, 14 if not mobile else 13.6, color, weight='bold')
        prob = 100 * case['intended_answer_probability']
        text(ax, x_heading, y_heading - 25,
             f'의도한 101의 확률 {prob:.3f}%' if ko else f'P(intended 101) = {prob:.3f}%',
             13 if not mobile else 12.6, color)
        chart = fig.add_axes(rect)
        values = [100 * p for p in case['after_one_iteration_probabilities']]
        colors = [color if x == mark else '#c7d3cf' for x in case['basis']]
        bars = chart.bar(range(8), values, color=colors, width=.72, zorder=3)
        bars[5].set_edgecolor(TEAL)
        bars[5].set_linewidth(1.6)
        chart.set_xticks(range(8), case['basis'], rotation=0, fontsize=10.3 if mobile else 11)
        chart.set_ylim(0, 91)
        chart.set_yticks([0, 25, 50, 75], ['0', '25', '50', '75'])
        style_plot(chart, '확률 (%)' if ko else 'Probability (%)', 11 if mobile else 12)
        chart.set_xlabel('비트열 (q2 q1 q0)' if ko else 'Bit string (q2 q1 q0)', fontsize=11, color=INK)
        peak = case['basis'].index(mark)
        chart.text(peak, values[peak] + 3, '25/32', ha='center', fontsize=12, color=color, fontweight='bold')
        note = ('나머지 각각 1/32' if ko else 'Each other state: 1/32') if not mobile else (
                '나머지 각각\n1/32' if ko else 'Each other state:\n1/32')
        chart.text(.1 if mobile else 1.4, 14 if mobile else 10, note,
                   ha='left', fontsize=10.2 if mobile else 10.5, color=MUTED)
    if not mobile:
        text(ax, 30, 58, '한 번의 Grover 반복 후 결과. 테두리는 의도한 정답 101을 가리킨다.\n리뷰의 NumPy 교육 계산이며 QPU 실행·공급자 성능·LLM 벤치마크가 아니다.' if ko else
             'After one Grover iteration. The outlined bar marks intended answer 101.\nReview-created NumPy teaching calculation; not QPU execution, a vendor benchmark or an LLM benchmark.', 11.6, MUTED)
    else:
        text(ax, 20, 90, '한 번의 Grover 반복 뒤 확률.\n테두리: 의도한 정답 101.\n리뷰의 NumPy 교육 계산.\nQPU·공급자·LLM 벤치마크 아님.' if ko else
             'Probabilities after one Grover iteration.\nOutline: intended answer 101.\nReview-created NumPy teaching calculation.\nNot a QPU, vendor or LLM benchmark.', 11, MUTED)
    save(fig, 'oracle_semantics', lang, mobile)


def synthesis_tradeoff(lang, mobile, data):
    ko = lang == 'ko'
    rows = data['reported_results']
    assert [(r['maximum_width_qubits'], r['actual_width_qubits'], r['cx_count']) for r in rows] == [(45, 44, 1480), (90, 47, 842)]
    w, h = (342, 660) if mobile else (864, 468)
    fig, ax = canvas(w, h)
    text(ax, 20 if mobile else 30, h - 22,
         ('폭 제약을 바꾸자\n선택된 회로가 달라졌다' if mobile else '폭 제약을 바꾸자 선택된 회로가 달라졌다') if ko else
         ('A width limit changes\nthe selected circuit' if mobile else 'A width limit changes the selected circuit'),
         17 if mobile else 22, weight='bold')
    text(ax, 20 if mobile else 30, h - (78 if mobile else 58),
         '저자 보고값 · 논리 CX 게이트 수' if ko else 'Author-reported logical CX gate counts', 11.7 if mobile else 13, MUTED)
    chart = fig.add_axes([.19, .35, .76, .43] if mobile else [.12, .31, .82, .44])
    bars = chart.bar([0, 1], [r['cx_count'] for r in rows], width=.47, color=[BLUE, TEAL], zorder=3)
    chart.set_ylim(0, 1780)
    chart.set_xlim(-.6, 1.6)
    chart.set_yticks([0, 500, 1000, 1500])
    labels = [f'폭 상한 {r["maximum_width_qubits"]}\n실제 폭 {r["actual_width_qubits"]}' if ko else
              f'Width cap {r["maximum_width_qubits"]}\nActual width {r["actual_width_qubits"]}' for r in rows]
    chart.set_xticks([0, 1], labels)
    style_plot(chart, '논리 CX 수' if ko else 'Logical CX count', 11.5 if mobile else 14)
    for bar, row in zip(bars, rows):
        chart.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 55,
                   f'{row["cx_count"]:,}', ha='center', fontsize=17 if mobile else 20, fontweight='bold', color=INK)
    if mobile:
        foot = ('N = 20: 행렬 크기는 2^20 × 2^20.\nN은 회로의 총 큐비트 수가 아니다.\n\nClassiq 0.60.0, 저자 Figure 3(b,c).\n두 점만 표시했으며 곡선·최적 경계가 아니다.\n\n리뷰에서 합성을 독립 실행하지 않았다.\n현재 버전·타 플랫폼 비교·QPU 성능이나\n양자우위를 입증하는 결과가 아니다.' if ko else
                'N = 20: matrix size is 2^20 × 2^20.\nN is not the total circuit-qubit count.\n\nClassiq 0.60.0, authors’ Figure 3(b,c).\nOnly two points, not a curve or optimal frontier.\n\nSynthesis was not independently run here.\nNot a current-version or cross-platform\nbenchmark, QPU result or quantum advantage.')
        text(ax, 20, 180, foot, 11.1, MUTED)
    else:
        foot = ('N = 20는 행렬 크기 2^20 × 2^20의 지수이며 총 회로 큐비트 수가 아니다.\nClassiq 0.60.0의 저자 보고 결과, Figure 3(b,c). 두 점은 완전한 최적 경계를 정의하지 않는다.\n독립 합성 미실행. 현행 버전·타 플랫폼·물리 QPU 성능이나 양자우위를 비교한 벤치마크가 아니다.' if ko else
                'N = 20 sets the matrix size, 2^20 × 2^20; it is not the total circuit-qubit count.\nAuthor-reported Classiq 0.60.0 results, Figure 3(b,c). Two points do not define a full optimal frontier.\nNot independently synthesized here; not a current-version, cross-platform, physical-QPU or quantum-advantage benchmark.')
        text(ax, 30, 88, foot, 11.7, MUTED)
    save(fig, 'synthesis_tradeoff', lang, mobile)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', type=Path, required=True, help='Openly licensed regular TTF font')
    parser.add_argument('--bold', type=Path, required=True, help='Matching bold TTF font')
    args = parser.parse_args()
    for p in [args.font, args.bold]:
        font_manager.fontManager.addfont(str(p))
    family = font_manager.FontProperties(fname=args.font).get_name()
    plt.rcParams.update({'font.family':family, 'font.size':13, 'text.color':INK,
                         'svg.fonttype':'path', 'svg.hashsalt':'ai-tech-review-quantum-software-2026-10-25',
                         'axes.unicode_minus':False})
    PREVIEW.mkdir(parents=True, exist_ok=True)
    oracle = json.loads((ART / 'oracle_results.json').read_text())
    synthesis = json.loads((ART / 'synthesis_reported.json').read_text())
    for lang in ['ko', 'en']:
        for mobile in [False, True]:
            program_paths(lang, mobile)
            oracle_semantics(lang, mobile, oracle)
            synthesis_tradeoff(lang, mobile, synthesis)
    print('Created 12 original outlined SVG figures and local PNG previews.')


if __name__ == '__main__':
    main()
