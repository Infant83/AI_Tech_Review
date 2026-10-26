#!/usr/bin/env python3
"""Recount published PES data; this does not rerun ED or calculate a PES.

Python standard library only. Keep the source workbook outside public assets:
  python3 artifacts/check_pes_counting.py --download
or:
  python3 artifacts/check_pes_counting.py --source-xlsx '/tmp/flatband-20261026/Figure 4.xlsx'

The source workbook is read only and accepted only under /tmp or archive/private.
The generated JSON contains source checksums and cell ranges, not a local path.
"""

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import tempfile
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
import zipfile


TOPIC = Path(__file__).resolve().parents[1]
REPO = TOPIC.parent
SOURCE_URL = "https://zenodo.org/api/records/21199721/files/Figure%204.xlsx/content"
SOURCE_SHA256 = "80c91a78e5dad9691dc5a839b497ae393ba7c307f2722d7c9de8ddcbea22de1f"
SOURCE_MD5 = "1a8f515450eb525bbd2c72074cf43032"
SOURCE_SIZE = 98461
SPECS = (
    {"band": "1st VB", "column": "G", "panel": "4b", "threshold": 4.7, "interpretation": "Laughlin-type FCI counting", "expected": 1088},
    {"band": "3rd CB", "column": "O", "panel": "4f", "threshold": 5.3, "interpretation": "Laughlin-type FCI counting", "expected": 1088},
    {"band": "2nd CB", "column": "W", "panel": "4d", "threshold": 2.5, "interpretation": "threefold CDW counting", "expected": 168},
)


def is_within(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def check_private_source_path(path):
    resolved = path.resolve()
    roots = [Path(tempfile.gettempdir()).resolve(), Path('/tmp').resolve(), (REPO / 'archive' / 'private').resolve()]
    if not any(is_within(resolved, root) for root in roots):
        raise ValueError('Source workbook must remain in a temporary directory or archive/private.')
    return resolved


def extract_columns(path):
    """Resolve Sheet1 through OOXML relationships and read exact numeric cells.

    Shared-string indices are never treated as numeric data. That distinction
    matters because this source has formatted header cells with shared index 0.
    """
    with zipfile.ZipFile(path) as z:
        workbook = ET.fromstring(z.read('xl/workbook.xml'))
        sheets = [s for s in workbook.findall('.//{*}sheet') if s.get('name') == 'Sheet1']
        if len(sheets) != 1:
            raise ValueError('Expected exactly one Sheet1.')
        rel_id = sheets[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        relationships = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        target = next(r.get('Target') for r in relationships if r.get('Id') == rel_id)
        xml_path = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        sheet = ET.fromstring(z.read(xml_path))
        cells = {c.get('r'): c for c in sheet.findall('.//{*}c')}
        result = {}
        for spec in SPECS:
            values = []
            for row in range(3, 2027):
                coordinate = f"{spec['column']}{row}"
                cell = cells.get(coordinate)
                if cell is None or cell.get('t', 'n') != 'n' or cell.find('{*}f') is not None:
                    raise ValueError(f'Expected a numeric source value at {coordinate}.')
                value = float(cell.find('{*}v').text)
                if not math.isfinite(value):
                    raise ValueError(f'Non-finite source value at {coordinate}.')
                values.append(value)
            result[spec['column']] = values
        return result, xml_path


def build_result(source):
    payload = source.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != SOURCE_SHA256 or len(payload) != SOURCE_SIZE:
        raise ValueError('Source content differs from the inspected Zenodo workbook; inspect the new revision first.')
    if hashlib.md5(payload).hexdigest() != SOURCE_MD5:
        raise ValueError('Source does not match the checksum published by Zenodo.')
    columns, xml_path = extract_columns(source)
    results = []
    for spec in SPECS:
        values = sorted(columns[spec['column']])
        threshold = spec['threshold']
        count = sum(value < threshold for value in values)
        stable_counts = {str(round(threshold + offset, 8)): sum(value < threshold + offset for value in values) for offset in (-0.1, 0.0, 0.1)}
        expected_total = math.comb(24, 3)
        if len(values) != expected_total or count != spec['expected'] or set(stable_counts.values()) != {count}:
            raise ValueError(f"Unexpected level count for {spec['band']}.")
        lower, upper = values[count - 1], values[count]
        if not lower < threshold < upper:
            raise ValueError('Separating threshold is outside the observed gap.')
        results.append({
            **spec, 'sheet': 'Sheet1', 'range': f"{spec['column']}3:{spec['column']}2026",
            'first_row': 3, 'last_row': 2026, 'total_numeric_values': len(values),
            'count_below_threshold': count, 'largest_value_below': lower,
            'smallest_value_above': upper, 'entanglement_gap': upper - lower,
            'threshold_sensitivity_counts': stable_counts,
            'count_matches_closed_form': count == spec['expected'],
        })
    laughlin_count = 24 * math.comb(18, 3) // 18
    cdw_count = 3 * math.comb(8, 3)
    admissible_states = sum(all(gap >= 3 for gap in (b-a, c-b, a+24-c)) for a, b, c in itertools.combinations(range(24), 3))
    cdw_subsets = {subset for offset in range(3) for subset in itertools.combinations(range(offset, 24, 3), 3)}
    if (laughlin_count, cdw_count) != (1088, 168) or (admissible_states, len(cdw_subsets)) != (laughlin_count, cdw_count):
        raise ValueError('Combinatorial arithmetic failed.')
    return {
        'analysis': 'Recount of authors\u2019 supplied particle-entanglement eigenvalues; no ED or PES recomputation',
        'checked_date': '2026-10-26',
        'source': {
            'article_doi': '10.1038/s42005-026-02924-w', 'data_doi': '10.5281/zenodo.21199721',
            'filename': 'Figure 4.xlsx', 'download_url': SOURCE_URL, 'bytes': len(payload),
            'sha256': digest, 'zenodo_published_checksum': 'md5:' + SOURCE_MD5,
            'sheet': 'Sheet1', 'worksheet_xml': xml_path, 'source_workbook_edited': False,
        },
        'conditions': {
            'C': -1, 'filling': '1/3', 'Nuc': 24, 'Ne': 8, 'NA': 3, 'NB': 5,
            'ground_state_density_matrix': 'equal mixture of three low-lying states',
            'many_body_model': 'single-band projected onsite interaction in flat-band limit',
        },
        'threshold_method': 'Fixed thresholds inside the visible entanglement gaps of the published Fig. 4; not selected by optimizing agreement with the combinatorial count. Stability tested at plus/minus 0.1.',
        'results': results,
        'closed_form': {
            'Laughlin_1_3_torus': {'formula': '24/(24-2*3) * binom(24-2*3,3)', 'value': laughlin_count, 'independent_cyclic_minimum_spacing_enumeration': admissible_states},
            'threefold_CDW': {'formula': '3 * binom(8,3)', 'value': cdw_count, 'independent_three_sublattice_subset_enumeration': len(cdw_subsets)},
            'full_NA_particle_space': {'formula': 'binom(24,3)', 'value': math.comb(24, 3)},
        },
        'checks': {'source_checksum': 'pass', 'exact_cell_types_and_ranges': 'pass', 'all_values_finite': 'pass', 'total_levels': 'pass', 'thresholds_inside_gaps': 'pass', 'threshold_sensitivity': 'pass', 'closed_form_arithmetic': 'pass', 'independent_combinatorial_enumeration': 'pass'},
        'limits': ['This recount does not reproduce the original ED eigenstates or reduced density matrices.', 'PES counting is one diagnostic together with ground-state momentum and spectral flow.', 'These results do not establish stability with the physical band dispersion, band mixing, or at a measured transition temperature.'],
    }


def make_svg(result):
    laughlin, cdw = 1088, 168
    left, width, max_count = 350, 700, 1200
    marks = ''.join(f'<line x1="{left + width * v/max_count:.2f}" y1="180" x2="{left + width * v/max_count:.2f}" y2="435" stroke="#d7dfea"/><text x="{left + width * v/max_count:.2f}" y="470" text-anchor="middle" class="tick">{v}</text>' for v in (0, 300, 600, 900, 1200))
    bars = ''
    for y, label, count, color, meaning in [(215, 'VB and 3rd CB', laughlin, '#155e75', 'Laughlin-type counting'), (350, '2nd CB', cdw, '#a14b21', 'Threefold CDW counting')]:
        bars += f'<text x="48" y="{y+22}" class="label">{label}</text><text x="48" y="{y+52}" class="small">{meaning}</text><rect x="{left}" y="{y}" width="{width*count/max_count:.2f}" height="62" rx="5" fill="{color}"/><text x="{left+width*count/max_count+16:.2f}" y="{y+41}" class="number">{count:,}</text>'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 660" role="img" aria-labelledby="title desc">
<title id="title">Same Chern number, different particle-entanglement counting</title>
<desc id="desc">Recounting the authors' source data gives 1088 particle-entanglement levels below the gap for the first valence and third conduction bands, versus 168 for the second conduction band. Each has Chern number minus one and one-third filling; the many-body model uses the flat-band limit.</desc>
<rect width="1200" height="660" fill="#f8fafc"/>
<style>text{{font-family:Arial,Helvetica,sans-serif;fill:#14263d}}.title{{font-size:32px;font-weight:700}}.subtitle{{font-size:22px}}.label{{font-size:25px;font-weight:700}}.small,.tick{{font-size:19px}}.number{{font-size:30px;font-weight:700}}.note{{font-size:20px}}</style>
<text x="48" y="59" class="title">Same Chern number, different many-body counting</text>
<text x="48" y="104" class="subtitle">C = −1 · ν = 1/3 · Nuc = 24 · Ne = 8 · NA = 3 · flat-band-limit model</text>
<text x="350" y="157" class="small">PES levels below the entanglement gap</text>
{marks}{bars}
<text x="48" y="525" class="note">1088 = 24/18 × binom(18, 3); 168 = 3 × binom(8, 3)</text>
<text x="48" y="570" class="note">Same flat dispersion and Chern number do not identify the correlated phase.</text>
<text x="48" y="607" class="small">Independent recount of authors' data; no new ED or PES calculation.</text>
<text x="48" y="637" class="small">Bao et al., Communications Physics (2026), Fig. 4 · Source: Zenodo 10.5281/zenodo.21199721</text>
</svg>'''
    # Inline attributes also render consistently in PDF/SVG preview engines
    # that do not implement stylesheet selectors.
    styles = {'title': (32, 700), 'subtitle': (22, 400), 'label': (25, 700), 'small': (19, 400), 'tick': (19, 400), 'number': (30, 700), 'note': (20, 400)}
    for class_name, (size, weight) in styles.items():
        svg = svg.replace(f'class="{class_name}"', f'font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="#14263d"')
    return svg


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-xlsx', type=Path, default=Path('/tmp/flatband-20261026/Figure 4.xlsx'))
    parser.add_argument('--download', action='store_true', help='Download the source workbook only to the private/temporary source path.')
    args = parser.parse_args()
    source = check_private_source_path(args.source_xlsx)
    if args.download:
        source.parent.mkdir(parents=True, exist_ok=True)
        payload = urlopen(Request(SOURCE_URL, headers={'User-Agent': 'AI-Tech-Review-PES-recount'}), timeout=45).read()
        if hashlib.sha256(payload).hexdigest() != SOURCE_SHA256:
            raise ValueError('Downloaded bytes differ from the inspected source.')
        source.write_bytes(payload)
    result = build_result(source)
    output = TOPIC / 'artifacts' / 'results' / 'pes-counting.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    figure = TOPIC / 'figures' / 'pes-counting.svg'
    figure.parent.mkdir(parents=True, exist_ok=True)
    figure.write_text(make_svg(result))
    ET.parse(figure)
    print(json.dumps({'status': 'pass', 'PES_counts': {r['band']: r['count_below_threshold'] for r in result['results']}, 'source_sha256': result['source']['sha256'], 'recomputed_ED': False}))


if __name__ == '__main__':
    main()
