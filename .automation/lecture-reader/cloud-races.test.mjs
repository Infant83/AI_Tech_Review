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
  context.lockReader ||= ()=>{};context.restoreDisplayedPermissions ||= async()=>{};
  context.updatePresenterPage ||= async()=>{};context.followPresentation ||= async()=>{};
  context.presentationIndicator ||= ()=>{};context.checkedPresentation ||= value=>value;
  context.presentation ??= null;context.presentationPoll ??= false;context.followPresenter ??= false;
  context.roleLabel ||= value=>value;
  context.safeMetadata ||= value=>value;
  context.setReaderRole ||= ()=>{};context.restrictPending ||= (state,snapshot)=>{state.metadata=snapshot.notebook;return false;};
  context.matches=session=>context.active===session&&context.epoch===session.epoch&&context.account?.id===session.accountId&&context.current()?.fingerprint===session.state.fingerprint;
  return vm.createContext(context);
}

function cachedActivation({remoteIds=['base','peer-new'],localIds=['base'],pending=[],lastPage=1}={}){
  let view=notebook(...localIds),mutationRevision=0,lastStatus;
  const metadata={id:'book',role:'owner',...doc,revision:2};
  const remote={notebook:metadata,pages:notebook(...remoteIds).pages,deleted:remoteIds.includes('base')?[]:[{page:1,id:'base'}],position:{page:2},bookmarks:[2]};
  const state={key:'owner:book',accountId:'owner',notebookId:'book',fingerprint:doc.fingerprint,
    metadata:{...metadata,revision:1},localBase:structuredClone(view),pending:structuredClone(pending),lastSent:{position:{page:lastPage},bookmarks:[]}};
  const marker={key:'working:'+doc.fingerprint,stateKey:state.key,accountId:'owner',notebookId:'book',transition:false};
  const stored=new Map([['states:'+state.key,state],['links:'+marker.key,marker]]),changes=[];
  const context=baseContext({current:()=>({...doc,drawing:false,busy:false,mutationRevision}),exported:async()=>structuredClone(view),
    readStore:async(store,key)=>structuredClone(stored.get(store+':'+key)||null),
    writeStore:async(store,value,remove=false)=>{if(remove)stored.delete(store+':'+value.key);else stored.set(store+':'+value.key,structuredClone(value));},
    stopSession:async()=>{context.active=null;context.epoch++;},preserveDisplayed:async()=>{},
    applyWorking:async value=>{view=structuredClone(value);mutationRevision++;},status:kind=>{lastStatus=kind;},
    api:async(url,options={})=>{
      if(options.method==='POST'){
        for(const operation of options.body.operations){
          const id=operation.type==='put'?operation.stroke.id:operation.id;
          if(operation.type==='put'){
            let page=remote.pages.find(page=>page.number===operation.page);
            if(!page){page={number:operation.page,strokes:[]};remote.pages.push(page);}
            page.strokes.push(structuredClone(operation.stroke));
          }else{
            for(const page of remote.pages)if(page.number===operation.page)page.strokes=page.strokes.filter(stroke=>stroke.id!==id);
            remote.deleted.push({page:operation.page,id});
          }
          changes.push({revision:++metadata.revision,type:operation.type,page:operation.page,id,stroke:operation.stroke||null});
        }
        if(options.body.position)remote.position=structuredClone(options.body.position);
        if(options.body.bookmarks)remote.bookmarks=structuredClone(options.body.bookmarks);
        return{ok:true};
      }
      if(url.includes('/pages?'))return{notebook:structuredClone(metadata),changes:structuredClone(changes.filter(change=>change.revision>Number(url.split('since=')[1]))),revision:metadata.revision,notebookRevision:metadata.revision,more:false};
      return structuredClone(remote);
    }});
  context.saveState=async session=>context.writeStore('states',session.state);
  vm.runInContext(tokenFunctions+activation+captureAndSync+section('async function refreshRemote(','async function sharing('),context);
  context.target=metadata;
  return{context,view:()=>view,remote:()=>remote,status:()=>lastStatus};
}

test('cached reopening merges peer additions and erasures before advancing the snapshot cursor',async()=>{
  for(const remoteIds of [['base','peer-new'],[]]){
    const run=cachedActivation({remoteIds});
    await vm.runInContext('activate(target)',run.context);await vm.runInContext('syncNow()',run.context);
    assert.deepEqual(ids(run.view()),remoteIds);
    assert.equal(run.view().position.page,1,'Automatic resume retains local progress');
    assert.equal(run.context.active.state.remoteCursor,2);assert.equal(run.status(),'synced');
  }
});

test('explicit reopening restores remote progress even when this device already sent an earlier position',async()=>{
  const run=cachedActivation();await vm.runInContext('activate(target,{restorePosition:true})',run.context);
  assert.deepEqual(ids(run.view()),['base','peer-new']);assert.equal(run.view().position.page,2);
  assert.deepEqual(run.view().bookmarks,[2]);assert.equal(run.context.active.state.lastSent.position.page,2);
});

test('cached reopening preserves pending offline ink and progress while incorporating the latest remote snapshot',async()=>{
  const run=cachedActivation({localIds:['base','offline-new'],pending:[{type:'put',page:1,stroke:stroke('offline-new')}],lastPage:2});
  await vm.runInContext('activate(target)',run.context);
  assert.deepEqual(ids(run.view()),['base','offline-new','peer-new']);
  assert.deepEqual(ids(remoteNotebookForTest(run.remote())),['base','offline-new','peer-new']);
  assert.equal(run.view().position.page,1);assert.equal(run.remote().position.page,1);
  assert.equal(run.context.active.state.pending.length,0);assert.equal(run.status(),'synced');
});
function remoteNotebookForTest(snapshot){return core.remoteNotebook(snapshot).notebook;}

for(const dispatchSaved of [true,false])test(`incoming apply preserves a stroke completed during IDB save (${dispatchSaved?'save event':'not yet flushed'})`,async()=>{
  let view=notebook('base'),revision=0,applies=0;
  const reached=deferred(),release=deferred();let delay=true;
  const metadata={id:'book',role:'owner',...doc,revision:0};
  let remote={notebook:metadata,pages:notebook('base','remote').pages,deleted:[],position:{page:1},bookmarks:[]};
  const session={accountId:'owner',epoch:0,localGeneration:0,dirty:false,state:{key:'owner:book',notebookId:'book',fingerprint:doc.fingerprint,
    localBase:structuredClone(view),metadata,pending:[],lastSent:{position:{page:1},bookmarks:[]}}};
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
    api:async()=>({notebook:b.metadata,pages:notebook('B').pages,deleted:[],position:{page:1},bookmarks:[]}),
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

test('a role downgrade rejects offline ink before upload and retains its device backup',async()=>{
  let view=notebook('offline-new'),sentInk=0,permission=null;
  const metadata={id:'book',role:'editor',...doc,revision:5};
  const remote={notebook:{...metadata,role:'viewer'},pages:notebook('owner-ink').pages,
    strokeAuthors:[{page:1,id:'owner-ink',accountId:'owner-account'}],deleted:[],position:{page:1},bookmarks:[]};
  const session={accountId:'owner',epoch:0,localGeneration:0,dirty:false,state:{key:'owner:book',accountId:'owner',notebookId:'book',fingerprint:doc.fingerprint,
    metadata,localBase:structuredClone(view),pending:[{type:'delete',page:1,id:'owner-ink'},{type:'put',page:1,stroke:stroke('offline-new')}],lastSent:{position:{page:1},bookmarks:[]}}};
  const context=baseContext({active:session,current:()=>({...doc,drawing:false,busy:false,mutationRevision:0}),exported:async()=>structuredClone(view),
    saveState:async()=>{},refreshRemote:async()=>({snapshot:structuredClone(remote),changed:false}),
    setReaderRole:meta=>{permission=meta.role;},api:async(_,{body})=>{sentInk+=body.operations.length;return{ok:true};},
    applyWorking:async value=>{view=structuredClone(value);}});
  const restriction=section('function restrictPending(','function status(');
  vm.runInContext(tokenFunctions+restriction+captureAndSync,context);await vm.runInContext('syncNow()',context);
  assert.equal(sentInk,0);assert.equal(permission,'viewer');assert.equal(session.state.pending.length,0);
  assert.deepEqual(ids(view),['owner-ink']);assert.deepEqual(ids(session.state.blockedLocal),['offline-new']);
});
