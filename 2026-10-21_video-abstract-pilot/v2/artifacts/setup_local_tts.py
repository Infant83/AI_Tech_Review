"""Verify or fetch the pinned local Supertonic assets; no speech service calls.

Run --download once after reading artifacts/local-tts-notes.md. Without that flag,
only existing files are checked. Model weights remain in ignored .runtime/.
"""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    base = root / '.runtime' / 'supertonic'
    lock = json.loads((root / 'artifacts' / 'tts-asset-lock.json').read_text())
    for item in lock['files']:
        path = base / item['destination']
        if path.exists():
            if path.stat().st_size == item['bytes'] and digest(path) == item['sha256']:
                print('verified', item['destination'])
                continue
            raise SystemExit('Existing asset differs from the pinned lock: ' + item['destination'])
        if not args.download:
            raise SystemExit('Missing asset; read the license notes then run --download: ' + item['destination'])
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + '.partial')
        try:
            with urllib.request.urlopen(item['url'], timeout=60) as response, temporary.open('wb') as output:
                for chunk in iter(lambda: response.read(1024 * 1024), b''):
                    output.write(chunk)
            if temporary.stat().st_size != item['bytes'] or digest(temporary) != item['sha256']:
                raise ValueError('Downloaded asset does not match the pinned lock: ' + item['destination'])
            temporary.replace(path)
        finally:
            if temporary.exists():
                temporary.unlink()
        print('downloaded and verified', item['destination'])
    print('Local TTS assets match the pinned model and source revisions.')


if __name__ == '__main__':
    main()
