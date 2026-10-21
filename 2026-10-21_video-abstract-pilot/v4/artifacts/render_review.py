"""Bilingual v4 article video abstract; NumPy/Pillow/FFmpeg and local Supertonic2.
Scientific geometry and states are code-generated. Existing v2 concept art is
atmosphere only. Narration is read exactly from script-{ko,en}.md paragraphs.
Run: python artifacts/render_review.py --lang both [--stills-only] [--text-only]
"""
from pathlib import Path
import argparse, hashlib, json, math, os, re, subprocess, time, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parents[1]
V2=ROOT.parent/'v2'; V3=ROOT.parent/'v3'; DIST=ROOT/'dist'; QA=ROOT/'qa'; ASSETS=V2/'assets'
SPEECH_DIR=QA/'speech-supertonic'
for directory in (DIST,QA,SPEECH_DIR):directory.mkdir(parents=True,exist_ok=True)
W,H=1600,900; FPS=int(os.environ.get('VIDEO_FPS','24'))
FFMPEG=os.environ.get('VIDEO_FFMPEG',str(ROOT.parent/'.runtime/imageio_ffmpeg/binaries/ffmpeg-macos-x86_64-v7.1'))
if not Path(FFMPEG).exists():
 import imageio_ffmpeg
 FFMPEG=imageio_ffmpeg.get_ffmpeg_exe()
FONT=os.environ.get('VIDEO_FONT','/System/Library/Fonts/AppleSDGothicNeo.ttc')
MATH_FONT=os.environ.get('VIDEO_MATH_FONT','/System/Library/Fonts/Supplemental/STIXTwoMath.otf')
INK='#e8f4f1';MUTE='#8ea8ac';GRID='#254249';CYAN='#60e0d1';COPPER='#efa36f';BLUE='#7ba8ec';BG='#071c26';WHITE='#ffffff'
FONTS={};BACKGROUNDS={};ART={};TIMELINES={};AUDIO={};CUES={}
DATA=json.loads((ROOT/'storyboard.json').read_text());SCENES=DATA['scenes']
LEAD=.45;PAUSE=.18;TAIL=1.50
def ft(size,bold=False):
    key=(size,bold)
    if key not in FONTS:
        FONTS[key]=ImageFont.truetype(os.environ.get('VIDEO_FONT_BOLD',FONT) if bold else FONT,size,index=1 if bold and 'AppleSDGothicNeo' in FONT else 0)
    return FONTS[key]

def txt(d,xy,s,size=30,fill=INK,bold=False,anchor=None):
    s=str(s)
    s=s.replace('qₙ₊₁','q[n+1]').replace('pₙ₊₁','p[n+1]').replace('qₙ','q[n]').replace('pₙ','p[n]').replace('Fᵢ','F_i').replace('∇ᵣᵢ','∇_{r_i}')
    math_only=not any('\uac00'<=c<='\ud7a3' for c in s) and any(c in s for c in '=∂²ₙ₀θ⁸⁶⁹∫−̇₁₃πΔ≤∇³′')
    if math_only:
        key=('math',size)
        if key not in FONTS:FONTS[key]=ImageFont.truetype(MATH_FONT,size)
        usefont=FONTS[key]
    else:
        s=s.translate(str.maketrans({'₀':'0','₁':'1','ₙ':'n','₊':'+','−':'-','⁸':'^8','⁹':'^9','⁶':'^6','̇':''}))
        usefont=ft(size,bold)
    d.text(xy,s,font=usefont,fill=fill,anchor=anchor,spacing=9)

def wrap(d,s,maxw,size=30):
    lines=[]
    for paragraph in str(s).split('\n'):
        line=''
        for word in paragraph.split():
            trial=(line+' '+word).strip()
            if line and d.textlength(trial,font=ft(size))>maxw: lines.append(line);line=word
            else:line=trial
        lines.append(line)
    return lines

def paragraph(d,xy,s,width,size=30,fill=INK,bold=False,spacing=1.3):
    lines=wrap(d,s,width,size)
    for i,line in enumerate(lines):txt(d,(xy[0],xy[1]+i*size*spacing),line,size,fill,bold)
    return len(lines)*size*spacing

def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)

def mix(a,b,u):return a+(b-a)*u

def dashed(d,a,b,fill=MUTE,width=2,dash=10,gap=8):
    dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy)
    if not l:return
    for x in np.arange(0,l,dash+gap):
        e=min(x+dash,l);d.line((a[0]+dx*x/l,a[1]+dy*x/l,a[0]+dx*e/l,a[1]+dy*e/l),fill=fill,width=width)

def arrow(d,a,b,fill=CYAN,width=3,head=12):
    d.line((*a,*b),fill=fill,width=width);ang=math.atan2(b[1]-a[1],b[0]-a[0])
    pts=[b,(b[0]-head*math.cos(ang-.45),b[1]-head*math.sin(ang-.45)),(b[0]-head*math.cos(ang+.45),b[1]-head*math.sin(ang+.45))]
    d.polygon(pts,fill=fill)

def dot(d,p,fill=CYAN,r=8):
    d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=fill,outline=BG,width=2)

def path(d,pts,fill=CYAN,width=4):
    if len(pts)>1:d.line(pts,fill=fill,width=width,joint='curve')

def art_load():
    for name in ('hero',):
        candidates=list(ASSETS.glob(name+'.*'))
        if not candidates:candidates=list(ASSETS.glob(name+'-*'))
        if candidates:
            ART[name]=ImageOps.fit(Image.open(candidates[0]).convert('RGB'),(W,H))

def background(kind):
    if kind in BACKGROUNDS:return BACKGROUNDS[kind].copy()
    yy,xx=np.mgrid[0:H,0:W].astype(float)
    glow=np.exp(-((xx-1120)**2/(720**2)+(yy-300)**2/(600**2)))
    grain=np.random.default_rng(8).normal(0,.65,(H,W))
    a=np.stack([6+glow*8+grain,21+glow*17+grain,30+glow*20+grain],axis=-1)
    im=Image.fromarray(np.uint8(np.clip(a,0,255)))
    if kind in ('intro','conclusion') and 'hero' in ART:
        art=ART['hero'];mask=Image.fromarray(np.uint8(np.tile(np.clip((np.arange(W)-390)/670,0,.94)*255,(H,1))))
        im.paste(art,(0,0),mask)
        # Dark footer maintains caption contrast, independent of art brightness.
        dark=Image.new('RGB',(W,H),BG)
        m=np.uint8(np.tile(np.clip((np.arange(H)-590)/210,0,.94)*255,(W,1)).T)
        im.paste(dark,(0,0),Image.fromarray(m))
    elif kind=='noether' and 'material' in ART:
        art=Image.blend(im,ART['material'],.16);im=art
    BACKGROUNDS[kind]=im
    return im.copy()


def validate():
 h=.1;n=2000;t=np.arange(n+1)*h
 e=np.zeros((n+1,2));v=e.copy();e[0]=v[0]=[1,0]
 for i in range(n):
  q,u=e[i];e[i+1]=[q+h*u,u-h*q]
  q,u=v[i];half=u-h*q/2;qn=q+h*half;v[i+1]=[qn,half-h*qn/2]
 energies={'euler':np.sum(e*e,axis=1),'verlet':np.sum(v*v,axis=1),'exact':np.ones(n+1)}
 theta=2*np.arcsin(h/2);closed=np.stack([np.cos(np.arange(n+1)*theta),-np.sqrt(1-h*h/4)*np.sin(np.arange(n+1)*theta)],axis=1)
 assert np.allclose(v,closed,atol=2e-13)
 assert np.allclose(energies['euler'],(1+h*h)**np.arange(n+1),rtol=5e-13)
 assert abs(energies['euler'][1]-1.01)<1e-14
 assert .00249<np.max(abs(energies['verlet']-1))<.002501
 result={'checks_passed':True,'normalization':{'q':'x/A','u':'v/(Aω)','tau':'ωt','h':'ωΔt','E/E0':'q²+u²','q0':1,'u0':0},'h':h,'steps':n,'euler_first_step':[float(x) for x in e[1]],'euler_energy_factor_numeric':float(energies['euler'][-1]),'euler_energy_factor_analytic':float((1+h*h)**n),'verlet_max_relative_error':float(np.max(abs(energies['verlet']-1))),'verlet_closed_form_max_state_difference':float(np.max(abs(v-closed))),'time_origin_shift_tau':float(math.pi/2),'hnn':'Method schematic only: smooth autonomous Htheta, canonical derivatives, continuous-time conservation; no training result.'}
 (QA/'numeric-validation.json').write_text(json.dumps(result,indent=2)+'\n')
 return t,e,v,energies,result
TIME,EULER,VERLET,ENERGY,VALIDATION=validate()

def say_audio(lang,scene):
 narration=scene['narration_'+lang]
 sentences=re.split(r'(?<=[.!?。])\s+',narration)
 parts=[];segments=[];cursor=0
 for i,sentence in enumerate(sentences):
  stem=SPEECH_DIR/f'{lang}-{scene["id"]}-s{i+1:02d}'
  target=stem.with_suffix('.wav');textfile=stem.with_suffix('.txt')
  if not target.exists():
   for cached_text in (V3/'qa/speech-supertonic').glob(lang+'-*.txt'):
    if cached_text.read_text()==sentence and cached_text.with_suffix('.wav').exists():
     import shutil
     for suffix in ('.wav','.txt','-44k.wav','-44k.json'):
      old=cached_text.with_suffix(suffix) if suffix.startswith('.') else cached_text.with_name(cached_text.stem+suffix)
      new=stem.with_suffix(suffix) if suffix.startswith('.') else stem.with_name(stem.name+suffix)
      if old.exists():shutil.copy2(old,new)
     break
  if not target.exists() or not textfile.exists() or textfile.read_text()!=sentence:
   textfile.write_text(sentence)
   source=stem.with_name(stem.name+'-44k').with_suffix('.wav')
   voice_python=os.environ.get('VIDEO_TTS_PYTHON',str(V2/'.runtime/tts-venv/bin/python'))
   subprocess.run([voice_python,str(V2/'artifacts/local_tts.py'),'--model-dir',str(V2/'.runtime/supertonic/assets'),'--lang',lang,'--text-file',str(textfile),'--output',str(source),'--voice','F1','--speed','1.0','--steps','8'],capture_output=True,text=True,check=True)
   subprocess.run([FFMPEG,'-v','error','-y','-i',str(source),'-ar','24000','-ac','1','-c:a','pcm_s16le',str(target)],check=True)
  with wave.open(str(target),'rb') as f:a=np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16).astype(float)
  peak=np.max(abs(a))
  if peak:a*=min(1.7,25000/peak)
  a=np.int16(np.clip(a,-32768,32767));parts.append(a)
  segments.append({'start':cursor,'end':cursor+len(a)/24000,'text':sentence});cursor+=len(a)/24000
  if i<len(sentences)-1:parts.append(np.zeros(round(24000*PAUSE),np.int16));cursor+=PAUSE
 print(f'{lang}: narration {scene["id"]} ({cursor:.1f}s)',flush=True)
 return np.concatenate(parts),segments

def timeline(lang,narration=True):
 scenes=[];parts=[];cursor=0;cues=[]
 for s in SCENES:
  if narration:a,segments=say_audio(lang,s)
  else:
   ss=re.split(r'(?<=[.!?。])\s+',s['narration_'+lang]);cc=0;segments=[]
   for sentence in ss:
    length=max(2,len(sentence)*(.065 if lang=='en' else .12));segments.append({'start':cc,'end':cc+length,'text':sentence});cc+=length+PAUSE
   a=np.zeros(round((cc-PAUSE)*24000),np.int16)
  rawdur=len(a)/24000;duration=math.ceil(max(s.get('duration_hint',14),rawdur+LEAD+TAIL)*FPS)/FPS
  item=dict(s,start=cursor,end=cursor+duration,duration_actual=duration,narration_duration=rawdur,speech_segments=segments)

  resolved={}
  for event in s['semantic_events']:
   anchor=event['anchor_'+lang]
   matches=[clip for clip in segments if clip['text'].startswith(anchor)]
   assert len(matches)==1,(lang,s['id'],event['id'],anchor,len(matches))
   clip=matches[0];resolved[event['id']]={'anchor':anchor,'spoken_text':clip['text'],'start':LEAD+clip['start'],'end':LEAD+clip['end'],'video_start':cursor+LEAD+clip['start'],'video_end':cursor+LEAD+clip['end']}
  item['semantic_cues']=resolved
  scenes.append(item);pad=np.zeros(round(duration*24000),np.int16);off=round(LEAD*24000);pad[off:off+len(a)]=a;parts.append(pad)
  probe=ImageDraw.Draw(Image.new('RGB',(10,10)))
  for segment in segments:
   lines=wrap(probe,segment['text'],1380,35)
   chunks=[' '.join(lines[i:i+2]) for i in range(0,len(lines),2)]
   lengths=[max(len(x),15) for x in chunks];total=sum(lengths);cc=cursor+LEAD+segment['start'];usable=segment['end']-segment['start']
   for chunk,l in zip(chunks,lengths):
    stop=cc+usable*l/total;cues.append({'start':cc,'end':stop,'text':chunk,'scene':s['id']});cc=stop
  if cues:cues[-1]['end']=cursor+duration-.15
  cursor+=duration
 audio=np.concatenate(parts);wav=QA/f'narration-{lang}.wav'
 with wave.open(str(wav),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(audio.tobytes())
 TIMELINES[lang]=scenes;AUDIO[lang]=wav;CUES[lang]=cues
 (QA/f'timeline-private-{lang}.json').write_text(json.dumps(scenes,ensure_ascii=False,indent=2)+'\n')
 return scenes

def event_time(scene,name,end=False):
 return scene['semantic_cues'][name]['end' if end else 'start']

def cue(scene,index):
 segments=scene['speech_segments'];return LEAD+segments[min(index,len(segments)-1)]['start']

def endcue(scene,index):
 segments=scene['speech_segments'];return LEAD+segments[min(index,len(segments)-1)]['end']

def progress(t,a,b):return max(0,min(1,(t-a)/max(.01,b-a)))

def panel(d,box,outline=GRID,fill='#0b2631'):
 d.rounded_rectangle(box,radius=15,fill=fill,outline=outline,width=2)

def spring(d,x0,x1,y,q,scale,color=CYAN):
 equilibrium=(x0+x1)/2+30;end=equilibrium+q*scale
 d.line((x0,y-38,x0,y+38),fill=MUTE,width=5)
 pts=[(x0,y),(x0+22,y)]
 for j in range(30):pts.append((x0+26+(end-x0-70)*j/29,y+(11 if j%2 else -11)))
 pts.extend([(end-20,y),(end,y)]);path(d,pts,color,3)
 d.rounded_rectangle((end,y-28,end+58,y+28),radius=11,fill=color)
 dashed(d,(equilibrium+29,y-50),(equilibrium+29,y+50),MUTE,1)
 d.line((x0,y+39,x1,y+39),fill=GRID,width=2)
 return end+29

def base(lang,scene,local_t,global_t):
 im=background(scene['kind']);d=ImageDraw.Draw(im)
 idx=next(i for i,s in enumerate(SCENES) if s['id']==scene['id'])
 txt(d,(66,30),'AI TECH REVIEW  /  VIDEO ABSTRACT',22,CYAN,True)
 txt(d,(1534,31),f'{idx+1:02d} / 06',22,MUTE,anchor='ra')
 d.line((66,77,1534,77),fill=GRID,width=1)
 if scene['kind']!='intro':
  size=42 if lang=='ko' else 36
  txt(d,(66,107),scene['title_'+lang],size,INK,True)
 label='노터 리뷰 · 게시물의 중심 논지와 대표 계산' if lang=='ko' else 'NOETHER REVIEW · CENTRAL ARGUMENT AND REPRESENTATIVE CALCULATION'
 txt(d,(66,856),label,17,MUTE)
 txt(d,(1534,856),' · '.join(scene.get('source_ids',[])),17,MUTE,anchor='ra')
 # The web master keeps this dark safe area for native VTT captions.
 total=TIMELINES[lang][-1]['end'];d.rectangle((0,H-5,W*global_t/total,H),fill=CYAN)
 return im,d

def energy_plot(d,box,n,labels=True):
 x0,y0,x1,y1=box
 px=lambda i:x0+(x1-x0)*i/2000;py=lambda z:y1-(z+.15)/9.15*(y1-y0)
 for exponent,label in [(0,'1'),(3,'10³'),(6,'10⁶'),(9,'10⁹')]:
  yy=py(exponent);d.line((x0,yy,x1,yy),fill=GRID,width=1)
  if labels:txt(d,(x0-15,yy),label,22,MUTE,anchor='rm')
 dashed(d,(x0,py(0)),(x1,py(0)),INK,2)
 for key,color in [('euler',COPPER),('verlet',CYAN)]:
  pts=[(px(i),py(math.log10(float(z)))) for i,z in enumerate(ENERGY[key][:n+1])];path(d,pts,color,4);dot(d,pts[-1],color,6)
 return px,py


def darken_region(im,box,amount=.55):
 crop=im.crop(box);base=Image.new('RGB',crop.size,BG);im.paste(Image.blend(crop,base,amount),box);return ImageDraw.Draw(im)

def region_frame(im,box,callback,opacity=1):
 if opacity<=0:return ImageDraw.Draw(im)
 layer=im.copy();callback(ImageDraw.Draw(layer));crop=layer.crop(box)
 if opacity<1:crop=Image.blend(im.crop(box),crop,opacity)
 im.paste(crop,box);return ImageDraw.Draw(im)

def initial_amplitude(d,x0,x1,y,scale,fill=MUTE):
 equilibrium=(x0+x1)/2+30+29
 for xx in (equilibrium-scale,equilibrium+scale):dashed(d,(xx,y-52),(xx,y+40),fill,1,6,6)
 arrow(d,(equilibrium,y+69),(equilibrium+scale,y+69),fill,2,8)
 txt(d,(equilibrium+scale/2,y+79),'A',20,fill,anchor='ma')

def render_frame(lang,scene,local_t,global_t):
 ko=lang=='ko';kind=scene['kind'];im,d=base(lang,scene,local_t,global_t)
 E=lambda name,end=False:event_time(scene,name,end)
 if kind=='intro':
  txt(d,(70,126),'대칭과 보존법칙으로' if ko else 'Using symmetry',49,INK,True)
  txt(d,(70,191),'과학 계산을 검사한다' if ko else 'to test computation',49,INK,True)
  paragraph(d,(74,297),'에너지를 넣지 않았는데,\n계산에서는 왜 진폭이 커질까?' if ko else 'No energy enters.\nWhy does the computed\namplitude grow?',580,35,COPPER,True)
  txt(d,(74,509),'진폭 A: 평형에서 가장 먼 거리' if ko else 'AMPLITUDE A: FARTHEST FROM EQUILIBRIUM',22,MUTE)
  paragraph(d,(74,563),'원 게시물: 대칭에서 보존법칙으로\n과학 계산과 학습 모형의 설계·검증' if ko else 'From symmetry to conservation\nDesign and testing of computation\nand learned models',585,25,MUTE)
  panel(d,(713,147,1530,681));txt(d,(751,178),'정확한 기준 운동' if ko else 'EXACT REFERENCE',27,CYAN,True)
  n=min(150,int(progress(local_t,E('euler'),E('article_question'))*150));tau=n*.1
  spring(d,760,1480,285,math.cos(tau),87,CYAN);initial_amplitude(d,760,1480,285,87,CYAN)
  euler_on=local_t>=E('euler')
  txt(d,(751,414),'전진 오일러 · 한 단계씩 근사 계산' if ko else 'FORWARD EULER · STEP-BY-STEP APPROXIMATION',25,COPPER if euler_on else MUTE,True)
  spring(d,760,1480,520,float(EULER[n,0]),87,COPPER if euler_on else MUTE);initial_amplitude(d,760,1480,520,87,MUTE)
  if n>=27:
   txt(d,(1470,562),'초기 ±A 범위를 넘어선 계산' if ko else 'INITIAL ±A HAS BEEN EXCEEDED',20,COPPER,True,anchor='ra')
  txt(d,(753,630),(f'계산 단계 n = {n:03d} · 같은 시각의 두 상태' if ko else f'COMPUTED STEP n = {n:03d} · SAME MOMENT'),25,INK)
  txt(d,(800,705),'무마찰·무구동 선형 용수철 · 같은 축척 · AI 합성음성: Supertonic 2/F1' if ko else 'UNDAMPED, UNDRIVEN LINEAR SPRING · FIXED SCALE · AI VOICE: SUPERTONIC 2/F1',20,MUTE,anchor='mm')
 elif kind=='principle':
  clock_on=local_t>=E('clock_origins');action_on=local_t>=E('action_definition');theorem_on=local_t>=E('noether_energy')
  # One exact state supplies spring, both bars and the eventual clock event.
  tau=progress(local_t,E('energy_exchange'),E('clock_origins'))*1.5*math.pi
  q=math.cos(tau);u=-math.sin(tau)
  def energy_group(ld):
   panel(ld,(65,182,724,652));txt(ld,(95,210),'정확한 기준 운동의 에너지' if ko else 'ENERGY OF THE EXACT MOTION',26,CYAN,True)
   spring(ld,108,670,333,q,92,CYAN)
   for j,(label,val,color) in enumerate([('운동에너지 T' if ko else 'KINETIC T',u*u,COPPER),('탄성에너지 V' if ko else 'ELASTIC V',q*q,CYAN)]):
    yy=427+j*75;txt(ld,(96,yy),label,23,color,True);ld.rounded_rectangle((276,yy,673,yy+28),radius=4,fill=GRID);ld.rounded_rectangle((276,yy,276+max(1,397*val),yy+28),radius=4,fill=color)
   txt(ld,(97,590),'T + V = E₀ · 초기 에너지' if ko else 'T + V = E₀ · INITIAL ENERGY',29,INK,True)
  d=region_frame(im,(65,182,725,653),energy_group,.5 if clock_on else 1)
  if not clock_on:
   paragraph(d,(840,302),'움직임과 변형 사이에서\n에너지가 오간다.' if ko else 'Energy moves between\nmotion and deformation.',650,37,INK,True)
   txt(d,(1148,514),'합은 그대로' if ko else 'THE SUM STAYS FIXED',35,CYAN,True,anchor='mm')
  else:
   def clock_group(ld):
    panel(ld,(755,182,1534,652));txt(ld,(787,210),'같은 운동, 다른 시간 원점' if ko else 'SAME MOTION, DIFFERENT CLOCK ORIGIN',25,INK,True)
    txt(ld,(787,246),'ω: 고유 각진동수 · τ=ωt: 단위 없는 시간' if ko else 'ω: NATURAL ANGULAR FREQUENCY · τ=ωt: DIMENSIONLESS TIME',18,MUTE)
    x0,x1=825,1486;phase=1.5*math.pi;mx=x0+(x1-x0)*phase/(2*math.pi)
    for row,yy,color in [(0,342,CYAN),(1,529,BLUE)]:
     arrow(ld,(x0,yy),(x1+12,yy),MUTE,2,9);path(ld,[(x,yy-49*math.cos((x-x0)/(x1-x0)*2*math.pi)) for x in np.linspace(x0,x1,250)],color,4);dot(ld,(mx,yy-49*math.cos(phase)),WHITE,7)
     for j in range(3):
      xx=x0+j*(x1-x0)/2;ld.line((xx,yy-5,xx,yy+5),fill=MUTE,width=2);lab=['0','π','2π'][j] if row==0 else ['−π/2','π/2','3π/2'][j];txt(ld,(xx,yy+63),lab,21,MUTE,anchor='ma')
     txt(ld,(787,yy-72),'τ = ωt' if row==0 else 'τ′ = τ − π/2',25,color)
   d=region_frame(im,(755,182,1535,653),clock_group,.35 if action_on else 1)
  if action_on:
   panel(d,(304,653,1493,717),COPPER)
   txt(d,(335,670),'작용' if ko else 'ACTION',24,COPPER,True)
   txt(d,(570,685),'S = ∫ (T − V) dt',34,INK,True,anchor='mm')
   txt(d,(1020,685),'시간 병진 대칭 → 에너지 보존' if ko else 'TIME SYMMETRY → CONSERVED ENERGY',24,COPPER if theorem_on else MUTE,True,anchor='mm')
  else:txt(d,(800,695),'정확한 기준 운동 · 두 에너지의 합은 일정 · E₀: 초기 에너지' if ko else 'EXACT MOTION · THE ENERGY SUM STAYS FIXED · E₀: INITIAL ENERGY',25,INK,anchor='mm')
 elif kind=='step':
  mapping=local_t>=E('state_mapping');phase_on=local_t>=E('phase_plane_name');circle_on=local_t>=E('energy_circle');tangent_on=local_t>=E('euler_tangent');energy_on=local_t>=E('one_percent')
  panel(d,(67,181,720,292));txt(d,(91,193),'같은 순간의 출발 상태' if ko else 'ONE INITIAL PHYSICAL STATE',22,CYAN,True)
  spring(d,106,663,244,1,70,CYAN)
  txt(d,(690,196),'위치 x = A · 속도 v = 0' if ko else 'POSITION x = A · VELOCITY v = 0',18,INK,anchor='ra')
  if mapping:
   txt(d,(101,311),'q = x/A = 1',27,INK,True);txt(d,(445,311),'u = v/(Aω) = 0',27,INK,True)
   txt(d,(800,190),'A: 기준 진폭 · Aω: 기준 속도' if ko else 'A: REFERENCE AMPLITUDE · Aω: REFERENCE SPEED',22,MUTE)
  if phase_on:
   cx,cy,r=400,530,150
   arrow(d,(cx-202,cy),(cx+214,cy),MUTE,2,9);arrow(d,(cx,cy+172),(cx,cy-185),MUTE,2,9)
   txt(d,(cx+230,cy),'q',27,INK,anchor='mm');txt(d,(cx,cy-200),'u',27,INK,anchor='mm')
   dot(d,(cx+r,cy),WHITE,9);txt(d,(cx+r-6,cy+20),'(1, 0)',22,INK,anchor='ra')
   txt(d,(79,700),'위상 평면 · 단위 없는 두 좌표' if ko else 'PHASE PLANE · DIMENSIONLESS COORDINATES',21,CYAN)
   if not circle_on:
    dashed(d,(255,350),(cx+r,cy),MUTE,2,7,7)
    paragraph(d,(812,331),'한순간의 위치·속도 한 쌍을\n한 점에 대응시킨다.' if ko else 'One position–velocity pair\nbecomes one plotted point.',620,32,INK,True)
   else:
    d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=CYAN,width=4);txt(d,(cx,cy-32),'E / E₀ = 1',31,CYAN,True,anchor='mm')
    if not tangent_on:
     txt(d,(817,344),'같은 에너지의 상태들' if ko else 'STATES WITH THE SAME ENERGY',30,CYAN,True)
     txt(d,(817,409),'E / E₀ = q² + u²',39,INK,True)
     paragraph(d,(817,509),'이 원은 물체가 공간에서\n그리는 경로가 아니다.' if ko else 'The circle is not the mass’s\npath through physical space.',620,27,MUTE)
   if tangent_on:
    # Algorithmic update, not an invented physical intermediate trajectory.
    endpoint=(cx+r,cy+r*.1);arrow(d,(cx+r,cy),endpoint,COPPER,4,10);dot(d,endpoint,COPPER,8)
    panel(d,(759,224,1533,686));txt(d,(788,246),'첫 오일러 갱신 · h = ωΔt = 0.1' if ko else 'FIRST EULER UPDATE · h = ωΔt = 0.1',25,COPPER,True)
    txt(d,(789,294),'q₁ = q₀ + h u₀ = 1',30,INK,True);txt(d,(789,336),'u₁ = u₀ − h q₀ = −0.1',30,INK,True)
    txt(d,(789,371),'Δt: 시간 간격 · h: 무차원 간격' if ko else 'Δt: PHYSICAL TIME STEP · h: DIMENSIONLESS STEP',20,MUTE)
    bx0,by0,bx1,by1=993,397,1498,626;scale=25*r;qx0=.94;uytop=-.075
    d.rectangle((bx0,by0,bx1,by1),fill='#061c25',outline=GRID,width=2)
    P=lambda q,u:(bx0+(q-qx0)*scale,by0+(uytop-u)*scale)
    low,high=uytop-(by1-by0)/scale,uytop
    path(d,[P(math.sqrt(1-u*u),u) for u in np.linspace(low,high,150)],CYAN,4)
    tx=P(1,-.1)[0];d.line((tx,by0,tx,by1),fill=COPPER,width=3)
    dot(d,P(math.cos(.1),-math.sin(.1)),CYAN,8);dot(d,P(1,-.1),COPPER,9)
    txt(d,(787,411),'좌표 25배 확대' if ko else '25× ZOOM',22,MUTE)
    txt(d,(787,466),'원 경계' if ko else 'CIRCLE',24,CYAN,True);txt(d,(787,512),'오일러 점' if ko else 'EULER POINT',24,COPPER,True)
    d.rectangle((cx+qx0*r,cy+.075*r,cx+(qx0+(bx1-bx0)/scale)*r,cy+(-uytop+(by1-by0)/scale)*r),outline=WHITE,width=2)
    if energy_on:txt(d,(1155,659),'E₁ / E₀ = 1.01  →  +1%',34,COPPER,True,anchor='mm')
    else:txt(d,(1155,659),'원 바깥: 더 큰 에너지' if ko else 'OUTSIDE THE CIRCLE: HIGHER ENERGY',25,COPPER,True,anchor='mm')
  else:
   txt(d,(1080,440),'일정한 에너지가 계산에도 남을까?' if ko else 'WILL THE CALCULATION KEEP THAT ENERGY?',29,INK,True,anchor='mm')
 elif kind=='comparison':
  euler_on=local_t>=E('euler_final');verlet_on=local_t>=E('verlet_curve');zoom_on=local_t>=E('percent_zoom');meaning_on=local_t>=E('interpret_methods');limit_on=local_t>=E('phase_limit')
  txt(d,(82,183),'앞의 1% 증가를 반복한다 · 같은 초기조건 · h = 0.1' if ko else 'REPEAT THE 1% INCREASE · SAME INITIAL STATE · h = 0.1',24,MUTE,True)
  n=min(2000,int(progress(local_t,E('repeat_one_percent'),E('euler_final'))*2000));x0,y0,x1,y1=137,280,1114,436
  px=lambda i:x0+(x1-x0)*i/2000;py=lambda z:y1-(z+.15)/9.15*(y1-y0)
  def upper(ld):
   txt(ld,(137,233),'에너지 / 초기 에너지 · 로그 눈금' if ko else 'ENERGY / INITIAL ENERGY · LOG SCALE',24,INK,True)
   for ex,lab in [(0,'1'),(3,'10³'),(6,'10⁶'),(9,'10⁹')]:
    yy=py(ex);ld.line((x0,yy,x1,yy),fill=GRID,width=1);txt(ld,(x0-15,yy),lab,22,MUTE,anchor='rm')
   dashed(ld,(x0,py(0)),(x1,py(0)),INK,2)
   for key,color in [('euler',COPPER),*([('verlet',CYAN)] if verlet_on else [])]:
    pts=[(px(i),py(math.log10(float(z)))) for i,z in enumerate(ENERGY[key][:n+1])];path(ld,pts,color,4);dot(ld,pts[-1],color,6)
   txt(ld,(1114,py(0)-27),'정확한 기준 = 1' if ko else 'EXACT REFERENCE = 1',21,INK,anchor='ra')
   txt(ld,(1210,277),'EULER',25,COPPER,True)
   if euler_on:txt(ld,(1210,319),'4.39 × 10⁸',40,COPPER,True)
   txt(ld,(1210,382),'2,000단계의 E/E₀' if ko else 'E/E₀ AT STEP 2,000',20,MUTE)
  d=region_frame(im,(75,224,1535,448),upper,.45 if zoom_on and not meaning_on else 1)
  if not zoom_on:
   txt(d,(140,489),'눈금 한 간격은 1,000배 차이' if ko else 'ONE TICK INTERVAL IS A FACTOR OF 1,000',24,MUTE)
   if verlet_on:
    txt(d,(145,568),'벨레는 기준값 가까이: 작은 차이는 아래에서 확대한다' if ko else 'VERLET STAYS NEAR 1: ENLARGE THE SMALL DIFFERENCE NEXT',26,CYAN,True)
    arrow(d,(625,588),(625,635),CYAN,2,10)
  else:
   txt(d,(137,490),'벨레 상대 에너지 오차 (%) · 선형 눈금' if ko else 'VERLET RELATIVE ENERGY ERROR (%) · LINEAR',24,CYAN,True)
   txt(d,(137,523),'100 × (E/E₀ − 1)',20,MUTE)
   low,high=-.28,0;y0b,y1b=550,650;py2=lambda v:y1b-(v-low)/(high-low)*(y1b-y0b)
   for val in [-.25,-.125,0]:
    yy=py2(val);d.line((x0,yy,x1,yy),fill=GRID,width=1);txt(d,(x0-17,yy),str(val),21,MUTE,anchor='rm')
   pts=[(px(i),py2(float(v-1)*100)) for i,v in enumerate(ENERGY['verlet'])];path(d,pts,CYAN,3);dot(d,pts[-1],CYAN,6)
   txt(d,(1210,519),'VERLET',25,CYAN,True);txt(d,(1210,561),'≤ 0.25%',42,CYAN,True);txt(d,(1210,623),'최대 |E/E₀−1|' if ko else 'MAX |E/E₀−1|',23,MUTE)
  for count in [0,500,1000,1500,2000]:txt(d,(px(count),674),f'{count:,}',21,MUTE,anchor='ma')
  txt(d,(1147,680),'n',25,MUTE)
  note=('작은 에너지 오차만으로 진동 타이밍의 정확성까지 보장하지 않는다' if ko else 'SMALL ENERGY ERROR DOES NOT GUARANTEE CORRECT OSCILLATION TIMING') if limit_on else ('리뷰 자체 계산 · 같은 h · 동일 비용 벤치마크가 아님' if ko else 'REVIEW CALCULATION · SAME h · NOT AN EQUAL-COST BENCHMARK')
  txt(d,(800,711),note,22 if limit_on else 20,COPPER if limit_on else MUTE,anchor='mm')
 elif kind=='learned':
  fn_on=local_t>=E('learn_function');old_symbols=local_t>=E('previous_symbols');symbols_on=local_t>=E('canonical_symbols');ham_on=local_t>=E('hamilton_equations');autonomous=local_t>=E('autonomous_condition');conserved=local_t>=E('continuous_conservation');truth=local_t>=E('true_energy_test');integrate=local_t>=E('numerical_error_test')
  if not fn_on:
   panel(d,(81,209,1519,679));txt(d,(118,243),'앞에서 검사한 것: 계산 방법의 에너지 오차' if ko else 'PREVIOUS TEST: ENERGY ERROR FROM THE NUMERICAL METHOD',29,COPPER,True)
   energy_plot(d,(153,330,952,480),2000)
   txt(d,(1125,401),'이제 검사할 것' if ko else 'NEXT TO TEST',25,MUTE,anchor='mm')
   txt(d,(1125,459),'학습한 모형' if ko else 'THE LEARNED MODEL',29,CYAN,True,anchor='mm')
  else:
   txt(d,(78,190),'해밀토니안 신경망 · 에너지에 해당하는 함수를 배운다' if ko else 'HAMILTONIAN NEURAL NETWORK · LEARN AN ENERGY-LIKE FUNCTION',25,CYAN,True)
   specs=[('운동 데이터' if ko else 'MOTION DATA','상태와 변화' if ko else 'states and changes'),('학습한 함수' if ko else 'LEARNED FUNCTION','Hθ(q, p)' if symbols_on else 'Hθ'),('해밀턴 방정식' if ko else 'HAMILTON’S EQUATIONS',''),('수치 적분' if ko else 'NUMERICAL INTEGRATION','Δt, integrator'),('예측한 상태' if ko else 'COMPUTED STATES','(q[n], p[n])')]
   for j,(label,value) in enumerate(specs):
    visible=j<=1 or (j==2 and ham_on) or (j>=3 and integrate)
    if not visible:continue
    xx=76+j*301;color=CYAN if j<=2 else COPPER
    panel(d,(xx,281,xx+258,441),color if ((j==1 and not ham_on) or(j==2 and ham_on and not integrate) or(j>=3 and integrate)) else GRID)
    txt(d,(xx+129,306),label,23 if ko else 17,color,True,anchor='ma')
    if j==2:
     txt(d,(xx+129,356),'q̇ = ∂Hθ/∂p',25,INK,True,anchor='mm');txt(d,(xx+129,399),'ṗ = −∂Hθ/∂q',25,INK,True,anchor='mm')
    else:txt(d,(xx+129,374),value,25,INK,True,anchor='mm')
    if j and (j<=1 or (j==2 and ham_on) or (j>=3 and integrate)):arrow(d,(xx-38,362),(xx-7,362),color,3,10)
   if old_symbols and not symbols_on:
    txt(d,(800,507),'앞의 위상 평면: q = 정규화 위치 · u = 정규화 속도' if ko else 'PREVIOUS PHASE PLANE: q = NORMALIZED POSITION · u = NORMALIZED VELOCITY',25,INK,anchor='mm')
   elif symbols_on:
    txt(d,(800,507),'지금의 정준 좌표: q = 좌표 · p = 정준 운동량' if ko else 'CANONICAL VARIABLES NOW: q = COORDINATE · p = CANONICAL MOMENTUM',25,INK,anchor='mm')
   if autonomous:txt(d,(800,552),'매끄러운 Hθ · 명시적인 시간 의존성 없음 · 정준 좌표' if ko else 'SMOOTH Hθ · NO EXPLICIT TIME DEPENDENCE · CANONICAL COORDINATES',24,MUTE,anchor='mm')
   if conserved:txt(d,(800,598),'연속시간 해: dHθ/dt = 0' if ko else 'CONTINUOUS-TIME SOLUTION: dHθ/dt = 0',33,CYAN,True,anchor='mm')
   if truth:
    panel(d,(76,643,750,709),CYAN);txt(d,(413,677),'실제 에너지를 배웠는가?' if ko else 'DOES Hθ REPRESENT THE ACTUAL ENERGY?',25,CYAN,True,anchor='mm')
   if integrate:
    panel(d,(790,643,1534,709),COPPER);txt(d,(1160,677),'한 단계씩 계산한 오차는 얼마인가?' if ko else 'HOW MUCH ERROR DOES THE INTEGRATOR ADD?',25,COPPER,True,anchor='mm')
  txt(d,(800,729),'구성도 · 새 학습 실험의 결과가 아님' if ko else 'METHOD SCHEMATIC · NOT A NEW TRAINING RESULT',17,MUTE,anchor='mm')
 elif kind=='conclusion':
  learned_on=local_t>=E('recall_learned_law');design_on=local_t>=E('design_constraints');claim_on=local_t>=E('article_argument');exchange_on=local_t>=E('external_exchange')
  def numerical_recall(ld):
   panel(ld,(70,202,785,491),COPPER);txt(ld,(104,230),'계산 오차 검사' if ko else 'TEST THE NUMERICAL ERROR',29,COPPER,True)
   txt(ld,(126,282),'E/E₀ · 로그 눈금' if ko else 'E/E₀ · LOG SCALE',20,MUTE)
   energy_plot(ld,(160,330,721,431),2000,True)
   txt(ld,(160,454),'0',18,MUTE,anchor='ma');txt(ld,(721,454),'n = 2,000',18,MUTE,anchor='ma')
  d=region_frame(im,(70,202,786,492),numerical_recall,.5 if learned_on and not design_on else 1)
  if learned_on:
   panel(d,(816,202,1530,491),CYAN);txt(d,(851,230),'배운 법칙 검사' if ko else 'TEST THE LEARNED LAW',29,CYAN,True)
   for j,lab in enumerate(['학습 함수' if ko else 'LEARNED Hθ','해밀턴 식' if ko else 'HAMILTON EQS.','수치 계산' if ko else 'INTEGRATION']):
    xx=846+j*220;panel(d,(xx,328,xx+185,423),CYAN if j<2 else COPPER);txt(d,(xx+92,375),lab,24 if ko else 19,INK,True,anchor='mm')
    if j<2:arrow(d,(xx+189,375),(xx+216,375),MUTE,2,8)
   txt(d,(1175,454),'배운 함수 ≠ 정확한 물리라는 보장' if ko else 'A LEARNED FUNCTION STILL NEEDS TESTING',20,MUTE,anchor='mm')
  if design_on:txt(d,(800,545),'대칭으로 설계 조건을 정한다' if ko else 'USE SYMMETRY TO SET DESIGN CONSTRAINTS',36,INK,True,anchor='mm')
  if claim_on:txt(d,(800,604),'보존량으로 실제 예측을 다시 검사한다' if ko else 'TEST THE RESULTING PHYSICAL PREDICTIONS',36,CYAN,True,anchor='mm')
  if exchange_on:txt(d,(800,668),'외부 일·열교환이 있다면 그 교환도 모형에 포함한다' if ko else 'INCLUDE EXTERNAL WORK AND HEAT EXCHANGE WHEN PRESENT',26,COPPER,anchor='mm')
  txt(d,(800,712),'게시물: 대칭에서 보존법칙으로 · AI 합성음성: Supertonic 2/F1' if ko else 'ARTICLE: FROM SYMMETRY TO CONSERVATION · AI VOICE: SUPERTONIC 2/F1',19,MUTE,anchor='mm')
 return im



def timestamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'

def clean_public_text(path,value):
 path.write_text('\n'.join(line.rstrip() for line in value.splitlines()).rstrip()+'\n')

def export_text(lang):
 lines=['WEBVTT','']
 for i,c in enumerate(CUES[lang]):lines.extend([str(i+1),f'{timestamp(c["start"])} --> {timestamp(c["end"])}',c['text'],''])
 clean_public_text(DIST/f'captions-{lang}.vtt','\n'.join(lines))
 disclosure='Supertonic 2 기본 음성 F1으로 기기에서 합성한 AI 음성입니다. 사람의 녹음이나 특정인의 복제 음성이 아닙니다.' if lang=='ko' else 'Machine-generated narration synthesized locally with Supertonic 2 preset F1; not a human recording or a cloned person.'
 transcript=[DATA['title_'+lang],'',disclosure,'']
 for s in TIMELINES[lang]:
  transcript.extend([f'[{timestamp(s["start"])}] {s["title_"+lang]}',s['narration_'+lang],('화면: ' if lang=='ko' else 'Visual: ')+s['visual_'+lang],('식: ' if lang=='ko' else 'Equations: ')+'; '.join(s['equations']),'Sources: '+', '.join(s['source_ids']),''])
 legend=dict(DATA['sources'])
 legend['V']='https://lagrangeweb.web.engr.illinois.edu/var_int/'
 legend['CALC']='https://github.com/Infant83/AI_Tech_Review/blob/main/2026-10-17_noether-symmetry-conservation/artifacts/build_figures.py'
 legend['DERIV']=legend['R'].rstrip('/')+'/#section-6'
 transcript.extend(['출처 코드와 원문' if lang=='ko' else 'Source-code legend and original references'])
 for code,url in legend.items():
  if url.startswith('https://'):transcript.append(code+' = '+url)
 clean_public_text(DIST/f'transcript-{lang}.txt','\n'.join(transcript))
 tl=[{'id':s['id'],'kind':s['kind'],'start':s['start'],'end':s['end'],'title':s['title_'+lang],'narration_duration':s['narration_duration'],'narration':s['narration_'+lang],'visual':s['visual_'+lang],'equations':s['equations'],'sources':s['source_ids'],'source_ids':s['source_ids']} for s in TIMELINES[lang]]
 clean_public_text(DIST/f'timeline-{lang}.json',json.dumps(tl,ensure_ascii=False,indent=2))

def produce(lang,stills_only=False):
 scenes=TIMELINES[lang];total=scenes[-1]['end'];export_text(lang)
 for i,s in enumerate(scenes):
  t=max(.6,s['duration_actual']-2);im=render_frame(lang,s,t,s['start']+t);im.save(QA/f'{lang}-{i+1:02d}-{s["kind"]}.jpg',quality=93)
  # Sentence-specific representative frames expose semantic transitions.
  for j,segment in enumerate(s['speech_segments']):
   t=min(s['duration_actual']-.1,LEAD+segment['start']+.35)
   render_frame(lang,s,t,s['start']+t).save(QA/f'{lang}-{s["id"]}-sentence-{j+1:02d}.jpg',quality=90)
 poster=render_frame(lang,scenes[0],event_time(scenes[0],'article_question'),event_time(scenes[0],'article_question'));poster.save(DIST/f'poster-{lang}.webp',quality=93)
 if stills_only:return
 out=DIST/f'noether-abstract-v4-{lang}.mp4'
 cmd=[FFMPEG,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',str(AUDIO[lang]),'-map_metadata','-1','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart','-shortest',str(out)]
 start=time.monotonic();proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE);nframes=round(total*FPS);idx=0
 try:
  for i in range(nframes):
   t=i/FPS
   while idx<len(scenes)-1 and t>=scenes[idx]['end']:idx+=1
   s=scenes[idx];im=render_frame(lang,s,t-s['start'],t);proc.stdin.write(im.tobytes())
   if i%(FPS*15)==0:print(f'{lang}: {t:.0f}/{total:.1f}s',flush=True)
  proc.stdin.close();err=proc.stderr.read().decode();code=proc.wait()
  if code:raise RuntimeError(err)
 except BaseException:proc.kill();raise
 report={'lang':lang,'duration':total,'frames':nframes,'fps':FPS,'render_seconds':time.monotonic()-start,'file_bytes':out.stat().st_size,'voice_engine':'Supertonic2 F1, local CPU','burn_in_narration_captions':False,'semantic_scheduling':'Exact matching spoken units keyed by semantic cue IDs.','timing':'Sentence WAV durations + .18s natural pauses + .45s scene lead +1.5s final reading hold; no time stretching.'}
 report['renderer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 report['storyboard_sha256']=hashlib.sha256((ROOT/'storyboard.json').read_bytes()).hexdigest()
 report['script_sha256']=hashlib.sha256((ROOT/f'script-{lang}.md').read_bytes()).hexdigest()
 (QA/f'render-{lang}.json').write_text(json.dumps(report,indent=2)+'\n');print(report,flush=True)

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--lang',choices=['ko','en','both'],default='both');parser.add_argument('--stills-only',action='store_true');parser.add_argument('--no-narration',action='store_true');parser.add_argument('--text-only',action='store_true')
 args=parser.parse_args();art_load()
 langs=['ko','en'] if args.lang=='both' else [args.lang]
 for lang in langs:
  # Fail loudly if the author revised a script after the storyboard was built.
  paragraphs=[p.strip() for p in (ROOT/f'script-{lang}.md').read_text().strip().split('\n\n')[1:]]
  assert paragraphs==[s['narration_'+lang] for s in SCENES],f'{lang} script/storyboard mismatch'
  timeline(lang,not args.no_narration);print(lang,'duration',TIMELINES[lang][-1]['end'],flush=True)
  if args.text_only:export_text(lang)
  else:produce(lang,args.stills_only)
if __name__=='__main__':main()
