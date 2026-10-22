/* Keep the picture 16:9. Inline captions follow the native CC selection;
   fullscreen and picture-in-picture retain the browser's caption renderer. */
document.querySelectorAll('.video-abstract').forEach(section=>{
 const video=section.querySelector('video');
 const stage=section.querySelector('.video-stage');
 const dock=section.querySelector('.video-captions');
 const node=video?.querySelector('track[kind="captions"]');
 const button=section.querySelector('.video-enable');
 if(!video||!stage||!dock||!node)return;
 let enhanced=false;
 let nativePresentation=false;
 const track=node.track;
 const render=()=>{
  try{
   const native=nativePresentation||document.fullscreenElement===video||
    document.pictureInPictureElement===video||video.webkitDisplayingFullscreen||
    ['fullscreen','picture-in-picture'].includes(video.webkitPresentationMode);
   const inline=enhanced&&!native;
   const cues=inline&&track.mode==='showing'?[...(track.activeCues||[])]:[];
   const text=cues.map(c=>c.getCueAsHTML?.().textContent??c.text).join('\n');
   dock.textContent=text;
   dock.hidden=!text;
   stage.dataset.inlineCaptions=inline?'true':'false';
  }catch{
   stage.dataset.inlineCaptions='false';
   dock.hidden=true;
  }
 };
 const enable=()=>{
  if(node.readyState===2&&track.cues?.length&&CSS.supports('selector(video::cue)'))enhanced=true;
  render();
 };
 node.addEventListener('load',enable);
 node.addEventListener('error',()=>{enhanced=false;render();});
 track.addEventListener('cuechange',render);
 video.textTracks.addEventListener('change',render);
 ['loadedmetadata','seeked','timeupdate'].forEach(name=>video.addEventListener(name,enable));
 document.addEventListener('fullscreenchange',render);
 video.addEventListener('webkitbeginfullscreen',()=>{nativePresentation=true;render();});
 video.addEventListener('webkitendfullscreen',()=>{nativePresentation=false;render();});
 video.addEventListener('webkitpresentationmodechanged',render);
 video.addEventListener('enterpictureinpicture',()=>{nativePresentation=true;render();});
 video.addEventListener('leavepictureinpicture',()=>{nativePresentation=false;render();});
 button?.addEventListener('click',()=>{
  section.dataset.manualVideo='true';
  button.setAttribute('aria-expanded','true');
  video.focus();
 });
 enable();
});
