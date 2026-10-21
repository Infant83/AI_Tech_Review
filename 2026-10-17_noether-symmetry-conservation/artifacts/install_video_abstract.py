"""Install only reviewed, named v4 media into this article's artifact directory.

The production package remains separate from the article's public asset set.
Run after independent encoded-output review; no rendering or publication here.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    args = parser.parse_args()
    source = args.source_dir.resolve()
    raw = json.loads((source / 'asset-manifest.json').read_text())
    if str(raw.get('version')) != 'v4':
        raise ValueError('Expected the independently reviewed v4 production package.')
    checks = raw.get('verification', {})
    if checks.get('encoded') is not True or checks.get('independent_encoded_visual_review') is not True:
        raise ValueError('Encoded and independent visual review must pass before installation.')
    registered = {r['file']: r for r in raw['public_assets']}
    result = {
        'version': 'v4', 'date': '2026-10-22', 'status': 'ready',
        'scope': 'Article argument through a spring calculation and Hamiltonian-learning construction.',
        'method': 'Deterministic local rendering; separate native WebVTT captions; no generative video API.',
        'production_manifest_sha256': digest(source / 'asset-manifest.json'),
        'production_source': '2026-10-21_video-abstract-pilot/v4',
        'synthetic_narration': 'Supertonic 2 F1; local inference; disclosed in video and article.',
        'audio_rights': raw.get('narration', {}).get('rights', ''),
        'sources': {k: v for k, v in raw.get('sources', {}).items() if '://' in v},
        'numeric_conditions': 'Normalized h=0.1, 2000 steps, q0=1,u0=0. Teaching calculation, not a matched-cost benchmark.',
        'interpretation_limits': raw.get('scientific_conditions', {}),
        'human_review': 'No human listening, pronunciation or reader-comprehension study.',
        'article_player_checks': 'Pending after installation; separate from encoded media review.',
        'languages': {},
    }
    for lang in ('ko', 'en'):
        mapping = {
            'video': (f'noether-abstract-v4-{lang}.mp4', f'noether-abstract-{lang}.mp4'),
            'poster': (f'poster-{lang}.webp', f'noether-abstract-poster-{lang}.webp'),
            'captions': (f'captions-{lang}.vtt', f'noether-abstract-{lang}.vtt'),
            'transcript': (f'transcript-{lang}.txt', f'noether-abstract-transcript-{lang}.txt'),
        }
        assets = {}
        for kind, (name, target_name) in mapping.items():
            record = registered[name]
            original = source / name
            if original.stat().st_size != record['bytes'] or digest(original) != record['sha256']:
                raise ValueError(f'Production asset differs from reviewed manifest: {name}')
            shutil.copyfile(original, ART / target_name)
            assets[kind] = {'file': target_name, 'bytes': record['bytes'], 'sha256': record['sha256']}
        result['languages'][lang] = {'duration_seconds': raw['languages'][lang]['duration_seconds'], 'assets': assets}
    (ART / 'video-abstract-manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('Installed eight reviewed article assets. Run the HTML/PDF builder and article-player QA next.')

if __name__ == '__main__':
    main()
