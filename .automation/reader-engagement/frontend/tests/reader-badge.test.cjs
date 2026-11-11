/* Node VM + real fake-indexeddb transactions. No browser is started. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {webcrypto}=require('node:crypto');
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
  if(options.getNotifications) {
    self.registration.getNotifications=options.getNotifications;
    self.registration.active={scriptURL:options.activeScript||scope+'sw.js'};
  }
  const context=vm.createContext({self,URL,Promise,Set,Date,Number,TextEncoder,crypto:webcrypto,fetch:options.fetch,
    setTimeout:options.clock?options.clock.setTimeout:setTimeout,clearTimeout:options.clock?options.clock.clearTimeout:clearTimeout});
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
  const read=(articleId,url,sender=normal)=>{
    let response;
    const pending=emit('message',{data:{type:'atr-reader-article-read',articleId,url},source:sender,
      ports:[{postMessage:value=>{response=plain(value);}}]});
    return pending.then(()=>response);
  };
  const openArticle=(id,url=article(id).url)=>{const client=windowClient({url});clients.set(client.id,client);return read(id,url,client);};
  const hintedClient=extra=>windowClient({postMessage:value=>hints.push(plain(value)),...extra});
  return {factory,handlers,shown,badges,opened,hints,self,clients,normal,context,push,message,read,openArticle,emit,hintedClient,
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

test('native proposed notifications with null data preserve article identity and required navigation',async()=>{
  const h=harness(),payload=article('native');
  await h.emit('push',{data:null,notification:{title:payload.title,body:payload.body,navigate:payload.url,
    tag:payload.tag,data:{articleId:payload.articleId}}});
  assert.equal(h.shown[0].title,payload.title);
  assert.equal(h.shown[0].settings.navigate,payload.url);
  assert.deepEqual(h.shown[0].settings.data,{url:payload.url,articleId:payload.articleId});
  const state=await stored(h.factory);
  assert.equal(state.count,1);assert.deepEqual(state.unreadArticleIds,['native']);
  assert.equal(state.notifications[0].id,'native');
});

const eventTag=async id=>Buffer.from(await webcrypto.subtle.digest('SHA-256',new TextEncoder().encode('article:'+id))).toString('hex');
function publicFeed(items) {return {ok:true,headers:{get:()=>null},text:async()=>JSON.stringify({revision:'a'.repeat(40),articles:items.map(item=>({id:item.articleId,path:new URL(item.url).pathname,title:item.title,topic:item.articleId.startsWith('lecture:')?'lecture':'review'}))})};}

test('notification-center recovery restores only strict delivered matches with observed time, never a received time',async()=>{
  const payload=article('restored'),tag=await eventTag(payload.articleId),requests=[];
  const h=harness({getNotifications:async()=>[
    {title:payload.title,tag,navigate:payload.url},
    {title:payload.title,tag:'wrong',navigate:payload.url,data:{articleId:payload.articleId}},
    {title:'different title',tag,navigate:payload.url},
    {title:payload.title,tag,navigate:'https://evil.example/AI_Tech_Review/reviews/restored/'},
    {title:'not delivered',tag:'wrong',navigate:payload.url},
  ],fetch:async(url,init)=>{requests.push({url,init});return publicFeed([payload,article('catalog-only')]);}});
  const first=await h.message();
  assert.equal(first.notifications.length,0,'the existing reply precedes optional reconciliation');
  const state=await stored(h.factory);
  assert.equal(state.count,1);assert.deepEqual(state.unreadArticleIds,['restored']);
  assert.equal(state.notifications.length,1);
  assert.equal(state.notifications[0].source,'notification-center');
  assert.ok(Number.isSafeInteger(state.notifications[0].observedAt));
  assert.equal(Object.hasOwn(state.notifications[0],'receivedAt'),false);
  assert.equal(requests.length,1);assert.equal(requests[0].url,scope+'reader-publications.json');
  assert.equal(requests[0].init.credentials,'omit');
  assert.equal(h.shown.length,0,'reconciliation must never redisplay or close notifications');
  await h.message();assert.equal(requests.length,1,'repeat state reads are debounced');
});

test('notification-center recovery preserves read IDs and old acknowledged seen IDs',async()=>{
  const one=article('read'),two=article('seen'),three=article('new-native');
  const h=harness({getNotifications:async()=>Promise.all([one,two,three].map(async item=>({title:item.title,navigate:item.url,tag:await eventTag(item.articleId),data:{articleId:item.articleId}}))),
    fetch:async()=>publicFeed([one,two,three])});
  await seed(h.factory,{count:0,seenArticleIds:['seen'],unreadArticleIds:[],readArticleIds:['read'],notifications:[]});
  await h.message();
  const state=await stored(h.factory);
  assert.equal(state.count,1);assert.deepEqual(state.unreadArticleIds,['new-native']);
  assert.equal(state.notifications.some(item=>item.id==='read'),true);
  assert.equal(state.notifications.some(item=>item.id==='seen'),false);
});

test('notification-center recovery keeps the newest twenty of twenty-one delivered articles',async()=>{
  const items=Array.from({length:21},(_,index)=>article('native-'+index));
  const displayed=await Promise.all(items.map(async item=>({title:item.title,navigate:item.url,tag:await eventTag(item.articleId)})));
  const h=harness({getNotifications:async()=>displayed,fetch:async()=>publicFeed(items)});
  await h.message();
  const state=await stored(h.factory);
  assert.equal(state.count,21);assert.equal(state.unreadArticleIds.length,21);
  assert.equal(state.notifications.length,20);
  assert.equal(state.notifications[0].id,'native-20');assert.equal(state.notifications.at(-1).id,'native-1');
});

test('notification-center recovery racing an article read and push cannot duplicate or revive unread state',async()=>{
  const payload=article('racing'),held=deferred(),entered=deferred(),tag=await eventTag(payload.articleId);
  const h=harness({getNotifications:async()=>[{title:payload.title,tag,navigate:payload.url,data:{articleId:payload.articleId}}],
    fetch:async()=>{entered.resolve();return held.promise;}});
  const recovering=h.message();await entered.promise;
  await Promise.all([h.openArticle(payload.articleId),h.push(payload)]);
  held.resolve(publicFeed([payload]));await recovering;
  const state=await stored(h.factory);
  assert.equal(state.count,0);assert.deepEqual(state.unreadArticleIds,[]);
  assert.equal(state.notifications.length,1);assert.equal(state.notifications[0].id,payload.articleId);
  assert.equal(h.shown.length,1,'only the real push may display a notification');
});

test('notification-center fetch timeout replies immediately and ignores late matching catalog data',async()=>{
  const clock=fakeClock(),held=deferred(),entered=deferred(),payload=article('fetch-late'),tag=await eventTag(payload.articleId);
  const h=harness({clock,getNotifications:async()=>[{title:payload.title,tag,navigate:payload.url}],
    fetch:async()=>{entered.resolve();return held.promise;}});
  let reply;
  const pending=h.emit('message',{data:{type:'atr-reader-notification-state'},source:h.normal,ports:[{postMessage:value=>{reply=plain(value);}}]});
  await entered.promise;assert.equal(reply.ok,true);
  clock.advance(2000);await pending;
  held.resolve(publicFeed([payload]));await new Promise(resolve=>setImmediate(resolve));
  assert.equal((await stored(h.factory)).notifications.length,0);
});

test('notification-center lookup is optional, scoped, bounded and cannot delay the port reply or apply late results',async()=>{
  const clock=fakeClock(),held=deferred(),payload=article('too-late');let fetches=0,replied;
  const h=harness({clock,getNotifications:()=>held.promise,fetch:async()=>{fetches++;return publicFeed([payload]);}});
  const pending=h.emit('message',{data:{type:'atr-reader-notification-state'},source:h.normal,
    ports:[{postMessage:value=>{replied=plain(value);}}]});
  await until(()=>replied);assert.equal(replied.ok,true);
  clock.advance(2000);await pending;
  held.resolve([{title:payload.title,navigate:payload.url,data:{articleId:payload.articleId}}]);
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal((await stored(h.factory)).notifications.length,0);assert.equal(fetches,0,'expired enumeration must not start a late catalog fetch');
  const wrong=harness({activeScript:scope+'other.js',getNotifications:()=>{throw Error('wrong worker must not be queried');},fetch:async()=>{fetches++;throw Error('no fetch');}});
  assert.equal((await wrong.message()).ok,true);assert.equal(fetches,0);
  const denied=harness({getNotifications:async()=>{throw Error('OS denied');},fetch:async()=>{throw Error('no fetch');}});
  assert.equal((await denied.message()).ok,true);
});

test('article reads acknowledge only the opened article while hub history remains read only',async()=>{
  const h=harness();await h.push(article('one'));await h.push(article('two'));
  const response=await h.message();assert.equal(response.count,2);
  const client=windowClient({url:article('one').url+'en/'});h.clients.set(client.id,client);
  const read=await h.read('one',article('one').url,client);
  assert.equal(read.count,1);
  const state=await stored(h.factory);
  assert.deepEqual(state.unreadArticleIds,['two']);assert.deepEqual(state.readArticleIds,['one']);
  assert.deepEqual(state.notifications.map(value=>value.id),['two','one']);
  await h.read('one',article('one').url,client);
  assert.equal((await stored(h.factory)).count,1,'repeated reads must be idempotent');
});

test('article reads migrate old counts without resurrecting cleared history',async()=>{
  const h=harness();
  const notifications=['two','one'].map(id=>({id,title:id,url:article(id).url,receivedAt:Date.now()}));
  await seed(h.factory,{count:0,seenArticleIds:['one','two'],notifications});
  assert.equal((await h.message()).count,0);
  assert.deepEqual((await stored(h.factory)).unreadArticleIds,[]);
  await h.push(article('one'));assert.equal((await stored(h.factory)).count,0);
  await seed(h.factory,{count:1,seenArticleIds:['one','two'],notifications});
  assert.equal((await h.message()).count,1);
  assert.deepEqual((await stored(h.factory)).unreadArticleIds,['two']);
  assert.deepEqual((await stored(h.factory)).notifications,notifications);
});

test('article reads migrate all twenty-four ordered legacy receipts beyond the twenty-item history',async()=>{
  const h=harness(),ids=Array.from({length:24},(_,index)=>'legacy-'+index);
  const notifications=ids.slice(-20).reverse().map(id=>({id,title:id,url:article(id).url,receivedAt:Date.now()}));
  await seed(h.factory,{count:24,seenArticleIds:ids,notifications});
  assert.equal((await h.message()).count,24);
  assert.deepEqual((await stored(h.factory)).unreadArticleIds,ids);
  for(const id of ids)await h.openArticle(id);
  const state=await stored(h.factory);
  assert.equal(state.count,0);assert.deepEqual(state.unreadArticleIds,[]);
  assert.deepEqual(state.seenArticleIds,ids);assert.deepEqual(state.notifications,notifications);
});

test('article reads before or after a push do not revive the same article unread count',async()=>{
  for(const before of [true,false]) {
    const h=harness(),payload=article('opened');
    const client=windowClient({url:payload.url});h.clients.set(client.id,client);
    if(before)await h.read(payload.articleId,payload.url,client);
    await h.push(payload);
    if(!before)await h.read(payload.articleId,payload.url,client);
    const state=await stored(h.factory);
    assert.equal(state.count,0);assert.equal(state.notifications.length,1);
    await h.push(payload);assert.equal((await stored(h.factory)).count,0);
  }
});

test('article reads reject hidden, hub, mismatched, stale and foreign sources',async()=>{
  for(const extra of [{url:scope},{url:article('two').url},{url:article('one').url,focused:false},
    {url:article('one').url,visibilityState:'hidden'},{url:'https://evil.example/AI_Tech_Review/reviews/one/'}]) {
    const h=harness();await h.push(article('one'));
    const client=windowClient(extra);h.clients.set(client.id,client);
    const response=await h.read('one',article('one').url,client);
    assert.equal(response.ok,false);assert.equal((await stored(h.factory)).count,1);
  }
});

test('article reads bind PDF lecture acknowledgments to the displayed public document ID',async()=>{
  const h=harness(),id='lecture:public-notes',url=scope+'archive/files/public-notes.pdf';
  await h.push(article(id,{url}));
  const wrong=windowClient({url:scope+'lectures/reader/?id=other-notes'});h.clients.set(wrong.id,wrong);
  assert.equal((await h.read(id,url,wrong)).ok,false);
  const current=windowClient({url:scope+'lectures/reader/?id=public-notes&lang=en'});h.clients.set(current.id,current);
  assert.equal((await h.read(id,url,current)).count,0);
  assert.equal((await stored(h.factory)).notifications[0].id,id);
});

function heldDatabaseOpen(factory) {
  const opened=deferred(),release=deferred();
  return {
    opened:opened.promise,release:()=>release.resolve(),
    indexedDB:{open(...args){
      const request=factory.open(...args),proxy={};
      for(const name of ['result','error'])Object.defineProperty(proxy,name,{get:()=>request[name]});
      for(const name of ['onupgradeneeded','onerror','onblocked'])Object.defineProperty(proxy,name,{set:handler=>{request[name]=handler;}});
      Object.defineProperty(proxy,'onsuccess',{set:handler=>{request.onsuccess=()=>{
        opened.resolve();release.promise.then(()=>handler());
      };}});
      return proxy;
    }},
  };
}

test('rejected or throwing visible notifications wait for delayed history before preserving the original error',async t=>{
  for(const mode of ['rejected','throws'])await t.test(mode,async()=>{
    const factory=new IDBFactory(),storage=heldDatabaseOpen(factory),failure=new Error('display denied');
    let failDisplay=true,settled=false,result;
    const h=harness({factory,indexedDB:storage.indexedDB,showNotification:()=>{
      if(!failDisplay)return Promise.resolve();
      if(mode==='throws')throw failure;
      return Promise.reject(failure);
    }});
    const payload=article('display-'+mode);
    const pending=h.push(payload).then(()=>{settled=true;return {};},error=>{settled=true;return {error};});
    assert.equal(h.shown.length,1,'display must start immediately, before storage');
    try {
      await storage.opened;
      await new Promise(resolve=>setImmediate(resolve));
      assert.equal(settled,false,'waitUntil must remain pending until history finishes');
    } finally {storage.release();result=await pending;}
    assert.equal(result.error,failure,'the original display error must reach waitUntil');
    const first=await stored(factory);
    assert.equal(first.count,1);
    assert.deepEqual(first.notifications.map(value=>value.id),[payload.articleId]);
    failDisplay=false;
    await h.push(payload);
    const repeated=await stored(factory);
    assert.deepEqual(repeated,first,'redelivery must not duplicate history or the badge count');
    assert.equal(h.shown.length,2);
    assert.equal(h.shown[1].settings.tag,payload.tag);
    assert.equal(h.shown[1].settings.renotify,false);
  });
});

test('successful display waits for delayed history and storage failure cannot replace a display error',async()=>{
  const factory=new IDBFactory(),storage=heldDatabaseOpen(factory);
  const h=harness({factory,indexedDB:storage.indexedDB});
  let settled=false;
  const pending=h.push(article('display-success')).then(()=>{settled=true;});
  assert.equal(h.shown.length,1);
  try {
    await storage.opened;
    await new Promise(resolve=>setImmediate(resolve));
    assert.equal(settled,false);
  } finally {storage.release();await pending;}
  assert.equal((await stored(factory)).notifications[0].id,'display-success');
  const failure=new Error('display rejected');
  const broken=harness({indexedDB:{open(){throw Error('storage denied');}},showNotification:()=>Promise.reject(failure)});
  await assert.rejects(broken.push(article('both-fail')),error=>error===failure);
  assert.equal(broken.shown.length,1);
});

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

test('foreground state request preserves unread count, recent records and dedup IDs',async()=>{
  const h=harness();
  await h.push(article('one'));await h.push(article('two'));
  const before=await stored(h.factory);
  const response=await h.message();
  assert.equal(response.ok,true);assert.equal(response.count,2);
  assert.deepEqual(response.notifications,before.notifications);
  const after=await stored(h.factory);
  assert.equal(after.count,2);assert.deepEqual(after.seenArticleIds,before.seenArticleIds);
  assert.deepEqual(h.badges.at(-1),{method:'set',count:2});
  await h.push(article('one'));
  assert.equal((await stored(h.factory)).count,2,'history queries and redelivery cannot change unread count');
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

test('push after the focused article has acknowledged reading stores history with count zero',async()=>{
  const h=harness();
  const current=h.hintedClient({url:article('new').url});h.setWindows([current]);
  await h.openArticle('new');h.badges.length=0;
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
  const clear=h.openArticle('before');
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
  const opening=h.openArticle('slow').then(value=>{clearDone=true;return value;});
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
  const clear=h.openArticle('first');
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
  assert.equal((await updated.openArticle('old-worker')).count,0);
  assert.equal(displayed,0);
  gate.resolve();await pushing;
  await until(()=>old.badges.some(value=>value.method==='clear'));
  assert.equal(displayed,0);assert.equal((await stored(factory)).count,0);
});

test('worker restart retains count/history/seen IDs; opening that article after restart clears its unread count',async()=>{
  const first=harness();await first.push(article('persistent'));
  const second=harness({factory:first.factory});
  await second.push(article('persistent'));
  assert.equal((await stored(first.factory)).count,1);
  const response=await second.openArticle('persistent');
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
  const response=await h.openArticle('android');assert.equal(response.count,0);assert.equal(response.notifications.length,1);
});

test('native badge failures are isolated from visible notification, persistence and later operations',async()=>{
  const h=harness({setBadge:()=>{throw Error('OS denied');},clearBadge:()=>{throw Error('OS denied');}});
  await h.push(article('one'));assert.equal(h.shown.length,1);
  assert.equal((await stored(h.factory)).count,1);
  assert.equal((await h.openArticle('one')).ok,true);
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
    assert.deepEqual(h.badges,[]);
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
  assert.equal(closed,1);assert.equal(h.opened.length,1);
  const fresh=new URL(h.opened[0]);assert.ok(fresh.searchParams.get('_atr_refresh'));
  fresh.searchParams.delete('_atr_refresh');assert.equal(fresh.href,article('slow').url);
  native.resolve();await pending;
  await h.emit('install',{});await h.emit('activate',{});
  assert.deepEqual(h.counts(),{skipped:1,claimed:1});
});
