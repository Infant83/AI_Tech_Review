import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

const source = await readFile(new URL('./reader.mjs', import.meta.url), 'utf8');
const start = source.indexOf('function readerFocusMode(');
const focusSource = start < 0 ? '' : source.slice(start, source.indexOf('async function renderPage(', start));
const renderSource = source.slice(source.indexOf('async function renderPage('), source.indexOf('async function ensurePage('));
const rasterSource = source.slice(source.indexOf('function readerRasterPlan('), source.indexOf('function readerBitmapPixels('));
function deferred() { let resolve, reject; const promise = new Promise((a,b) => { resolve=a; reject=b; }); return {promise,resolve,reject}; }
function harness({ native = null } = {}) {
  const listeners = {}, timers = new Map(), calls = [];
  let nextTimer=0, now=0;
  const icon = { href:'#i-fullscreen', setAttribute(name,value) { this[name]=value; } };
  const button = { attributes:{}, addEventListener(name,listener) { listeners['button:'+name]=listener; },
    setAttribute(name,value) { this.attributes[name]=value; }, querySelector:()=>icon, focus() { calls.push('focus'); } };
  const area = { clientWidth:1600, scrollLeft:17, scrollTop:23, hidden:false };
  const sheet = {style:{}};
  const canvas = { style:{}, getContext:()=>({}) };
  const elements = { 'toggle-fullscreen':button, 'page-area':area, 'page-sheet':sheet,
    'pdf-canvas':canvas, 'ink-canvas':{...canvas,style:{}}, zoom:{value:'1'}, 'loading-state':{hidden:true} };
  const root = { dataset:{} };
  const document = { documentElement:root, fullscreenElement:null, fullscreenEnabled:true, activeElement:button,
    querySelector:()=>null, addEventListener(name,listener,options) { const previous=listeners[name];listeners[name]=previous
      ? options?.capture ? event=>{listener(event);previous(event);} : event=>{previous(event);listener(event);} : listener; },
    exitFullscreen:async()=>{ calls.push('exit'); document.fullscreenElement=null; } };
  if(native)root.requestFullscreen=()=>{calls.push('request');return native(document,root);};
  const page = {getViewport:({scale})=>({width:600*scale,height:800*scale}),render:()=>({promise:Promise.resolve(),cancel(){}})};
  const context = { document, window:{devicePixelRatio:2,addEventListener(name,listener) { listeners['window:'+name]=listener; }, scrollTo(){}},
    $:id=>elements[id], t:key=>key, finishStroke:()=>calls.push('finish'), pdf:{getPage:async()=>page}, current:{fingerprint:'public'},
    active:null,busy:false,pageNumber:3,renderSequence:0,renderTask:null,baseWidth:595,pageAspect:1.414,cssWidth:595,cssHeight:842,pixelRatio:1,
    pdfCanvas:canvas,inkCanvas:elements['ink-canvas'],sheet,devicePixelRatio:2,innerWidth:1600,
    controls(){},drawInk:()=>calls.push('draw'),showError:()=>calls.push('error'),
    readerFocusGeneration:0,readerNativeFullscreen:false,readerFocusReturn:null,readerResizePending:false,readerResizeAnchorPending:false,resizeTimer:null,
    readerFocusAnchor:null,readerFocusInputEpoch:0,readerExpectedNativeExit:0,documentOpenGeneration:0,
    readerViews:new Map(),readerMountedViews:new Set(),readerPositionTimer:null,readerScrollPending:false,queueReaderNeighbours(){},
    readerResizePending:false,readerResizeAnchorPending:false,scheduleReaderVisible(){},
    getComputedStyle:()=>({paddingLeft:'4px',paddingRight:'4px'}),
    setTimeout(callback,delay) { const id=++nextTimer;timers.set(id,{callback,at:now+delay});return id; },
    clearTimeout(id) { timers.delete(id); },
  };
  vm.createContext(context);vm.runInContext(rasterSource+focusSource+renderSource,context);
  if(context.initializeReaderFullscreen)context.initializeReaderFullscreen();
  return {context,document,root,button,icon,area,elements,calls,listeners,
    advance(ms) { now+=ms;for(const [id,timer]of [...timers])if(timer.at<=now){timers.delete(id);timer.callback();} },
    tick:()=>new Promise(resolve=>setImmediate(resolve))};
}

function geometry(h) {
  const main={scrollLeft:0,scrollTop:0,clientHeight:740,scrollHeight:740};h.elements['reader-main']=main;
  const width=()=>h.root.dataset.readerFocus==='true'?1400:1000;
  h.context.window.innerHeight=800;h.context.window.scrollX=0;h.context.window.scrollY=500;
  Object.defineProperty(h.context.window,'innerWidth',{get:width});
  h.context.window.scrollTo=({left=0,top=0})=>{h.context.window.scrollX=left;h.context.window.scrollY=Math.max(0,top);};
  h.context.window.scrollBy=({left=0,top=0})=>h.context.window.scrollTo({left:h.context.window.scrollX+left,top:h.context.window.scrollY+top});
  h.area.scrollTop=0;h.area.scrollLeft=0;
  Object.defineProperty(h.area,'clientWidth',{get:width});
  Object.defineProperty(h.area,'clientHeight',{get:()=>h.root.dataset.readerFocus==='true'?740:h.context.cssHeight+80});
  Object.defineProperty(h.area,'scrollHeight',{get:()=>h.context.cssHeight+80});
  Object.defineProperty(h.area,'scrollWidth',{get:()=>Math.max(width(),h.context.cssWidth+8)});
  const rect=(left,top,right,bottom)=>({left,top,right,bottom,width:right-left,height:bottom-top});
  h.area.getBoundingClientRect=()=>h.root.dataset.readerFocus==='true'?rect(0,60,width(),800):rect(0,136-h.context.window.scrollY,width(),136+h.area.clientHeight-h.context.window.scrollY);
  h.context.sheet.getBoundingClientRect=()=>{
    const focus=h.root.dataset.readerFocus==='true',left=(focus?4:(width()-h.context.cssWidth)/2)-h.area.scrollLeft;
    const top=(focus?68:166-h.context.window.scrollY)-h.area.scrollTop;
    return rect(left,top,left+h.context.cssWidth,top+h.context.cssHeight);
  };
  const header={getBoundingClientRect:()=>rect(0,0,width(),h.root.dataset.readerFocus==='true'?60:136)};
  h.document.querySelector=selector=>selector==='.reader-header'?header:null;
  h.elements['page-controls']={hidden:false,getBoundingClientRect:()=>rect(0,740,160,800)};
  h.context.cssWidth=992;h.context.cssHeight=992*4/3;
  const normalizedCenter=()=>{
    const paper=h.context.sheet.getBoundingClientRect(),top=h.root.dataset.readerFocus==='true'?60:136;
    return {x:(width()/2-paper.left)/paper.width,y:((top+740)/2-paper.top)/paper.height};
  };
  return {main,normalizedCenter};
}

test('reader focus fills the app viewport and retains one accessible exit without changing page or zoom',async()=>{
  const h=harness();assert.equal(typeof h.context.toggleReaderFullscreen,'function');
  h.listeners['button:click']();
  assert.equal(h.root.dataset.readerFocus,'true');assert.equal(h.button.attributes['aria-pressed'],'true');
  assert.equal(h.button.attributes['aria-label'],'exitFullscreen');assert.equal(h.icon.href,'#i-fullscreen-exit');
  assert.equal(h.context.pageNumber,3);assert.equal(h.elements.zoom.value,'1');
  h.listeners['button:click']();
  assert.equal(h.root.dataset.readerFocus,'false');assert.equal(h.icon.href,'#i-fullscreen');
});

test('cached HTML without the new fullscreen button still initializes and renders normally',async()=>{
  const h=harness();delete h.elements['toggle-fullscreen'];
  assert.doesNotThrow(()=>h.context.initializeReaderFullscreen());
  await h.context.renderPage(false);
  assert.equal(h.context.cssWidth,1100);assert.equal(h.root.dataset.readerFocus,undefined);
});

test('native fullscreen is requested inside the click and denial retains the usable app fallback',async()=>{
  const h=harness({native:()=>Promise.reject(Error('not supported'))});
  assert.equal(typeof h.context.toggleReaderFullscreen,'function');
  h.listeners['button:click']();assert.ok(h.calls.includes('request'));
  await h.tick();assert.equal(h.root.dataset.readerFocus,'true');
  h.listeners['button:click']();assert.equal(h.root.dataset.readerFocus,'false');
});

test('a native request completing after exit cannot reopen focus mode and native OS exit restores the controls',async()=>{
  const held=deferred(),h=harness({native:()=>held.promise});
  assert.equal(typeof h.context.toggleReaderFullscreen,'function');
  h.listeners['button:click']();h.listeners['button:click']();
  h.document.fullscreenElement=h.root;held.resolve();await h.tick();
  assert.equal(h.root.dataset.readerFocus,'false');assert.ok(h.calls.includes('exit'));
  const live=harness({native:async(document,root)=>{document.fullscreenElement=root;}});
  live.listeners['button:click']();await live.tick();live.listeners.fullscreenchange();
  live.document.fullscreenElement=null;live.listeners.fullscreenchange();
  assert.equal(live.root.dataset.readerFocus,'false');
});

test('an old enter completion cannot exit a newer native session',async()=>{
  const first=deferred();let requests=0;
  const h=harness({native:async(document,root)=>{if(++requests===1)await first.promise;document.fullscreenElement=root;}});
  h.listeners['button:click']();h.listeners['button:click']();h.listeners['button:click']();await h.tick();
  first.resolve();await h.tick();
  assert.equal(h.root.dataset.readerFocus,'true');assert.equal(h.document.fullscreenElement,h.root);
  assert.equal(h.calls.filter(value=>value==='exit').length,0);
});

test('an earlier pending native exit cannot close a newly entered app focus mode',async()=>{
  const held=deferred(),h=harness({native:async(document,root)=>{document.fullscreenElement=root;}});
  h.listeners['button:click']();await h.tick();h.listeners.fullscreenchange();
  h.document.exitFullscreen=async()=>{await held.promise;h.document.fullscreenElement=null;};
  h.listeners['button:click']();h.listeners['button:click']();
  held.resolve();await h.tick();h.listeners.fullscreenchange();
  assert.equal(h.root.dataset.readerFocus,'true');
});

test('failed native exits clear their own token while retaining a newer pending exit',async()=>{
  for(const synchronous of [false,true]) {
    const h=harness({native:async(document,root)=>{document.fullscreenElement=root;}});
    h.listeners['button:click']();await h.tick();h.listeners.fullscreenchange();
    h.document.exitFullscreen=()=>{if(synchronous)throw Error('denied');return Promise.reject(Error('denied'));};
    h.listeners['button:click']();await h.tick();assert.equal(h.context.readerExpectedNativeExit,0);
    h.listeners['button:click']();h.document.fullscreenElement=null;h.listeners.fullscreenchange();
    assert.equal(h.root.dataset.readerFocus,'false');
  }
  const first=deferred(),second=deferred(),h=harness({native:async(document,root)=>{document.fullscreenElement=root;}});let exits=0;
  h.listeners['button:click']();await h.tick();h.listeners.fullscreenchange();
  h.document.exitFullscreen=()=>++exits===1?first.promise:second.promise;
  h.listeners['button:click']();h.listeners['button:click']();h.listeners['button:click']();
  const latest=h.context.readerExpectedNativeExit;first.reject(Error('old request denied'));await h.tick();
  assert.equal(h.context.readerExpectedNativeExit,latest);
  h.listeners['button:click']();h.document.fullscreenElement=null;second.resolve();await h.tick();h.listeners.fullscreenchange();
  assert.equal(h.root.dataset.readerFocus,'true');
});

test('mode changes keep the same normalized visible document point through the new render',async()=>{
  const h=harness(),view=geometry(h),before=view.normalizedCenter();
  h.listeners['button:click']();h.advance(180);await h.tick();
  const focused=view.normalizedCenter();
  assert.ok(Math.abs(focused.y-before.y)<1e-9);assert.ok(Math.abs(focused.x-before.x)<1e-9);
  h.listeners['button:click']();h.advance(180);await h.tick();
  assert.ok(Math.abs(view.normalizedCenter().y-before.y)<1e-9);
});

test('pending position restoration never overrides a new document, page, generation, or user scroll/input',async()=>{
  for(const change of [h=>{h.context.current={...h.context.current};},h=>{h.context.pageNumber++;},
    h=>{h.context.documentOpenGeneration++;},h=>{h.area.scrollTop=123;},h=>{h.listeners.wheel?.({type:'wheel'});}]) {
    const h=harness();geometry(h);h.listeners['button:click']();change(h);
    const chosen=h.area.scrollTop;h.advance(180);await h.tick();
    assert.equal(h.area.scrollTop,chosen);
  }
});

test('position restoration also rejects new document or input intent while the replacement canvas is rendering',async()=>{
  for(const change of [h=>{h.context.current={...h.context.current};},h=>{h.context.pageNumber++;},
    h=>{h.context.documentOpenGeneration++;},h=>{h.area.scrollTop=88;h.listeners.wheel({type:'wheel'});},
    h=>{h.area.scrollTop=97;}]) {
    const held=deferred(),entered=deferred(),h=harness();geometry(h);
    h.context.pdf={getPage:async()=>({getViewport:({scale})=>({width:600*scale,height:800*scale}),
      render:()=>{entered.resolve();return {promise:held.promise,cancel(){}};}})};
    h.listeners['button:click']();h.advance(180);await entered.promise;
    change(h);const chosen=h.area.scrollTop;held.resolve();await h.tick();
    assert.equal(h.area.scrollTop,chosen);
  }
});

test('rapid mode toggles coalesce the original position until one final render',async()=>{
  const h=harness(),view=geometry(h),before=view.normalizedCenter();
  h.listeners['button:click']();h.context.window.scrollY=0;h.listeners['button:click']();h.advance(180);await h.tick();
  assert.ok(Math.abs(view.normalizedCenter().y-before.y)<1e-9);
});

test('a superseded in-flight focus render cannot consume the next mode position restoration',async()=>{
  const held=deferred(),entered=deferred(),h=harness(),view=geometry(h),before=view.normalizedCenter();let renders=0;
  h.context.pdf={getPage:async()=>({getViewport:({scale})=>({width:600*scale,height:800*scale}),
    render:()=>{renders++;if(renders===1)entered.resolve();return {promise:renders===1?held.promise:Promise.resolve(),cancel(){}};}})};
  h.listeners['button:click']();h.advance(180);await entered.promise;
  h.listeners['button:click']();held.resolve();await h.tick();h.advance(180);await h.tick();
  assert.equal(renders,2);assert.equal(h.root.dataset.readerFocus,'false');
  assert.ok(Math.abs(view.normalizedCenter().y-before.y)<1e-9);
});

test('Escape closes app focus while an open dialog keeps its own Escape behavior',()=>{
  const h=harness();assert.equal(typeof h.context.toggleReaderFullscreen,'function');
  h.listeners['button:click']();h.document.querySelector=()=>({open:true});
  h.listeners.keydown({key:'Escape',preventDefault(){}});assert.equal(h.root.dataset.readerFocus,'true');
  h.document.querySelector=()=>null;h.listeners.keydown({key:'Escape',preventDefault(){}});
  assert.equal(h.root.dataset.readerFocus,'false');
});

test('resize bursts defer one final render until an active stroke or current render finishes',async()=>{
  const h=harness();assert.equal(typeof h.context.scheduleReaderResize,'function');
  h.context.active={id:'stroke',points:[{x:.2,y:.3}]};
  h.context.scheduleReaderResize();h.context.scheduleReaderResize();h.advance(180);
  assert.equal(h.calls.includes('draw'),false);assert.equal(h.context.readerResizePending,true);
  assert.deepEqual(h.context.active.points,[{x:.2,y:.3}]);
  h.context.active=null;h.context.busy=true;h.context.scheduleReaderResize();h.advance(180);
  assert.equal(h.calls.includes('draw'),false);
  h.context.busy=false;h.context.scheduleReaderResize();h.advance(180);await h.tick();
  assert.equal(h.calls.filter(value=>value==='draw').length,1);assert.equal(h.context.readerResizePending,false);
});

test('finishing the actual stroke drains a deferred resize without discarding its normalized points',async()=>{
  const h=harness(),points=[{x:.2,y:.3,p:.5}],ink=[{id:'ink',points}];
  h.elements['finger-draw']={checked:false};
  Object.assign(h.context,{tool:'pen',active:{id:1,page:3,before:[]},state:()=>ink,historyEntry(){},markDirty(){},flush:async()=>true,requestInk(){}});
  vm.runInContext(source.slice(source.indexOf('function finishStroke('),source.indexOf('function chooseTool(')),h.context);
  h.context.scheduleReaderResize();h.advance(180);assert.equal(h.calls.includes('draw'),false);
  h.context.finishStroke();h.advance(180);await h.tick();
  assert.equal(h.calls.filter(value=>value==='draw').length,1);
  assert.deepEqual(ink[0].points,points);assert.equal(h.context.readerResizePending,false);
});

test('focus rendering uses actual CSS padding and keeps canvas limits and normalized ink untouched',async()=>{
  const h=harness();
  h.root.dataset.readerFocus='true';h.elements.zoom.value='1.5';
  await h.context.renderPage(false);
  assert.equal(h.context.cssWidth,(1600-8)*1.5);
  assert.ok(h.context.pixelRatio*h.context.cssWidth<=4096);
  assert.ok(h.context.pixelRatio**2*h.context.cssWidth*h.context.cssHeight<=10000000);
  assert.equal(h.context.pageNumber,3);assert.equal(h.area.scrollTop,23);
  h.root.dataset.readerFocus='false';await h.context.renderPage(false);
  assert.equal(h.context.cssWidth,1100*1.5);
});
