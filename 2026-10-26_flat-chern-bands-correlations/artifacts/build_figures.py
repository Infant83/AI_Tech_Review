#!/usr/bin/env python3
"""Reproduce this review's eight localized desktop/mobile SVGs.

Standard-library only.  Reads the approved educational/source-count SVGs and
PES counting JSON in the earlier draft folder.  No source data are downloaded,
and no material ED/PES or FCI is calculated here.  The original 41x41 link-flux
cell rectangles and palette are retained exactly; mobile layouts move/scale
them without interpolation.  PES bars keep a linear 0--1200 count axis.

Usage from this article directory:
    python3 artifacts/build_figures.py --output-dir figures-preview

Omit --output-dir to regenerate the topic's figures/ directory.  This script
does not alter artifacts/, dist/, manuscripts or the public site.
"""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import xml.etree.ElementTree as ET


TOPIC = Path(__file__).resolve().parents[1]
REPO = TOPIC.parent
DRAFT = REPO / "2026-10-26_flat-bands-and-targeted-dynamics"
NS = {"s": "http://www.w3.org/2000/svg"}

TRANSLATIONS = {
    "flatness-and-topology": {
        "Identical flat energies do not determine band topology": "같은 평탄한 에너지, 서로 다른 밴드 위상",
        "Independent two-band teaching models; not ReAg2Cl6 data or a fractional-state calculation": "독립 두 밴드 교육 모형 · ReAg₂Cl₆ 데이터나 분수 상태 계산이 아님",
        "A  Energy eigenvalues": "A  에너지 고유값",
        "B  Lower-band Berry curvature": "B  낮은 밴드의 Berry 곡률",
        "k along any path": "임의 경로의 운동량 k",
        "Energy (model units)": "에너지 (모형 단위)",
        "Curvature": "곡률",
        "Both models: lower-band width W = 0, interband gap = 2 (up to floating-point error).": "두 모형 모두 낮은 밴드폭 W = 0, 밴드 간격 = 2 (부동소수점 오차 이내).",
        "Rescaling H by 20 leaves W = 0 and C unchanged, while ||H|| increases from 1 to 20.": "H를 20배 해도 W = 0과 C는 유지되지만 ||H||는 1에서 20으로 증가한다.",
        "Spectral flattening preserves eigenvectors and generally requires long-range hopping. C uses oriented link phases.": "스펙트럼 평탄화는 고유벡터를 보존하며 보통 장거리 hopping이 필요하다. C는 방향을 둔 link 위상으로 계산했다.",
    },
    "pes-counting": {
        "Same Chern number, different particle-entanglement counting": "같은 Chern 수, 다른 입자 얽힘 계수",
        "Recounting the authors' source data gives 1088 particle-entanglement levels below the gap for the first valence and third conduction bands, versus 168 for the second conduction band. Each has Chern number minus one and one-third filling; the many-body model uses the flat-band limit.": "저자 원자료의 얽힘 gap 아래 준위 수는 첫 가전자대와 세 번째 전도대에서 1088, 두 번째 전도대에서 168이다. Chern 수는 모두 −1, 채움은 1/3이며 다체 모형은 flat-band limit를 사용한다.",
        "Same Chern number, different many-body counting": "같은 Chern 수, 다른 다체 상태 계수",
        "C = −1 · ν = 1/3 · Nuc = 24 · Ne = 8 · NA = 3 · flat-band-limit model": "C = −1 · ν = 1/3 · Nuc = 24 · Ne = 8 · NA = 3 · flat-band-limit 모형",
        "PES levels below the entanglement gap": "입자 얽힘 gap 아래의 PES 준위 수",
        "VB and 3rd CB": "VB · 세 번째 CB",
        "Laughlin-type counting": "Laughlin형 계수",
        "2nd CB": "두 번째 CB",
        "Threefold CDW counting": "세 배치 CDW 계수",
        "Same flat dispersion and Chern number do not identify the correlated phase.": "평탄한 분산과 Chern 수가 같아도 상관 상태가 같지는 않다.",
        "Independent recount of authors' data; no new ED or PES calculation.": "저자 원자료의 독립 계수 대조 · 새로운 ED·PES 계산이 아님",
        "Bao et al., Communications Physics (2026), Fig. 4 · Source: Zenodo 10.5281/zenodo.21199721": "Bao 등, Communications Physics (2026), 그림 4 · 원자료: Zenodo 10.5281/zenodo.21199721",
    },
}


def text(out: list[str], x: int, y: int, value: str, size: int = 23,
         bold: bool = False) -> None:
    out.append(f'<text x="{x}" y="{y}" font-size="{size}"'
               + (' font-weight="700"' if bold else '')
               + '>' + escape(value) + '</text>')


def source_rect(e: ET.Element) -> str:
    return '<rect ' + ' '.join(f'{k}="{v}"' for k, v in e.attrib.items()) + '/>'


def flat_mobile(language: str, rects: list[ET.Element],
                bars: list[ET.Element]) -> str:
    ko = language == "ko"
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="1180" viewBox="0 0 600 1180" role="img" aria-labelledby="title desc">',
        '<title id="title">' + escape("같은 평탄한 에너지, 다른 밴드 위상" if ko else "Identical flat energies, different band topology") + '</title>',
        '<desc id="desc">Two independent two-band teaching models have W=0 and gap=2, but lower-band Chern numbers zero and minus one. A stacked view preserves the original 41 by 41 link-flux curvature data.</desc>',
        '<rect width="600" height="1180" fill="#f6f4ed"/>',
        '<g font-family="Arial, Noto Sans CJK KR, sans-serif" fill="#173c4c">',
    ]
    text(out, 35, 42, '같은 평탄한 에너지, 다른 밴드 위상' if ko else 'Flat energies, different topology', 25, True)
    text(out, 35, 76, '독립 교육 모형 · ReAg₂Cl₆ 데이터가 아님' if ko else 'Teaching models · not ReAg₂Cl₆ data', 20)
    text(out, 45, 125, 'A  두 모형의 같은 에너지' if ko else 'A  Equal energies in both models', 24, True)
    text(out, 75, 170, 'H = σz : C = 0', 22)
    text(out, 75, 201, 'H = d̂(k) · σ : C = −1', 22)
    out += [
        '<path d="M80 225V420H550" fill="none" stroke="#536b75" stroke-width="2"/>',
        '<path d="M80 245H530M80 395H530" fill="none" stroke="#007e8c" stroke-width="5"/>',
    ]
    text(out, 35, 252, '+1')
    text(out, 35, 403, '−1')
    text(out, 160, 458, '임의 경로의 운동량 k' if ko else 'k along any path', 22)
    text(out, 75, 496, 'W = 0 · 밴드 간격 = 2 (모형 단위)' if ko else 'W = 0 · gap = 2 (model units)', 22)
    text(out, 45, 550, 'B  낮은 밴드의 Berry 곡률 (C = −1)' if ko else 'B  Lower-band curvature (C = −1)', 24, True)
    # Original x=[675,985], y=[150,460] becomes a 420 px square.
    # Rectangles, values and source colors are retained without resampling.
    out.append('<g transform="translate(-830.81,379.19) scale(1.35484)">')
    out.extend(source_rect(e) for e in rects)
    out.append('</g>')
    out.append('<rect x="83.7" y="582.4" width="420" height="420" fill="none" stroke="#536b75" stroke-width="1.5"/>')
    text(out, 45, 594, 'π', 20)
    text(out, 30, 801, 'ky', 22)
    text(out, 38, 1000, '−π', 20)
    text(out, 78, 1030, '−π', 20)
    text(out, 484, 1030, 'π', 20)
    text(out, 280, 1057, 'kx', 22)
    out.append('<g transform="translate(-864,383) scale(1.35)">')
    out.extend(source_rect(e) for e in bars)
    out.append('</g>')
    text(out, 548, 644, '+0.5', 18)
    text(out, 548, 780, '0', 18)
    text(out, 548, 923, '−0.5', 18)
    text(out, 35, 1100, '41×41 link-flux 격자 · 스펙트럼 평탄화' if ko else '41×41 link-flux grid · spectral flattening', 20)
    text(out, 35, 1132, '고유벡터 보존 · 보통 장거리 hopping 필요' if ko else 'Eigenvectors retained; long-range hopping typical', 20)
    text(out, 35, 1162, 'FCI·재료 밴드 계산을 재현한 그림이 아님' if ko else 'Not a reproduction of material bands or an FCI', 20)
    out += ['</g></svg>']
    return '\n'.join(out)


def pes_mobile(language: str, count_fci: int, count_cdw: int) -> str:
    ko = language == "ko"
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="850" viewBox="0 0 600 850" role="img" aria-labelledby="title desc">',
        '<title id="title">' + escape('같은 Chern 수, 다른 PES 계수' if ko else 'Same Chern number, different PES counting') + '</title>',
        '<desc id="desc">Authors source data recounted: 1088 low PES levels in the VB and third CB, 168 in the second CB, at C=-1 and one-third filling in the flat-band limit. No new ED or PES calculation.</desc>',
        '<rect width="600" height="850" fill="#f8fafc"/>',
        '<g font-family="Arial, Noto Sans CJK KR, sans-serif" fill="#14263d">',
    ]
    text(out, 35, 45, '같은 Chern 수, 다른 PES 계수' if ko else 'Same Chern number, different', 27, True)
    if not ko:
        text(out, 35, 80, 'PES counting', 27, True)
    text(out, 35, 119, 'C = −1 · ν = 1/3 · flat-band limit', 23)
    text(out, 35, 154, 'Nuc = 24 · Ne = 8 · NA = 3', 23)
    text(out, 35, 200, '얽힘 gap 아래의 PES 준위 수' if ko else 'PES levels below the entanglement gap', 22)
    text(out, 60, 252, 'VB · 세 번째 CB' if ko else 'VB and 3rd CB', 26, True)
    text(out, 60, 283, 'Laughlin형 계수' if ko else 'Laughlin-type counting', 22)
    # Every bar uses the same 430 px / 1200 count scale, rounded to .01 px.
    out.append(f'<rect x="60" y="302" width="{430*count_fci/1200:.2f}" height="55" rx="4" fill="#155e75"/>')
    text(out, 465, 340, f'{count_fci:,}', 26, True)
    text(out, 60, 410, '두 번째 CB' if ko else '2nd CB', 26, True)
    text(out, 60, 441, '세 배치 CDW 계수' if ko else 'Threefold CDW counting', 22)
    out.append(f'<rect x="60" y="460" width="{430*count_cdw/1200:.2f}" height="55" rx="4" fill="#a14b21"/>')
    text(out, 137, 498, str(count_cdw), 26, True)
    out.append('<path d="M60 540H490" stroke="#aebbc7" fill="none"/>')
    for n in [0, 300, 600, 900, 1200]:
        x = 60 + 430*n/1200
        out.append(f'<path d="M{x} 540V547" stroke="#aebbc7"/>')
        out.append(f'<text x="{x}" y="575" text-anchor="middle" font-size="19">{n}</text>')
    text(out, 35, 626, '1088 = 24/18 × binom(18, 3)', 22)
    text(out, 35, 659, '168 = 3 × binom(8, 3)', 22)
    text(out, 35, 704, '같은 평탄한 분산과 C가 상을 결정하지 않는다.' if ko else 'Same flat dispersion and C do not identify the phase.', 21)
    text(out, 35, 742, '저자 원자료 독립 계수 · ED·PES 재계산 아님' if ko else 'Independent recount; no new ED or PES calculation.', 21)
    text(out, 35, 786, 'Bao 등 (2026), 그림 4 · 원자료 Zenodo' if ko else 'Bao et al. (2026), Fig. 4 · source: Zenodo', 20)
    text(out, 35, 820, '10.5281/zenodo.21199721', 20)
    out += ['</g></svg>']
    return '\n'.join(out)


def build(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    source_dir = DRAFT / 'figures'
    result = json.loads((DRAFT / 'artifacts/results/pes-counting.json').read_text())
    counts = {r['band']: r['count_below_threshold'] for r in result['results']}
    assert counts == {'1st VB': 1088, '3rd CB': 1088, '2nd CB': 168}, counts
    for stem, mapping in TRANSLATIONS.items():
        original = (source_dir / f'{stem}.svg').read_text()
        (output_dir / f'{stem}_en.svg').write_text(original)
        localized = original
        for before, after in mapping.items():
            assert before in localized, before
            localized = localized.replace(before, after)
        localized = localized.replace('Arial,Helvetica,sans-serif', 'Arial,"Noto Sans CJK KR",sans-serif')
        localized = localized.replace('font-family="Arial,"Noto Sans CJK KR",sans-serif"', 'font-family="Arial,Noto Sans CJK KR,sans-serif"')
        localized = localized.replace('Arial, sans-serif', 'Arial, Noto Sans CJK KR, sans-serif')
        ET.fromstring(localized)
        (output_dir / f'{stem}_ko.svg').write_text(localized)
    original = ET.fromstring((source_dir / 'flatness-and-topology.svg').read_text())
    rects = [e for e in original.findall('.//s:rect', NS)
             if e.get('x') is not None and 675 <= float(e.get('x')) < 985
             and float(e.get('width')) < 8]
    bars = [e for e in original.findall('.//s:rect', NS) if e.get('x') == '1020']
    assert len(rects) == 41*41, len(rects)
    assert len(bars) > 100, len(bars)
    for language in ['ko', 'en']:
        for stem, data in [('flatness-and-topology', flat_mobile(language, rects, bars)),
                           ('pes-counting', pes_mobile(language, counts['1st VB'], counts['2nd CB']))]:
            ET.fromstring(data)
            (output_dir / f'{stem}_mobile_{language}.svg').write_text(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=TOPIC / 'figures')
    args = parser.parse_args()
    build(args.output_dir)
    print('Wrote eight SVGs to', args.output_dir)
