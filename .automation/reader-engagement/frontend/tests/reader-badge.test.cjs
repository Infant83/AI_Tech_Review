/* Node VM + real fake-indexeddb transactions. No browser is started. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {IDBFactory}=require('fake-indexeddb');

const source=fs.readFileSync(path.join(__dirname,'../sw.js'),'utf8');
const scope='https://infant83.io/AI_Tech_Review/';
const databaseName='atr-reader-notifications:/AI_Tech_Review/';
const article=(id='2026-10-25_test',extra={})=>({articleId:id,title:'새 글 '+id,body:'A new article',url:scope+'reviews/'+id+'/',tag:'event-'+id,...extra});
const windowClient=(extra={})=>({id:'reader-window',type:'window',url:scope,visibilityState:'visible',focused:true,...extra});
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
const plain=value=>structuredClone(value);
function fakeClock() {
  let now=0,next=0;const timers=new Map();
  return {
    setTimeout(callback,delay){const id=++next;timers.set(id,{callback,due:now+delay});return id;},
    clearTimeout(id){timers.delete(id);},
    advance(milliseconds){now+=milliseconds;for(const [id,timer]of [...timers])if(timer.due<=now){timers.delete(id);timer.callback();}},
  };
}

function harness(options={}) {
  const factory=options.factory||new IDBFactory();
  const handlers={},shown=[],badges=[],opened=[],hints=[];
  let windows=options.windows||[];
  const normal=windowClient();
  const clients=new Map([[normal.id,normal]]);
  let skipped=0,claimed=0;
  const badgeNavigator=options.badgeUnsupported?{}:{
    setAppBadge:async count=>{badges.push({method:'set',count});if(options.setBadge)await options.setBadge(count);},
    clearAppBadge:async ()=>{badges.push({method:'clear',count:0});if(options.clearBadge)await options.clearBadge();},
  };
  const self={
    indexedDB:options.indexedDB===undefined?factory:options.indexedDB,
    navigator:badgeNavigator,
    registration:{scope:options.scope||scope,showNotification:(title,settings)=>{
      shown.push({title,settings:plain(settings)});
      return options.showNotification?options.showNotification(title,settings):Promise.resolve();
    }},
    addEventListener:(name,handler)=>{handlers[name]=handler;},
    skipWaiting:async()=>{skipped++;},
    clients:{
      matchAll:async()=>windows,
      get:async id=>clients.get(id),
      openWindow:async url=>{opened.push(url);},
      claim:async()=>{claimed++;},
    },
  };
  const context=vm.createContext({self,URL,Promise,Set,Date,Number,setTimeout:options.clock?options.clock.setTimeout:setTimeout,clearTimeout:options.clock?options.clock.clearTimeout:clearTimeout});
  vm.runInContext(source,context);
  function emit(name,event) {
    let pending=Promise.resolve();
    handlers[name]({...event,waitUntil:promise=>{pending=promise;}});
    return Promise.resolve(pending);
  }
  const push=payload=>emit('push',{data:{json:()=>payload}});
  const message=(sender=normal,{type='atr-reader-notification-state'}={})=>{
    let response;
    const pending=emit('message',{data:{type},source:sender,ports:[{postMessage:value=>{response=plain(value);}}]});
    return pending.then(()=>response);
  };
  const hintedClient=extra=>windowClient({postMessage:value=>hints.push(plain(value)),...extra});
  return {factory,handlers,shown,badges,opened,hints,self,clients,normal,context,push,message,emit,hintedClient,
    setWindows:value=>{windows=value;},counts:()=>({skipped,claimed})};
}

async function database(factory) {
  return new Promise((resolve,reject)=>{
    const request=factory.open(databaseName,1);
    request.onupgradeneeded=()=>request.result.createObjectStore('state');
    request.onerror=()=>reject(request.error);
    request.onsuccess=()=>resolve(request.result);
  });
}
async function stored(factory) {
  const db=await database(factory);
  try {
    return await new Promise((resolve,reject)=>{
      const transaction=db.transaction('state','readonly'),request=transaction.objectStore('state').get('notification-state');
      request.onsuccess=()=>resolve(plain(request.result));
      request.onerror=()=>reject(request.error);
    });
  } finally {db.close();}
}
async function seed(factory,state) {
  const db=await database(factory);
  try {
    await new Promise((resolve,reject)=>{
      const transaction=db.transaction('state','readwrite');
      transaction.objectStore('state').put(plain(state),'notification-state');
      transaction.oncomplete=resolve;transaction.onabort=()=>reject(transaction.error);
    });
  } finally {db.close();}
}
async function until(predicate) {
  for(let i=0;i<100;i++) {if(predicate())return;await new Promise(resolve=>setImmediate(resolve));}
  assert.fail('asynchronous operation did not reach its expected stage');
}

test('new article push stores a bounded public record and preserves visible notification/icon',async()=>{
  const h=harness();
  const payload=article('first',{title:'<b>Plain title</b>\nnext',endpoint:'https://private.invalid',keys:{auth:'not-stored'},token:'not-stored'});
  await h.push(payload);
  const state=await stored(h.factory);
  assert.equal(state.count,1);
  assert.deepEqual(state.seenArticleIds,['first']);
  assert.equal(state.notifications[0].title,'<b>Plain title</b> next');
  assert.equal(state.notifications[0].url,payload.url);
  assert.ok(Number.isSafeInteger(state.notifications[0].receivedAt));
  assert.ok(Math.abs(Date.now()-state.notifications[0].receivedAt)<5000);
  assert.deepEqual(Object.keys(state.notifications[0]).sort(),['id','receivedAt','title','url']);
  assert.equal(JSON.stringify(state).includes('not-stored'),false);
  assert.deepEqual(h.badges,[{method:'set',count:1}]);
  assert.equal(h.shown.length,1);
  assert.equal(h.shown[0].settings.icon,scope+'assets/apple-touch-icon.png');
  assert.equal(h.shown[0].settings.badge,scope+'assets/apple-touch-icon.png');
  assert.equal(h.shown[0].settings.renotify,false);
  assert.equal(Object.hasOwn(h.handlers,'fetch'),false);
});

test('test notifications and malformed article metadata never increment or enter history',async()=>{
  const h=harness();
  const invalid=[
    article('test',{articleId:null}),article('test',{articleId:''}),article('test',{articleId:'../escape'}),
    article('test',{articleId:'<img>'}),article('test',{articleId:{toString:null}}),
    article('test',{title:{toString:null}}),article('test',{title:''}),
    article('test',{url:'https://evil.example/AI_Tech_Review/reviews/test/'}),
    article('test',{url:'https://infant83.io/other/'}),article('test',{url:'javascript:alert(1)'}),
    article('test',{url:'https://user:password@infant83.io/AI_Tech_Review/reviews/test/'}),
    article('test',{url:{toString:null}}),article('test',{url:scope+'reviews/different-id/'}),
  ];
  for(const payload of invalid)await h.push(payload);
  assert.equal(h.shown.length,invalid.length);
  assert.equal(h.shown[7].settings.data.url,scope);
  assert.deepEqual(h.badges,[]);
  assert.equal((await h.factory.databases()).length,0);
});

test('Korean/English aliases and concurrent redelivery count one unique article',async()=>{
  const h=harness();
  await Promise.all([h.push(article('same')),h.push(article('same',{url:scope+'reviews/same/en/'})),h.push(article('same'))]);
  const state=await stored(h.factory);
  assert.equal(state.count,1);
  assert.equal(state.notifications.length,1);
  assert.equal(h.shown.length,3,'the existing visible delivery path is unchanged');
  assert.deepEqual(h.badges.map(value=>value.count),[1,1,1]);
});

test('lecture document IDs may differ from web slugs and retain PDF-only links',async()=>{
  const h=harness();
  await h.push(article('lecture:2026-notes',{url:scope+'lectures/quantum-learning/'}));
  await h.push(article('lecture:older-pdf',{url:scope+'archive/files/older-pdf.pdf'}));
  const state=await stored(h.factory);
  assert.equal(state.count,2);
  assert.deepEqual(state.notifications.map(value=>value.id),['lecture:older-pdf','lecture:2026-notes']);
});

test('foreground state request clears only the count and preserves recent records and dedup IDs',async()=>{
  const h=harness();
  await h.push(article('one'));await h.push(article('two'));
  const before=await stored(h.factory);
  const response=await h.message();
  assert.equal(response.ok,true);assert.equal(response.count,0);
  assert.deepEqual(response.notifications,before.notifications);
  const after=await stored(h.factory);
  assert.equal(after.count,0);assert.deepEqual(after.seenArticleIds,before.seenArticleIds);
  assert.deepEqual(h.badges.at(-1),{method:'clear',count:0});
  await h.push(article('one'));
  assert.equal((await stored(h.factory)).count,0,'a retry after opening cannot restore an old badge');
  assert.equal((await stored(h.factory)).notifications.length,2);
});

test('background/hidden source may read history but cannot clear the badge',async()=>{
  const h=harness();await h.push(article('one'));
  h.clients.set(h.normal.id,windowClient({visibilityState:'hidden',focused:false}));
  const response=await h.message();
  assert.equal(response.ok,true);assert.equal(response.count,1);assert.equal(response.notifications.length,1);
  assert.equal((await stored(h.factory)).count,1);
  assert.equal(h.badges.filter(value=>value.method==='clear').length,0);
  h.clients.set(h.normal.id,windowClient({visibilityState:'visible',focused:false}));
  assert.equal((await h.message()).count,1,'a visible window behind another app is still not focused');
});

test('push while an in-scope window is visible and focused stores history with count zero',async()=>{
  const h=harness();
  const current=h.hintedClient();h.setWindows([current]);
  await h.push(article('new'));
  assert.equal((await stored(h.factory)).count,0);
  assert.equal((await stored(h.factory)).notifications.length,1);
  assert.deepEqual(h.badges,[{method:'clear',count:0}]);
  assert.deepEqual(h.hints,[{type:'atr-reader-notifications-changed'}]);
  await h.push(article('new'));await h.push(article('test',{articleId:null}));await h.message();
  assert.equal(h.hints.length,1,'test, duplicate and state reads must not trigger a refresh loop');
});

test('visible but unfocused, hidden, and foreign-scope windows do not auto-confirm new articles',async()=>{
  const h=harness();
  let foreignHints=0;
  h.setWindows([
    h.hintedClient({id:'background',focused:false}),
    h.hintedClient({id:'hidden',visibilityState:'hidden'}),
    windowClient({id:'outside',url:'https://infant83.io/another-app/',postMessage:()=>foreignHints++}),
    windowClient({id:'foreign',url:'https://evil.example/AI_Tech_Review/',postMessage:()=>foreignHints++}),
  ]);
  await h.push(article('unseen'));
  assert.equal((await stored(h.factory)).count,1);
  assert.equal(h.hints.length,2);
  assert.equal(foreignHints,0);
});

test('outside-origin/scope, stale navigated, missing and non-window message clients are rejected',async()=>{
  const h=harness();await h.push(article('one'));
  for(const sender of [windowClient({url:'https://evil.example/AI_Tech_Review/'}),windowClient({url:'https://infant83.io/AI_Tech_Review-other/'}),windowClient({type:'worker'}),windowClient({id:'missing'}),null]) {
    assert.deepEqual(await h.message(sender),{ok:false,error:'source_not_allowed'});
  }
  h.clients.set(h.normal.id,windowClient({url:'https://infant83.io/outside/'}));
  assert.deepEqual(await h.message(),{ok:false,error:'source_not_allowed'},'recheck actual current client, not stale event.source URL');
  assert.equal((await stored(h.factory)).count,1);
  assert.equal(h.badges.filter(value=>value.method==='clear').length,0);
});

test('serial push/clear/push operations preserve event order and list contents',async()=>{
  const h=harness();
  const first=h.push(article('before'));
  const clear=h.message();
  const second=h.push(article('after'));
  await Promise.all([first,clear,second]);
  const state=await stored(h.factory);
  assert.equal(state.count,1);
  assert.deepEqual(state.notifications.map(value=>value.id),['after','before']);
  assert.deepEqual(h.badges.map(value=>value.count),[1,0,1]);
});

test('a delayed native set does not block a newer clear and is reconciled when it finally completes',async()=>{
  const gate=deferred();
  const h=harness({setBadge:()=>gate.promise});
  const pushing=h.push(article('slow'));
  await until(()=>h.badges.length===1);
  let clearDone=false;
  const opening=h.message().then(value=>{clearDone=true;return value;});
  await new Promise(resolve=>setImmediate(resolve));
  await until(()=>clearDone);
  assert.deepEqual(h.badges.at(-1),{method:'clear',count:0});
  gate.resolve();await Promise.all([pushing,opening]);
  await until(()=>h.badges.length>=3);
  assert.deepEqual(h.badges,[{method:'set',count:1},{method:'clear',count:0},{method:'clear',count:0}]);
  assert.equal((await stored(h.factory)).count,0);
});

test('forever-pending native badge calls cannot block later IDB writes/history reads/clear',async()=>{
  const pending=new Promise(()=>{}),clock=fakeClock();
  const h=harness({clock,setBadge:()=>pending,clearBadge:()=>pending});
  const first=h.push(article('first'));
  await until(()=>h.badges.length===1);
  const clear=h.message();
  await until(()=>h.badges.length===2);
  assert.equal((await stored(h.factory)).count,0);
  const second=h.push(article('second'));
  await until(()=>h.badges.length===3);
  assert.equal((await stored(h.factory)).notifications.length,2);
  assert.equal((await stored(h.factory)).count,1);
  clock.advance(1200);
  const response=await clear;
  assert.equal(response.ok,true);assert.equal(response.count,0);assert.equal(response.notifications.length,1);
  await Promise.all([first,second]);
});

test('overlapping old/new worker globals reconcile a late set against the shared durable cleared count',async()=>{
  const factory=new IDBFactory(),gate=deferred();
  let displayed=null;
  const old=harness({factory,setBadge:async count=>{await gate.promise;displayed=count;},clearBadge:()=>{displayed=0;}});
  const pushing=old.push(article('old-worker'));
  await until(()=>old.badges.length===1);
  const updated=harness({factory,clearBadge:()=>{displayed=0;}});
  assert.equal((await updated.message()).count,0);
  assert.equal(displayed,0);
  gate.resolve();await pushing;
  await until(()=>old.badges.some(value=>value.method==='clear'));
  assert.equal(displayed,0);assert.equal((await stored(factory)).count,0);
});

test('worker restart retains count/history/seen IDs; opening after restart clears only count',async()=>{
  const first=harness();await first.push(article('persistent'));
  const second=harness({factory:first.factory});
  await second.push(article('persistent'));
  assert.equal((await stored(first.factory)).count,1);
  const response=await second.message();
  assert.equal(response.count,0);assert.equal(response.notifications.length,1);
  const third=harness({factory:first.factory});await third.push(article('persistent'));
  assert.equal((await stored(first.factory)).count,0);
});

test('recent list is capped at twenty and seen article IDs at two thousand',async()=>{
  const h=harness();
  const seen=Array.from({length:2000},(_,index)=>'old-'+index);
  await seed(h.factory,{count:2000,seenArticleIds:seen,notifications:[]});
  for(let index=0;index<23;index++)await h.push(article('recent-'+index));
  const state=await stored(h.factory);
  assert.equal(state.count,2023);assert.equal(state.seenArticleIds.length,2000);assert.equal(state.notifications.length,20);
  assert.equal(state.seenArticleIds[0],'old-23');
  assert.equal(state.notifications[0].id,'recent-22');assert.equal(state.notifications.at(-1).id,'recent-3');
  const before=state.notifications[0].receivedAt;await h.push(article('recent-22',{title:'duplicate title'}));
  const after=await stored(h.factory);
  assert.equal(after.count,2023);assert.equal(after.notifications[0].receivedAt,before);assert.equal(after.notifications[0].title,'새 글 recent-22');
});

test('missing Badging API still stores history and acknowledges foreground state',async()=>{
  const h=harness({badgeUnsupported:true});await h.push(article('android'));
  assert.equal((await stored(h.factory)).count,1);assert.equal(h.shown.length,1);
  const response=await h.message();assert.equal(response.count,0);assert.equal(response.notifications.length,1);
});

test('native badge failures are isolated from visible notification, persistence and later operations',async()=>{
  const h=harness({setBadge:()=>{throw Error('OS denied');},clearBadge:()=>{throw Error('OS denied');}});
  await h.push(article('one'));assert.equal(h.shown.length,1);
  assert.equal((await stored(h.factory)).count,1);
  assert.equal((await h.message()).ok,true);
  await h.push(article('two'));assert.equal((await stored(h.factory)).count,1);assert.equal(h.shown.length,2);
});

test('IDB open failure/blocked state never suppresses the independent visible notification',async()=>{
  for(const mode of ['throw','blocked','error']) {
    const indexedDB={open(){
      if(mode==='throw')throw Error('storage denied');
      const request={error:Error('storage failed')};
      setImmediate(()=>mode==='blocked'?request.onblocked():request.onerror());return request;
    }};
    const h=harness({indexedDB});
    await h.push(article('storage-'+mode));
    assert.equal(h.shown.length,1);assert.equal(h.shown[0].settings.data.url,article('storage-'+mode).url);
    const response=await h.message();assert.deepEqual(response,{ok:false,error:'state_unavailable'});
    assert.deepEqual(h.badges,[{method:'clear',count:0}]);
  }
});

test('an aborted real IDB transaction does not suppress a push or poison the next state operation',async()=>{
  const factory=new IDBFactory(),h=harness({factory});
  await h.push(article('one'));
  const open=factory.open.bind(factory);
  // Restart with a wrapper that aborts its first real read/write transaction.
  let aborted=false;
  const wrapped={open(...args){
    const request=open(...args);
    const proxy={};
    for(const name of ['onupgradeneeded','onerror','onblocked'])Object.defineProperty(proxy,name,{set:value=>{request[name]=value;}});
    Object.defineProperty(proxy,'onsuccess',{set:handler=>{request.onsuccess=()=>{
      const db=request.result,transaction=db.transaction.bind(db);
      db.transaction=(...values)=>{const tx=transaction(...values);if(!aborted){aborted=true;setImmediate(()=>tx.abort());}return tx;};
      proxy.result=db;handler();
    };}});
    return proxy;
  }};
  const restarted=harness({factory,indexedDB:wrapped});
  await restarted.push(article('two'));
  assert.equal(restarted.shown.length,1);assert.equal((await stored(factory)).count,1);
  await restarted.push(article('three'));
  assert.equal((await stored(factory)).count,2);
});

test('visible notification starts before slow storage/badging and click navigation stays independent',async()=>{
  const native=deferred();
  const h=harness({setBadge:()=>native.promise});
  const pending=h.push(article('slow'));
  assert.equal(h.shown.length,1,'showNotification is called synchronously before storage');
  await until(()=>h.badges.length===1);
  let closed=0;
  await h.emit('notificationclick',{notification:{data:{url:article('slow').url},close(){closed++;}}});
  assert.equal(closed,1);assert.deepEqual(h.opened,[article('slow').url]);
  native.resolve();await pending;
  await h.emit('install',{});await h.emit('activate',{});
  assert.deepEqual(h.counts(),{skipped:1,claimed:1});
});
