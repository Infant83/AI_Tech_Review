"""Subset licensed full fonts from current manuscripts, labels and renderer text."""
from pathlib import Path
import argparse
import hashlib
import json
import unicodedata
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]


def name_font(font, family, style):
    names = {1: family, 2: style, 3: family.replace(' ', '') + '-' + style,
             4: family + ' ' + style, 6: family.replace(' ', '') + '-' + style,
             16: family, 17: style}
    for record in font['name'].names:
        if record.nameID in names:
            record.string = names[record.nameID].encode(record.getEncoding())
    if 'CFF ' in font:
        cff = font['CFF '].cff
        cff.fontNames = [names[6]]
        for top in cff.topDictIndex:
            top.FullName = names[4]
            top.FamilyName = family


def write_subset(font, codepoints, output):
    font.recalcTimestamp = False
    options = subset.Options()
    options.flavor = 'woff2'
    options.recalc_timestamp = False
    options.name_IDs = ['*']
    worker = subset.Subsetter(options=options)
    worker.populate(unicodes=codepoints | {32})
    worker.subset(font)
    font.flavor = 'woff2'
    font.save(output)
    return set(TTFont(output).getBestCmap())


def main():
    parser = argparse.ArgumentParser()
    for label in ['regular', 'bold', 'symbols', 'math']:
        parser.add_argument('--' + label, type=Path, required=True)
    args = parser.parse_args()
    artifacts = ROOT / 'artifacts'
    manuscripts = [ROOT / 'reports' / f'review_{lang}.md' for lang in ['ko', 'en']]
    if any(not p.is_file() for p in manuscripts):
        parser.error('Both final manuscripts are required before generating publication subsets.')
    inputs = manuscripts + list(artifacts.glob('*.svg')) + [artifacts / 'build_review.mjs']
    metadata = artifacts / 'publication-metadata.json'
    if metadata.exists():
        inputs.append(metadata)
    text = ''.join(p.read_text(encoding='utf-8') for p in inputs)
    codepoints = {ord(c) for c in text if not c.isspace() and not unicodedata.category(c).startswith('C')}
    codepoints |= {n for n in range(32, 256) if not unicodedata.category(chr(n)).startswith('C')}
    primary = set(TTFont(args.regular).getBestCmap())
    missing = codepoints - primary
    symbols_cmap = set(TTFont(args.symbols).getBestCmap())
    symbols_needed = missing & symbols_cmap
    math_needed = missing - symbols_needed
    math_cmap = set(TTFont(args.math).getBestCmap())
    if math_needed - math_cmap:
        raise ValueError('Glyphs absent from all supplied licensed fonts: ' + str(sorted(math_needed - math_cmap)))
    coverage = {}
    for label in ['regular', 'bold']:
        font = TTFont(getattr(args, label))
        available = set(font.getBestCmap())
        missing_korean = {c for c in codepoints if 0xAC00 <= c <= 0xD7A3 and c not in available}
        if missing_korean:
            raise ValueError(f'{label} source lacks Korean syllables: {sorted(missing_korean)}')
        name_font(font, 'Qunova Review Sans Subset', 'Bold' if label == 'bold' else 'Regular')
        target = artifacts / f'review-{label}.woff2'
        provided = write_subset(font, codepoints & available, target)
        assert codepoints & available <= provided
        coverage[label] = {'bytes': target.stat().st_size, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
    for label, weight in [('regular', 400), ('bold', 700)]:
        font = TTFont(args.symbols)
        if 'fvar' in font:
            axes = {axis.axisTag: axis.defaultValue for axis in font['fvar'].axes}
            if 'wght' in axes:
                axes['wght'] = weight
            font = instantiateVariableFont(font, axes, inplace=True)
        name_font(font, 'Qunova Review Symbols Subset', 'Bold' if label == 'bold' else 'Regular')
        target = artifacts / f'review-symbols-{label}.woff2'
        assert symbols_needed <= write_subset(font, symbols_needed, target)
        coverage['symbols_' + label] = {'bytes': target.stat().st_size, 'codepoints': sorted(symbols_needed)}
    font = TTFont(args.math)
    name_font(font, 'Qunova Review Math Subset', 'Regular')
    target = artifacts / 'review-math.woff2'
    assert math_needed <= write_subset(font, math_needed, target)
    coverage['math'] = {'bytes': target.stat().st_size, 'codepoints': sorted(math_needed)}
    for file in ['font-OFL.txt', 'noto-OFL.txt', 'noto-math-OFL.txt']:
        if not (artifacts / file).is_file():
            raise ValueError('Missing complete source-font license: ' + file)
    license_parts = [(artifacts / file).read_text(encoding='utf-8') for file in ['font-OFL.txt', 'noto-OFL.txt', 'noto-math-OFL.txt']]
    (artifacts / 'font-license.txt').write_text('\n\n'.join(license_parts).rstrip() + '\n', encoding='utf-8')
    report = {'inputs_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
              'source_fonts': {label: {'filename': getattr(args, label).name,
                                     'sha256': hashlib.sha256(getattr(args, label).read_bytes()).hexdigest()}
                               for label in ['regular', 'bold', 'symbols', 'math']},
              'missing_codepoints': [], 'subsets': coverage}
    qa = ROOT / 'tmp' / 'fonts'
    qa.mkdir(parents=True, exist_ok=True)
    (qa / 'coverage.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'missing_codepoints': [], 'subsets': coverage}, ensure_ascii=False))


if __name__ == '__main__':
    main()
