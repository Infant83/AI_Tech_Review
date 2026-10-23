#!/usr/bin/env python3
"""Build compact bilingual figures for the independent deep review.

This is an editorial research-design schematic, not a measured model or a
completed safety evaluation. Geometry encodes the order of tests only.
"""
from build_figures import Diagram, BLUE, TEAL, ORANGE, MUTED, INK


def two_line_box(d, x, y, width, lines, color, fill='#ffffff'):
    d.rect(x, y, width, 74, fill=fill, stroke=color, radius=10)
    d.lines(x+width/2, y+29, lines, size=26, gap=32, weight=700, fill=color, anchor='middle')


def build(lang):
    ko = lang == 'ko'
    title = '읽고, 고치고, 다시 확인하기' if ko else 'Read, change, and check again'
    desc = ('리뷰의 연구 설계 제안. 같은 모델에서 행동을 찾고, 내부 설명이 새 입력을 예측하는지 시험한 뒤, 뉴런이나 회로에 개입하고 목표 행동과 정상 능력을 함께 재평가한다. 특정 성향 신호의 추적은 이미 보고되었다. 모델과 문맥이 바뀌어도 오탐과 누락을 평가하며 배포 감사를 지속하는 것은 후속 과제다. 관측과 개입의 성공만으로 안전을 보장할 수 없다. 화살표는 검사 순서이며 신경망 내부의 계산 연결이 아니다.' if ko else
            'Research design proposed by this review. Find a behavior, test an internal hypothesis on new inputs, intervene on units or circuits, and reassess both the target behavior and ordinary capabilities. Tracking specific trait signals has already been reported. Sustained deployment audits that measure false alarms and missed cases across model and context changes remain a further task. Readable explanations and successful edits do not establish safety. Arrows show test order, not computational connections inside a network.')
    d = Diagram(860, title, desc)
    d.text(40, 58, title, 39, 700)
    d.text(40, 105, '같은 모델·같은 과제에서 시험한 뒤, 새 버전에서 다시 묻는다.' if ko else 'Test one model and task; repeat when the model changes.', 26, fill=MUTED)

    panels = [
        (140, BLUE, '#edf3f8', '1 · 읽기: 설명이 새 예를 맞히는가?' if ko else '1 · Read: does the explanation predict new examples?',
         ['행동 패턴', '발견'] if ko else ['Find a', 'behavior pattern'],
         ['내부 가설 고정', '새 입력에서 시험'] if ko else ['Fix an internal hypothesis', 'test on new inputs'],
         '표현에 붙인 이름을 예측 가능한 주장으로 바꾼다.' if ko else 'Turn a label into a testable prediction.'),
        (350, ORANGE, '#fcf1e7', '2 · 수정: 목표 행동과 다른 능력이 어떻게 달라지는가?' if ko else '2 · Change: what improves, and what else changes?',
         ['뉴런·회로', '인과 개입'] if ko else ['Intervene on', 'units or circuits'],
         ['목표 행동 + 정상 능력', '함께 재평가'] if ko else ['Reassess target behavior', 'and ordinary capabilities'],
         '개입 전후와 대조 개입을 비교하고, 부작용도 찾는다.' if ko else 'Compare before/after and control edits; look for side effects.'),
        (560, TEAL, '#edf5f1', '3 · 추적: 연구에서 배포 감사로 잇는 조건' if ko else '3 · Track: from research signals to deployment audits',
         ['이미 보고된 연구', '특정 성향 신호 추적'] if ko else ['Already reported', 'track specific trait signals'],
         ['후속 과제: 버전·문맥 변화', '오탐·누락 평가하며 감사'] if ko else ['Next: audit across versions', 'measure false alarms / misses'],
         '모델·문맥이 바뀌면 행동·가설·개입을 다시 시험한다.' if ko else 'Repeat behavior, hypothesis and intervention tests after changes.'),
    ]
    for y, color, fill, heading, left, right, bottom in panels:
        d.rect(30, y, 940, 185, fill=fill, stroke=color, radius=16)
        d.text(55, y+39, heading, 28 if ko else 27, 700, color)
        two_line_box(d, 55, y+59, 330, left, color)
        two_line_box(d, 480, y+59, 465, right, color)
        d.line(404, y+96, 460, y+96, color, 3, True)
        d.text(55, y+165, bottom, 24, fill=INK)
    d.line(500, 330, 500, 343, MUTED, 3, True)
    d.line(500, 540, 500, 553, MUTED, 3, True)
    d.text(40, 792, '읽기·수정·안전 보장은 각각 새 검증이 필요한 주장이다.' if ko else 'Reading, editing and safety each require their own evidence.', 25, 700, INK)
    d.text(40, 834, '리뷰 재구성 · Persona Vectors 등에서 출발한 연구·평가 순서의 제안.' if ko else 'Review reconstruction · test design informed by Persona Vectors and related work.', 24, fill=MUTED)
    d.save(f'circuits-to-engineering-{lang}.svg')


def reasoning(lang):
    ko = lang == 'ko'
    title = '중간 계산을 바꾸면 답도 바뀔까?' if ko else 'Changing the middle changes the answer'
    desc = ('Anthropic 2025 Claude 3.5 Haiku 사례의 교육 재구성. Dallas가 속한 주의 주도를 묻는 원 입력에 Austin을 답한다. 연구자는 CLT로 찾은 Texas 관련 특징군을 억제하고 Oakland 입력에서 찾은 California 관련 특징군을 활성화하여, Dallas 입력을 유지한 채 Sacramento 출력을 보고했다. 특징군은 단일 뉴런이 아니다. Dallas에서 Austin으로 향하는 지름길도 공존한다. 화살표는 보고된 관계의 요약이며 실제 뉴런·가중치·전체 배선이 아니다.' if ko else
            'Educational reconstruction of an Anthropic 2025 case in Claude 3.5 Haiku. The model completes a prompt asking for the capital of the state containing Dallas with Austin. Researchers suppress Texas-related features found with a cross-layer transcoder and activate California-related features identified from an Oakland prompt. Keeping the Dallas input, they report a Sacramento output. Feature groups are not single neurons. A Dallas-to-Austin shortcut also coexists. Arrows summarize reported relationships, not actual neurons, weights or complete wiring.')
    d = Diagram(850, title, desc)
    d.text(40, 60, title, 39 if ko else 37, 700)
    d.text(40, 107, 'Claude 3.5 Haiku · “Dallas가 속한 주의 주도는?”에 해당하는 입력' if ko else 'Claude 3.5 Haiku · prompt asks for the capital of the state containing Dallas', 26 if ko else 24, fill=MUTED)

    d.rect(30, 140, 940, 220, fill='#edf3f8', stroke=BLUE, radius=16)
    d.text(55, 182, '1 · 읽기: 내부 계산에 대한 가설' if ko else '1 · Read: a hypothesis about an internal computation', 30 if ko else 29, 700, BLUE)
    for x, heading in [(60, '도시 입력' if ko else 'City input'), (355, '중간 특징군' if ko else 'Intermediate features'), (760, '출력' if ko else 'Output')]:
        d.text(x, 222, heading, 25, fill=MUTED)
    d.rect(55, 237, 195, 74, fill='#ffffff', stroke=BLUE, radius=10)
    d.text(152, 285, 'Dallas', 33, 700, BLUE, 'middle')
    d.rect(350, 237, 310, 74, fill='#ffffff', stroke=BLUE, radius=10)
    d.text(505, 285, 'Texas', 33, 700, BLUE, 'middle')
    d.rect(755, 237, 190, 74, fill='#ffffff', stroke=BLUE, radius=10)
    d.text(850, 285, 'Austin', 33, 700, BLUE, 'middle')
    d.line(269, 274, 330, 274, BLUE, 3, True)
    d.line(680, 274, 735, 274, BLUE, 3, True)
    d.text(55, 340, '분석에는 “주도” 단서와 Dallas→Austin 지름길도 함께 나타난다.' if ko else 'Capital-related features and a Dallas-to-Austin shortcut also contribute.', 24, fill=INK)

    d.rect(30, 390, 940, 280, fill='#fcf1e7', stroke=ORANGE, radius=16)
    d.text(55, 434, '2 · 개입: 같은 질문, 바꾼 중간 표현' if ko else '2 · Intervene: same prompt, altered intermediate features', 30 if ko else 29, 700, ORANGE)
    d.text(55, 477, '입력 유지' if ko else 'Input held fixed', 25, fill=MUTED)
    d.text(355, 477, 'CLT로 찾은 특징군에 개입' if ko else 'Intervene on CLT features', 25 if ko else 24, fill=MUTED)
    d.text(760, 477, '보고된 출력' if ko else 'Reported output', 25, fill=MUTED)
    d.rect(55, 493, 195, 102, fill='#ffffff', stroke=ORANGE, radius=10)
    d.text(152, 554, 'Dallas', 33, 700, ORANGE, 'middle')
    two_line_box(d, 350, 507, 310, ['Texas 억제', 'California 활성화'] if ko else ['Suppress Texas', 'Activate California'], ORANGE)
    d.rect(755, 493, 190, 102, fill='#ffffff', stroke=ORANGE, radius=10)
    d.text(850, 553, 'Sacramento', 27, 700, ORANGE, 'middle')
    d.line(269, 545, 330, 545, ORANGE, 3, True)
    d.line(680, 545, 735, 545, ORANGE, 3, True)
    d.text(55, 640, 'California 관련 특징은 별도의 Oakland 입력에서 찾아 사용했다.' if ko else 'California features were identified using a separate Oakland prompt.', 24, fill=INK)

    d.text(40, 717, '판단: 이 조건에서 중간 표현이 답을 바꾸는 데 인과적으로 관여했다.' if ko else 'Finding: the intermediate representation causally affected this answer.', 25 if ko else 24, 700)
    d.lines(40, 758, ['CLT 기반 분석 · Anthropic(2025) 저자 보고의 교육 재구성.', '화살표는 관계의 요약이다. 특징군은 단일 뉴런이 아니며 전체 배선이 아니다.'] if ko else ['CLT-based analysis · educational reconstruction of Anthropic (2025).', 'Arrows summarize reported relationships.', 'Feature groups are not single neurons or complete wiring.'], 24, 37, fill=MUTED)
    d.save(f'city-circuit-intervention-{lang}.svg')


if __name__ == '__main__':
    for language in ('ko', 'en'):
        build(language)
        reasoning(language)
    print('Built four compact bilingual SVGs; text ≥24 px.')
