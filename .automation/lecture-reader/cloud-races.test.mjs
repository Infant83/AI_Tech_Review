import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
import * as core from './cloud-core.mjs';

// Run the actual orchestration functions without a browser or a test-only
// production export. Delayed durable writes reproduce the reviewer’s races.
const source=await readFile(new URL('./cloud.mjs',import.meta.url),'utf8');
function section(from,to){const start=source.indexOf(from),end=source.indexOf(to,start+from.length);assert.ok(start>=0&&end>start);return source.slice(start,end);}
const tokenFunctions=section('function workingToken(','async function exported(');
const captureAndSync=section('async function capture(','async function refreshRemote(');
const activation=section('async function activate(','async function disconnect(');
const initialization=section('async function initializeCloud(','await initializeCloud();');
const invitationParser=section('function readInviteFragment(','let inviteToken=');
const invitationChange=section('async function inviteFragmentChanged(',"window.addEventListener('hashchange'");
const doc={fingerprint:'a'.repeat(64),title:'Lecture',pageCount:2};
const stroke=id=>({id,color:'#0d7c66',width:.003,points:[{x:.1,y:.2,p:.5}]});
const notebook=(...ids)=>({...core.emptyNotebook(doc),pages:[{number:1,strokes:ids.map(stroke)}]});
const ids=note=>note.pages.flatMap(page=>page.strokes.map(item=>item.id)).sort();
function deferred(){let resolve;const promise=new Promise(done=>{resolve=done;});return{promise,resolve};}
function baseContext(extra={}){
  const context={...core,console,structuredClone,path:'/v1/study',account:{id:'owner'},epoch:0,workingGeneration:0,activationGeneration:0,
    active:null,running:false,needSync:false,timer:null,idleWaiters:[],status(){},schedule(){},setTimeout(){return 0;},clearTimeout(){},t:(_,english)=>english,
    document:{visibilityState:'visible'},error:code=>new Error(code),help:cause=>{throw cause;},stateKey:(a,b)=>a+':'+b,
    linkKey:(a,b)=>a+':'+b,workingKey:fp=>'working:'+fp,...extra};
  context.matches=session=>context.active===session&&context.epoch===session.epoch&&context.account?.id===session.accountId&&context.current()?.fingerprint===session.state.fingerprint;
  return vm.createContext(context);
}

for(const dispatchSaved of [true,false])test(`incoming apply preserves a stroke completed during IDB save (${dispatchSaved?'save event':'not yet flushed'})`,async()=>{
  let view=notebook('base'),revision=0,applies=0;
  const reached=deferred(),release=deferred();let delay=true;
  const metadata={id:'book',role:'owner',...doc,revision:0};
  let remote={notebook:metadata,pages:notebook('base','remote').pages,deleted:[],position:{page:1},bookmarks:[]};
  const session={accountId:'owner',epoch:0,localGeneration:0,dirty:false,state:{key:'owner:book',notebookId:'book',fingerprint:doc.fingerprint,
    localBase:structuredClone(view),pending:[],lastSent:{position:{page:1},bookmarks:[]}}};
  const context=baseContext({active:session,current:()=>({...doc,drawing:false,busy:false,mutationRevision:revision}),exported:async()=>structuredClone(view),
    saveState:async()=>{if(delay){delay=false;reached.resolve();await release.promise;}},
    refreshRemote:async()=>({snapshot:structuredClone(remote),changed:true}),safeMetadata:value=>value,
    api:async(_,{body})=>{for(const operation of body.operations)if(operation.type==='put')remote.pages[0].strokes.push(structuredClone(operation.stroke));return{ok:true};},
    applyWorking:async value=>{applies++;view=structuredClone(value);}});
  vm.runInContext(tokenFunctions+captureAndSync,context);
  const run=vm.runInContext('syncNow()',context);await reached.promise;
  view=notebook('base','late');revision++;
  if(dispatchSaved){session.localGeneration++;session.dirty=true;context.workingGeneration++;}
  release.resolve();await run;
  assert.equal(applies,0,'An exported snapshot cannot replace ink changed during its durable checkpoint');
  assert.deepEqual(ids(view),['base','late']);assert.equal(session.dirty,true);
  await vm.runInContext('syncNow()',context);
  assert.deepEqual(ids(view),['base','late','remote'],'The next capture retries and merges the retained stroke');
});

test('activation rolls back the target marker and retains the old binding if ink changes during the switch',async()=>{
  let view=notebook('A'),revision=0,applies=0;
  const reached=deferred(),release=deferred();
  const a={key:'owner:A',accountId:'owner',notebookId:'A',fingerprint:doc.fingerprint,localBase:notebook('A'),pending:[],metadata:{id:'A',role:'owner',...doc}};
  const b={...structuredClone(a),key:'owner:B',notebookId:'B',localBase:notebook('B'),metadata:{id:'B',role:'owner',...doc}};
  const marker={key:'working:'+doc.fingerprint,stateKey:a.key,accountId:'owner',notebookId:'A',transition:false};
  const values=new Map([['states:'+a.key,a],['states:'+b.key,b],['links:'+marker.key,marker]]);
  const previous={accountId:'owner',epoch:0,localGeneration:0,dirty:false,state:structuredClone(a)};
  const context=baseContext({active:previous,current:()=>({...doc,drawing:false,busy:false,mutationRevision:revision}),exported:async()=>structuredClone(view),
    readStore:async(store,key)=>structuredClone(values.get(store+':'+key)||null),
    writeStore:async(store,value,remove=false)=>{
      if(remove)values.delete(store+':'+value.key);else values.set(store+':'+value.key,structuredClone(value));
      if(store==='links'&&value.transition){reached.resolve();await release.promise;}
    },
    stopSession:async()=>{context.active=null;context.epoch++;},
    preserveDisplayed:async()=>{},applyWorking:async value=>{applies++;view=structuredClone(value);},
    syncNow:async()=>{throw Error('Switch should not reach network synchronization');}});
  vm.runInContext(tokenFunctions+activation,context);
  context.target=b.metadata;
  const run=vm.runInContext('activate(target)',context);await reached.promise;
  view=notebook('A','late-A');revision++;release.resolve();
  await assert.rejects(run,/READER_BUSY/);
  assert.equal(applies,0);assert.deepEqual(ids(view),['A','late-A']);
  assert.equal(values.get('links:'+marker.key).stateKey,a.key);
  assert.equal(values.get('links:'+marker.key).transition,false);
  assert.equal(context.active.state.key,a.key);assert.equal(context.active.dirty,true);
  assert.deepEqual(ids(values.get('states:'+b.key).localBase),['B']);
});

test('a private invitation opens consent before an unrelated notebook can resume',async()=>{
  let shown=0,resumed=0;
  const context=baseContext({authGeneration:0,inviteToken:'private-invitation-fixture',requestedId:null,initialized:false,
    api:async()=>({ok:true,account:{id:'owner',displayName:'Owner'}}),safeAccount:value=>value,
    show:async()=>{shown++;},resume:async()=>{resumed++;throw Error('READER_BUSY');},feedbackText(){}});
  vm.runInContext(initialization,context);await vm.runInContext('initializeCloud()',context);
  assert.equal(shown,1);assert.equal(resumed,0);assert.equal(context.initialized,true);
});

test('a temporarily busy requested notebook does not suppress its sign-in/dialog entry',async()=>{
  let shown=0;
  const context=baseContext({authGeneration:0,inviteToken:null,requestedId:'requested-book',initialized:false,
    api:async()=>({ok:true,account:{id:'owner',displayName:'Owner'}}),safeAccount:value=>value,
    show:async()=>{shown++;},resume:async()=>{throw Error('READER_BUSY');},help:cause=>cause.message,feedbackText(){}});
  vm.runInContext(initialization,context);await vm.runInContext('initializeCloud()',context);
  assert.equal(shown,1);
});

test('same-document invitation navigation opens consent without rerunning module initialization',async()=>{
  let shown=0,resumed=0;
  const context=baseContext({location:{hash:''},URLSearchParams,inviteToken:null,initialized:true,dialog:null,
    show:async()=>{shown++;},resume:async()=>{resumed++;},feedbackText(){}});
  vm.runInContext(invitationParser+invitationChange,context);
  context.location.hash='#invite='+'a'.repeat(43);
  await vm.runInContext('inviteFragmentChanged()',context);
  assert.equal(context.inviteToken,'a'.repeat(43));assert.equal(shown,1);assert.equal(resumed,0);
  context.location.hash='#invite=invalid';await vm.runInContext('inviteFragmentChanged()',context);
  assert.equal(context.inviteToken,null);assert.equal(shown,1);assert.equal(resumed,1);
});

test('an invitation arriving during the initial account request remains pending for bootstrap',async()=>{
  let shown=0;
  const context=baseContext({location:{hash:'#invite='+'b'.repeat(43)},URLSearchParams,inviteToken:null,initialized:false,
    show:async()=>{shown++;},feedbackText(){}});
  vm.runInContext(invitationParser+invitationChange,context);await vm.runInContext('inviteFragmentChanged()',context);
  assert.equal(context.inviteToken,'b'.repeat(43));assert.equal(shown,0);
});
