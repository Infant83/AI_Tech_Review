import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { clamp, normalizedPoint } from './ink-core.mjs';
const source = fs.readFileSync(new URL('./reader.mjs', import.meta.url), 'utf8');
const section = (start, end) => { const a=source.indexOf(start),b=source.indexOf(end,a+start.length);assert.ok(a>=0&&b>a,start);return source.slice(a,b); };
const continuous = section('const READER_BITMAP_BUDGET', 'function readerFocusMode(');
const raster = section('function readerRasterPlan(', 'function readerDesiredPixelRatio(');
const rendering = section('async function renderPage(', 'async function ensurePage(');
const loading = section('async function ensurePage(', 'async function goPage(');
const drawing = section('function drawStroke(', 'function chooseTool(');
const pointerDown = section('function onInkPointerDown(', 'function onInkPointerMove(');
const pointGeometry = section('function pointerPoint(', 'function eraseAt(');
const applyNotebook = section('async function applyNotebook(', 'async function exportPDF(');
const pageNavigation = section('async function goPage(', 'function renderBookmarks(');
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
const tick=()=>new Promise(resolve=>setImmediate(resolve));

function harness({count=25,failPage=null,dpr=3,scale=1,aspect=number=>number===4?.75:1.414}={}) {
  let rectReads=0,nextTimer=0;const timers=new Map(),requests=[],cleanups=[],strokes=new Map(),failures=[];
  const noop=()=>{};
  const context2d=()=>({setTransform:noop,clearRect:noop,beginPath:noop,arc:noop,fill:noop,moveTo:noop,lineTo:noop,stroke:noop});
  class Node {
    constructor(tag='div'){this.tagName=tag.toUpperCase();this.dataset={};this.style={};this.children=[];this.parentNode=null;this.attributes={};this.listeners={};this.width=0;this.height=0;this.id='';this.scrollTop=0;this.scrollLeft=0;this.hidden=false;this.classes=new Set();this.classList={toggle:(name,on)=>on?this.classes.add(name):this.classes.delete(name)};}
    append(...children){for(const child of children){if(child.tagName==='#FRAGMENT'){this.append(...[...child.children]);continue;}child.remove();child.parentNode=this;this.children.push(child);}}
    prepend(...children){for(const child of [...children].reverse()){child.remove();child.parentNode=this;this.children.unshift(child);}}
    replaceChildren(...children){this.children.forEach(c=>{c.parentNode=null;});this.children=[];this.append(...children);}
    remove(){if(this.parentNode){const p=this.parentNode;this.parentNode=null;p.children=p.children.filter(c=>c!==this);}}
    setAttribute(name,value){this.attributes[name]=String(value);if(name==='id')this.id=String(value);}
    removeAttribute(name){delete this.attributes[name];if(name==='id')this.id='';}
    addEventListener(name,handler){this.listeners[name]=handler;}
    getContext(){return this.ctx ||= context2d();}
    setPointerCapture(){} releasePointerCapture(){}
    get clientWidth(){return this===area?390:Number.parseFloat(this.style.width)||390;}
    get clientHeight(){return this===area?660:Number.parseFloat(this.style.height)||0;}
    get scrollHeight(){return this===area?this.children.reduce((sum,c)=>sum+(Number.parseFloat(c.style.height)||0)+24,16):this.clientHeight;}
    get scrollWidth(){return this===area?Math.max(390,...this.children.map(c=>Number.parseFloat(c.style.width)||0)):this.clientWidth;}
    getBoundingClientRect(){rectReads++;if(this===area)return {left:0,right:390,top:40,bottom:700,width:390,height:660};
      if(this.tagName==='CANVAS')return this.parentNode.getBoundingClientRect();
      const siblings=this.parentNode?.children||[],i=siblings.indexOf(this);
      const top=48+siblings.slice(0,i).reduce((sum,c)=>sum+(Number.parseFloat(c.style.height)||0)+24,0)-area.scrollTop;
      const width=Number.parseFloat(this.style.width)||0,height=Number.parseFloat(this.style.height)||0;
      return {left:-area.scrollLeft,right:width-area.scrollLeft,top,bottom:top+height,width,height};}
    closest(selector){if(selector==='.reader-page')return this.dataset.page?this:this.parentNode?.closest(selector);return null;}
  }
  const area=new Node(),root={dataset:{readerFocus:'true'}},elements={'page-area':area,zoom:{value:'1'},'finger-draw':{checked:false},'loading-state':{hidden:true}};
  const document={documentElement:root,createElement:tag=>new Node(tag),createDocumentFragment:()=>new Node('#fragment'),querySelector:()=>null,querySelectorAll:()=>[]};
  const initial=new Node();elements['page-sheet']=initial;
  const ctx={console,document,window:{devicePixelRatio:dpr,visualViewport:{scale},scrollX:0,scrollY:0,scrollTo:noop,addEventListener:noop},
    $:id=>{if(elements[id])return elements[id];let found=null;const find=n=>{if(n.id===id)found=n;n.children.forEach(find);};area.children.forEach(find);return found;},
    current:{fingerprint:'public-pdf',pageCount:count},pdf:null,documentOpenGeneration:1,readerInkEpoch:0,pageNumber:1,tool:'pen',permissions:{role:'local'},
    active:null,busy:false,renderTask:null,renderSequence:0,readerFocusAnchor:null,readerFocusGeneration:0,readerFocusInputEpoch:0,readerResizePending:false,readerResizeAnchorPending:false,resizeTimer:null,
    sheet:initial,pdfCanvas:new Node('canvas'),inkCanvas:new Node('canvas'),cssWidth:595,cssHeight:842,baseWidth:595,pageAspect:1.414,pixelRatio:1,drawingFrame:0,
    pages:new Map(),histories:new Map(),dirty:new Map(),versions:new Map(),retiredIds:new Set(),color:'#123456',mutationRevision:0,
    t:x=>x,clamp,normalizedPoint,clone:structuredClone,uid:()=>`ink-${Math.random()}`,ownStroke:noop,
    canAddInk:()=>true,canEraseStroke:()=>true,controls:noop,finishStroke:noop,
    readerFocusMode:()=>true,readerVisibleViewport:()=>({left:0,right:390,top:40,bottom:700}),
    readerAnchorCurrent:()=>false,captureReaderFocusAnchor:()=>null,restoreReaderFocusAnchor:noop,readerScrollOffsets:()=>[0,0,area.scrollLeft,area.scrollTop,0,0],
    bindReaderInk:noop,requestAnimationFrame:fn=>{const id=++nextTimer;timers.set(id,fn);return id;},
    setTimeout:(fn)=>{const id=++nextTimer;timers.set(id,fn);return id;},clearTimeout:id=>timers.delete(id),
    getComputedStyle:()=>({paddingLeft:'4px',paddingRight:'4px'}),
    storage:{loadPage:async(_,n)=>structuredClone(strokes.get(n)||[])},storageFailure:()=>failures.push('storage'),showError:()=>failures.push('render'),
    markDirty:(n=ctx.pageNumber)=>{ctx.dirty.set(n,1);},markMeta:()=>{ctx.mutationRevision++;},
    state:()=>ctx.pages.get(ctx.pageNumber)||[],history:()=>{let h=ctx.histories.get(ctx.pageNumber);if(!h)ctx.histories.set(ctx.pageNumber,h={undo:[],redo:[]});return h;},
    flush:async()=>true,scheduleReaderResize:noop,eraseAt:noop,validateNotebook:v=>v,renderBookmarks:noop,status:noop,signal:noop,currentInfo:()=>({}),
    storageFailure:()=>failures.push('storage'),
  };
  elements['pen-width']={value:'2'};
  ctx.pdf={getPage:async number=>{requests.push(number);if(number===failPage)throw Error('page failed');return {getViewport:({scale})=>({width:600*scale,height:600*aspect(number)*scale}),cleanup:()=>cleanups.push(number),render:()=>({promise:Promise.resolve(),cancel(){}})};}};
  vm.createContext(ctx);vm.runInContext(continuous+drawing+loading+rendering+pageNavigation+pointGeometry+pointerDown+applyNotebook,ctx);
  vm.runInContext('globalThis.views=readerViews;globalThis.mounted=readerMountedViews;globalThis.waitNeighbours=()=>readerNeighbourQueue;globalThis.pixelBudget=READER_BITMAP_BUDGET;',ctx);
  return {ctx,area,elements,requests,cleanups,strokes,failures,timers,get rectReads(){return rectReads;},Node,
    async render(){await ctx.renderPage();await ctx.waitNeighbours();},
    async settle(){await tick();await ctx.waitNeighbours();},
    pointer(view=ctx.views.get(ctx.pageNumber),extra={}){return {type:'pointerdown',pointerType:'mouse',button:0,buttons:1,pointerId:9,currentTarget:view.inkCanvas,target:view.inkCanvas,clientX:100,clientY:view.sheet.getBoundingClientRect().top+80,pressure:.5,preventDefault(){},...extra};},
  };
}

test('raster plans preserve DPR3 and native pinch detail while enforcing exact rounded pixel and dimension caps',()=>{
 const c=vm.createContext({});vm.runInContext(raster,c);
 const fit=c.readerRasterPlan(370,523,3,8_000_000),pinch=c.readerRasterPlan(370,523,6,8_000_000);
 assert.equal(fit.ratio,3);assert.equal(pinch.ratio,6);assert.ok(pinch.width>fit.width);
 for(const [w,h,d,limit]of [[2399.5,3393.6,6,8_000_000],[400.1,10_000,4,1_000_000],[9000,3000,9,8_000_000]]){
  const p=c.readerRasterPlan(w,h,d,limit);assert.ok(p.width<=4096&&p.height<=4096);assert.ok(p.pixels<=limit);assert.equal(p.pixels,p.width*p.height);
 }
});

test('a 10000-page PDF renders only the active page and adjacent preview and owns at most three canvas pairs',async()=>{
 const h=harness({count:10_000});await h.render();
 assert.equal(h.ctx.views.size,10_000);assert.equal(h.area.children.length,10_000);
 assert.deepEqual(h.requests,[1,2]);assert.equal(h.ctx.mounted.size,2);assert.ok(h.ctx.readerBitmapPixels()<=h.ctx.pixelBudget);
 await h.ctx.goPage(5000);await h.settle();
 assert.deepEqual([...h.ctx.mounted].map(v=>v.number).sort((a,b)=>a-b),[4999,5000,5001]);
 assert.ok(h.cleanups.includes(1)&&h.cleanups.includes(2));assert.ok(h.ctx.readerBitmapPixels()<=20_000_000);
 assert.equal(h.ctx.sheet.dataset.page,'5000');assert.equal(h.ctx.sheet.id,'page-sheet');
});

test('scrolling directly past an unprefetched page loads its saved ink before allowing its first stroke',async()=>{
 const h=harness();h.strokes.set(3,[{id:'saved-page3',color:'#112233',width:.003,points:[{x:.1,y:.2,p:.5}]}]);await h.render();
 const third=h.ctx.views.get(3);assert.equal(h.ctx.pages.has(3),false);
 h.area.scrollTop=third.sheet.getBoundingClientRect().top-48+200;const reads=h.rectReads;h.ctx.readerVisibleChanged();await h.settle();
 assert.equal(h.ctx.pageNumber,3);assert.equal(third.ready,true);assert.ok(h.ctx.pages.has(3));
 assert.equal(h.ctx.pages.get(3)[0].id,'saved-page3');assert.ok(h.rectReads-reads<35,'active-page selection uses bounded geometry lookups');
 h.ctx.onInkPointerDown(h.pointer(third));assert.equal(h.ctx.active.page,3);assert.equal(h.ctx.pages.get(3).length,2);
 h.ctx.finishStroke();assert.ok(h.ctx.dirty.has(3));assert.equal(h.ctx.pages.get(1).length,0);
});

test('a pointer selects the actual adjacent page synchronously and scrolling cannot switch geometry during that stroke',async()=>{
 const h=harness();await h.render();const second=h.ctx.views.get(2);h.ctx.onInkPointerDown(h.pointer(second));
 assert.equal(h.ctx.active.page,2);assert.equal(h.ctx.pageNumber,2);const width=h.ctx.cssWidth,canvas=h.ctx.inkCanvas;
 h.area.scrollTop=3000;h.ctx.readerVisibleChanged();assert.equal(h.ctx.pageNumber,2);assert.equal(h.ctx.cssWidth,width);assert.equal(h.ctx.inkCanvas,canvas);
 h.ctx.finishStroke();assert.equal(h.ctx.pages.get(2).length,1);assert.ok(h.ctx.histories.get(2).undo.length);
});

test('failed adjacent previews preserve the active page, ink and edit lock',async()=>{
 const h=harness({failPage:2});h.strokes.set(1,[{id:'local',color:'#123456',width:.002,points:[{x:.1,y:.2,p:.5}]}]);await h.render();
 assert.equal(h.ctx.busy,false);assert.equal(h.ctx.views.get(1).ready,true);assert.equal(h.ctx.pages.get(1)[0].id,'local');assert.deepEqual(h.failures,[]);
});

test('a late page read cannot populate another document or enable stale input',async()=>{
 const h=harness(),held=deferred();h.ctx.storage.loadPage=()=>held.promise;
 const loading=h.ctx.ensurePage(5);h.ctx.current={fingerprint:'another',pageCount:25};h.ctx.documentOpenGeneration++;
 held.resolve([{id:'old'}]);assert.equal(await loading,false);assert.equal(h.ctx.pages.has(5),false);
});

test('eviction waits for a cancelled PDF render before cleaning its page resources',async()=>{
 const h=harness();await h.render();const view=h.ctx.views.get(2),held=deferred();let cancelled=0,cleaned=0;
 view.renderTask={promise:held.promise,cancel(){cancelled++;}};view.pdfPage={cleanup(){cleaned++;}};
 const release=h.ctx.releaseReaderView(view);assert.equal(cancelled,1);assert.equal(cleaned,0);assert.equal(view.pdfCanvas,null);
 held.reject(Object.assign(Error('cancelled'),{name:'RenderingCancelledException'}));await release;assert.equal(cleaned,1);
});

function gestures() {
 let now=1000;const zooms=[],view={number:2,ready:true},fakeDate={now:()=>now};
 const c=vm.createContext({Date:fakeDate,Math,Set,readerTouchPointers:new Set(),readerGestureCandidate:null,readerLastGestureTap:null,readerNonMouseAt:0,
  current:{fingerprint:'doc'},documentOpenGeneration:1,active:null,busy:false,tool:'pen',$:()=>({checked:false}),readerGestureView:()=>view,
  toggleReaderZoom:(x,y,n)=>zooms.push([x,y,n]),resetReaderTap(){c.readerGestureCandidate=null;c.readerLastGestureTap=null;}});
 const code=section('function readerTapEligible(', 'function readerPointAnchor(');vm.runInContext(code,c);
 const event=(type,id=1,extra={})=>({type,pointerId:id,pointerType:'touch',clientX:100,clientY:120,preventDefault(){},...extra});
 const tap=(id=1)=>{c.captureReaderTap(event('pointerdown',id));now+=40;c.finishReaderTap(event('pointerup',id));c.finishReaderTap(event('lostpointercapture',id));now+=100;};
 return {c,zooms,event,tap,advance:n=>{now+=n;}};
}

test('a real touch double-tap survives implicit lostpointercapture and zooms exactly once',()=>{
 const h=gestures();h.tap(1);h.tap(2);assert.deepEqual(h.zooms,[[100,120,2]]);assert.equal(h.c.readerLastGestureTap,null);
});

for(const kind of ['finger-ink','eraser','pen','drag','pinch','cancel','long-press','scroll','other-document'])test(`${kind} cannot accidentally become double-tap zoom`,()=>{
 const h=gestures();h.tap(1);
 if(kind==='finger-ink')h.c.$=()=>({checked:true});
 if(kind==='eraser')h.c.tool='eraser';
 if(kind==='pen'){h.c.captureReaderTap(h.event('pointerdown',2,{pointerType:'pen'}));h.c.finishReaderTap(h.event('pointerup',2,{pointerType:'pen'}));}
 else {
  h.c.captureReaderTap(h.event('pointerdown',2));
  if(kind==='drag')h.c.moveReaderTap(h.event('pointermove',2,{clientX:150}));
  if(kind==='pinch')h.c.captureReaderTap(h.event('pointerdown',3));
  if(kind==='long-press')h.advance(300);
  if(kind==='scroll')h.c.resetReaderTap();
  if(kind==='other-document')h.c.documentOpenGeneration++;
  h.c.finishReaderTap(h.event(kind==='cancel'?'pointercancel':'pointerup',2));
 }
 assert.deepEqual(h.zooms,[]);
});

for(const replacement of ['new-remote','empty'])test(`an old same-document page load cannot overwrite ${replacement} notebook import`,async()=>{
 const h=harness(),held=deferred();let reads=0;
 h.ctx.pages.set(1,[]);
 h.ctx.storage.loadPage=async(_,number)=>{if(number===2&&++reads===1)return held.promise;return structuredClone(h.strokes.get(number)||[]);};
 h.ctx.storage.importPages=async(_,incoming)=>{h.strokes.clear();for(const p of incoming)h.strokes.set(p.number,structuredClone(p.strokes));};
 const old=h.ctx.ensurePage(2);
 const remote={id:'new-remote',color:'#445566',width:.004,points:[{x:.6,y:.7,p:.5}]};
 await h.ctx.applyNotebook({document:{fingerprint:'public-pdf',pageCount:25},pages:replacement==='empty'?[]:[{number:2,strokes:[remote]}],bookmarks:[],position:1},{silent:true,preservePosition:true});
 held.resolve([{id:'old-local',color:'#112233',width:.003,points:[{x:.1,y:.2,p:.5}]}]);
 assert.equal(await old,false);await h.settle();
 assert.deepEqual((h.ctx.pages.get(2)||[]).map(s=>s.id),replacement==='empty'?[]:['new-remote']);
 assert.equal(h.ctx.busy,false);assert.equal(h.ctx.views.get(2).ready,true,'cancelled preview is retried with the imported durable state');
});

test('a slower duplicate page read preserves strokes added after the first completed read',async()=>{
 const h=harness(),held=deferred();let reads=0;
 h.ctx.storage.loadPage=async()=>++reads===1?held.promise:[];
 const old=h.ctx.ensurePage(2);assert.equal(await h.ctx.ensurePage(2),true);
 h.ctx.pages.get(2).push({id:'fresh-ink',color:'#123456',width:.002,points:[{x:.1,y:.2,p:.5}]});
 held.resolve([{id:'stale'}]);assert.equal(await old,true);assert.deepEqual(h.ctx.pages.get(2).map(s=>s.id),['fresh-ink']);
});

test('an old document preview waiting for storage cannot block the next document preview queue',async()=>{
 const h=harness(),held=deferred(),entered=deferred();let old=true;
 h.ctx.storage.loadPage=async(_,n)=>{if(old&&n===2){entered.resolve();return held.promise;}return [];};
 await h.ctx.renderPage();await entered.promise;
 old=false;h.ctx.current={fingerprint:'second-pdf',pageCount:25};h.ctx.documentOpenGeneration++;h.ctx.pages.clear();
 await h.ctx.renderPage();await h.ctx.waitNeighbours();
 assert.equal(h.ctx.views.get(2).ready,true);assert.equal(h.ctx.busy,false);
 held.resolve([{id:'old-document'}]);await tick();assert.deepEqual(h.ctx.pages.get(2),[]);
});

test('an old eviction await cannot capture a newer document and duplicate its preview work',async()=>{
 const h=harness(),entered=deferred(),held=deferred(),previews=[];let evictions=0;
 h.ctx.initializeReaderViews();
 h.ctx.evictReaderDistant=async()=>{if(++evictions===1){entered.resolve();await held.promise;}};
 h.ctx.renderReaderNeighbour=async(_,__,owner)=>previews.push(owner.fingerprint);
 h.ctx.queueReaderNeighbours();const old=h.ctx.waitNeighbours();await entered.promise;
 h.ctx.current={fingerprint:'new-document',pageCount:25};h.ctx.documentOpenGeneration++;h.ctx.initializeReaderViews();
 h.ctx.queueReaderNeighbours();await h.ctx.waitNeighbours();held.resolve();await old;
 assert.deepEqual(previews,['new-document']);
});

test('a rejected old page read cannot paint a storage failure after a same-document import epoch changed',async()=>{
 const h=harness(),held=deferred();h.ctx.storage.loadPage=()=>held.promise;
 const old=h.ctx.ensurePage(2);h.ctx.readerInkEpoch++;
 held.reject(Error('old read failed'));await assert.rejects(old,/old read failed/);assert.deepEqual(h.failures,[]);
});

function realPositioning(h) {
 let width=390;
 h.ctx.window.innerWidth=390;h.ctx.window.innerHeight=740;
 Object.defineProperty(h.area,'clientWidth',{get:()=>width});
 h.area.getBoundingClientRect=()=>({left:0,right:width,top:40,bottom:700,width,height:660});
 vm.runInContext(section('function readerFocusMode(', 'function cancelReaderFocusPosition(')+
  section('function scheduleReaderResize(', 'function setReaderFocus('),h.ctx);
 return {resize(next){width=next;h.ctx.window.innerWidth=next;},
  point(){const rect=h.ctx.views.get(h.ctx.pageNumber).sheet.getBoundingClientRect();return (370-rect.top)/rect.height;}};
}

test('a real viewport width resize retains a middle page and its visible normalized point',async()=>{
 const h=harness({count:30,aspect:()=>2});await h.render();const view=realPositioning(h);
 await h.ctx.goPage(5);await h.settle();h.area.scrollTop+=100;const before=view.point();view.resize(844);
 h.ctx.scheduleReaderResize({type:'resize'});const callback=[...h.timers.values()].at(-1);callback();await h.settle();
 assert.equal(h.ctx.pageNumber,5);assert.equal(h.ctx.nearestReaderView().number,5);
 assert.ok(Math.abs(view.point()-before)<1e-9);assert.equal(h.ctx.readerResizeAnchorPending,false);
});

test('the zoom dropdown retains a middle page instead of jumping into an earlier resized placeholder',async()=>{
 const h=harness({count:30,aspect:()=>2});await h.render();const view=realPositioning(h);
 await h.ctx.goPage(5);await h.settle();h.area.scrollTop+=100;const before=view.point(),listeners={};
 h.elements.zoom.addEventListener=(name,handler)=>{listeners[name]=handler;};
 vm.runInContext(section("$('zoom').addEventListener('change'", "$('bookmark').addEventListener('click'"),h.ctx);
 h.elements.zoom.value='2';listeners.change();await h.settle();
 assert.equal(h.ctx.pageNumber,5);assert.equal(h.ctx.nearestReaderView().number,5);assert.ok(Math.abs(view.point()-before)<1e-9);
});

test('mode-transition scroll clamping cannot select page one before a valid middle-page anchor is restored',async()=>{
 const h=harness({count:30,aspect:()=>2});await h.render();realPositioning(h);
 vm.runInContext(section('function cancelReaderFocusPosition(', 'function scheduleReaderResize('),h.ctx);
 await h.ctx.goPage(15);await h.settle();h.ctx.readerFocusAnchor=h.ctx.captureReaderFocusAnchor();
 // Fullscreen moves the scroll container and clamps the old window scroll.
 h.area.scrollTop=0;h.ctx.readerFocusAnchor.scroll=h.ctx.readerScrollOffsets();h.ctx.readerResizePending=true;
 h.ctx.readerVisibleChanged();assert.equal(h.ctx.pageNumber,15);assert.equal(vm.runInContext('readerScrollPending',h.ctx),true);
 // Real new reader input cancels the old restoration and chooses its own page.
 h.ctx.cancelReaderFocusPosition({type:'wheel'});h.ctx.readerVisibleChanged();await h.settle();
 assert.equal(h.ctx.pageNumber,1);
});

test('an unchanged-aspect adjacent preview cannot leave an anchor which freezes inertial scrolling',async()=>{
 const h=harness({count:30,aspect:()=>1.414});realPositioning(h);await h.render();
 assert.equal(h.ctx.readerFocusAnchor,null);
 const third=h.ctx.views.get(3);h.area.scrollTop=third.sheet.getBoundingClientRect().top-48+100;
 h.ctx.readerVisibleChanged();await h.settle();assert.equal(h.ctx.pageNumber,3);
});
