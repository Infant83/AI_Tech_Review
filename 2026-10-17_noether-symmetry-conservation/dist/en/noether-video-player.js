/* Explicit reveal for readers who prefer reduced motion; playback stays manual. */
document.querySelectorAll('.video-abstract').forEach(section=>{
 const button=section.querySelector('.video-enable');
 const video=section.querySelector('video');
 if(!button||!video)return;
 const stage=section.querySelector('.video-stage');
 const fullscreen=section.querySelector('.video-fullscreen');
 if(stage?.requestFullscreen&&fullscreen){
  fullscreen.hidden=false;
  video.controlsList.add('nofullscreen');
  fullscreen.addEventListener('click',async()=>{
   try{
    if(document.fullscreenElement===stage)await document.exitFullscreen();
    else await stage.requestFullscreen();
   }catch{video.controlsList.remove('nofullscreen');}
  });
  document.addEventListener('fullscreenchange',()=>{
   fullscreen.textContent=document.fullscreenElement===stage?fullscreen.dataset.exit:fullscreen.dataset.enter;
  });
  document.addEventListener('keydown',event=>{
   if(event.key==='Escape'&&document.fullscreenElement===stage)document.exitFullscreen().catch(()=>{});
  });
 }
 const view=section.querySelector('.video-view');
 view?.addEventListener('toggle',()=>{if(!view.open)video.pause();});
 button.addEventListener('click',()=>{
  section.dataset.manualVideo='true';
  button.setAttribute('aria-expanded','true');
  video.focus();
 });
});
