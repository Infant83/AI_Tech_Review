#!/usr/bin/env python3
"""Local CPU Supertonic-2 preset narration; downloads nothing at inference time.

Use v2/.runtime/tts-venv/bin/python after explicit local model setup. Output audio
must be intelligibly disclosed as machine generated (model license Attachment A).
No cloning or external synthesis service is used.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import time


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lang', choices=['ko', 'en'], required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text')
    group.add_argument('--text-file', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--model-dir', type=Path, default=root/'.runtime/supertonic/assets')
    parser.add_argument('--helper', type=Path, default=root/'.runtime/supertonic/helper.py')
    parser.add_argument('--voice', default='F1', choices=['F1'])
    parser.add_argument('--steps', type=int, default=8)
    parser.add_argument('--speed', type=float, default=1.0)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    import numpy as np
    import soundfile as sf
    import onnxruntime as ort
    text = args.text if args.text is not None else args.text_file.read_text().strip()
    if not text:
        parser.error('Narration text is empty')
    spec = importlib.util.spec_from_file_location('supertonic_local_helper', args.helper)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    np.random.seed(args.seed)
    start = time.perf_counter()
    tts = helper.load_text_to_speech(str(args.model_dir/'onnx'), False)
    voice_path = args.model_dir/'voice_styles'/f'{args.voice}.json'
    style = helper.load_voice_style([str(voice_path)])
    load_seconds = time.perf_counter()-start
    start = time.perf_counter()
    wav, duration = tts(text, args.lang, style, args.steps, args.speed)
    inference_seconds = time.perf_counter()-start
    wave = wav[0, :int(tts.sample_rate*float(duration[0]))]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(args.output), wave, tts.sample_rate, subtype='PCM_16')
    metadata = {
        'engine': 'Supertonic 2', 'model_repository': 'Supertone/supertonic-2',
        'model_revision': '75e6727618a02f323c720cba9478152d4bc16ca4',
        'source_repository': 'https://github.com/supertone-oss-archive/supertonic',
        'source_commit': '1e9799e964ea4c0dad7cde993b65c3c813a7b373',
        'model_license': 'BigScience Open RAIL-M, 2022-08-18',
        'code_license': 'MIT',
        'disclosure_ko': 'Supertonic 2의 기본 음성으로 기기에서 합성한 AI 음성입니다. 사람의 녹음이나 특정인의 복제 음성이 아닙니다.',
        'disclosure_en': 'Machine-generated narration synthesized locally with a Supertonic 2 preset voice; not a human recording or a cloned person.',
        'license_conditions': ['Model license section 6: licensor claims no output rights except as stated in the license.', 'Attachment A(e): expressly and intelligibly disclose machine-generated content.', 'All model use restrictions remain applicable; this is educational narration.'],
        'lang': args.lang, 'text': text, 'preset': args.voice, 'steps': args.steps,
        'speed': args.speed, 'seed': args.seed, 'sample_rate': tts.sample_rate,
        'duration_seconds': len(wave)/tts.sample_rate,
        'load_seconds': load_seconds, 'inference_seconds': inference_seconds,
        'realtime_factor': inference_seconds/(len(wave)/tts.sample_rate),
        'runtime': {'python': platform.python_version(), 'onnxruntime': ort.__version__, 'numpy': np.__version__, 'platform': platform.system(), 'machine': platform.machine()},
        'sha256': sha256(args.output), 'voice_style_sha256': sha256(voice_path),
        'helper_sha256': sha256(args.helper),
        'validation': 'WAV generated and metadata recorded; listening QA is separate.'
    }
    args.output.with_suffix('.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: metadata[k] for k in ['lang','duration_seconds','load_seconds','inference_seconds','realtime_factor','sha256']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
