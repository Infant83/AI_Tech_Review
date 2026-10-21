"""Inspect v4 final streams and timed captions; write private technical QA.

Not a listening or comprehension assessment. Every still comes from encoded
MP4, not from an unencoded render. Downloaded runtimes remain outside dist/.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, struct, subprocess, wave
import numpy as np
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DIST, QA = ROOT/'dist', ROOT/'qa'
SCENES = ['intro', 'principle', 'step', 'comparison', 'learned', 'conclusion']
ALLOWLIST = [f'{name}-{lang}.{ext}' for lang in ('ko','en') for name,ext in [('noether-abstract-v4','mp4'),('poster','webp'),('captions','vtt'),('transcript','txt'),('timeline','json')]]
FFMPEG = os.environ.get('VIDEO_FFMPEG', str(ROOT.parent/'.runtime/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1'))
if not Path(FFMPEG).exists():
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def call(args): return subprocess.run([FFMPEG, *args], capture_output=True, text=True, check=True)
def atom_order(path):
    atoms=[]
    with path.open('rb') as stream:
        while stream.tell()<path.stat().st_size:
            offset=stream.tell();header=stream.read(8)
            assert len(header)==8
            size,kind=struct.unpack('>I4s',header)
            if size==1:size=struct.unpack('>Q',stream.read(8))[0]
            if size==0:size=path.stat().st_size-offset
            assert size>=8
            atoms.append(kind.decode('ascii'));stream.seek(offset+size)
    assert 'moov' in atoms and 'mdat' in atoms and atoms.index('moov')<atoms.index('mdat'),atoms
    return atoms

def seconds(value):
    h,m,s=value.split(':');return int(h)*3600+int(m)*60+float(s)
def extract(lang, timestamp, name):
    target=QA/f'encoded-{lang}-{name}.png'
    call(['-v','error','-y','-ss',str(timestamp),'-i',str(DIST/f'noether-abstract-v4-{lang}.mp4'),'-frames:v','1',str(target)])
    assert target.is_file(), target
    return target

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lang',choices=['ko','en','all'],default='all')
    args=parser.parse_args()
    languages=('ko','en') if args.lang=='all' else (args.lang,)
    QA.mkdir(exist_ok=True)
    actual={p.name for p in DIST.iterdir()}
    assert actual <= set(ALLOWLIST+['asset-manifest.json']), actual-set(ALLOWLIST+['asset-manifest.json'])
    assert set(ALLOWLIST) <= actual, set(ALLOWLIST)-actual
    report={'version':'v4','scope':'Actual final MP4 full decode, PCM signal/clipping, sentence captions, source hashes and encoded keyframes. No human listening, comprehension, physical-device or publication approval.','checks_passed':False,'languages':{},'public_text_scan':{},'image_metadata':{}}
    prior_path=QA/'encoded-validation.json'
    if prior_path.exists():
        prior=json.loads(prior_path.read_text())
        for lang,entry in prior.get('languages',{}).items():
            path=DIST/f'noether-abstract-v4-{lang}.mp4'
            if path.is_file() and entry.get('sha256')==sha(path):report['languages'][lang]=entry
    numeric=json.loads((QA/'numeric-validation.json').read_text())
    assert numeric.get('checks_passed') is True
    report['numeric_report_sha256']=sha(QA/'numeric-validation.json')
    voice_metadata=list((QA/'speech-supertonic').glob('*-44k.json'))
    assert voice_metadata, 'Final sentence audio provenance is required.'
    for p in voice_metadata:
        metadata=json.loads(p.read_text())
        assert metadata['engine']=='Supertonic 2' and metadata['preset']=='F1'
        assert metadata['model_revision']=='75e6727618a02f323c720cba9478152d4bc16ca4'
        assert sha(p.with_suffix('.wav'))==metadata['sha256']
        assert 'machine' in metadata['disclosure_en'].lower()
    report['voice_source_validation']={'sentence_wavs':len(voice_metadata),'engine':'Supertonic 2','preset':'F1','model_revision':'75e6727618a02f323c720cba9478152d4bc16ca4','checks':'Every generated sentence WAV matches its recorded SHA256, model revision, preset and machine-generated disclosure metadata.'}
    for lang in languages:
        path=DIST/f'noether-abstract-v4-{lang}.mp4'
        timeline=json.loads((DIST/f'timeline-{lang}.json').read_text())
        private=json.loads((QA/f'timeline-private-{lang}.json').read_text())
        assert [s['id'] for s in timeline]==SCENES
        assert [s['id'] for s in private]==SCENES
        assert abs(timeline[0]['start'])<1e-8
        for i, scene in enumerate(timeline):
            assert scene['end']>scene['start']
            if i: assert abs(scene['start']-timeline[i-1]['end'])<1e-6
            assert scene['narration'].strip() and scene['visual'].strip()
            assert abs(private[i]['start']-scene['start'])<1e-6
            assert abs(private[i]['end']-scene['end'])<1e-6
        atoms=atom_order(path)
        decode=call(['-v','error','-i',str(path),'-f','null','-'])
        assert not decode.stderr.strip(), decode.stderr
        meta=call(['-v','error','-i',str(path),'-f','ffmetadata','-']).stdout
        assert not re.search(r'/Users/|/home/|sk-[A-Za-z0-9]{20}|file://',meta)
        stream=subprocess.run([FFMPEG,'-hide_banner','-i',str(path)],capture_output=True,text=True).stderr
        assert all(marker in stream for marker in ['1600x900','24 fps','aac','yuv420p','h264']),stream
        duration=seconds(re.search(r'Duration: ([\d:.]+)',stream).group(1))
        assert abs(duration-timeline[-1]['end'])<.06,(duration,timeline[-1]['end'])
        vtt=(DIST/f'captions-{lang}.vtt').read_text();assert vtt.startswith('WEBVTT\n')
        cues=[]
        for block in re.split(r'\r?\n\r?\n',vtt):
            lines=block.splitlines();index=next((i for i,line in enumerate(lines) if ' --> ' in line),None)
            if index is None:continue
            start,end=lines[index].split(' --> ')
            cues.append({'start':seconds(start),'end':seconds(end),'text':' '.join(lines[index+1:])})
        assert cues
        previous=0
        for cue in cues:
            assert cue['start']>=previous-.001 and cue['end']>cue['start'] and cue['end']<=timeline[-1]['end']+.001
            previous=cue['end']
        clean=lambda text:re.sub(r'\s+','',text)
        assert clean(' '.join(c['text'] for c in cues))==clean(' '.join(s['narration'] for s in timeline)), 'Captions differ from final narration.'
        keyframes={}
        for scene in private:
            assert scene['speech_segments']
            spoken=' '.join(s['text'] for s in scene['speech_segments'])
            assert clean(spoken)==clean(next(s for s in timeline if s['id']==scene['id'])['narration'])
            for index,segment in enumerate(scene['speech_segments'],1):
                start=scene['start']+.45+segment['start'];end=scene['start']+.45+segment['end']
                assert scene['start']<=start<end<=scene['end']
                key=f"{scene['id']}-s{index:02d}"
                stamp=(start+end)/2
                frame=extract(lang,stamp,key)
                keyframes[key]={'file':frame.name,'seconds':stamp,'sentence_start':start,'sentence_end':end,'spoken_text':segment['text']}
            for semantic_id, event in scene['semantic_cues'].items():
                assert event['anchor'] and event['spoken_text'].startswith(event['anchor'])
                assert scene['start'] <= event['video_start'] < event['video_end'] <= scene['end']
                for moment, stamp in [('before',max(scene['start']+.02,event['video_start']-.15)),('after',min(scene['end']-.10,event['video_start']+.35)),('held',min(scene['end']-.10,event['video_end']+.10))]:
                    key=scene['id']+'-'+semantic_id+'-'+moment
                    frame=extract(lang,stamp,key)
                    keyframes[key]={'file':frame.name,'seconds':stamp,'semantic_id':semantic_id,'anchor':event['anchor'],'spoken_text':event['spoken_text'],'external_captions':'Matching native VTT supplied separately; no burn-in narration.'}
            endpoint=extract(lang,scene['end']-.4,scene['id']+'-endpoint')
            keyframes[scene['id']+'-endpoint']={'file':endpoint.name,'seconds':scene['end']-.4}
        for index in range(1,len(private)):
            boundary=private[index]['start']
            for side,stamp in [('before',boundary-.15),('after',boundary+.55)]:
                key='transition-'+private[index-1]['id']+'-to-'+private[index]['id']+'-'+side
                frame=extract(lang,stamp,key)
                keyframes[key]={'file':frame.name,'seconds':stamp,'transition':'Actual encoded cut; no interpolated scientific states.'}
        # Six encoded end states, plus isolated grayscale and thumbnail files.
        sheet=Image.new('RGB',(960,3*292),'#061820');draw=ImageDraw.Draw(sheet)
        for index,scene in enumerate(private):
            im=Image.open(QA/f"encoded-{lang}-{scene['id']}-endpoint.png").convert('RGB')
            im.thumbnail((480,270));x=(index%2)*480;y=(index//2)*292
            sheet.paste(im,(x,y));draw.text((x+8,y+272),scene['id'],fill='white')
        sheet.save(QA/f'encoded-contact-sheet-{lang}.jpg',quality=92)
        for image in [DIST/f'poster-{lang}.webp', QA/f'encoded-{lang}-comparison-endpoint.png',QA/f'encoded-{lang}-learned-endpoint.png']:
            with Image.open(image) as im:ImageOps.grayscale(im).save(QA/f'grayscale-{image.stem}.png')
        with Image.open(DIST/f'poster-{lang}.webp') as im:im.resize((320,180),Image.Resampling.LANCZOS).save(QA/f'thumbnail-{lang}.png')
        wav=QA/f'decoded-audio-{lang}.wav'
        call(['-v','error','-y','-i',str(path),'-vn','-ar','24000','-ac','1','-c:a','pcm_s16le',str(wav)])
        with wave.open(str(wav),'rb') as f:
            audio=np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16).astype(float)
            audio_duration=len(audio)/f.getframerate()
        peak=float(np.max(abs(audio)));clipped=float(np.mean(abs(audio)>=32767))
        assert peak>1000 and clipped<1e-5
        assert abs(audio_duration-timeline[-1]['end'])<.12
        report['languages'][lang]={'file':path.name,'sha256':sha(path),'full_decode':'passed, no FFmpeg error output','encoded_duration_seconds':duration,'timeline_duration_seconds':timeline[-1]['end'],'mp4_top_level_atom_order':atoms,'faststart':True,'chapters':len(timeline),'caption_cues':len(cues),'caption_timing':'Ordered, positive and within final duration; normalized full text matches narration.','audio_peak_sample':peak,'audio_rms':float(np.sqrt(np.mean(audio**2))),'clipped_fraction':clipped,'audio_duration_seconds':audio_duration,'mp4_bytes':path.stat().st_size,'metadata':meta,'stream_description':stream,'sentence_keyframes':keyframes,'contact_sheet':f'encoded-contact-sheet-{lang}.jpg'}
    for p in DIST.iterdir():
        if p.suffix in ('.json','.txt','.vtt','.html'):
            hits=re.findall(r'/Users/|/home/|file://|sk-[A-Za-z0-9]{20}',p.read_text())
            assert not hits,(p.name,hits)
            report['public_text_scan'][p.name]='No internal absolute path or credential-like match.'
        if p.suffix=='.webp':
            with Image.open(p) as im:
                assert not im.getexif()
                report['image_metadata'][p.name]={'exif_present':False,'metadata_keys':list(im.info)}
    report['checks_passed']=all(report['languages'].get(lang,{}).get('sha256')==sha(DIST/f'noether-abstract-v4-{lang}.mp4') for lang in ('ko','en'))
    (QA/'encoded-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f"v4 {args.lang}: full decode, audio signal, caption text/timing, provenance, metadata and encoded keyframe extraction passed. Both masters checked: {report['checks_passed']}. Human listening not performed.")

if __name__=='__main__':main()
