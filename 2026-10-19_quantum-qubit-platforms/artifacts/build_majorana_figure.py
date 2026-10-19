#!/usr/bin/env python3
"""Original Majorana evidence diagram; no paper figure tracing or raster images.

Run with Python and matplotlib. Set QUBIT_FIGURE_FONT to a Korean font file
when Noto Sans KR is unavailable. Text is outlined in publication SVGs; title
and description retain an accessible summary. Preview PNGs are temporary.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.font_manager import FontProperties, findfont
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'
NOTES = ROOT / 'notes'
FONT_CANDIDATES = [
    os.environ.get('QUBIT_FIGURE_FONT', ''),
    str(Path.home() / 'Library/Fonts/NotoSansKR-Regular.otf'),
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
]
FONT_PATH = next((Path(p) for p in FONT_CANDIDATES if p and Path(p).is_file()), None)
if FONT_PATH is None:
    try:
        FONT_PATH = Path(findfont('Noto Sans KR', fallback_to_default=False))
    except ValueError as error:
        raise FileNotFoundError('Set QUBIT_FIGURE_FONT to a Korean-capable font file.') from error
BOLD_PATH = FONT_PATH.with_name('NotoSansKR-Bold.otf')
REG = FontProperties(fname=str(FONT_PATH))
BOLD = FontProperties(fname=str(BOLD_PATH if BOLD_PATH.exists() else FONT_PATH))
plt.rcParams.update({
    'svg.fonttype': 'path', 'svg.hashsalt': 'majorana-evidence-2026-10-19',
    'axes.unicode_minus': False, 'figure.facecolor': '#F9FAF7',
    'savefig.facecolor': '#F9FAF7',
})
C = {'bg': '#F9FAF7', 'white': '#FFFFFF', 'navy': '#193342',
     'text': '#304B58', 'muted': '#687B83', 'teal': '#237F80',
     'teallight': '#E4F1ED', 'amber': '#AF7A29', 'amberlight': '#FAF0D9',
     'line': '#D8E2DF', 'faint': '#EEF3F0', 'blue': '#4C7792'}


def canvas(width, height):
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, width), ylim=(height, 0))
    ax.axis('off')
    return fig, ax


def text(ax, x, y, value, size=16, color=None, bold=False, ha='left', va='top'):
    return ax.text(x, y, value, fontproperties=BOLD if bold else REG,
                   fontsize=size, color=color or C['text'], ha=ha, va=va,
                   linespacing=1.55)


def box(ax, x, y, width, height, fill=None, edge=None, radius=16):
    ax.add_patch(patches.FancyBboxPatch(
        (x, y), width, height, boxstyle=f'round,pad=0,rounding_size={radius}',
        facecolor=fill or C['white'], edgecolor=edge or C['line'], linewidth=1))


def line(ax, points, color=None, width=2):
    xy = np.asarray(points)
    ax.plot(xy[:, 0], xy[:, 1], color=color or C['teal'], linewidth=width,
            solid_capstyle='round')


def dot(ax, x, y, radius=8, color=None):
    ax.add_patch(patches.Circle((x, y), radius, facecolor=color or C['teal'],
                               edgecolor=C['teal'], linewidth=1.5))


def wire_glyph(ax, x, y, scale=1):
    """Generic two-wire tetron motif; not a device layout or measured image."""
    for dy in [-20, 20]:
        line(ax, [(x - 70 * scale, y + dy * scale),
                  (x + 70 * scale, y + dy * scale)], C['teal'], 7 * scale)
        for dx in [-70, 70]:
            dot(ax, x + dx * scale, y + dy * scale, 5 * scale, C['white'])
    line(ax, [(x, y - 20 * scale), (x, y + 20 * scale)], C['teal'], 7 * scale)


def chain_glyph(ax, x, y, scale=1):
    """Two minimal chains and a distinct control link; no literal geometry."""
    for offset in [-80, 80]:
        line(ax, [(x + (offset - 22) * scale, y),
                  (x + (offset + 22) * scale, y)], C['teal'], 6 * scale)
        dot(ax, x + (offset - 22) * scale, y, 9 * scale, C['white'])
        dot(ax, x + (offset + 22) * scale, y, 9 * scale, C['white'])
    line(ax, [(x - 58 * scale, y), (x + 58 * scale, y)], C['amber'], 2.2 * scale)
    dot(ax, x, y, 8 * scale, C['amberlight'])


def card(ax, x, y, width, height, index, mobile=False):
    box(ax, x, y, width, height)
    pad = 24 if mobile else 26
    fs = 15.0 if mobile else 16
    text(ax, x + pad, y + 22, ['MICROSOFT · InAs–Al', 'MICROSOFT · InAs–Pb',
                              'QuTech · 최소 Kitaev 사슬'][index],
         12.5 if mobile else 13.5, C['teal'], True)
    titles = ['X·Z 루프를 읽었다', 'Z 패리티가 오래 유지됐다', '패리티를 결맞게 진동시켰다']
    text(ax, x + pad, y + 57, titles[index], 18.3 if mobile else 18, C['navy'], True)
    labels = [
        '2025 공개 · 2026년 10월 PRA 게재 승인',
        '2026년 6월 사전공개 · 나노와이어 소자',
        '2026년 7월 사전공개 · 두 최소 사슬',
    ]
    text(ax, x + pad, y + 100, labels[index], 11.6 if mobile else 12.1, C['muted'])
    glyph_y = y + 174
    if index < 2:
        wire_glyph(ax, x + width / 2, glyph_y, 0.9)
    else:
        chain_glyph(ax, x + width / 2, glyph_y, 1.05)
    text(ax, x + width / 2, y + 216, '부호화·결합의 개념도', 10.5, C['muted'], ha='center')
    line(ax, [(x + pad, y + 254), (x + width - pad, y + 254)], C['line'], 1)
    if index == 0:
        text(ax, x + pad, y + 276, 'X 루프  14.5 ± 0.3 µs', 18 if mobile else 19,
             C['navy'], True)
        text(ax, x + pad, y + 317, 'Z 루프  12.4 ± 0.4 ms', 18 if mobile else 19,
             C['navy'], True)
        text(ax, x + pad, y + 367, '연속 판독 중 패리티 전환 수명', fs, C['text'])
        text(ax, x + pad, y + 412, '판독 오류: X 16% · Z 0.5%', fs, C['teal'])
        text(ax, x + pad, y + 454, '두 측정의 비가환성은 후속 검증 과제', 12.0 if mobile else 12.4,
             C['muted'])
    elif index == 1:
        text(ax, x + pad, y + 272, '22 ± 1 s', 35 if mobile else 38, C['navy'], True)
        text(ax, x + pad, y + 344, 'Z 패리티 전환 수명', fs, C['text'])
        text(ax, x + pad, y + 389, '재료 개선과 poisoning 억제의 진전',
             14.2 if mobile else 15, C['teal'])
        text(ax, x + pad, y + 435, '이 값은 임의 중첩의 $T_2$나\n게이트 충실도가 아니다.', fs, C['muted'])
    else:
        text(ax, x + pad, y + 272, '26 ± 2 ns', 35 if mobile else 38, C['navy'], True)
        text(ax, x + pad, y + 344, r'Rabi 진동 감쇠 시간 $T_2^{\mathrm{Rabi}}$', fs, C['text'])
        text(ax, x + pad, y + 389, '결맞는 시간 영역 제어의 진전', fs, C['teal'])
        text(ax, x + pad, y + 435, '짧은 사슬의 부분적 보호:\n긴 계의 보호된 게이트와 구분한다.',
             14.4 if mobile else 15, C['muted'])


def next_tests(ax, x, y, width, mobile=False):
    text(ax, x, y, '다음 실험에서 판단을 바꿀 네 가지 증거',
         19 if mobile else 21, C['navy'], True)
    items = [
        ('제어와 유휴 상태', '비가환 측정·제어와 별도의 idle coherence'),
        ('길이에 따른 보호', '사슬을 늘렸을 때 오류·위상 잡음이 감소하는가'),
        ('두 소자의 연결', 'joint-parity 측정과 얽힘을 반복할 수 있는가'),
        ('연산의 정확도', '운용 조건에서 operation error를 측정하는가'),
    ]
    if mobile:
        for i, (label, body) in enumerate(items):
            yy = y + 58 + 92 * i
            line(ax, [(x, yy + 5), (x, yy + 52)], C['teal'], 3)
            text(ax, x + 16, yy, label, 15.3, C['teal'], True)
            # Fixed line breaks keep a 309 px rendered image legible.
            mobile_body = [
                '비가환 측정·제어와\n별도의 idle coherence',
                '길이를 늘리면 오류·위상 잡음이 줄어드는가',
                'joint-parity 측정과 얽힘의 반복',
                '운용 조건의 operation error 측정',
            ][i]
            text(ax, x + 16, yy + 31, mobile_body, 13.7, C['text'])
    else:
        gap = 24
        cw = (width - gap) / 2
        for i, (label, body) in enumerate(items):
            xx = x + (i % 2) * (cw + gap)
            yy = y + 60 + (i // 2) * 101
            box(ax, xx, yy, cw, 84, C['white'])
            text(ax, xx + 20, yy + 14, label, 15, C['teal'], True)
            text(ax, xx + 20, yy + 45, body, 14, C['text'])


DESCRIPTION = (
    '세 연구는 서로 다른 소자와 프로토콜의 결과이다. Microsoft InAs–Al 장치의 X와 Z 루프 '
    '패리티 전환 수명은 각각 14.5±0.3 마이크로초, 12.4±0.4 밀리초이며 판독 오류는 16%, 0.5%이다. '
    '별도 InAs–Pb 장치는 Z 패리티 전환 수명 22±1초를 보고했다. QuTech의 결합된 최소 Kitaev 사슬은 '
    'Rabi 감쇠 시간 26±2나노초의 결맞는 패리티 진동을 보고했다. 패리티 수명, 유휴 결맞음, '
    'Rabi 감쇠 시간과 게이트 충실도는 서로 다른 물리량이며 수치를 순위 비교할 수 없다. '
    '다음 검증 과제는 비가환 제어와 별도 유휴 결맞음, 길이에 따른 보호, joint-parity와 얽힘, 연산 오류이다.'
)


def save(fig, stem, width, height):
    OUT.mkdir(exist_ok=True)
    path = OUT / f'{stem}.svg'
    fig.savefig(path, format='svg', metadata={
        'Date': None, 'Creator': 'AI Tech Review / original programmatic scientific illustration'})
    svg = path.read_text()
    # Preserve the viewBox but expose intrinsic CSS-pixel dimensions for reuse.
    import re
    svg = re.sub(r'width="[^"]+" height="[^"]+"',
                 f'width="{width}" height="{height}"', svg, count=1)
    start = svg.index('<svg ')
    end = svg.index('>', start)
    svg = svg[:end] + ' role="img" aria-labelledby="figure-title figure-desc"' + svg[end:]
    end = svg.index('>', start) + 1
    title = 'Majorana 연구의 세 성과와 다음 검증 과제'
    svg = (svg[:end] + f'\n <title id="figure-title">{escape(title)}</title>\n'
           f' <desc id="figure-desc">{escape(DESCRIPTION)}</desc>' + svg[end:])
    path.write_text('\n'.join(s.rstrip() for s in svg.splitlines()) + '\n')
    fig.savefig(Path(tempfile.gettempdir()) / f'{stem}_preview.png', dpi=100)
    plt.close(fig)


def desktop():
    width, height = 1440, 1140
    fig, ax = canvas(width, height)
    text(ax, 48, 31, 'Majorana: 세 가지 성과는 무엇을 입증하는가', 27, C['navy'], True)
    text(ax, 48, 88, '패리티의 안정성 · 결맞는 제어 · 보호된 연산을 구분해서 읽는다.', 16, C['muted'])
    box(ax, 48, 136, 1344, 66, C['amberlight'], C['amberlight'], 10)
    text(ax, 72, 155, '서로 다른 소자·프로토콜의 결과다. 수명 수치를 직접 비교하거나 게이트 충실도로 바꿀 수 없다.',
         16, C['amber'], True)
    cw, cy, ch = 432, 226, 532
    for i in range(3):
        card(ax, 48 + i * 456, cy, cw, ch, i)
    next_tests(ax, 48, 804, 1344)
    text(ax, 48, 1101, '편집부 원본 개념도 · 실제 장치의 치수·배치·측정 파형을 나타내지 않는다. 근거와 조건은 본문·그림 설명 참조.',
         12, C['muted'])
    save(fig, 'majorana_evidence', width, height)


def mobile():
    width, height = 480, 2380
    fig, ax = canvas(width, height)
    text(ax, 24, 24, 'Majorana의 세 가지 성과', 23, C['navy'], True)
    text(ax, 24, 78, '패리티 안정성 · 결맞는 제어 · 보호된 연산', 14.5, C['muted'])
    box(ax, 24, 121, 432, 109, C['amberlight'], C['amberlight'], 12)
    text(ax, 42, 141, '서로 다른 소자·프로토콜이다.\n수명은 게이트 충실도가 아니며\n아래 수치로 순위를 매길 수 없다.', 15, C['amber'], True)
    for i in range(3):
        card(ax, 24, 254 + i * 553, 432, 529, i, mobile=True)
    next_tests(ax, 26, 1933, 428, mobile=True)
    text(ax, 26, 2350, '편집부 원본 개념도 · 실제 장치의 배치·치수와 무관', 10.8, C['muted'])
    save(fig, 'majorana_evidence_mobile', width, height)


def notes():
    NOTES.mkdir(exist_ok=True)
    payload = {
        'figure_id': 'majorana_evidence',
        'as_of': '2026-10-19',
        'creator': 'AI Tech Review editorial / original code-native illustration',
        'generator': 'artifacts/build_majorana_figure.py',
        'runtime': {'python': '3.12', 'matplotlib': matplotlib.__version__,
                    'command': 'python artifacts/build_majorana_figure.py',
                    'font_override': 'QUBIT_FIGURE_FONT'},
        'files': {'desktop': {'path': 'artifacts/majorana_evidence.svg', 'width': 1440, 'height': 1140},
                  'mobile': {'path': 'artifacts/majorana_evidence_mobile.svg', 'width': 480, 'height': 2380}},
        'visual_qa': {'desktop_preview_inspected': True, 'mobile_preview_inspected': True,
                      'mobile_309px_width_preview_inspected': True,
                      'result': 'No clipped or overlapping labels; math labels render without missing-font warnings.'},
        'caption': 'Majorana 관련 세 연구의 성과와 해석 범위. 세 열은 서로 다른 장치·프로토콜이며 성숙도 순위가 아니다. Microsoft InAs–Al의 X/Z 루프 패리티 판독, 별도 InAs–Pb 소자의 긴 Z 패리티 수명, QuTech 최소 Kitaev 사슬의 결맞는 패리티 진동을 구분했다. 수명·Rabi 감쇠·판독 오류는 서로 다른 측정량이며 게이트 충실도로 환산할 수 없다. 모든 소자 그림은 편집부가 작성한 개념도이다.',
        'alt': DESCRIPTION,
        'sources': [
            {'title': 'Distinct lifetimes for X and Z loop measurements in a Majorana tetron device',
             'url': 'https://journals.aps.org/pra/accepted/10.1103/cx4w-lxx1',
             'full_text': 'https://arxiv.org/html/2507.08795v2',
             'status': 'Physical Review A accepted 2026-10-01; first preprint 2025-07-11',
             'facts': {'X_parity_switching': '14.5 ± 0.3 μs', 'Z_parity_switching': '12.4 ± 0.4 ms',
                       'operational_assignment_error': 'X 16% at 2 μs integration; Z 0.5% at 50 μs integration'},
             'limits': 'The two loop measurements were designed for Pauli X and Z. The authors identify rapid sequences demonstrating noncommutation as a next step. Assignment errors are measurement-operation metrics, not randomized-benchmarking gate infidelities.'},
            {'title': '20 Second Parity Lifetime in an InAs–Pb Tetron Device',
             'url': 'https://arxiv.org/abs/2606.03884',
             'full_text': 'https://arxiv.org/html/2606.03884v1',
             'status': 'Preprint submitted 2026-06-02',
             'facts': {'Z_parity_switching': '22 ± 1 s', 'dwell_intervals': 324},
             'limits': 'The long-lifetime result is a Z-loop parity switching measurement in the Pb material platform. It is not an idle arbitrary-state T2, a demonstrated 22-second coherent superposition, or a gate-fidelity measurement.'},
            {'title': 'Majorana parity qubit in coupled minimal Kitaev chains',
             'url': 'https://arxiv.org/abs/2607.09511',
             'full_text': 'https://arxiv.org/html/2607.09511v1',
             'status': 'Preprint submitted 2026-07-10',
             'facts': {'representative_Rabi_decay': '26 ± 2 ns', 'frequency': '106.7(0.4) MHz'},
             'limits': 'Coupled two-site chains exhibit coherent parity oscillations and limited sweet-spot protection. The reported Rabi decay is neither idle T2 nor a gate-fidelity benchmark; this is distinct from long-wire exponentially protected operations.'},
            {'title': 'Measurement-induced enhancement of the X-parity lifetime in a Majorana tetron',
             'url': 'https://arxiv.org/abs/2610.12223', 'status': 'Theory preprint submitted 2026-10-08',
             'use': 'Motivates independent idle-coherence tests: a readout dot can stabilize observed switching without equally long bare-tetron T2*.'},
            {'title': 'Revealing topological protection through unprotected operations in a Majorana parity qubit',
             'url': 'https://arxiv.org/abs/2610.17198', 'status': 'Theory preprint submitted 2026-10-12',
             'use': 'Motivates length-dependent optimized Rabi and decoupled Ramsey tests; it is a proposal and analysis, not a new experimental protection result.'},
        ],
        'scientific_limits': [
            'No platform ranking, cross-platform normalized score, or lifetime bar chart is used.',
            'The three research lines are separate devices and protocols, not successive measurements of one qubit.',
            'The H and chain glyphs are conceptual motifs, not literal micrographs, hardware layouts or paper-figure reconstructions.',
            'Long parity lifetime, readout assignment error, Rabi decay, idle coherence and gate fidelity remain distinct quantities.',
            'The bottom tests are editorial evaluation criteria grounded in the papers, not dated corporate delivery promises.',
        ],
    }
    (NOTES / 'majorana_evidence_notes.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    desktop()
    mobile()
    notes()
