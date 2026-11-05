/** Private study workspace. Original PDF uploads require an explicit owner action. */
import {normalizeNotebook,diffOperations,compactOperations,pendingAfterSnapshot,
  mergeNotebook,remoteNotebook,operationBatches,applyRemoteChanges,switchNotebookView,applyNotebookIfCurrent,
  NOTEBOOK_ROLES,roleCapabilities,partitionOperations,strokeKey} from './cloud-core.mjs';

const en = new URL(location.href).searchParams.get('lang') === 'en';
const t = (ko,english) => en ? english : ko;
const loopback = host => ['localhost','127.0.0.1','[::1]'].includes(host);
let apiBase = 'https://api.infant83.io';
if (loopback(location.hostname)) {
  try {
    const override = new URL(new URL(location.href).searchParams.get('api'));
    if (loopback(override.hostname) && ['http:','https:'].includes(override.protocol) && !override.username &&
        !override.password && override.pathname === '/' && !override.search && !override.hash) apiBase = override.origin;
  } catch { /* Public pages always use the fixed API host. */ }
}
const path = '/v1/study';
const idPattern = /^[A-Za-z0-9][A-Za-z0-9_-]{0,159}$/;
let account = null, active = null, timer = null, running = false, needSync = false, epoch = 0;
let dialog, content, feedback, opener, busyUI = false, requestedId = new URL(location.href).searchParams.get('notebook');
let lastStatus = '', dbPromise, selection = null, initialized = false, renderGeneration = 0, authGeneration = 0;
let workingGeneration=0,activationGeneration=0;
let notebookOpenGeneration=0;
let features={documentStorage:false,drafts:false,presenter:false,additionalPasskeys:false},storageUsage=null;
let presentation=null,followPresenter=false,presentationPoll=false;
const idleWaiters=[];
const button = document.getElementById('cloud-sync');
const live = document.createElement('span'); live.className = 'cloud-live'; live.setAttribute('role','status');
document.body.append(live);
function readInviteFragment(){
  try{
    const candidate=new URLSearchParams(location.hash.slice(1)).get('invite');
    return candidate&&/^[A-Za-z0-9_-]{20,512}$/.test(candidate)?candidate:null;
  }catch{return null;}
}
let inviteToken=readInviteFragment();
let invitePreview=null;

function error(code,status = 0) { const value = new Error(code); value.status = status; return value; }
async function api(endpoint,{method='GET',body}={}) {
  if (!endpoint.startsWith(path+'/')) throw error('INVALID_API_PATH');
  const controller = new AbortController(), deadline = setTimeout(()=>controller.abort(),15000);
  try {
    const response = await fetch(apiBase+endpoint,{method,credentials:'include',cache:'no-store',redirect:'error',
      headers:body === undefined ? {Accept:'application/json'} : {Accept:'application/json','Content-Type':'application/json'},
      body:body === undefined ? undefined : JSON.stringify(body),signal:controller.signal});
    const text = await response.text();
    if (text.length > 40000000) throw error('RESPONSE_TOO_LARGE');
    let value; try { value = JSON.parse(text); } catch { throw error('INVALID_RESPONSE',response.status); }
    if (!response.ok || value?.ok !== true) throw error(value?.error || 'REQUEST_FAILED',response.status);
    return value;
  } catch (cause) {
    if (cause?.name === 'AbortError') throw error('TIMEOUT');
    if (cause instanceof TypeError) throw error('NETWORK');
    throw cause;
  } finally { clearTimeout(deadline); }
}
async function documentFile(notebook,{upload=false}={}){
  const blob=upload?window.ATRNotebook?.pdfBlob?.():null;
  if(upload&&(!blob||current()?.fingerprint!==notebook.fingerprint))throw error('FINGERPRINT_MISMATCH');
  if(blob?.size>50*1024*1024)throw error('PDF_TOO_LARGE');
  const response=await fetch(apiBase+path+'/notebooks/'+encodeURIComponent(notebook.id)+'/document'+(upload?'?size='+blob.size:''),{
    method:upload?'POST':'GET',credentials:'include',cache:'no-store',redirect:'error',
    ...(upload?{headers:{'Content-Type':'application/pdf'},body:blob}:{}),signal:AbortSignal.timeout(120000)});
  if(!response.ok){let message='DOCUMENT_UNAVAILABLE';try{message=(await response.json()).error||message;}catch{}throw error(message,response.status);}
  if(upload)return response.json();
  const result=await response.blob();if(result.size>50*1024*1024)throw error('PDF_TOO_LARGE');return result;
}
function safeAccount(value) {
  if (value === null) return null;
  if (!value || !idPattern.test(value.id) || typeof value.displayName !== 'string' || value.displayName.length > 120) throw error('INVALID_RESPONSE');
  return {id:value.id,displayName:value.displayName};
}
function safeMetadata(value) {
  if (!value || !idPattern.test(value.id) || !/^[a-f0-9]{64}$/.test(value.fingerprint) ||
      typeof value.title !== 'string' || value.title.length > 500 || !Number.isInteger(value.pageCount) ||
      value.pageCount < 1 || value.pageCount > 10000 || !NOTEBOOK_ROLES.includes(value.role)) throw error('INVALID_RESPONSE');
  if (value.publicId != null && !/^[A-Za-z0-9][A-Za-z0-9_-]{0,179}$/.test(value.publicId)) throw error('INVALID_RESPONSE');
  if (value.ownerName != null && (typeof value.ownerName!=='string'||value.ownerName.length>120)) throw error('INVALID_RESPONSE');
  return {...value,publicId:value.publicId || null};
}
async function allNotebookMetadata({includeDeleted=false}={}){
  const owner=account?.id,notebooks=[],seen=new Set();let cursor=null;
  for(let page=0;page<51;page++){
    const query=new URLSearchParams();if(includeDeleted)query.set('includeDeleted','1');if(cursor!==null)query.set('cursor',String(cursor));
    const result=await api(path+'/notebooks'+(query.size?'?'+query:''));
    if(account?.id!==owner)throw error('READER_BUSY');
    if(!Array.isArray(result.notebooks)||result.notebooks.length>200)throw error('INVALID_RESPONSE');
    for(const value of result.notebooks){const notebook=safeMetadata(value);if(!seen.has(notebook.id)){seen.add(notebook.id);notebooks.push(notebook);}}
    if(result.nextCursor==null)return notebooks;
    if(!Number.isInteger(result.nextCursor)||result.nextCursor<=Number(cursor)||result.nextCursor>10000)throw error('NOTEBOOK_LIST_LIMIT');
    cursor=result.nextCursor;
  }
  throw error('NOTEBOOK_LIST_LIMIT');
}
function roleLabel(role){return {owner:t('내 노트','Owner'),editor:t('공동 편집','Co-edit'),contributor:t('내 필기 추가','Add own notes'),viewer:t('보기만','View only')}[role]||'';}
function roleDescription(role){return {
  owner:t('모든 필기와 공유 권한을 관리합니다.','Manage all ink and sharing permissions.'),
  editor:t('새 필기를 추가하고 기존 필기도 지울 수 있습니다. 변경은 참여자 모두에게 보입니다.','Add ink and erase existing ink. Changes are visible to every member.'),
  contributor:t('새 필기는 모두에게 보입니다. 내가 추가한 필기만 지울 수 있고 기존 필기와 다른 사람의 필기는 보호됩니다.','New ink is visible to every member. Erase only your own additions; existing and other members’ ink is protected.'),
  viewer:t('공유된 필기를 읽을 수 있습니다. 필기를 추가하거나 지울 수 없습니다.','Read the shared notes. Adding or erasing ink is unavailable.')
}[role]||'';}
function roleSelect(selected='viewer',label=t('공유 권한','Sharing permission')){
  const select=el('select',undefined,'cloud-role-select');select.setAttribute('aria-label',label);
  for(const role of ['viewer','contributor','editor']){const option=el('option',roleLabel(role));option.value=role;select.append(option);}
  select.value=selected;select.disabled=busyUI;return select;
}
function setReaderRole(metadata,snapshot=null,pending=[]){
  if(!current()?.fingerprint||metadata.fingerprint!==current().fingerprint)return;
  const authors=new Map((snapshot?.strokeAuthors||[]).map(item=>[strokeKey(item.page,item.id),item]));
  for(const operation of pending)if(operation.type==='put'){
    const key=strokeKey(operation.page,operation.stroke.id);
    if(!authors.has(key))authors.set(key,{page:operation.page,id:operation.stroke.id,accountId:account?.id||null});
  }
  window.ATRNotebook?.setPermissions?.({fingerprint:metadata.fingerprint,notebookId:metadata.id,role:metadata.role,
    accountId:account?.id||null,strokeAuthors:[...authors.values()]});
  const permissionNode=dialog?.querySelector('[data-cloud-permission]');if(permissionNode)permissionNode.textContent=roleLabel(metadata.role)+' · '+roleDescription(metadata.role);
  const context=document.getElementById('notebook-context');
  if(context){context.textContent=roleLabel(metadata.role)+' · '+metadata.title+(metadata.ownerName?t(' · 소유자 ',' · Owner: ')+metadata.ownerName:'')+(metadata.documentAvailable?t(' · 원본 클라우드 보관',' · Original in cloud'):'');context.title=context.textContent;}
}
function lockReader(){const view=current();if(view)window.ATRNotebook?.setPermissions?.({fingerprint:view.fingerprint,role:'viewer'});}
async function restoreDisplayedPermissions(){
  const view=current(),attempt=activationGeneration,generation=workingGeneration;if(!view)return;
  const sameView=()=>current()?.fingerprint===view.fingerprint&&attempt===activationGeneration&&generation===workingGeneration;
  const marker=await readStore('links',workingKey(view.fingerprint));
  if(!sameView())return;
  if(matches(active)){setReaderRole(active.state.metadata,active.state.remote,active.state.pending);return;}
  if(!marker){window.ATRNotebook?.setPermissions?.({fingerprint:view.fingerprint,role:'local'});const context=document.getElementById('notebook-context');if(context)context.textContent=t('이 기기의 개인 필기 · 원본 PDF와 별도 저장','Personal device notes · Stored separately from the original PDF');return;}
  const state=marker.stateKey?await readStore('states',marker.stateKey):null;
  if(!sameView())return;
  if(state&&account?.id===state.accountId&&!marker.transition)setReaderRole(safeMetadata(state.metadata),state.remote,state.pending);
  else lockReader();
}
function current() { return window.ATRNotebook?.current?.() || null; }
function matches(session) { return session && active === session && session.epoch === epoch && account?.id === session.accountId && current()?.fingerprint === session.state.fingerprint; }
function workingToken(session=null){
  const view=current();
  if(!view||view.drawing||view.busy||(session&&!matches(session)))return null;
  return{fingerprint:view.fingerprint,mutationRevision:view.mutationRevision,generation:workingGeneration,
    sessionGeneration:session?.localGeneration,epoch,accountId:account?.id};
}
function unchanged(expected,session=null){const now=workingToken(session);return Boolean(expected&&now&&Object.keys(expected).every(key=>expected[key]===now[key]));}
async function exported() {
  if (!window.ATRNotebook?.exportNotebook || current()?.drawing || current()?.busy) throw error('READER_BUSY');
  return normalizeNotebook(await window.ATRNotebook.exportNotebook());
}

function database() {
  if (!dbPromise) dbPromise = new Promise((resolve,reject)=>{
    if (!globalThis.indexedDB) return reject(error('SYNC_STORAGE_UNAVAILABLE'));
    const request = indexedDB.open('atr-study-cloud-sync',1);
    const deadline = setTimeout(()=>reject(error('SYNC_STORAGE_UNAVAILABLE')),5000);
    request.onupgradeneeded = ()=>{
      for (const name of ['states','links']) if (!request.result.objectStoreNames.contains(name)) request.result.createObjectStore(name,{keyPath:'key'});
    };
    request.onsuccess = ()=>{
      clearTimeout(deadline); const db = request.result;
      db.onversionchange = ()=>{db.close();dbPromise=null;}; resolve(db);
    };
    request.onerror = request.onblocked = ()=>{clearTimeout(deadline);reject(error('SYNC_STORAGE_UNAVAILABLE'));};
  }).catch(cause=>{dbPromise=null;throw cause;});
  return dbPromise;
}
async function readStore(store,key) {
  const db=await database();
  return new Promise((resolve,reject)=>{
    const request=db.transaction(store).objectStore(store).get(key);
    request.onsuccess=()=>resolve(request.result || null);request.onerror=()=>reject(error('SYNC_STORAGE_UNAVAILABLE'));
  });
}
async function writeStore(store,value,remove=false) {
  const db=await database();
  return new Promise((resolve,reject)=>{
    const transaction=db.transaction(store,'readwrite'), bucket=transaction.objectStore(store);
    if (remove) bucket.delete(value.key); else bucket.put(value);
    transaction.oncomplete=resolve;transaction.onerror=transaction.onabort=()=>reject(error('SYNC_STORAGE_UNAVAILABLE'));
  });
}
const stateKey=(accountId,notebookId)=>accountId+':'+notebookId;
const linkKey=(accountId,fingerprint)=>accountId+':'+fingerprint;
const workingKey=fingerprint=>'working:'+fingerprint;
async function saveState(session) { await writeStore('states',session.state); }
async function stopSession(){active=null;epoch++;clearTimeout(timer);presentation=null;followPresenter=false;presentationPoll=false;presentationIndicator();if(running)await new Promise(resolve=>idleWaiters.push(resolve));}
async function preserveDisplayed(displayed,local){
  if(!displayed?.stateKey||displayed.transition)return;
  const previous=await readStore('states',displayed.stateKey);if(!previous)return;
  previous.pending=compactOperations([...previous.pending,...diffOperations(previous.localBase,local)]);
  previous.localBase=local;await writeStore('states',previous);
}
async function applyWorking(notebook,options={}){
  // Reader backups use a numeric position; the network uses {page}.
  return window.ATRNotebook.applyNotebook({...notebook,position:notebook.position.page},options);
}
function downloadBlocked(state){
  if(!state.blockedLocal)return;
  const notebook=normalizeNotebook(state.blockedLocal),blob=new Blob([JSON.stringify({...notebook,position:notebook.position.page})],{type:'application/json'});
  const url=URL.createObjectURL(blob),link=el('a');link.href=url;link.download='unsent-device-notes.json';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
}
function restrictPending(state,snapshot,local=state.localBase){
  const metadata=safeMetadata(snapshot.notebook),partition=partitionOperations(state.pending,metadata.role,state.accountId,snapshot.strokeAuthors||[],snapshot.pages);
  state.metadata=metadata;
  if(partition.blocked.length){state.blockedLocal=normalizeNotebook(local);state.pending=partition.allowed;}
  return partition.blocked.length>0;
}

function status(kind,message) {
  const label = kind === 'synced' ? t('연결됨','Connected') : kind === 'pending' ? t('저장 대기','Pending') :
    kind === 'syncing' ? t('동기화 중','Syncing') : kind === 'error' ? t('동기화 확인','Check sync') : t('동기화','Sync');
  if (button) {
    button.dataset.cloudState=kind;
    const name=account?.displayName||t('로그인','Sign in');
    const text=button.querySelector('span'); if(text) text.textContent=name;
    button.classList.toggle('signed-in',Boolean(account));
    button.title=name+' · '+label+(message?' · '+message:'');button.setAttribute('aria-label',button.title);
  }
  if (message && lastStatus !== message) {live.textContent=message;lastStatus=message;}
  const node=dialog?.querySelector('[data-cloud-status]');if(node) node.textContent=message || '';
}
function help(cause) {
  if (cause?.name === 'NotAllowedError' || cause?.name === 'AbortError') return t('패스키 확인을 취소했습니다. 다시 시도할 수 있습니다.','Passkey confirmation was cancelled. You can try again.');
  if (cause.status === 401) return t('다시 로그인해 주세요. 기기 필기는 보관되어 있습니다.','Sign in again. Your device notes are retained.');
  if (cause.status === 410) return t('초대 링크가 만료되었거나 이미 사용되었습니다. 소유자에게 새 초대 링크를 요청해 주세요.','This invitation has expired or was already used. Ask the owner for a new invitation link.');
  if (cause.message === 'document_storage_unavailable') return t('원본 PDF 클라우드 보관을 아직 사용할 수 없습니다. 기기에서 가져오기와 필기 동기화는 계속 사용할 수 있습니다.','Cloud storage for PDF originals is unavailable. Device import and ink sync remain available.');
  if (cause.message === 'document_quota_exceeded') return t('이 계정의 원본 PDF 보관 한도 500 MB를 넘었습니다. 이 파일은 기기에 그대로 두고 필기를 동기화할 수 있습니다.','This account’s 500 MB PDF storage limit has been reached. Keep the file on this device and continue syncing ink.');
  if (cause.message === 'draft_content_required') return t('검토할 본문을 입력하거나 클라우드에 보관한 원본 PDF를 첨부해 주세요. 초안은 그대로 보관됩니다.','Add review text or attach an original PDF stored in the cloud. Your draft is retained.');
  if (cause.message === 'notebook_limit') return t('활성 노트 한도 100권에 도달했습니다. 사용하지 않는 노트를 휴지통으로 옮긴 뒤 다시 시도해 주세요.','The 100 active-notebook limit has been reached. Move an unused notebook to trash before trying again.');
  if (cause.message === 'notebook_retention_limit') return t('휴지통을 포함한 노트 보관 한도 200권에 도달했습니다. 중요한 필기를 백업한 뒤 보관량 정리를 관리자에게 요청해 주세요.','The 200 retained-notebook limit, including trash, has been reached. Back up important notes and ask the administrator to review retained storage.');
  if (cause.message === 'presentation_in_use') return t('다른 발표가 시작되었거나 발표자가 바뀌었습니다. 발표 화면을 다시 열어 확인해 주세요.','Another presentation started or its presenter changed. Reopen the presentation panel to check.');
  if (cause.message === 'PDF_TOO_LARGE') return t('PDF는 50 MB 이하의 파일을 선택해 주세요.','Choose a PDF up to 50 MB.');
  if (cause.message === 'draft_locked_for_review') return t('검토 대기 중인 제출본입니다. 요청을 취소하면 다시 수정할 수 있습니다.','This draft is awaiting review. Withdraw the request before editing it.');
  if (cause.message === 'INVALID_TITLE') return t('제목을 입력해 주세요.','Enter a title.');
  if (cause.message === 'COPY_SYNC_REQUIRED') return t('이 노트의 기기 필기를 먼저 동기화한 뒤 사본을 만들어 주세요. 전송되지 않은 필기는 백업할 수 있습니다.','Sync this notebook’s device notes before copying it. Unsent notes remain available for backup.');
  if (cause.message === 'SAVE_FAILED') return t('기기 필기를 저장하지 못했습니다. 현재 노트를 유지하고 필기를 백업해 주세요.','Device notes could not be saved. Keep the current notebook open and export a backup.');
  if (cause.message === 'NOTEBOOK_LIST_LIMIT') return t('노트 목록을 끝까지 불러오지 못했습니다. 잠시 후 목록을 다시 확인해 주세요.','The complete notebook list could not be loaded. Refresh the list shortly.');
  if (cause.status === 403 || cause.status === 404) return t('이 노트에 접근할 수 없습니다. 기기 필기는 보관되어 있습니다.','This notebook is unavailable to your account. Device notes are retained.');
  if (cause.message === 'PASSKEY_UNAVAILABLE') return t('이 브라우저에서 패스키를 사용할 수 없습니다. Safari나 최신 브라우저에서 열어 주세요.','Passkeys are unavailable in this browser. Open Safari or another current browser.');
  if (cause.message === 'SYNC_STORAGE_UNAVAILABLE') return t('동기화 대기열을 저장할 수 없습니다. 기기 저장 상태를 확인해 주세요.','The sync queue could not be saved. Check this browser’s storage.');
  if (cause.message === 'FINGERPRINT_MISMATCH') return t('이 노트에 연결된 것과 같은 원본 PDF를 열어 주세요.','Open the identical original PDF linked to this notebook.');
  if (cause.message === 'STROKE_TOO_LARGE') return t('한 획이 동기화 크기 제한을 넘었습니다. 필기는 기기에 남아 있습니다.','A stroke exceeds the sync size limit. It remains saved on this device.');
  if (cause.message === 'STROKE_ID_CONFLICT') return t('필기 판본이 충돌했습니다. 기기 필기를 백업한 뒤 다시 연결해 주세요.','Stroke versions conflict. Back up the device notes before reconnecting.');
  if (cause.message === 'READER_BUSY') return t('현재 필기를 마친 뒤 다시 시도해 주세요.','Finish the current drawing action, then try again.');
  if (cause.status === 429) return t('요청이 많습니다. 잠시 후 자동으로 다시 확인합니다.','Too many requests. Sync will check again shortly.');
  return t('연결을 확인해 주세요. 기기 필기는 유지되며 동기화를 다시 시도합니다.','Check your connection. Device notes are retained and sync will retry.');
}
function feedbackText(message,isError=false) { if(feedback){feedback.textContent=message;feedback.classList.toggle('cloud-error',isError);} }
function el(tag,text,className) {const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;}
function action(text,handler,className='cloud-action') {
  const control=el('button',text,className);control.type='button';control.disabled=busyUI;
  control.addEventListener('click',()=>void runUI(handler));return control;
}
async function runUI(handler) {
  if(busyUI)return;busyUI=true;dialog?.setAttribute('aria-busy','true');
  const controls=[...dialog?.querySelectorAll('button,select') || []];controls.forEach(node=>node.disabled=true);feedbackText('');
  try {await handler();}catch(cause){feedbackText(help(cause),true);}
  finally {
    busyUI=false;dialog?.removeAttribute('aria-busy');
    // Rendering can replace the original controls while an async action runs.
    // Cloud buttons/selects have no permanent disabled policy; unlock the
    // currently displayed controls too, rather than only detached old nodes.
    new Set([...controls,...dialog?.querySelectorAll('button,select') || []]).forEach(node=>{if(node.isConnected)node.disabled=false;});
  }
}
function ensureDialog() {
  if(dialog)return;
  dialog=el('dialog',undefined,'cloud-dialog');dialog.setAttribute('aria-labelledby','study-cloud-title');
  const header=el('header',undefined,'cloud-header');const title=el('h2',t('내 학습 공간','My study space'));title.id='study-cloud-title';
  const close=el('button','×','cloud-close');close.type='button';close.setAttribute('aria-label',t('닫기','Close'));close.addEventListener('click',()=>dialog.close());
  header.append(title,close);content=el('div',undefined,'cloud-content');feedback=el('p',undefined,'cloud-feedback');feedback.setAttribute('role','status');
  dialog.append(header,content,feedback);document.body.append(dialog);
  dialog.addEventListener('close',()=>{if(opener?.isConnected)opener.focus();});
  dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
  dialog.addEventListener('keydown',event=>{
    if(event.key!=='Tab')return;
    const controls=[...dialog.querySelectorAll('button:not(:disabled),input:not(:disabled),select:not(:disabled),a[href]')].filter(node=>!node.hidden);
    if(!controls.length){event.preventDefault();return;}
    if(event.shiftKey&&document.activeElement===controls[0]){event.preventDefault();controls.at(-1).focus();}
    else if(!event.shiftKey&&document.activeElement===controls.at(-1)){event.preventDefault();controls[0].focus();}
  });
}
async function show() {
  document.getElementById('library-dialog')?.close();
  ensureDialog();opener=document.activeElement;content.replaceChildren();feedbackText('');
  if(!dialog.open)dialog.showModal();
  await render();
}
async function appendDeviceLibrary(generation,renderedAccount){
  const source=await window.ATRNotebook?.libraryData?.();
  if(!dialog.open||generation!==renderGeneration||account?.id!==renderedAccount)return;
  const section=el('section',undefined,'cloud-section');section.append(el('h3',t('이 기기에 보관','On this device')),
    action(t('내 PDF 가져오기','Bring your own PDF'),()=>{dialog.close();window.ATRNotebook?.chooseLocalPDF?.();},'cloud-action cloud-primary'));
  section.append(el('p',t('가져오기는 이 기기에서 열기입니다. PDF 원본의 클라우드 보관은 선택한 노트에서 따로 설정합니다.','Import opens a file on this device. Cloud storage for the original PDF is a separate choice in its notebook.'),'cloud-muted'));
  const list=el('ul',undefined,'cloud-notebooks');
  const local=(source?.local||[]).filter(item=>!item.deletedAt),trashed=(source?.local||[]).filter(item=>item.deletedAt);
  for(const item of local){
    const row=el('li'),text=el('div');text.append(el('strong',item.title),el('small',`${item.position||1} / ${item.pageCount} `+t('쪽 · 필기 ','pages · ink on ')+(item.annotatedPages?.length||0)+t('쪽',' pages')));
    const actions=el('div',undefined,'cloud-row-actions');actions.append(action(t('열기','Open'),async()=>{await window.ATRNotebook?.chooseStored?.(item.fingerprint);if(dialog.open)dialog.close();}),action(t('기기 휴지통','Device trash'),async()=>{
      if(!confirm(t('이 기기의 목록에서 휴지통으로 옮길까요? 기기 원본과 필기는 보관되며 클라우드 노트는 유지됩니다.','Move this device copy to device trash? The original and notes remain stored, and cloud notebooks are retained.')))return;
      await window.ATRNotebook?.trashLocal?.(item.fingerprint);await render();
    },'cloud-text-button'));row.append(text,actions);list.append(row);
  }
  if(!list.children.length)section.append(el('p',t('이 기기에 가져온 PDF가 없습니다.','No PDFs have been saved on this device.'),'cloud-muted'));
  section.append(list);content.append(section);
  if(trashed.length){
    const trash=el('details',undefined,'cloud-published');trash.append(el('summary',t('기기 휴지통','Device trash')));
    const rows=el('ul',undefined,'cloud-notebooks');for(const item of trashed){const row=el('li');row.append(el('strong',item.title),action(t('복원','Restore'),async()=>{await window.ATRNotebook?.restoreLocal?.(item.fingerprint);await render();}));rows.append(row);}trash.append(rows);content.append(trash);
  }
  const published=el('details',undefined,'cloud-published');published.append(el('summary',t('공개 렉처 자료','Published lecture material')));
  const lectures=el('ul',undefined,'cloud-notebooks');
  for(const item of source?.published||[]){
    const row=el('li'),text=el('div');text.append(el('strong',en&&item.title_en?item.title_en:item.title),el('small',item.date+' · PDF'));
    row.append(text,action(t('열기','Open'),async()=>{await window.ATRNotebook?.choosePublished?.(item.id);if(dialog.open)dialog.close();}));lectures.append(row);
  }
  published.append(lectures);content.append(published);
}
async function notebookDetails(notebook){
  ensureDialog();if(!dialog.open)dialog.showModal();content.replaceChildren();feedbackText('');
  content.append(el('h3',notebook.title),el('p',roleLabel(notebook.role)+(notebook.ownerName?t(' · 소유자 ',' · Owner: ')+notebook.ownerName:'')+' · '+roleDescription(notebook.role),'cloud-permission-note'));
  content.append(el('p',notebook.publicId?t('공개 렉처의 원본 PDF를 사용합니다. 필기는 이 노트에 별도로 저장합니다.','Uses a published lecture PDF, with ink stored separately in this notebook.'):
    notebook.documentAvailable?t('원본 PDF가 클라우드에 보관되어 다른 기기와 현재 공유 구성원이 열 수 있습니다.','The original PDF is stored in the cloud and can be opened on other devices and by current members.'):
      t('원본 PDF는 기기에만 있습니다. 다른 기기에서는 같은 파일을 가져와야 합니다.','The original PDF is device-local. Bring the identical file on another device.'),'cloud-file-state'));
  const actions=el('div',undefined,'cloud-notebook-tools');actions.append(action(t('노트 열기','Open notebook'),()=>openNotebook(notebook)),action(t('새 학습 사본','New study copy'),()=>copyNotebookForm(notebook,false)),action(t('처음부터 새로 공부','Start a fresh notebook'),()=>copyNotebookForm(notebook,true)));
  if(notebook.role==='owner'){
    actions.append(action(t('공유·구성원','Share & members'),()=>sharing(notebook)));
    if(!notebook.publicId&&!notebook.documentAvailable&&features.documentStorage&&current()?.fingerprint===notebook.fingerprint)actions.append(action(t('원본 PDF 클라우드 보관','Store original PDF in cloud'),async()=>{
      if(!confirm(t('이 원본 PDF를 클라우드에 보관할까요? 이 노트의 공유 구성원도 원본 파일을 열 수 있습니다. 공개 게시물로 발행되지는 않습니다.','Store this original PDF in the cloud? Members of this notebook can also open the file. This does not publish a public article.')))return;
      await documentFile(notebook,{upload:true});notebook={...notebook,documentAvailable:true};if(matches(active)&&active.state.notebookId===notebook.id){active.state.metadata=notebook;await saveState(active);setReaderRole(notebook,active.state.remote,active.state.pending);}await notebookDetails(notebook);
    }));
    if(!notebook.publicId&&!notebook.documentAvailable)content.append(el('p',features.documentStorage?
      t('이 기기에서 원본을 연 뒤 이 화면의 ‘원본 PDF 클라우드 보관’을 선택하면 다른 기기에서도 파일을 열 수 있습니다.','Open the original on this device, then choose “Store original PDF in cloud” here to open it on other devices.'):
      t('원본 파일 클라우드 보관은 현재 준비되지 않았습니다. 기기에서 PDF를 열고 필기만 동기화할 수 있습니다.','Cloud file storage is not currently available. Open the PDF on this device and sync its ink.'),'cloud-muted'));
    actions.append(action(t('클라우드 휴지통','Cloud trash'),async()=>{
      if(!confirm(t('이 클라우드 노트를 휴지통으로 옮길까요? 공유 구성원의 접근도 중지되며, 소유자가 휴지통에서 복원할 수 있습니다.','Move this cloud notebook to trash? Member access stops; its owner can restore it from trash.')))return;
      await api(path+'/notebooks/'+encodeURIComponent(notebook.id),{method:'DELETE',body:{}});
      if(active?.state.notebookId===notebook.id){await stopSession();lockReader();}
      await render();
    },'cloud-action cloud-danger'));
  }
  actions.append(action(t('내 학습 공간','My study space'),render,'cloud-text-button'));content.append(actions);
}
function copyNotebookForm(notebook,blank){
  content.replaceChildren();feedbackText('');content.append(el('h3',blank?t('처음부터 새로 공부','Start a fresh notebook'):t('새 학습 사본','New study copy')),
    el('p',blank?t('필기 없는 개인 학습본을 새로 만듭니다. 원본 PDF와 기존 노트·공유 필기는 보관합니다.','Create a new private notebook without ink. Keep the original PDF and the existing shared notes.'):
      t('선택한 클라우드 노트의 필기를 복사합니다. 원래 노트의 공유 권한은 이어지지 않고, 전송되지 않은 기기 필기는 포함하지 않습니다.','Copy the selected cloud notebook’s ink. Sharing permissions and unsent device notes are not inherited.'),'cloud-muted'));
  const field=el('label',t('새 노트 제목','New notebook title'),'cloud-field'),input=el('input');input.maxLength=240;input.value=notebook.title+(blank?t(' · 새 학습',' · Fresh study'):t(' · 내 사본',' · My copy'));field.append(input);content.append(field);
  const actions=el('div',undefined,'cloud-actions');actions.append(action(t('만들기','Create'),async()=>{
    if(!input.value.trim())throw error('INVALID_TITLE');
    await prepareCopySource(notebook);
    const reset=blank&&notebook.role==='owner';
    const result=await api(path+'/notebooks/'+encodeURIComponent(notebook.id)+(reset?'/reset':'/copy'),{method:'POST',body:reset?{title:input.value.trim()}:{title:input.value.trim(),includeInk:!blank}});
    await openNotebook(safeMetadata(result.notebook));
  },'cloud-action cloud-primary'),action(t('취소','Cancel'),()=>notebookDetails(notebook),'cloud-text-button'));content.append(actions);
}
async function prepareCopySource(notebook){
  const session=active;if(!matches(session)||session.state.notebookId!==notebook.id)return;
  if(await window.ATRNotebook?.flush?.()===false)throw error('SAVE_FAILED');
  if(running)await new Promise(resolve=>idleWaiters.push(resolve));
  if(!matches(session))throw error('READER_BUSY');
  await capture(session);await syncNow();
  if(!matches(session)||session.dirty||session.state.pending.length||session.reconcile)throw error('COPY_SYNC_REQUIRED');
}
async function reauthenticate(){
  if(!globalThis.PublicKeyCredential||!window.SimpleWebAuthnBrowser)throw error('PASSKEY_UNAVAILABLE');
  const options=await api(path+'/auth/reauth/options',{method:'POST',body:{}});
  const response=await window.SimpleWebAuthnBrowser.startAuthentication({optionsJSON:options.options});
  await api(path+'/auth/reauth/verify',{method:'POST',body:{response}});
}
async function accountSettings(){
  ensureDialog();if(!dialog.open)dialog.showModal();content.replaceChildren();feedbackText('');
  const me=await api(path+'/me');account=safeAccount(me.account);features={...features,...me.features};storageUsage=me.usage||null;
  if(!account){await render();return;}
  content.append(el('h3',account.displayName),el('p',t('현재 계정에 연결된 패스키를 관리합니다. 새 계정 만들기와 추가 패스키 등록은 서로 다른 동작입니다.','Manage passkeys attached to this account. Registering another passkey does not create a new account.'),'cloud-muted'));
  if(storageUsage)content.append(el('p',t('원본 PDF 보관: ','PDF originals: ')+Math.ceil(storageUsage.documentBytes/1024/1024)+' / '+Math.floor(storageUsage.quotaBytes/1024/1024)+' MB','cloud-file-state'));
  if(features.additionalPasskeys){
    const result=await api(path+'/credentials');if(!Array.isArray(result.credentials))throw error('INVALID_RESPONSE');
    const list=el('ul',undefined,'cloud-notebooks');
    for(const credential of result.credentials){
      const row=el('li'),text=el('div');text.append(el('strong',credential.label||t('패스키','Passkey')),el('small',t('등록: ','Added: ')+new Date(credential.createdAt).toLocaleDateString(en?'en-US':'ko-KR')));row.append(text);
      if(result.credentials.length>1)row.append(action(t('패스키 삭제','Remove passkey'),async()=>{
        if(!confirm(t('이 패스키를 계정에서 삭제할까요? 다른 등록된 패스키로 계속 로그인할 수 있습니다.','Remove this passkey? You can continue signing in with your other registered passkeys.')))return;
        await reauthenticate();await api(path+'/credentials/'+encodeURIComponent(credential.id),{method:'DELETE',body:{}});await accountSettings();
      },'cloud-text-button'));list.append(row);
    }
    content.append(list);
    const field=el('label',t('추가할 패스키 이름','New passkey label'),'cloud-field'),input=el('input');input.maxLength=100;input.placeholder=t('예: iPad, 보안 키','For example: iPad, security key');field.append(input);content.append(field);
    content.append(action(t('이 계정에 패스키 추가','Add passkey to this account'),async()=>{
      await reauthenticate();
      const options=await api(path+'/auth/credential/options',{method:'POST',body:{label:input.value.trim()||t('추가 패스키','Additional passkey')}});
      const response=await window.SimpleWebAuthnBrowser.startRegistration({optionsJSON:options.options});
      await api(path+'/auth/credential/verify',{method:'POST',body:{response}});await accountSettings();
    },'cloud-action cloud-primary'));
    content.append(el('p',t('현재 패스키로 본인 확인 후 새 패스키를 등록합니다. 마지막 패스키는 삭제하지 않습니다.','Verify with an existing passkey before adding another one. Your last passkey cannot be removed.'),'cloud-muted'));
  }
  content.append(action(t('내 학습 공간','My study space'),render,'cloud-text-button'));
}
function checkedPresentation(value,metadata){
  if(value===null)return null;
  if(!value||!idPattern.test(value.id)||!idPattern.test(value.presenterId)||typeof value.presenterName!=='string'||value.presenterName.length>120||
    !Number.isInteger(value.page)||value.page<1||value.page>metadata.pageCount||!Number.isFinite(value.expiresAt))throw error('INVALID_RESPONSE');
  return value.expiresAt<=Date.now()?null:value;
}
function presentationIndicator(){
  const bar=document.getElementById('presentation-bar');if(!bar)return;bar.hidden=!presentation;
  if(presentation){const text=presentation.presenterName+' · '+presentation.page+t('쪽',' page')+' · '+(presentation.presenterId===account?.id?t('내 페이지 발표 중','Presenting my page'):followPresenter?t('페이지 따라가는 중','Following presenter'):t('발표 진행 중','Presentation active'));
    const description=document.getElementById('presentation-description');if(description&&description.textContent!==text)description.textContent=text;
    const control=document.getElementById('presentation-action');if(control)control.textContent=followPresenter?t('따라가기 중지','Stop following'):t('발표 페이지','Presenter page');}
  const toggle=dialog?.querySelector('[data-follow-presenter]');if(toggle)toggle.checked=followPresenter;
}
async function presentationPanel(notebook){
  if(!matches(active)||active.state.notebookId!==notebook.id)throw error('READER_BUSY');
  ensureDialog();if(!dialog.open)dialog.showModal();
  const session=active,result=await api(path+'/notebooks/'+encodeURIComponent(notebook.id)+'/presentation');
  if(!matches(session))return;presentation=checkedPresentation(result.presentation,notebook);presentationPoll=Boolean(presentation);
  session.state.presentation=presentation;await saveState(session);
  presentationIndicator();
  content.replaceChildren();feedbackText('');content.append(el('h3',t('발표 페이지','Presenter page')),
    el('p',t('발표자가 보는 페이지를 주기적으로 따라갑니다. 필기는 이 노트의 공유 권한을 따르며, 펜 이동이나 음성·영상 전송은 포함하지 않습니다.','Follow the presenter’s page through periodic updates. Ink follows this notebook’s sharing permissions; pen gestures, audio and video are not streamed.'),'cloud-muted'));
  if(presentation){
    content.append(el('p',presentation.presenterName+' · '+presentation.page+t('쪽 발표 중',' presenting'),'cloud-presenter'));
    if(presentation.presenterId!==account.id){
      const label=el('label',undefined,'cloud-check'),toggle=el('input');toggle.type='checkbox';toggle.checked=followPresenter;toggle.dataset.followPresenter='';
      toggle.addEventListener('change',()=>{if(busyUI){toggle.checked=followPresenter;return;}toggle.disabled=true;void runUI(async()=>{followPresenter=toggle.checked;session.state.followPresenter=followPresenter;await saveState(session);presentationIndicator();if(followPresenter)await followPresentation(session);}).finally(()=>{toggle.disabled=false;});});
      label.append(toggle,el('span',t('발표 페이지 따라가기','Follow presenter page')));content.append(label);
    }
    if(presentation.presenterId===account.id||notebook.role==='owner')content.append(action(t('발표 종료','End presentation'),async()=>{
      await api(path+'/notebooks/'+encodeURIComponent(notebook.id)+'/presentation',{method:'DELETE',body:{}});presentation=null;followPresenter=false;presentationPoll=false;session.state.presentation=null;session.state.followPresenter=false;presentationIndicator();await saveState(session);await presentationPanel(notebook);
    }));
  }else{
    followPresenter=false;session.state.followPresenter=false;await saveState(session);
    content.append(el('p',t('현재 진행 중인 발표가 없습니다.','No presentation is active.'),'cloud-muted'));
    if(['owner','editor'].includes(notebook.role))content.append(action(t('내 페이지 발표 시작','Present my current page'),async()=>{
      await api(path+'/notebooks/'+encodeURIComponent(notebook.id)+'/presentation',{method:'POST',body:{page:current().page||1}});await presentationPanel(notebook);
    },'cloud-action cloud-primary'));
  }
  const actions=el('div',undefined,'cloud-notebook-tools');actions.append(action(t('새로 확인','Refresh'),()=>presentationPanel(notebook)),action(t('내 학습 공간','My study space'),render,'cloud-text-button'));content.append(actions);
}
async function followPresentation(session){
  if(!matches(session)||!followPresenter||!presentation||presentation.presenterId===account.id||current()?.drawing||current()?.busy)return;
  if(current()?.page!==presentation.page)await window.ATRNotebook?.goPage?.(presentation.page);
}
async function updatePresenterPage(session){
  if(!matches(session)||!presentation||presentation.presenterId!==account.id||current()?.drawing||current()?.busy)return;
  const page=current().page||1;if(page===presentation.page)return;
  const result=await api(path+'/notebooks/'+encodeURIComponent(session.state.notebookId)+'/presentation',{method:'PATCH',body:{page}});
  if(!matches(session))return;presentation=checkedPresentation(result.presentation,session.state.metadata);session.state.presentation=presentation;presentationIndicator();await saveState(session);
}
const draftStatus=value=>({draft:t('작성 중','Draft'),submitted:t('검토 대기','Submitted for review'),approved:t('승인','Approved'),rejected:t('반려','Needs revision'),published:t('공개됨','Published')}[value]||value);
async function draftLibrary(){
  content.replaceChildren();feedbackText('');content.append(el('h3',t('내 초안·공개 신청','My drafts & publication requests')),
    el('p',t('초안은 계정에 비공개로 보관됩니다. 공개 신청은 검토 요청이며, 사이트에 자동으로 게시되지 않습니다.','Drafts stay private to your account. Submitting requests editorial review and does not publish directly to the site.'),'cloud-muted'));
  const actions=el('div',undefined,'cloud-actions');actions.append(action(t('새 초안','New draft'),()=>draftEditor(null),'cloud-action cloud-primary'),action(t('내 학습 공간','My study space'),render,'cloud-text-button'));content.append(actions);
  const result=await api(path+'/drafts');if(!Array.isArray(result.drafts))throw error('INVALID_RESPONSE');
  const list=el('ul',undefined,'cloud-notebooks');for(const draft of result.drafts){const row=el('li'),text=el('div');text.append(el('strong',draft.title||t('제목 없는 초안','Untitled draft')),el('small',draftStatus(draft.status)+' · '+new Date(draft.updatedAt).toLocaleDateString(en?'en-US':'ko-KR')));row.append(text,action(t('열기','Open'),()=>draftEditor(draft)));list.append(row);}content.append(list);
}
async function draftEditor(draft){
  content.replaceChildren();feedbackText('');content.append(el('h3',draft?t('초안 수정','Edit draft'):t('새 초안','New draft')));
  if(draft?.status==='submitted'){
    content.append(el('strong',draft.title),el('p',t('검토 대기 중입니다. 제출본을 보존하기 위해 수정이 잠겨 있습니다. 요청을 취소하면 다시 수정할 수 있습니다.','Awaiting review. Editing is locked to preserve the submission. Withdraw the request to edit again.'),'cloud-warning'),el('p',draft.summary||''),el('div',draft.body||'','cloud-draft-preview'));
    const actions=el('div',undefined,'cloud-notebook-tools');actions.append(action(t('검토 요청 취소','Withdraw review request'),async()=>{
      if(!confirm(t('이 검토 요청을 취소하고 초안 수정으로 돌아갈까요?','Withdraw this review request and return to editing the draft?')))return;
      const result=await api(path+'/drafts/'+encodeURIComponent(draft.id)+'/withdraw',{method:'POST',body:{}});await draftEditor(result.draft);
    }),action(t('초안 목록','Draft list'),draftLibrary,'cloud-text-button'));content.append(actions);return;
  }
  const fields=el('div',undefined,'cloud-form');
  function field(label,value,tag='input',maxLength=240){const node=el(tag);node.value=value||'';node.maxLength=maxLength;const wrapper=el('label',label);wrapper.append(node);fields.append(wrapper);return node;}
  const title=field(t('제목','Title'),draft?.title),summary=field(t('요약','Summary'),draft?.summary,'textarea',4000),body=field(t('공개 검토용 본문','Text for editorial review'),draft?.body,'textarea',50000);
  const attached=el('select',undefined,'cloud-role-select');attached.setAttribute('aria-label',t('검토할 원본 PDF','Original PDF for review'));const noFile=el('option',t('PDF 첨부 안 함','No PDF attachment'));noFile.value='';attached.append(noFile);
  const notebooks=await allNotebookMetadata();for(const notebook of notebooks)if(notebook.role==='owner'&&(notebook.documentAvailable||notebook.publicId)){const option=el('option',notebook.title);option.value=notebook.id;attached.append(option);}
  attached.value=draft?.notebookId||'';const attachment=el('label',t('검토할 원본 PDF (선택)','Original PDF for review (optional)'));attachment.append(attached);fields.append(attachment);
  content.append(fields,el('p',t('직접 작성한 제목·요약·본문과 선택한 원본 PDF를 검토에 제출합니다. 개인 필기는 자동으로 포함되지 않습니다. 개인 PDF는 먼저 노트에서 클라우드 보관을 선택해야 합니다.','Review includes the title, summary, text and optional original PDF you select. Personal ink is not automatically included. Store a private PDF in the cloud before attaching it.'),'cloud-muted'));
  const rightsLabel=el('label',undefined,'cloud-check'),rights=el('input');rights.type='checkbox';rightsLabel.append(rights,el('span',t('작성 내용과 첨부 PDF를 공개 검토에 제출할 권한이 있습니다.','I have permission to submit this text and attached PDF for publication review.')));content.append(rightsLabel);
  async function save(){
    if(!title.value.trim())throw error('INVALID_TITLE');
    const result=await api(path+'/drafts'+(draft?'/'+encodeURIComponent(draft.id):''),{method:draft?'PATCH':'POST',body:{title:title.value.trim(),summary:summary.value.trim(),body:body.value.trim(),notebookId:attached.value||null}});draft=result.draft;return draft;
  }
  const actions=el('div',undefined,'cloud-notebook-tools');actions.append(action(t('초안 저장','Save draft'),async()=>{await save();feedbackText(t('비공개 초안을 저장했습니다.','Private draft saved.'));},'cloud-action cloud-primary'),action(t('공개 검토 요청','Request publication review'),async()=>{
    if(!rights.checked){feedbackText(t('제출 권한 확인을 선택해 주세요.','Confirm your permission to submit this material.'),true);return;}
    await save();const result=await api(path+'/drafts/'+encodeURIComponent(draft.id)+'/submit',{method:'POST',body:{rightsConfirmed:true}});
    if(result.submission?.published!==false)throw error('INVALID_RESPONSE');await draftLibrary();feedbackText(t('검토를 요청했습니다. 승인·게시 전까지 공개되지 않습니다.','Review requested. It remains unpublished until editorial approval and publication.'));
  }),action(t('초안 목록','Draft list'),draftLibrary,'cloud-text-button'));content.append(actions);
}
async function render() {
  if(!dialog?.open)return;
  const generation=++renderGeneration, renderedAccount=account?.id;
  content.replaceChildren();feedbackText('');
  if(!account){
    content.append(el('p',t('패스키로 로그인하면 다른 기기에서도 필기를 이어서 읽을 수 있습니다.','Sign in with a passkey to continue your notes on another device.'),'cloud-intro'));
    const label=el('label',t('이름','Display name'),'cloud-field');const input=el('input');input.type='text';input.maxLength=100;input.autocomplete='nickname';input.placeholder=t('노트에 표시할 이름','Name for your notebooks');label.append(input);content.append(label);
    const actions=el('div',undefined,'cloud-actions');actions.append(
      action(t('새 계정 만들기','Create account'),()=>authenticate('register',input.value.trim()),'cloud-action cloud-primary'),
      action(t('패스키로 로그인','Sign in with passkey'),()=>authenticate('login')));content.append(actions);
    content.append(el('p',t('처음 사용하면 새 계정과 패스키를 만듭니다. 기존 노트는 ‘패스키로 로그인’한 계정에서 이어갑니다. 동기화할 노트는 별도로 선택합니다.','First use creates a new account and passkey. Use “Sign in with passkey” to continue an existing account’s notes, then choose which notebook to sync.'),'cloud-muted'));
    if(inviteToken)content.append(el('p',t('초대받은 노트에 참여하려면 먼저 로그인해 주세요.','Sign in to accept the notebook invitation.'),'cloud-invite-note'));
    await appendDeviceLibrary(generation,renderedAccount);return;
  }
  const accountRow=el('div',undefined,'cloud-account');const accountActions=el('div',undefined,'cloud-actions');accountActions.append(action(t('계정·패스키','Account & passkeys'),accountSettings,'cloud-text-button'),action(t('로그아웃','Sign out'),logout,'cloud-text-button'));accountRow.append(el('strong',account.displayName),accountActions);content.append(accountRow);
  if(inviteToken){
    const previewFor=inviteToken;
    let previewFailure=null;
    if(invitePreview?.for!==previewFor){
      try{
        const preview=await api(path+'/invites/preview',{method:'POST',body: { token: previewFor }});
        if(inviteToken!==previewFor||generation!==renderGeneration||account?.id!==renderedAccount)return;
        if(!preview.invitation||!['viewer','contributor','editor'].includes(preview.invitation.role)||typeof preview.invitation.title!=='string')throw error('INVALID_RESPONSE');
        invitePreview={...preview.invitation,for:previewFor};
      }catch(cause){
        if(inviteToken!==previewFor||generation!==renderGeneration||account?.id!==renderedAccount)return;
        previewFailure=cause;
      }
    }
    const invitation=el('section',undefined,'cloud-section');invitation.append(el('h3',t('공유 노트 초대','Notebook invitation')));
    if(previewFailure){
      const message=previewFailure.status===404?t('초대 링크를 찾을 수 없습니다. 소유자에게 새 초대 링크를 요청해 주세요.','This invitation could not be found. Ask the owner for a new invitation link.'):help(previewFailure);
      const notice=el('p',message,'cloud-error');notice.setAttribute('role','alert');invitation.append(notice,
        action(t('다시 확인','Try again'),render));
    }else invitation.append(el('strong',invitePreview.title),el('p',roleLabel(invitePreview.role)+' · '+roleDescription(invitePreview.role)),
      el('p',t('이미 참여한 노트라면 현재 권한을 유지합니다. 권한 변경은 소유자가 설정합니다.','If you already belong to this notebook, your current permission stays unchanged. Its owner controls permission changes.'),'cloud-muted'),
      action(t('초대 수락','Accept invitation'),acceptInvite,'cloud-action cloud-primary'));
    invitation.append(action(t('초대 닫고 내 노트 보기','Dismiss invitation and view my notes'),dismissInvitation,'cloud-text-button'));content.append(invitation);
  }
  const document=current();
  if(document?.fingerprint){
    const section=el('section',undefined,'cloud-section');section.append(el('h3',matches(active)?active.state.metadata.title:document.title));
    const summary=el('p',matches(active)?lastStatus:t('기기 필기를 클라우드 노트와 연결합니다. 원본 PDF 클라우드 보관은 별도로 선택합니다.','Connect device notes to your cloud notebook. Storing the original PDF in the cloud is a separate choice.'),'cloud-muted');summary.dataset.cloudStatus='';section.append(summary);
    if(matches(active)){
      const permissionNode=el('p',roleLabel(active.state.metadata.role)+' · '+roleDescription(active.state.metadata.role),'cloud-permission-note');permissionNode.dataset.cloudPermission='';section.append(permissionNode);
      const actions=el('div',undefined,'cloud-actions');actions.append(action(t('지금 동기화','Sync now'),()=>syncNow()));
      if(active.state.metadata.role==='owner')actions.append(action(t('공유·구성원','Share & members'),()=>sharing(active.state.metadata)));
      actions.append(action(t('내 학습 사본 만들기','Create my study copy'),()=>copyNotebookForm(active.state.metadata,false)));
      actions.append(action(t('노트 관리·학습 사본','Manage or copy notebook'),()=>notebookDetails(active.state.metadata)));
      if(features.presenter)actions.append(action(t('발표 페이지','Presenter page'),()=>presentationPanel(active.state.metadata)));
      actions.append(action(t('이 기기 연결 해제','Disconnect this device'),disconnect,'cloud-text-button'));section.append(actions);
      if(active.state.blockedLocal)section.append(action(t('전송되지 않은 기기 필기 백업','Export unsent device notes'),()=>downloadBlocked(active.state),'cloud-text-button'));
    }else section.append(action(t('이 노트 동기화','Sync this notebook'),enableCurrent,'cloud-action cloud-primary'));
    content.append(section);
  }
  const library=el('section',undefined,'cloud-section');library.append(el('h3',t('클라우드 노트','Cloud notebooks')));content.append(library);
  const loading=el('p',t('불러오는 중…','Loading…'),'cloud-muted');library.append(loading);
  let allNotebooks;
  try{allNotebooks=await allNotebookMetadata({includeDeleted:true});}
  catch(cause){loading.textContent=help(cause);library.append(action(t('다시 확인','Try again'),render));await appendDeviceLibrary(generation,renderedAccount);return;}
  if(!dialog.open||!account||account.id!==renderedAccount||generation!==renderGeneration)return;
  const notebooks=allNotebooks.filter(item=>!item.deletedAt),trashed=allNotebooks.filter(item=>item.deletedAt);loading.remove();
  if(!notebooks.length)library.append(el('p',t('PDF를 연 뒤 ‘이 노트 동기화’를 누르세요.','Open a PDF, then choose “Sync this notebook”.'),'cloud-muted'));
  const list=el('ul',undefined,'cloud-notebooks');
  for(const notebook of notebooks){
    const row=el('li');const text=el('div');text.append(el('strong',notebook.title),el('small',notebook.pageCount+t('쪽 · ',' pages · ')+roleLabel(notebook.role)+(notebook.ownerName?t(' · 소유자 ',' · Owner: ')+notebook.ownerName:'')+(notebook.publicId?t(' · 공개 렉처 원본',' · Published original'):notebook.documentAvailable?t(' · 원본 클라우드 보관',' · Original in cloud'):t(' · 원본 파일 필요',' · Original file needed'))));
    const actions=el('div',undefined,'cloud-row-actions');actions.append(action(t('열기','Open'),()=>openNotebook(notebook)));
    if(notebook.role==='owner')actions.append(action(t('공유','Share'),()=>sharing(notebook),'cloud-text-button'));
    actions.append(action(t('관리·사본','Manage or copy'),()=>notebookDetails(notebook),'cloud-text-button'));
    row.append(text,actions);list.append(row);
  }
  library.append(list);
  if(trashed.length){const trash=el('details',undefined,'cloud-published');trash.append(el('summary',t('클라우드 휴지통','Cloud trash')));const rows=el('ul',undefined,'cloud-notebooks');
    for(const notebook of trashed){const row=el('li');row.append(el('strong',notebook.title),action(t('복원','Restore'),async()=>{await api(path+'/notebooks/'+encodeURIComponent(notebook.id)+'/restore',{method:'POST',body:{}});await render();}));rows.append(row);}trash.append(rows);content.append(trash);}
  if(features.drafts)content.append(action(t('내 초안·공개 신청','My drafts & publication requests'),draftLibrary,'cloud-action'));
  await appendDeviceLibrary(generation,renderedAccount);
}

async function authenticate(kind,displayName='') {
  if(!globalThis.PublicKeyCredential||!window.SimpleWebAuthnBrowser)throw error('PASSKEY_UNAVAILABLE');
  if(kind==='register'&&!displayName){feedbackText(t('표시할 이름을 입력해 주세요.','Enter a display name.'),true);return;}
  const options=await api(path+'/auth/'+kind+'/options',{method:'POST',body:kind==='register'?{displayName}:{}});
  if(!options.options||typeof options.options!=='object')throw error('INVALID_RESPONSE');
  const response=kind==='register'?await window.SimpleWebAuthnBrowser.startRegistration({optionsJSON:options.options}):
    await window.SimpleWebAuthnBrowser.startAuthentication({optionsJSON:options.options});
  const verified=await api(path+'/auth/'+kind+'/verify',{method:'POST',body:{response}});authGeneration++;account=safeAccount(verified.account);
  if(!account)throw error('INVALID_RESPONSE');status('idle',t('로그인했습니다. 동기화할 노트를 선택하세요.','Signed in. Choose a notebook to sync.'));
  await render();await resume();
}
async function logout(){
  await stopSession();
  if(!current()?.drawing&&!current()?.busy&&current()?.fingerprint){
    const local=await exported();await preserveDisplayed(await readStore('links',workingKey(local.document.fingerprint)),local);
  }
  await api(path+'/logout',{method:'POST',body:{}});authGeneration++;account=null;
  lockReader();
  // Anonymous writing remains available for documents without an account
  // binding. Previously connected notebooks stay read-only after sign-out.
  try{await restoreDisplayedPermissions();}catch{lockReader();}
  status('idle',t('로그아웃했습니다. 기기 필기는 유지됩니다.','Signed out. Device notes are retained.'));await render();
}

async function enableCurrent(){
  const document=current();if(!document?.fingerprint)throw error('READER_BUSY');
  const local=await exported(), notebooks=await allNotebookMetadata();
  let notebook=notebooks.find(item=>item.fingerprint===document.fingerprint&&item.role==='owner');
  if(!notebook){
    const created=await api(path+'/notebooks',{method:'POST',body:{publicId:document.publicId||null,title:local.document.title,
      fingerprint:document.fingerprint,pageCount:local.document.pageCount}});notebook=safeMetadata(created.notebook);
  }
  await activate(notebook,{allowUpload:true,restorePosition:false});if(dialog.open)await render();
}
function notebookURL(notebook){
  const url=new URL(location.href);url.search='';url.hash='';url.searchParams.set('id',notebook.publicId);url.searchParams.set('notebook',notebook.id);
  if(en)url.searchParams.set('lang','en');if(loopback(location.hostname)&&apiBase!=='https://api.infant83.io')url.searchParams.set('api',apiBase);
  return url;
}
async function openNotebook(notebook){
  if(current()?.busy||current()?.drawing)throw error('READER_BUSY');
  const attempt=++notebookOpenGeneration,owner=account?.id;
  requestedId=notebook.id;selection=notebook;
  window.dispatchEvent(new CustomEvent('atr:cloud-document-request'));
  if(current()?.fingerprint===notebook.fingerprint){await activate(notebook,{allowUpload:false,restorePosition:true});if(matches(active)&&active.state.notebookId===notebook.id&&dialog.open)dialog.close();return;}
  if(notebook.publicId){location.assign(notebookURL(notebook).href);return;}
  const opened=await window.ATRNotebook?.openStored?.(notebook.fingerprint,{quietMissing:true});
  // A newer PDF choice also cancels the pending notebook and its missing-file prompt.
  if(attempt!==notebookOpenGeneration||selection!==notebook||account?.id!==owner)return;
  if(opened){if(dialog.open)dialog.close();return;}
  if(notebook.documentAvailable){
    const blob=await documentFile(notebook);
    if(attempt!==notebookOpenGeneration||selection!==notebook||account?.id!==owner)return;
    const cloudOpened=await window.ATRNotebook?.openCloudPDF?.(blob,{title:notebook.title,publicId:notebook.publicId,sha256:notebook.fingerprint});
    if(attempt!==notebookOpenGeneration||selection!==notebook||account?.id!==owner)return;
    if(cloudOpened){if(dialog.open)dialog.close();return;}
  }
  if(dialog.open)dialog.close();
  window.dispatchEvent(new CustomEvent('atr:cloud-open-local',{detail:{fingerprint:notebook.fingerprint,title:notebook.title}}));
  status('pending',t('보관함에서 같은 원본 PDF 파일을 선택해 주세요. 클라우드 파일 보관은 별도로 선택합니다.','Choose the identical original PDF from the library. Cloud file storage is a separate choice.'));
}
window.addEventListener('atr:document-selection',event=>{
  notebookOpenGeneration++;
  if(selection?.fingerprint&&selection.fingerprint===event.detail?.fingerprint)return;
  selection=null;requestedId=null;
  const clean=new URL(location.href);clean.searchParams.delete('notebook');
  history.replaceState(history.state,'',clean.href);
});
window.addEventListener('atr:cloud-local-cancel',event=>{
  if(selection?.fingerprint!==event.detail?.fingerprint)return;
  notebookOpenGeneration++;selection=null;requestedId=null;
  status(matches(active)?'synced':'idle',t('원본 PDF 선택을 취소했습니다. 보관된 필기는 유지됩니다.','Original PDF selection cancelled. Saved notes are retained.'));
});
async function activate(notebook,{allowUpload=false,restorePosition=false}={}){
  if(!account)throw error('SIGN_IN_REQUIRED');
  const previousSession=active,attempt=++activationGeneration;
  await stopSession();
  const viewStamp=workingToken();if(!viewStamp)throw error('READER_BUSY');
  const local=await exported();if(local.document.fingerprint!==notebook.fingerprint||local.document.pageCount!==notebook.pageCount)throw error('FINGERPRINT_MISMATCH');
  const owner=account.id,key=stateKey(owner,notebook.id),displayed=await readStore('links',workingKey(notebook.fingerprint));
  if(!unchanged(viewStamp)||attempt!==activationGeneration){await restoreBinding(previousSession);throw error('READER_BUSY');}
  await preserveDisplayed(displayed,local);
  let state=await readStore('states',key),snapshot=null;
  const existingState=Boolean(state);
  if(state&&(state.accountId!==owner||state.fingerprint!==notebook.fingerprint))throw error('INVALID_NOTEBOOK');
  snapshot=await api(path+'/notebooks/'+encodeURIComponent(notebook.id));remoteNotebook(snapshot);
  if(snapshot.notebook.fingerprint!==notebook.fingerprint)throw error('FINGERPRINT_MISMATCH');
  notebook=safeMetadata(snapshot.notebook);
  const target=state?normalizeNotebook(state.localBase,local.document):remoteNotebook(snapshot).notebook;
  const currentKey=displayed?.transition?'interrupted-switch':displayed?.stateKey || (state&&!allowUpload?'unattributed-working-ink':null);
  let plan;
  try{plan=switchNotebookView({current:local,currentKey,targetKey:key,target,allowUpload});}
  catch(cause){
    if(cause.message!=='UNBOUND_NOTES_REQUIRE_CONSENT')throw cause;
    ensureDialog();if(!dialog.open)dialog.showModal();content.replaceChildren();
    content.append(el('h3',t('기기 필기와 함께 동기화','Sync with your device notes')),
      el('p',t('이 PDF에 저장한 기기 필기를 선택한 클라우드 노트와 합칩니다.','Merge the notes already saved for this PDF with the selected cloud notebook.')),
      action(t('이 노트 동기화','Sync this notebook'),async()=>{await activate(notebook,{allowUpload:true,restorePosition:false});await render();},'cloud-action cloud-primary'),
      action(t('취소','Cancel'),()=>render()));return;
  }
  state ||= {key,accountId:owner,notebookId:notebook.id,fingerprint:notebook.fingerprint,metadata:notebook,
    localBase:target,pending:[],lastSent:null,remote:snapshot,remoteCursor:snapshot?.notebook.revision};
  state.metadata=notebook;normalizeNotebook(state.localBase,local.document);
  if(!Array.isArray(state.pending))throw error('INVALID_NOTEBOOK');
  state.pending=compactOperations([...state.pending,...plan.added]);state.localBase=plan.notebook;
  state.remote=snapshot;state.remoteCursor=snapshot.notebook.revision;
  restrictPending(state,snapshot,plan.notebook);
  // A cached working view may predate the snapshot just fetched. Reconcile it
  // before advancing its remote cursor; an empty next delta cannot replay
  // changes already included in that snapshot. Durable pending edits still win.
  plan.notebook=mergeNotebook(snapshot,plan.notebook,state.pending);state.localBase=plan.notebook;
  await writeStore('states',state);
  const displayedNext={key:workingKey(notebook.fingerprint),stateKey:key,accountId:owner,notebookId:notebook.id,transition:true,attempt};
  // Persist the target before replacing the fingerprint-indexed reader view.
  // An interrupted switch restores this target before any local diff is made.
  await writeStore('links',displayedNext);
  let applied=false,applyStarted=false,applyRevision=viewStamp.mutationRevision;
  try{
    applied=await applyNotebookIfCurrent(viewStamp,()=>attempt===activationGeneration?workingToken():null,
      ()=>{applyStarted=true;lockReader();applyRevision=current()?.mutationRevision;return applyWorking(plan.notebook,{silent:true,preservePosition:currentKey===key});});
  }catch(cause){
    // A rendering failure can follow a successful transactional import. Keep
    // the target marker in that case; relabeling imported B ink as A is unsafe.
    const imported=applyStarted&&current()?.fingerprint===notebook.fingerprint&&current()?.mutationRevision!==applyRevision;
    if(attempt===activationGeneration&&!imported)await rollbackActivation(displayed,displayedNext,key,existingState,previousSession);
    throw cause;
  }
  if(!applied){
    if(attempt===activationGeneration)await rollbackActivation(displayed,displayedNext,key,existingState,previousSession);
    throw error('READER_BUSY');
  }
  await writeStore('links',{...displayedNext,transition:false});
  const session={accountId:owner,state,epoch:++epoch,restorePosition,dirty:false,localGeneration:0};active=session;
  try{presentation=checkedPresentation(state.presentation||null,state.metadata);}catch{presentation=null;state.presentation=null;state.followPresenter=false;}
  followPresenter=Boolean(presentation&&state.followPresenter);presentationPoll=Boolean(presentation);
  if(!presentation){state.presentation=null;state.followPresenter=false;}
  presentationIndicator();
  setReaderRole(state.metadata,state.remote,state.pending);
  await writeStore('links',{key:linkKey(owner,notebook.fingerprint),notebookId:notebook.id});
  selection=null;requestedId=null;status('syncing',t('클라우드 노트를 연결하는 중…','Connecting the cloud notebook…'));
  await syncNow();
}
async function restoreBinding(previousSession){
  if(previousSession&&account?.id===previousSession.accountId&&current()?.fingerprint===previousSession.state.fingerprint){
    const saved=await readStore('states',previousSession.state.key);if(saved)previousSession.state=saved;
    previousSession.epoch=++epoch;previousSession.dirty=true;active=previousSession;schedule(500);
    try{presentation=checkedPresentation(previousSession.state.presentation||null,previousSession.state.metadata);}catch{presentation=null;}
    followPresenter=Boolean(presentation&&previousSession.state.followPresenter);presentationPoll=Boolean(presentation);presentationIndicator();
    setReaderRole(previousSession.state.metadata,previousSession.state.remote,previousSession.state.pending);
  }
}
async function rollbackActivation(displayed,next,key,existingState,previousSession){
  const marker=await readStore('links',next.key);
  if(marker?.attempt===next.attempt&&marker.transition){
    if(displayed)await writeStore('links',displayed);else await writeStore('links',{key:next.key},true);
    if(!existingState)await writeStore('states',{key},true);
  }
  await restoreBinding(previousSession);
  if(!active)await restoreDisplayedPermissions();
}
async function disconnect(){
  if(!active)return;const session=active;await stopSession();
  const local=await exported();await preserveDisplayed(await readStore('links',workingKey(local.document.fingerprint)),local);
  await writeStore('links',{key:linkKey(session.accountId,session.state.fingerprint)},true);
  active=null;epoch++;clearTimeout(timer);status('idle',t('이 기기 연결을 해제했습니다. 필기는 그대로 보관됩니다.','This device is disconnected. Notes are retained.'));await render();
  lockReader();
}
async function capture(session){
  if(!matches(session))throw error('READER_BUSY');const viewStamp=workingToken(session);if(!viewStamp)throw error('READER_BUSY');
  const local=await exported();
  if(!matches(session))throw error('READER_BUSY');
  session.state.pending=compactOperations([...session.state.pending,...diffOperations(session.state.localBase,local)]);
  session.state.localBase=local;
  if(session.state.remote&&restrictPending(session.state,session.state.remote,local))session.reconcile=true;
  await saveState(session);session.captureToken=viewStamp;session.dirty=!unchanged(viewStamp,session);return local;
}
function schedule(delay=4000){
  clearTimeout(timer);if(active&&account&&document.visibilityState==='visible')timer=setTimeout(()=>void syncNow(),delay);
}
async function syncNow(){
  if(running){needSync=true;return;}
  const session=active;if(!matches(session)||document.visibilityState!=='visible')return;
  if(current()?.drawing||current()?.busy){schedule(750);return;}
  running=true;needSync=false;
  try{
    if(session.dirty)await capture(session);if(!matches(session))return;
    if(session.state.pending.length||!session.state.remote)status('syncing',t('기기에 저장됨 · 클라우드 확인 중…','Saved on device · checking cloud…'));
    let remote=await refreshRemote(session),snapshot=remote.snapshot;
    if(!matches(session))return;const metadata=safeMetadata(snapshot.notebook);
    const roleChanged=session.state.metadata.role!==metadata.role;
    const blocked=restrictPending(session.state,snapshot);
    setReaderRole(metadata,snapshot,session.state.pending);
    if(roleChanged||blocked){remote.changed=true;await saveState(session);}
    const remaining=pendingAfterSnapshot(session.state.pending,snapshot);
    if(remaining.length!==session.state.pending.length){session.state.pending=remaining;await saveState(session);}
    let sent=false;
    for(const batch of operationBatches(session.state.pending)){
      if(!matches(session))return;
      try{await api(path+'/notebooks/'+encodeURIComponent(metadata.id)+'/operations',{method:'POST',body:{operations:batch}});}
      catch(cause){
        if(cause.status!==403)throw cause;
        session.state.blockedLocal=await exported();session.state.pending=[];
        session.state.remote=null;session.state.remoteCursor=null;await saveState(session);lockReader();needSync=true;return;
      }
      const done=new Set(batch.map(operation=>operation.page+':'+(operation.type==='put'?operation.stroke.id:operation.id)));
      session.state.pending=session.state.pending.filter(operation=>!done.has(operation.page+':'+(operation.type==='put'?operation.stroke.id:operation.id)));
      await saveState(session);sent=true;
    }
    if(!matches(session))return;
    let local=session.state.localBase;
    if(session.dirty)try{local=await capture(session);}catch(cause){if(cause.message==='READER_BUSY'){needSync=true;return;}throw cause;}
    const progress={position:local.position,bookmarks:local.bookmarks};
    if(!session.restorePosition&&JSON.stringify(progress)!==JSON.stringify(session.state.lastSent)){
      await api(path+'/notebooks/'+encodeURIComponent(metadata.id)+'/operations',{method:'POST',body:{operations:[],...progress}});
      session.state.lastSent=progress;await saveState(session);
    }
    if(sent){const latest=await refreshRemote(session);snapshot=latest.snapshot;remote.changed ||= latest.changed;}
    if(!matches(session)||current()?.drawing||current()?.busy){needSync=true;return;}
    if(remote.changed||sent||session.restorePosition||session.reconcile){
      // Capture after network waits only when applying incoming changes. Idle
      // polling never reexports or rewrites a potentially large local notebook.
      local=await capture(session);let merged=mergeNotebook(snapshot,local,session.state.pending);
      if(session.restorePosition){const previous=remoteNotebook(snapshot).notebook;merged={...merged,position:previous.position,bookmarks:previous.bookmarks};}
      const applied=await applyNotebookIfCurrent(session.captureToken,()=>workingToken(session),
        ()=>applyWorking(merged,{silent:true,preservePosition:!session.restorePosition,preserveHistory:true}));
      if(!applied){session.dirty=true;needSync=true;return;}
      if(!matches(session))return;
      session.state.localBase=normalizeNotebook(merged);session.state.metadata=safeMetadata(snapshot.notebook);
      session.reconcile=false;
      setReaderRole(session.state.metadata,snapshot,session.state.pending);
      if(session.restorePosition)session.state.lastSent={position:merged.position,bookmarks:merged.bookmarks};session.restorePosition=false;
      await saveState(session);
    }
    try{await updatePresenterPage(session);await followPresentation(session);}
    catch(cause){
      if([403,404,410].includes(cause.status)){presentation=null;presentationPoll=false;followPresenter=false;session.state.presentation=null;session.state.followPresenter=false;presentationIndicator();await saveState(session);}
      else throw cause;
    }
    status(session.state.pending.length?'pending':'synced',session.state.pending.length?
      t('기기에 저장됨 · 클라우드 저장 대기','Saved on device · cloud save pending'):
      roleLabel(session.state.metadata.role)+' · '+(session.state.blockedLocal?
        t('전송되지 않은 필기는 동기화 화면에서 백업할 수 있습니다.','Export unsent device notes from the sync panel.'):
        t('기기·클라우드에 저장됨 · 주기적으로 동기화','Saved on device and cloud · periodically synchronized')));
  }catch(cause){
    if(matches(session)){
      if(cause.status===401){account=null;active=null;epoch++;lockReader();}
      else if(cause.status===403||cause.status===404){active=null;epoch++;lockReader();}
      if(!active){presentation=null;followPresenter=false;presentationPoll=false;presentationIndicator();}
      status('error',help(cause));
    }
  }finally{running=false;idleWaiters.splice(0).forEach(resolve=>resolve());if(active)schedule(needSync?500:4000);}
}

async function refreshRemote(session){
  let changed=false,save=false;
  if(!session.state.remote||!Number.isSafeInteger(session.state.remoteCursor)){
    const snapshot=await api(path+'/notebooks/'+encodeURIComponent(session.state.notebookId));
    if(!matches(session))throw error('READER_BUSY');
    const metadata=safeMetadata(snapshot.notebook);remoteNotebook(snapshot);
    if(metadata.fingerprint!==session.state.fingerprint||!Number.isSafeInteger(metadata.revision)||metadata.revision<0)throw error('INVALID_REMOTE_NOTEBOOK');
    if(presentationPoll||followPresenter){const result=await api(path+'/notebooks/'+encodeURIComponent(session.state.notebookId)+'/presentation');if(!matches(session))throw error('READER_BUSY');presentation=checkedPresentation(result.presentation,metadata);snapshot.presentation=presentation;session.state.presentation=presentation;if(!presentation){followPresenter=false;presentationPoll=false;session.state.followPresenter=false;}presentationIndicator();}
    session.state.remote=snapshot;session.state.remoteCursor=metadata.revision;changed=true;save=true;
  }else{
    for(let page=0;page<4;page++){
      const delta=await api(path+'/notebooks/'+encodeURIComponent(session.state.notebookId)+'/pages?since='+session.state.remoteCursor+((presentationPoll||followPresenter)?'&follow=1':''));
      if(!matches(session))throw error('READER_BUSY');
      const previous=session.state.remoteCursor;
      session.state.remote=applyRemoteChanges(session.state.remote,delta,previous);session.state.remoteCursor=delta.revision;
      if(Object.hasOwn(delta,'presentation')){
        const previousPresentation=JSON.stringify(session.state.presentation||null);
        presentation=checkedPresentation(delta.presentation,session.state.metadata);session.state.presentation=presentation;
        if(!presentation){followPresenter=false;presentationPoll=false;session.state.followPresenter=false;}
        presentationIndicator();
        save ||= previousPresentation!==JSON.stringify(presentation);
      }
      changed ||= delta.changes.length>0||delta.notebook?.role!==session.state.metadata.role;
      save ||= delta.revision!==previous||delta.notebook?.role!==session.state.metadata.role;
      if(!delta.more)break;
      if(delta.revision===previous)throw error('INVALID_REMOTE_NOTEBOOK');
      if(page===3)needSync=true;
    }
  }
  if(save)await saveState(session);return{snapshot:session.state.remote,changed};
}

async function sharing(notebook){
  if(notebook.role!=='owner')return;ensureDialog();if(!dialog.open)dialog.showModal();content.replaceChildren();feedbackText('');
  content.append(el('h3',notebook.title));
  content.append(el('p',t('초대 링크는 한 사람이 한 번 사용하며, 24시간 후 만료됩니다.','Each invitation link can be used once by one person and expires after 24 hours.'),'cloud-muted'));
  const field=el('label',t('공유 권한','Sharing permission'),'cloud-field'),permission=roleSelect();field.append(permission);content.append(field);
  const description=el('p',roleDescription(permission.value),'cloud-permission-note');content.append(description);
  permission.addEventListener('change',()=>{description.textContent=roleDescription(permission.value);content.querySelectorAll('.cloud-invite-link').forEach(node=>node.remove());});
  const tools=el('div',undefined,'cloud-actions');tools.append(action(t('초대 링크 만들기','Create invite link'),async()=>{
    const role=permission.value;
    const invitation=await api(path+'/notebooks/'+encodeURIComponent(notebook.id)+'/invites',{method:'POST',body:{role}});
    if(typeof invitation.token!=='string'||!/^[A-Za-z0-9_-]{20,512}$/.test(invitation.token))throw error('INVALID_RESPONSE');
    if(invitation.role!==role)throw error('INVALID_RESPONSE');
    const url=new URL(location.href);url.search='';url.hash='invite='+invitation.token;if(en)url.searchParams.set('lang','en');
    if(loopback(location.hostname)&&apiBase!=='https://api.infant83.io')url.searchParams.set('api',apiBase);
    content.querySelectorAll('.cloud-invite-link').forEach(node=>node.remove());
    const area=el('div',undefined,'cloud-invite-link');area.append(el('strong',roleLabel(role)));const input=el('input');input.readOnly=true;input.value=url.href;input.setAttribute('aria-label',t('비공개 초대 링크','Private invitation link'));
    const copy=action(t('링크 복사','Copy link'),async()=>{
      try{await navigator.clipboard.writeText(url.href);feedbackText(t('초대 링크를 복사했습니다.','Invitation link copied.'));}catch{input.focus();input.select();feedbackText(t('선택한 링크를 복사해 주세요.','Copy the selected link.'));}
    });area.append(input,copy);content.append(area);
    const expiry=new Date(invitation.expiresAt);if(!Number.isNaN(expiry.valueOf()))area.append(el('small',t('만료: ','Expires: ')+expiry.toLocaleString(en?'en-US':'ko-KR')));
  },'cloud-action cloud-primary'),action(t('노트 목록','Notebooks'),render,'cloud-text-button'));content.append(tools);
  const result=await api(path+'/notebooks/'+encodeURIComponent(notebook.id)+'/members');
  if(!Array.isArray(result.members)||result.members.length>1000)throw error('INVALID_RESPONSE');
  const list=el('ul',undefined,'cloud-members');
  for(const member of result.members){
    const memberId=member.accountId||member.id;
    if(!idPattern.test(memberId)||typeof member.displayName!=='string'||member.displayName.length>120)throw error('INVALID_RESPONSE');
    if(!NOTEBOOK_ROLES.includes(member.role))throw error('INVALID_RESPONSE');
    const row=el('li');row.append(el('span',member.displayName));
    if(memberId!==account.id&&member.role!=='owner'){
      const actions=el('div',undefined,'cloud-member-actions'),select=roleSelect(member.role,member.displayName+' '+t('권한','permission'));
      actions.append(select,action(t('권한 저장','Save permission'),async()=>{
        await api(path+'/notebooks/'+encodeURIComponent(notebook.id)+'/members/'+encodeURIComponent(memberId),{method:'PATCH',body:{role:select.value}});await sharing(notebook);
      }),action(t('접근 해제','Remove access'),async()=>{
      await api(path+'/notebooks/'+encodeURIComponent(notebook.id)+'/members/'+encodeURIComponent(memberId),{method:'DELETE'});await sharing(notebook);
      },'cloud-text-button'));row.append(actions);
    }else row.append(el('small',t('소유자','Owner')));list.append(row);
  }
  content.append(el('h3',t('구성원','Members')),list);
}
async function dismissInvitation(){
  inviteToken=null;invitePreview=null;
  const clean=new URL(location.href),fragment=new URLSearchParams(clean.hash.slice(1));fragment.delete('invite');clean.hash=fragment.toString();
  history.replaceState(history.state,'',clean.href);
  // An unavailable invitation must not hold the personal library or automatic
  // notebook resume hostage to the same failed request.
  try{await render();}catch(cause){feedbackText(help(cause),true);}
  try{await resume();}catch(cause){status('error',help(cause));}
}
async function acceptInvite(){
  if(!account||!inviteToken)return;
  const acceptedInvitation=inviteToken;
  const result=await api(path+'/invites/accept',{method:'POST',body: { token: acceptedInvitation }});const notebook=safeMetadata(result.notebook);
  if(inviteToken!==acceptedInvitation){await render();return;}
  inviteToken=null;invitePreview=null;const clean=new URL(location.href);clean.hash='';history.replaceState(history.state,'',clean.href);
  feedbackText(t('공유 노트에 참여했습니다.','You joined the notebook.'));await openNotebook(notebook);
}
async function resume(){
  if(!account||inviteToken)return;
  const document=current();
  const attempt=notebookOpenGeneration,owner=account.id;
  const stillRequested=()=>attempt===notebookOpenGeneration&&account?.id===owner&&current()?.fingerprint===document?.fingerprint;
  if(requestedId&&idPattern.test(requestedId)){
    const target=requestedId,result=await api(path+'/notebooks/'+encodeURIComponent(target));
    if(!stillRequested()||requestedId!==target)return;
    await openNotebook(safeMetadata(result.notebook));return;
  }
  if(selection){await openNotebook(selection);return;}
  if(!document?.fingerprint)return;
  const link=await readStore('links',linkKey(account.id,document.fingerprint));
  if(!stillRequested())return;
  if(link&&idPattern.test(link.notebookId)){
    const state=await readStore('states',stateKey(account.id,link.notebookId));
    if(!stillRequested())return;
    if(state?.metadata)await activate(safeMetadata(state.metadata),{allowUpload:false,restorePosition:false});
  }
}
async function documentOpened(){
  workingGeneration++;epoch++;active=null;clearTimeout(timer);status('idle','');
  presentation=null;followPresenter=false;presentationPoll=false;presentationIndicator();
  lockReader();
  try{await restoreDisplayedPermissions();if(initialized)await resume();}catch(cause){status('error',help(cause));}
}
async function inviteFragmentChanged(){
  const candidate=readInviteFragment();
  if(!candidate){
    const previous=inviteToken;inviteToken=null;invitePreview=null;
    if(previous&&initialized){
      if(dialog?.open)try{await render();}catch(cause){feedbackText(help(cause),true);}
      try{await resume();}catch(cause){status('error',help(cause));}
    }
    return;
  }
  inviteToken=candidate;
  invitePreview=null;
  // A browser can reuse this document when only #invite changes. Module
  // initialization does not run again, so consent must follow fragment changes.
  if(initialized)try{await show();}catch(cause){feedbackText(help(cause),true);}
}
window.addEventListener('hashchange',()=>void inviteFragmentChanged());
window.addEventListener('atr:cloud-request',event=>{
  event.preventDefault();void show().catch(cause=>feedbackText(help(cause),true));
});
window.addEventListener('atr:workspace-request',event=>{
  event.preventDefault();void show().catch(cause=>feedbackText(help(cause),true));
});
window.addEventListener('atr:presentation-action',()=>void runUI(async()=>{
  if(!matches(active))return;
  if(followPresenter){followPresenter=false;active.state.followPresenter=false;presentationIndicator();await saveState(active);}
  else await presentationPanel(active.state.metadata);
}));
window.addEventListener('atr:document-open',()=>void documentOpened());
window.addEventListener('atr:notes-saved',event=>{
  workingGeneration++;
  if(active&&event.detail?.fingerprint===active.state.fingerprint){active.localGeneration++;active.dirty=true;needSync=true;status('pending',t('기기에 저장됨 · 클라우드 저장 대기','Saved on device · cloud save pending'));schedule(250);}
});
document.addEventListener('visibilitychange',()=>{
  if(document.visibilityState==='visible'){if(active)schedule(50);}
  else{clearTimeout(timer);if(active&&!running&&!current()?.drawing&&!current()?.busy)void capture(active).catch(()=>{});}
});
window.addEventListener('online',()=>{if(active)schedule(50);});
window.addEventListener('pagehide',()=>{clearTimeout(timer);if(active&&!running&&!current()?.drawing&&!current()?.busy)void capture(active).catch(()=>{});});
async function initializeCloud(){
  lockReader();try{await restoreDisplayedPermissions();}catch(cause){status('error',help(cause));}
  const initialAuth=authGeneration;
  try{const me=await api(path+'/me');if(initialAuth===authGeneration){account=safeAccount(me.account);features={...features,...me.features};storageUsage=me.usage||null;status('idle','');}}
  catch{if(initialAuth===authGeneration)status('idle',t('기기에서 계속 읽을 수 있습니다. 동기화에서 로그인해 주세요.','Continue reading on this device. Open Sync to sign in.'));}
  initialized=true;
  try{await restoreDisplayedPermissions();}catch(cause){status('error',help(cause));}
  // Invitation consent must not wait behind an unrelated notebook resume, or
  // disappear if that resume is temporarily busy while the PDF is rendering.
  if(inviteToken){try{await show();}catch(cause){feedbackText(help(cause),true);}return;}
  try{await resume();}catch(cause){status('error',help(cause));}
  if(requestedId||new URL(location.href).searchParams.get('library')==='1')try{await show();}catch(cause){feedbackText(help(cause),true);}
}
await initializeCloud();
