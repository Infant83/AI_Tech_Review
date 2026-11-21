"""Excerpt and arrange published CC BY 4.0 panels without altering data."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse, hashlib, json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-figure', type=Path, required=True)
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw = args.source_figure.read_bytes()
    source_sha = hashlib.sha256(raw).hexdigest()
    source = Image.open(args.source_figure).convert('RGB')
    if source.size != (1450, 711):
        raise ValueError('Crop coordinates require the verified 1450 x 711 publisher image.')
    crops = {'3a': (0, 0, 476, 349), '3b': (480, 0, 1450, 349), '3e': (988, 354, 1450, 711)}
    panels = {}
    manifest = []
    for key, box in crops.items():
        image = source.crop(box)
        path = args.output_dir / ('sic-published-panel-' + key + '.png')
        image.save(path)
        panels[key] = image
        manifest.append({'file': path.name, 'source_figure': key, 'pixel_crop': box,
                         'source_sha256': source_sha, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'license': 'CC BY 4.0', 'modifications': 'Rectangular excerpt only; data/axes/legend unaltered.'})
    canvas = Image.new('RGB', (2200, 1090), 'white')
    draw = ImageDraw.Draw(canvas)
    font = lambda size: ImageFont.truetype(str(args.font), size)
    color = '#193E54'
    draw.text((55, 30), 'RF-free nuclear-spin control: tilt and readable signal', font=font(50), fill=color)
    draw.text((55, 104), 'Wörnle et al. | npj Quantum Information 12, 191 (2026) | published Fig. 3(a,e)', font=font(31), fill='#526B7C')
    draw.line((55, 155, 2140, 155), fill='#BED1DA', width=2)
    draw.text((70, 185), 'A  Nuclear precession about an effective field', font=font(32), fill=color)
    draw.text((1150, 185), 'B  Tilt changes the measured contrast', font=font(32), fill=color)
    for key, box in [('3a', (70, 245, 1030, 940)), ('3e', (1150, 245, 2120, 940))]:
        im = panels[key].copy()
        im.thumbnail((box[2]-box[0], box[3]-box[1]), Image.Resampling.LANCZOS)
        # Enlarge the publisher excerpt by a single isotropic resampling operation.
        scale = min((box[2]-box[0])/panels[key].width, (box[3]-box[1])/panels[key].height)
        im = panels[key].resize((round(panels[key].width*scale), round(panels[key].height*scale)), Image.Resampling.LANCZOS)
        canvas.paste(im, (box[0]+(box[2]-box[0]-im.width)//2, box[1]+(box[3]-box[1]-im.height)//2))
    draw.line((55, 975, 2140, 975), fill='#BED1DA', width=2)
    draw.text((55, 996), 'Excerpts rearranged; axes, error bars and the published model curve preserved. No new fit or experiment.', font=font(28), fill='#526B7C')
    draw.text((55, 1040), 'CC BY 4.0 | DOI 10.1038/s41534-026-01415-8 | Figure labels and headings added by the review.', font=font(28), fill='#526B7C')
    path = args.output_dir / 'sic-fig3ae-composite.png'
    canvas.save(path)
    manifest.append({'file': path.name, 'source_panels': ['3a', '3e'], 'source_sha256': source_sha,
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'license': 'CC BY 4.0',
                     'modifications': 'Panel excerpts, isotropic enlargement, rearrangement and editorial headings/credit added. No data transformation or curve reconstruction.'})
    (args.output_dir/'sic-panel-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'source_sha256': source_sha, 'assets': manifest}))

if __name__ == '__main__':
    main()
