"""Freeze exact final v4 web assets; source and private QA remain outside dist/."""
from pathlib import Path
import hashlib,json,mimetypes
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist';QA=ROOT/'qa';V2=ROOT.parent/'v2';V3=ROOT.parent/'v3'
ALLOWLIST=[f'{name}-{lang}.{ext}' for lang in ('ko','en') for name,ext in [('noether-abstract-v4','mp4'),('poster','webp'),('captions','vtt'),('transcript','txt'),('timeline','json')]]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 assert {p.name for p in DIST.iterdir()}<=set(ALLOWLIST+['asset-manifest.json'])
 for name in ALLOWLIST:assert(DIST/name).is_file(),name
 timeline={l:read(DIST/f'timeline-{l}.json') for l in ('ko','en')}
 masters={l:DIST/f'noether-abstract-v4-{l}.mp4' for l in ('ko','en')}
 hashes={l:sha(p) for l,p in masters.items()}
 numeric=read(QA/'numeric-validation.json');assert numeric['checks_passed']
 encoded=read(QA/'encoded-validation.json') if (QA/'encoded-validation.json').exists() else {}
 encoded_ok=encoded.get('checks_passed') is True and all(encoded.get('languages',{}).get(l,{}).get('sha256')==hashes[l] for l in masters)
 science=read(QA/'science-visual-review.json') if (QA/'science-visual-review.json').exists() else {}
 checks=science.get('checks_passed',{})
 science_ok=isinstance(checks,dict) and checks.get('actual_encoded_frames') is True and all(science.get('reviewed_master_hashes',{}).get(l)==hashes[l] for l in masters)
 sb=read(ROOT/'storyboard.json')
 public_sources={k:v for k,v in sb['sources'].items() if v.startswith('https://')}
 public_sources.update(V='https://lagrangeweb.web.engr.illinois.edu/var_int/',CALC='https://github.com/Infant83/AI_Tech_Review/blob/main/2026-10-17_noether-symmetry-conservation/artifacts/build_figures.py',DERIV=sb['sources']['R'].rstrip('/')+'/#section-6')
 old_text={p.read_text() for p in (V3/'qa/speech-supertonic').glob('*.txt')}
 clips=list((QA/'speech-supertonic').glob('*.txt'));reused=sum(p.read_text() in old_text for p in clips)
 art=read(V2/'assets/image-provenance.json');hero=next(x for x in art['assets'] if x['file']=='hero.png')
 result={
  'version':'v4','created':'2026-10-22','title':sb['title_ko'],'title_en':sb['title_en'],
  'status':'Rendered for the authorized bilingual Noether article video module; publication is performed and verified by the article publisher.',
  'scope':'Representative oscillator calculation and Hamiltonian-learning construction convey the article argument. Not every article section is summarized; no new trained performance result is claimed.',
  'article_argument':'Use symmetry as a model-design constraint and conserved quantities as a test, while checking learned physical laws and numerical error separately.',
  'dimensions':[1600,900],'fps':24,'codec':'H.264 yuv420p + AAC160k, faststart',
  'languages':{l:{'duration_seconds':tl[-1]['end'],'chapters':len(tl),'scene_ids':[s['id'] for s in tl]} for l,tl in timeline.items()},
  'captions':{'burned_in':False,'format':'Separate language WebVTT for the native article player. Download the VTT with the MP4 when captions are needed.','text':'Full spoken text; sentence timing based on actual local synthesis.'},
  'narration':{'engine':'Supertonic 2','preset':'F1','model_repository':'Supertone/supertonic-2','revision':'75e6727618a02f323c720cba9478152d4bc16ca4','machine_generated':True,'cloned_voice':False,'local_cpu':True,'existing_sentence_wavs_reused':reused,'new_or_revised_sentence_wavs_synthesized':len(clips)-reused,'speed':1.0,'timing':'0.45s lead, 0.18s phrase pauses, natural voice duration, 1.5s reading tail; no time stretching.','rights':'MIT inference code; BigScience OpenRAIL-M model. Model section6 disclaims output rights except as stated; use restrictions apply. AttachmentA(e) requires synthetic-content disclosure, supplied in video and transcript. No macOS system-voice recording is included.'},
  'reproducibility_source_sha256':{name:sha(ROOT/name) for name in ['artifacts/render_review.py','storyboard.json','script-ko.md','script-en.md']},
  'method':'NumPy validated states and equations → Pillow frames with exact semantic spoken-unit anchors → local FFmpeg. Scientific geometry is deterministic; reused concept artwork is background only.',
  'api_use':{'generative_video_api_calls':0,'external_paid_tts_api_calls':0,'new_image_generation_operations':0,'note':'Agent usage, prior artwork generation, local computation, storage and hosting remain separate costs.'},
  'artwork':{'source_version':'v2','asset':'hero.png','sha256':hero['sha256'],'meaning':'Conceptual temporal layers only; no measured apparatus, physical trajectory or new result.'},
  'scientific_conditions':{'model':'Undamped undriven horizontal linear spring, fixed mass and stiffness.','normalization':{'q':'x/A','u':'v/(Aω)','tau':'ωt','h':'ωΔt'},'h':.1,'steps':2000,'initial_state':[1,0],'initial_normalized_energy':.5,'Euler_energy_factor':numeric['euler_energy_factor_numeric'],'Verlet_max_abs_relative_energy_error':numeric['verlet_max_relative_error'],'comparison_scope':'Same h teaching calculation, not an equal-cost or equal-accuracy benchmark.','HNN':'Smooth autonomous learned function in canonical coordinates; Hamilton equations conserve it in continuous time. Learned physical accuracy and discrete integration error remain separate tests.'},
  'sources':public_sources,
  'editorial':{'responsible_editor':'Hyun-Jung Kim','AI_assistance':'OpenAI Codex','exact_model_identifier':'not retained','human_listening_or_comprehension_review':'Not performed.','scope_of_review':'Independent agent science/visual review and technical file validation, not a human audience study.'},
  'verification':{'numeric':True,'encoded':bool(encoded_ok),'independent_encoded_visual_review':bool(science_ok),'human_listening':'Not performed.','human_comprehension':'Not performed.','continuous_playback':'See the independent review record; extraction of transition stills alone is not continuous playback.','public_asset_allowlist':'Only the named final files below; sources, runtime, private speech and QA are excluded.'},
  'public_assets':[{'file':name,'bytes':(DIST/name).stat().st_size,'sha256':sha(DIST/name),'mime':mimetypes.guess_type(name)[0] or 'application/octet-stream'} for name in ALLOWLIST],
  'excluded':'Source scripts, editorial plans, private QA, screenshots, speech caches, intermediate audio, downloaded model/runtime/font/encoder files and internal paths.'
 }
 text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
 assert '/Users/' not in text and '/home/' not in text
 (DIST/'asset-manifest.json').write_text(text)
 print(f'v4 manifest: {len(ALLOWLIST)} final assets, encoded={encoded_ok}, independent_encoded_visual_review={science_ok}')
if __name__=='__main__':main()
