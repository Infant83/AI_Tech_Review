import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

const source=await readFile(new URL('./cloud.mjs',import.meta.url),'utf8');
function section(start,end){const a=source.indexOf(start),b=source.indexOf(end,a+start.length);assert.ok(a>=0&&b>a,start);return source.slice(a,b);}
const fingerprint='a'.repeat(64);
function node(tag,text=''){return{tag,text,children:[],dataset:{},value:'',checked:false,append(...items){this.children.push(...items);},replaceChildren(...items){this.children=items;},setAttribute(){},addEventListener(){},remove(){},focus(){}};}
const nodes=root=>[root,...root.children.flatMap(nodes)];
function base(extra={}){const content=node('content');return vm.createContext({content,dialog:{open:true},account:{id:'member',displayName:'Member'},
  features:{documentStorage:true,drafts:true,presenter:true,additionalPasskeys:true},storageUsage:null,path:'/v1/study',en:false,URLSearchParams,
  t:key=>key,el:node,action:(text,handler)=>({...node('button',text),handler}),feedbackText(){},ensureDialog(){},confirm:()=>true,
  safeMetadata:value=>value,safeAccount:value=>value,roleLabel:value=>value,roleDescription:value=>value,
  current:()=>({fingerprint,page:1,pageCount:114}),active:null,matches:()=>false,render:async()=>{},error:(message,status=0)=>Object.assign(new Error(message),{status}),...extra});}

test('the unified anonymous workspace exposes device notes, import and published material together',async()=>{
  let imported=0,chosen;
  const ctx=base({account:null,renderGeneration:3,window:{ATRNotebook:{libraryData:async()=>({local:[{fingerprint,title:'My PDF',pageCount:2,position:2,annotatedPages:[1]}],published:[{id:'lecture',title:'Lecture',date:'2026-11-05'}]}),chooseLocalPDF:()=>{imported++;},chooseStored:async value=>{chosen=value;}}},dialog:{open:true,close(){this.open=false;}}});
  vm.runInContext(section('async function appendDeviceLibrary(','async function notebookDetails('),ctx);await ctx.appendDeviceLibrary(3,undefined);
  const all=nodes(ctx.content);assert.ok(all.some(n=>n.text==='이 기기에 보관'));assert.ok(all.some(n=>n.text==='공개 렉처 자료'));
  all.find(n=>n.text==='내 PDF 가져오기').handler();assert.equal(imported,1);
  await all.find(n=>n.tag==='button'&&n.text==='열기').handler();assert.equal(chosen,fingerprint);
});

test('signed-in bootstrap displays the account name before any PDF has been opened',async()=>{
  const span={textContent:''},classes=new Set(),button={dataset:{},querySelector:()=>span,setAttribute(){},classList:{toggle(name,value){if(value)classes.add(name);else classes.delete(name);}}};
  const ctx=base({account:null,current:()=>null,button,live:{},lastStatus:'',dialog:{querySelector:()=>null},authGeneration:0,initialized:false,
    lockReader(){},restoreDisplayedPermissions:async()=>{},api:async()=>({account:{id:'returning',displayName:'Returning learner'},features:{},usage:null}),
    inviteToken:null,resume:async()=>{},requestedId:null,URL,location:{href:'http://localhost/reader/'}});
  vm.runInContext(section('function status(','function help(')+section('async function initializeCloud(','await initializeCloud();'),ctx);await ctx.initializeCloud();
  assert.equal(span.textContent,'Returning learner');assert.ok(classes.has('signed-in'));
});

test('the current-notebook section identifies the selected study copy separately from the PDF title',async()=>{
  const session={state:{metadata:{id:'copy',title:'My private study copy',role:'owner'}}};
  const ctx=base({active:session,matches:value=>value===session,current:()=>({fingerprint,title:'Original PDF title'}),renderGeneration:0,inviteToken:null,lastStatus:'Connected',
    accountSettings(){},logout(){},disconnect(){},features:{drafts:false,presenter:false},allNotebookMetadata:async()=>[],appendDeviceLibrary:async()=>{}});
  vm.runInContext(section('async function render()','async function authenticate('),ctx);await ctx.render();
  const headings=nodes(ctx.content).filter(n=>n.tag==='h3').map(n=>n.text);assert.ok(headings.includes('My private study copy'));assert.equal(headings.includes('Original PDF title'),false);
});

test('cloud library and draft attachment metadata include later pages and separate trash',async()=>{
  const calls=[];
  const ctx=base({api:async url=>{calls.push(url);return calls.length===1?{notebooks:[{id:'first'}],nextCursor:200}:{notebooks:[{id:'later',deletedAt:10}],nextCursor:null};}});
  vm.runInContext(section('async function allNotebookMetadata(','function roleLabel('),ctx);
  const result=await ctx.allNotebookMetadata({includeDeleted:true});assert.deepEqual(Array.from(result,n=>n.id),['first','later']);
  assert.deepEqual(calls,['/v1/study/notebooks?includeDeleted=1','/v1/study/notebooks?includeDeleted=1&cursor=200']);
  assert.equal(result[1].deletedAt,10);
});

test('repeated pagination cursors fail explicitly instead of silently omitting later notes',async()=>{
  const ctx=base({api:async()=>({notebooks:[{id:'first'}],nextCursor:200})});
  vm.runInContext(section('async function allNotebookMetadata(','function roleLabel('),ctx);
  await assert.rejects(ctx.allNotebookMetadata(),/NOTEBOOK_LIST_LIMIT/);
});

for(const [role,blank,endpoint,includeInk] of [['viewer',false,'copy',true],['contributor',true,'copy',false],['owner',true,'reset',undefined]]){
  test(`${role} creates a separate ${blank?'fresh':'inked'} study copy without modifying the source`,async()=>{
    const requests=[];let opened;
    const ctx=base({api:async(url,args)=>{requests.push({url,...args});return{notebook:{id:'new-private',role:'owner',fingerprint}};},openNotebook:async value=>{opened=value;}});
    vm.runInContext(section('function copyNotebookForm(','async function reauthenticate('),ctx);
    ctx.copyNotebookForm({id:'source',title:'Source',role,fingerprint},blank);
    await nodes(ctx.content).find(n=>n.tag==='button'&&n.text==='만들기').handler();
    assert.equal(requests.length,1);assert.equal(requests[0].url,`/v1/study/notebooks/source/${endpoint}`);assert.equal(requests[0].method,'POST');
    assert.equal(requests[0].body.includeInk,includeInk);assert.equal(opened.id,'new-private');assert.equal(opened.role,'owner');
  });
}

test('a viewer can discover private study copies without owner-only destructive or upload actions',async()=>{
  const ctx=base();vm.runInContext(section('async function notebookDetails(','function copyNotebookForm('),ctx);
  await ctx.notebookDetails({id:'shared',role:'viewer',title:'Shared',fingerprint,documentAvailable:true});
  const labels=nodes(ctx.content).filter(n=>n.tag==='button').map(n=>n.text);
  assert.ok(labels.includes('새 학습 사본'));assert.ok(labels.includes('처음부터 새로 공부'));
  assert.equal(labels.includes('클라우드 휴지통'),false);assert.equal(labels.includes('원본 PDF 클라우드 보관'),false);
});

test('copying the active notebook flushes and uploads local ink before copying its server snapshot',async()=>{
  const calls=[],session={state:{notebookId:'source',pending:[]},dirty:false};
  const ctx=base({active:session,matches:value=>value===session,running:false,window:{ATRNotebook:{flush:async()=>{calls.push('flush');return true;}}},
    capture:async value=>{assert.equal(value,session);calls.push('capture');session.state.pending=[{type:'put'}];},
    syncNow:async()=>{calls.push('sync');session.state.pending=[];}});
  vm.runInContext(section('async function prepareCopySource(','async function reauthenticate('),ctx);await ctx.prepareCopySource({id:'source'});
  assert.deepEqual(calls,['flush','capture','sync']);
});

for(const role of ['owner','contributor'])test(`fresh study from an active ${role} notebook syncs its pending ink before creating the empty copy`,async()=>{
  const calls=[],session={state:{notebookId:'source',pending:[]},dirty:false};
  const ctx=base({active:session,matches:value=>value===session,running:false,window:{ATRNotebook:{flush:async()=>{calls.push('flush');return true;}}},
    capture:async()=>{calls.push('capture');session.state.pending=[{type:'put',stroke:{id:'last-stroke'}}];},syncNow:async()=>{calls.push('sync');session.state.pending=[];},
    api:async url=>{assert.equal(session.state.pending.length,0,'The old notebook must be complete before a new blank notebook is created');calls.push(url);return{notebook:{id:'blank',role:'owner',fingerprint}};},
    openNotebook:async value=>{assert.equal(value.id,'blank');calls.push('open');}});
  vm.runInContext(section('function copyNotebookForm(','async function reauthenticate('),ctx);ctx.copyNotebookForm({id:'source',title:'Source',role,fingerprint},true);
  await nodes(ctx.content).find(n=>n.tag==='button'&&n.text==='만들기').handler();
  assert.deepEqual(calls,['flush','capture','sync',`/v1/study/notebooks/source/${role==='owner'?'reset':'copy'}`,'open']);
});

for(const failure of ['save','pending'])test(`copying refuses a ${failure} failure without discarding device ink`,async()=>{
  const pending=[{type:'put',stroke:{id:'unsent'}}],session={state:{notebookId:'source',pending},dirty:false};let synced=0;
  const ctx=base({active:session,matches:()=>true,running:false,window:{ATRNotebook:{flush:async()=>failure!=='save'}},capture:async()=>{},syncNow:async()=>{synced++;}});
  vm.runInContext(section('async function prepareCopySource(','async function reauthenticate('),ctx);
  await assert.rejects(ctx.prepareCopySource({id:'source'}),new RegExp(failure==='save'?'SAVE_FAILED':'COPY_SYNC_REQUIRED'));
  assert.equal(session.state.pending,pending);assert.equal(synced,failure==='save'?0:1);
});

test('a cloud-stored private original opens on an empty device with its expected hash',async()=>{
  const blob=new Blob(['original']),book={id:'cloud-private',fingerprint,title:'Private',documentAvailable:true};let opened;
  const ctx=base({current:()=>null,notebookOpenGeneration:0,requestedId:null,selection:null,CustomEvent:class{constructor(type){this.type=type;}},
    window:{dispatchEvent(){},addEventListener(){},ATRNotebook:{openStored:async()=>false,openCloudPDF:async(value,metadata)=>{opened={value,metadata};return true;}}},
    documentFile:async value=>{assert.equal(value,book);return blob;},dialog:{open:true,close(){this.open=false;}}});
  vm.runInContext(section('async function openNotebook(','async function activate('),ctx);await ctx.openNotebook(book);
  assert.equal(opened.value,blob);assert.equal(opened.metadata.sha256,fingerprint);assert.equal(ctx.dialog.open,false);
});

test('a newer PDF selection cancels a delayed private cloud original download',async()=>{
  let finish,opened=0;const waiting=new Promise(resolve=>{finish=resolve;});
  const book={id:'cloud-private',fingerprint,title:'Private',documentAvailable:true};
  const ctx=base({current:()=>({fingerprint:'b'.repeat(64)}),notebookOpenGeneration:0,requestedId:null,selection:null,CustomEvent:class{constructor(type){this.type=type;}},
    window:{dispatchEvent(){},addEventListener(){},ATRNotebook:{openStored:async()=>false,openCloudPDF:async()=>{opened++;return true;}}},documentFile:()=>waiting});
  vm.runInContext(section('async function openNotebook(','async function activate('),ctx);const opening=ctx.openNotebook(book);
  await Promise.resolve();ctx.notebookOpenGeneration++;ctx.selection=null;finish(new Blob(['stale original']));await opening;
  assert.equal(opened,0);assert.equal(ctx.dialog.open,true);
});

test('a direct notebook link resumes on a new signed-in device without a previously opened PDF',async()=>{
  let opened;const book={id:'private-note',fingerprint};
  const ctx=base({current:()=>null,inviteToken:null,notebookOpenGeneration:0,requestedId:book.id,selection:null,idPattern:/^[A-Za-z0-9_-]+$/,
    api:async url=>{assert.equal(url,'/v1/study/notebooks/private-note');return{notebook:book};},openNotebook:async value=>{opened=value;}});
  vm.runInContext(section('async function resume(','async function documentOpened('),ctx);await ctx.resume();assert.equal(opened,book);
});

test('original document storage sends only the exact PDF Blob to the credentialed size-bounded endpoint',async()=>{
  const blob=new Blob(['%PDF-fixture'],{type:'application/pdf'});let request;
  const ctx=base({apiBase:'https://api.example.test',AbortSignal,window:{ATRNotebook:{pdfBlob:()=>blob}},
    fetch:async(url,args)=>{request={url,...args};return{ok:true,json:async()=>({ok:true})};}});
  vm.runInContext(section('async function documentFile(','function safeAccount('),ctx);await ctx.documentFile({id:'book',fingerprint},{upload:true});
  assert.equal(request.url,`https://api.example.test/v1/study/notebooks/book/document?size=${blob.size}`);
  assert.equal(request.credentials,'include');assert.equal(request.headers['Content-Type'],'application/pdf');assert.equal(request.body,blob);
  assert.equal(request.method,'POST');assert.equal(request.body.type,'application/pdf');
});

test('reauthentication verifies the existing account before credential management',async()=>{
  const calls=[];
  const ctx=base({PublicKeyCredential:class{},window:{SimpleWebAuthnBrowser:{startAuthentication:async()=>{calls.push('native-auth');return{id:'existing-key'};}}},
    api:async(url,args)=>{calls.push(url);return{options:{challenge:'fixture'}};}});
  vm.runInContext(section('async function reauthenticate(','async function accountSettings('),ctx);await ctx.reauthenticate();
  assert.deepEqual(calls,['/v1/study/auth/reauth/options','native-auth','/v1/study/auth/reauth/verify']);
  assert.equal(ctx.account.id,'member');
});

test('adding a passkey uses existing-account credential endpoints and keeps the last key non-removable',async()=>{
  const calls=[];let rerendered=0;
  const ctx=base({api:async(url,args)=>{calls.push(url);if(url.endsWith('/me'))return{account:{id:'member',displayName:'Member'},features:{additionalPasskeys:true}};if(url.endsWith('/credentials'))return{credentials:[{id:'existing',label:'Old key',createdAt:1}]};return{options:{challenge:'new-key'}};},
    window:{SimpleWebAuthnBrowser:{startRegistration:async()=>({id:'additional-key'})}},reauthenticate:async()=>{calls.push('reauth');}});
  vm.runInContext(section('async function accountSettings(','function checkedPresentation('),ctx);await ctx.accountSettings();
  assert.equal(nodes(ctx.content).some(n=>n.tag==='button'&&n.text==='패스키 삭제'),false);
  const add=nodes(ctx.content).find(n=>n.text==='이 계정에 패스키 추가');ctx.accountSettings=async()=>{rerendered++;};await add.handler();
  assert.ok(calls.indexOf('reauth')<calls.indexOf('/v1/study/auth/credential/options'));assert.ok(calls.includes('/v1/study/auth/credential/verify'));
  assert.equal(calls.some(path=>path.includes('/auth/register/')),false);assert.equal(ctx.account.id,'member');assert.equal(rerendered,1);
});

test('publication review requires rights confirmation and submits draft text without personal ink',async()=>{
  const requests=[];let listed=0;
  const ctx=base({api:async(url,args)=>{requests.push({url,...args});if(url.endsWith('/notebooks'))return{notebooks:[]};if(url.endsWith('/submit'))return{submission:{id:'submission',published:false}};return{draft:{id:'draft-1',status:'draft'}};},draftLibrary:async()=>{listed++;}});
  vm.runInContext(section('async function allNotebookMetadata(','function roleLabel(')+section('async function draftEditor(','async function render()'),ctx);await ctx.draftEditor(null);
  const all=nodes(ctx.content);all.find(n=>n.tag==='label'&&n.text==='제목').children[0].value='Review title';
  const submit=all.find(n=>n.tag==='button'&&n.text==='공개 검토 요청');await submit.handler();assert.equal(requests.filter(r=>r.method==='POST').length,0);
  all.find(n=>n.tag==='input'&&n.type==='checkbox').checked=true;await submit.handler();
  const created=requests.find(r=>r.url==='/v1/study/drafts');assert.equal(created.body.notebookId,null);assert.equal('pages'in created.body,false);assert.equal('ink'in created.body,false);
  assert.equal(requests.at(-1).url,'/v1/study/drafts/draft-1/submit');assert.equal(requests.at(-1).body.rightsConfirmed,true);assert.equal(listed,1);
});

test('submitted drafts remain read-only until the review request is explicitly withdrawn',async()=>{
  let endpoint,edited;
  const ctx=base({draftLibrary:async()=>{},api:async url=>{endpoint=url;return{draft:{id:'d',status:'draft'}};}});
  vm.runInContext(section('async function draftEditor(','async function render()'),ctx);
  await ctx.draftEditor({id:'d',status:'submitted',title:'Submitted',summary:'Summary',body:'Text'});
  assert.equal(nodes(ctx.content).some(n=>n.tag==='textarea'),false);
  const withdraw=nodes(ctx.content).find(n=>n.text==='검토 요청 취소');ctx.draftEditor=async value=>{edited=value;};await withdraw.handler();
  assert.equal(endpoint,'/v1/study/drafts/d/withdraw');assert.equal(edited.status,'draft');
});

test('presenter following is opt-in and defers page changes while the student writes',async()=>{
  const pages=[],session={state:{metadata:{pageCount:114}}};
  const ctx=base({active:session,matches:value=>value===session,followPresenter:false,presentation:{presenterId:'teacher',page:12},
    window:{ATRNotebook:{goPage:async page=>pages.push(page)}}});
  vm.runInContext(section('async function followPresentation(','const draftStatus='),ctx);
  await ctx.followPresentation(session);assert.equal(pages.length,0);
  ctx.followPresenter=true;ctx.current=()=>({page:1,drawing:true});await ctx.followPresentation(session);assert.equal(pages.length,0);
  ctx.current=()=>({page:1,drawing:false,busy:false});await ctx.followPresentation(session);assert.deepEqual(pages,[12]);
  ctx.presentation.presenterId='member';await ctx.followPresentation(session);assert.deepEqual(pages,[12]);
});

test('expired presentation state cannot re-enable page following after reopening',()=>{
  const ctx=base({idPattern:/^[A-Za-z0-9_-]+$/});vm.runInContext(section('function checkedPresentation(','function presentationIndicator('),ctx);
  assert.equal(ctx.checkedPresentation({id:'p',presenterId:'teacher',presenterName:'Teacher',page:2,expiresAt:Date.now()-1000},{pageCount:3}),null);
  assert.throws(()=>ctx.checkedPresentation({id:'p',presenterId:'teacher',presenterName:'Teacher',page:4,expiresAt:Date.now()+1000},{pageCount:3}),/INVALID_RESPONSE/);
});
