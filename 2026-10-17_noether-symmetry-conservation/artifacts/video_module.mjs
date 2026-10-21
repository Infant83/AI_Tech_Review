import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');

export function videoModule({lang,artifacts,publicBase='',preview=false}){
 const ko=lang==='ko';
 const manifest=JSON.parse(fs.readFileSync(path.join(artifacts,'video-abstract-manifest.json'),'utf8'));
 if(manifest.status!=='ready'&&!preview)throw Error('Video production is not ready; --video-preview is for local layout QA only.');
 const entry=manifest.languages[lang];
 const files={video:`noether-abstract-${lang}.mp4`,poster:`noether-abstract-poster-${lang}.webp`,captions:`noether-abstract-${lang}.vtt`,transcript:`noether-abstract-transcript-${lang}.txt`};
 for(const [kind,name] of Object.entries(files)){
  const record=entry.assets[kind];
  if(record.file!==name)throw Error(`Unexpected video asset name: ${record.file}`);
  const bytes=fs.readFileSync(path.join(artifacts,name));
  if(bytes.length!==record.bytes||crypto.createHash('sha256').update(bytes).digest('hex')!==record.sha256)throw Error(`Video asset differs from the reviewed manifest: ${name}`);
 }
 const transcript=fs.readFileSync(path.join(artifacts,files.transcript),'utf8');
 if(/(?:\/(?:Users|private|tmp|Volumes)\/|file:\/\/|localhost|127\.0\.0\.1)/i.test(transcript))throw Error('Private location in video transcript.');
 const seconds=Math.ceil(entry.duration_seconds);
 const duration=`${Math.floor(seconds/60)}:${String(seconds%60).padStart(2,'0')}`;
 const base=publicBase||'https://infant83.github.io/AI_Tech_Review/reviews/2026-10-17_noether-symmetry-conservation/';
 const videoURL=base+(ko?'':'en/')+'#video-abstract';
 const label=ko?'비디오 abstract':'Video abstract';
 const summary=ko?'용수철 계산과 학습 모형을 통해, 대칭과 보존량을 설계·검증에 쓰는 이유를 설명합니다.':'A spring calculation and a learned-model construction explain why symmetry and conservation help design and test scientific computation.';
 const posterAlt=ko?'대칭과 보존량으로 과학 계산을 검사하는 영상의 정지 화면':'Still from the video about using symmetry and conservation to test scientific computation';
 const html=`<section class="video-abstract" id="video-abstract" aria-labelledby="video-abstract-title" data-manual-video="false">
 <details class="video-view" open><summary class="video-heading"><h2 id="video-abstract-title">${label}</h2><span class="video-duration">${duration} · ${ko?'한국어':'English'}</span></summary>
 <p class="video-intro">${summary}</p>
 <div class="video-web">
  <div class="video-stage">
   <img class="video-static" src="${files.poster}" alt="${posterAlt}">
   <button class="video-enable" type="button" aria-controls="noether-video" aria-expanded="false">${ko?'영상 플레이어 열기':'Show video player'}</button>
   <video id="noether-video" controls playsinline preload="none" poster="${files.poster}" width="1600" height="900" tabindex="0" aria-label="${ko?'노터 정리 게시물의 핵심 해설':'Video abstract of the Noether review'}">
    <source src="${files.video}" type="video/mp4">
    <track kind="captions" src="${files.captions}" srclang="${lang}" label="${ko?'한국어':'English'}" default>
    <p><a href="${files.video}">${ko?'영상 파일 열기':'Open the video file'}</a></p>
   </video>
   <div class="video-tools"><button class="video-fullscreen" type="button" hidden data-enter="${ko?'전체 화면':'Full screen'}" data-exit="${ko?'전체 화면 종료':'Exit full screen'}">${ko?'전체 화면':'Full screen'}</button></div>
  </div>
  <p class="video-caption">${ko?'진동자는 리뷰 자체 계산, 학습 모형은 방법 구성도입니다. 합성음성을 사용했습니다.':'The oscillator is a teaching calculation; the learned model is a method schematic. Narration uses synthetic speech.'}</p>
  <div class="video-links"><a href="${files.video}" download>MP4</a><a href="${files.captions}" download>${ko?'자막 VTT':'Captions VTT'}</a><a href="${files.transcript}" download>${ko?'시각 설명 내려받기':'Download visual transcript'}</a></div>
  <details class="video-transcript"><summary>${ko?'대본과 장면의 시각 설명 읽기':'Read the script and visual description'}</summary><pre>${esc(transcript)}</pre></details>
  <details class="video-production"><summary>${ko?'영상의 근거와 제작 정보':'Sources and production'}</summary><p>${ko?'본문의 진동자 계산과 해밀토니안 신경망 설명을 바탕으로 식·데이터·도식을 코드로 그린 영상입니다. 개념 배경은 AI 생성 정지 이미지를 재사용했습니다. 음성은 Supertonic 2 F1로 합성했습니다. 진동자는 교육용 계산이며 학습 모형은 구성도입니다.':'Equations, data and diagrams are rendered from code using the article’s oscillator calculation and Hamiltonian-network discussion. The conceptual background reuses an AI-generated still. Narration is synthesized with Supertonic 2 F1. The oscillator is a teaching calculation and the learned model is a schematic.'}</p></details>
  <noscript><p><a href="${files.video}">${ko?'영상 파일 열기':'Open the video file'}</a></p></noscript>
 </div>
 <div class="video-print"><figure><a href="${videoURL}"><img src="${files.poster}" alt="${posterAlt}"></a><figcaption>${ko?'영상 요약':'Video abstract'} · ${duration} · ${ko?'합성음성 사용':'Synthetic narration'}. <a href="${videoURL}">${ko?'웹에서 영상과 시각 설명 보기':'Watch and read the visual transcript online'}</a></figcaption></figure></div>
</details></section>`;
 return {html,assets:[...Object.values(files),'noether-video-player.js'],version:manifest.version,duration_seconds:entry.duration_seconds};
}
