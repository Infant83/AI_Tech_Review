"""Original bilingual, responsive HI-VQE workflow diagrams."""
from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FAMILY = "ReviewFigure,ReviewFigureSymbols,ReviewFigureMath,'Noto Sans KR',sans-serif"
INK = '#243d45'
MUTED = '#617275'

LABELS = {
    'en': {
        'title': 'A QPU proposes configurations; a classical solver sets their coefficients',
        'mobile_title': ['A QPU proposes configurations;', 'a classical solver sets coefficients'],
        'subtitle': 'Explanatory workflow for the 2026 HI-VQE formulation',
        'mobile_subtitle': 'HI-VQE: from samples to selected subspaces',
        'quantum': 'Quantum sampling', 'prepare': 'Prepare U(θ)|HF⟩',
        'samples': 'Computational-basis samples', 'classical': 'Classical processing',
        'recovery': 'Recover valid occupations', 'spin': 'Recombine spin configurations',
        'expansion': 'Expand and screen candidates', 'optional': 'Optional steps depend on the run',
        'current': 'Current-iteration subspace ', 'mobile_current': 'Current subspace ',
        'training': 'Diagonalize → training energy', 'training_note': 'Circuit update uses this track',
        'cumulative': 'Cumulative subspace ', 'mobile_cumulative': 'Cumulative subspace ',
        'reported': 'Diagonalize → reported energy', 'retained': 'Retain selected earlier configurations',
        'selection': 'Retain selected configurations', 'feedback': 'Classical update of θ',
        'mobile_feedback': 'Update θ',
        'integrals': 'Electronic integrals define the projected Hamiltonian',
        'mobile_integrals': 'Electronic integrals define H',
        'solver_note': 'The solver returns coefficients and energy in the chosen subspace.',
        'mobile_solver_note': 'Both spaces use the same integrals.',
        'footer': 'Conceptual diagram; arrows show information flow. No measured performance is plotted.',
        'mobile_footer': ['Conceptual workflow.', 'Arrows show information flow.'],
        'desc': 'The QPU proposes occupation strings. Classical recovery, spin recombination and expansion create candidate configurations. The current subspace supplies circuit-training feedback. Selected configurations are retained in the cumulative subspace, which supplies the reported energy. Both projected Hamiltonians use known electronic integrals.'
    },
    'ko': {
        'title': '양자 장치는 배치를 제안하고 고전 계산은 계수를 정한다',
        'mobile_title': ['양자는 배치를 제안하고', '고전 계산은 계수를 정한다'],
        'subtitle': '2026년 HI-VQE의 표본·부분공간·에너지 계산',
        'mobile_subtitle': 'HI-VQE: 표본에서 부분공간으로',
        'quantum': '양자 샘플링', 'prepare': 'U(θ)|HF⟩ 준비',
        'samples': '계산 기저에서 반복 측정', 'classical': '고전적 후보 처리',
        'recovery': '유효한 점유수로 회복', 'spin': '스핀별 배치를 다시 조합',
        'expansion': '후보를 확장하고 선별', 'optional': '설정에 따라 선택적으로 적용',
        'current': '현재 반복의 부분공간 ', 'mobile_current': '현재 반복의 공간 ',
        'training': '대각화 → 학습용 에너지', 'training_note': '이 경로로 회로를 갱신',
        'cumulative': '누적 부분공간 ', 'mobile_cumulative': '누적 공간 ',
        'reported': '대각화 → 보고 에너지', 'retained': '이전 반복의 선별 배치도 보존',
        'selection': '선별한 배치를 보존', 'feedback': '회로 매개변수 θ 갱신',
        'mobile_feedback': 'θ 갱신',
        'integrals': '전자 적분으로 투영 해밀토니안을 구성',
        'mobile_integrals': '전자 적분으로 투영 행렬 구성',
        'solver_note': '선택한 부분공간의 계수와 에너지를 구한다.',
        'mobile_solver_note': '두 공간 모두 같은 전자 적분을 사용',
        'footer': '리뷰가 작성한 개념도. 화살표는 정보의 흐름을 나타낸다.',
        'mobile_footer': ['리뷰가 작성한 개념도.', '화살표는 정보의 흐름을 나타낸다.'],
        'desc': '양자 장치가 점유 비트열을 제안한다. 고전적 회복·스핀 조합·확장으로 후보 배치를 구성한다. 현재 부분공간은 회로 학습의 피드백을 제공한다. 선별된 배치는 누적 부분공간에 보존되며 누적 공간은 보고 에너지를 제공한다. 두 투영 해밀토니안은 알려진 전자 적분으로 구성한다.'
    },
}


def text(x, y, value, size=21, weight=400, color=INK, extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" {extra}>{escape(value)}</text>'


def rich(x, y, value, size=22, weight=400, color=INK):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}">{value}</text>'


def sub(value, subscript, size=16):
    return escape(value) + f'<tspan baseline-shift="sub" font-size="{size}">{escape(subscript)}</tspan>'


def box(x, y, width, height, fill, stroke, radius=14):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'


def arrow(path, color='#6c8587', width=2.5, marker='arrow'):
    return f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{width}" marker-end="url(#{marker})"/>'


def start(lang, width, height):
    label = LABELS[lang]
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" xml:lang="{lang}">',
            f'<title id="title">{escape(label["title"])}</title>',
            f'<desc id="desc">{escape(label["desc"])}</desc>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#6c8587"/></marker><marker id="feedback-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#679885"/></marker></defs>',
            f'<rect width="{width}" height="{height}" rx="18" fill="#fcfaf5"/>',
            f'<g font-family="{FAMILY}" fill="{INK}">']


def desktop(lang):
    l = LABELS[lang]
    s = start(lang, 1200, 660)
    s += [text(40, 48, l['title'], 27, 700), text(40, 83, l['subtitle'], 19, color=MUTED),
          box(40, 150, 275, 245, '#f4e6ce', '#bb9868', 16),
          text(64, 188, l['quantum'], 23, 700), text(64, 231, l['prepare'], 22),
          text(65, 281, '1010…   0101…', 21, color='#7c5c31'),
          text(65, 315, '1001…   1010…', 21, color='#7c5c31'), text(64, 359, l['samples'], 17),
          arrow('M315 270H361', width=3),
          box(375, 150, 335, 245, '#edf1ee', '#86a696', 16),
          text(399, 188, l['classical'], 23, 700), text(399, 235, l['recovery'], 20),
          text(399, 273, l['spin'], 20), text(399, 311, l['expansion'], 20),
          text(399, 359, l['optional'], 18, color=MUTED),
          arrow('M710 270H742', width=3),
          box(770, 135, 390, 132, '#e4eeeb', '#679885'),
          rich(795, 173, escape(l['current']) + sub('S', 't'), 22, 700),
          text(795, 210, l['training']), text(795, 242, l['training_note'], 18),
          box(770, 300, 390, 132, '#e9eef4', '#8a9eb7'),
          rich(795, 338, escape(l['cumulative']) + sub('Ω', 't'), 22, 700),
          text(795, 375, l['reported']), text(795, 407, l['retained'], 18),
          arrow('M742 270V201H765', width=2), arrow('M742 270V366H765', width=2),
          arrow('M1130 270V296', width=2), text(806, 290, l['selection'], 16, color=MUTED),
          arrow('M960 135V108H178V145', '#679885', marker='feedback-arrow'),
          '<rect x="436" y="94" width="277" height="29" fill="#fcfaf5"/>',
          text(445, 115, l['feedback'], 18, color='#446f5e'),
          box(375, 479, 785, 120, '#f2f0e9', '#b9b7aa'),
          text(400, 516, l['integrals'], 22, 700),
          rich(400, 555, '(' + sub('H', 'S') + ')' + sub('', 'ij') + ' = ⟨' + sub('D', 'i') + '|H|' + sub('D', 'j') + '⟩', 24),
          rich(795, 555, sub('H', 'S') + ' c = ' + sub('E', 'S') + ' c', 24),
          text(400, 584, l['solver_note'], 18), arrow('M1020 479V439', width=2),
          text(40, 634, l['footer'], 17, color=MUTED)]
    return '\n'.join(s + ['</g></svg>']) + '\n'


def mobile(lang):
    l = LABELS[lang]
    s = start(lang, 480, 1300)
    s += [text(24, 43, l['mobile_title'][0], 25, 700), text(24, 78, l['mobile_title'][1], 25, 700),
          text(24, 111, l['mobile_subtitle'], 18, color=MUTED),
          box(72, 149, 384, 184, '#f4e6ce', '#bb9868', 16),
          text(96, 186, l['quantum'], 25, 700), text(96, 226, l['prepare'], 23),
          text(96, 268, '1010…  0101…  1001…', 22, color='#7c5c31'),
          text(96, 309, l['samples'], 20), arrow('M264 336V373'),
          box(72, 380, 384, 216, '#edf1ee', '#86a696', 16),
          text(96, 419, l['classical'], 25, 700), text(96, 461, l['recovery'], 22),
          text(96, 497, l['spin'], 22), text(96, 533, l['expansion'], 22),
          text(96, 574, l['optional'], 18, color=MUTED), arrow('M264 599V644'),
          box(72, 652, 384, 144, '#e4eeeb', '#679885'),
          rich(96, 690, escape(l['mobile_current']) + sub('S', 't'), 23, 700),
          text(96, 731, l['training'], 22), text(96, 769, l['training_note'], 20),
          arrow('M72 724H36V226H65', '#679885', marker='feedback-arrow'),
          text(22, 522, l['mobile_feedback'], 18, color='#446f5e', extra='transform="rotate(-90 22 522)" text-anchor="middle"'),
          arrow('M422 799V864', width=2), text(96, 838, l['selection'], 19, color=MUTED),
          box(72, 872, 384, 144, '#e9eef4', '#8a9eb7'),
          rich(96, 910, escape(l['mobile_cumulative']) + sub('Ω', 't'), 23, 700),
          text(96, 951, l['reported'], 22), text(96, 989, l['retained'], 18),
          box(72, 1064, 384, 150, '#f2f0e9', '#b9b7aa'),
          text(96, 1102, l['mobile_integrals'], 20, 700),
          rich(96, 1142, '(' + sub('H', 'S') + ')' + sub('', 'ij') + ' = ⟨' + sub('D', 'i') + '|H|' + sub('D', 'j') + '⟩', 24),
          rich(96, 1176, sub('H', 'S') + ' c = ' + sub('E', 'S') + ' c', 23),
          text(96, 1201, l['mobile_solver_note'], 17),
          text(24, 1250, l['mobile_footer'][0], 17, color=MUTED),
          text(24, 1277, l['mobile_footer'][1], 17, color=MUTED)]
    return '\n'.join(s + ['</g></svg>']) + '\n'


if __name__ == '__main__':
    for language in ['ko', 'en']:
        for is_mobile, draw in [(False, desktop), (True, mobile)]:
            filename = f'handover_workflow{"_mobile" if is_mobile else ""}_{language}.svg'
            (ROOT / filename).write_text(draw(language), encoding='utf-8')
            print(filename)
