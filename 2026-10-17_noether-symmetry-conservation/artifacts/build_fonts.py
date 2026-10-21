"""Create a local WOFF2 subset from user-supplied, openly licensed TTF fonts."""
from pathlib import Path
import argparse
import re
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--regular', type=Path, required=True)
    parser.add_argument('--bold', type=Path, required=True)
    parser.add_argument('--license', type=Path, default=ROOT / 'artifacts' / 'font-OFL.txt')
    args = parser.parse_args()
    text = ''.join(p.read_text(encoding='utf-8') for p in (ROOT / 'reports').glob('review_*.md'))
    text += ''.join(chr(i) for i in range(32, 256))
    text += '김현중책임편집보조작성근거기준일검토본로컬검증정보모델식별자미보존사람주제요청문장단위승인없음역할원문조사학술응용한영종합시각자료조판출력결과독립실험재현수행하지않았습니다입력산출물하네스개념그림수식도표번역참고출처페이지목차내용살펴보기한국어영어내려받기이동PDF'
    # UI/disclosure strings are included so generated typography remains self-contained.
    text += (ROOT / 'artifacts' / 'build_review.mjs').read_text(encoding='utf-8')
    text += (ROOT / 'artifacts' / 'video_module.mjs').read_text(encoding='utf-8')
    transcript = ROOT / 'artifacts' / 'noether-abstract-transcript-ko.txt'
    if transcript.exists():
        text += transcript.read_text(encoding='utf-8')
    license_parts = []
    for label, source in [('regular', args.regular), ('bold', args.bold)]:
        font = TTFont(source)
        for name_id in [0, 13, 14]:
            values = {n.toUnicode() for n in font['name'].names if n.nameID == name_id}
            license_parts.extend(sorted(values))
        # Subsetting makes a derivative. Give it a new primary name instead of
        # retaining the source font's Reserved Font Name.
        family = 'Review Sans Subset'
        style = 'Bold' if label == 'bold' else 'Regular'
        renamed = {1:family,2:style,3:f'ReviewSansSubset-{style}',4:f'{family} {style}',6:f'ReviewSansSubset-{style}',16:family,17:style}
        for record in font['name'].names:
            if record.nameID in renamed:
                record.string = renamed[record.nameID].encode(record.getEncoding())
        options = subset.Options()
        options.flavor = 'woff2'
        options.desubroutinize = True
        options.recalc_timestamp = False
        options.name_IDs = ['*']
        sub = subset.Subsetter(options=options)
        sub.populate(text=text)
        sub.subset(font)
        font.flavor = 'woff2'
        font.save(ROOT / 'artifacts' / f'review-{label}.woff2')
    if not args.license.exists():
        raise FileNotFoundError('A complete source-font license is required; pass --license.')
    license_text = '\n\n'.join(dict.fromkeys(license_parts)).strip() + '\n\n' + args.license.read_text(encoding='utf-8')
    (ROOT / 'artifacts' / 'font-license.txt').write_text(license_text.rstrip() + '\n', encoding='utf-8')
    print('Created two local font subsets and retained font licensing records.')

if __name__ == '__main__':
    main()
