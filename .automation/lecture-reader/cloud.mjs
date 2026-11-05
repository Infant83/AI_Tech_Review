/** Explicit passkey sign-in and private notebook synchronization. PDF bytes stay on the device. */
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
  return {...value,publicId:value.publicId || null};
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
}
function lockReader(){const view=current();if(view)window.ATRNotebook?.setPermissions?.({fingerprint:view.fingerprint,role:'viewer'});}
async function restoreDisplayedPermissions(){
  const view=current(),attempt=activationGeneration,generation=workingGeneration;if(!view)return;
  const sameView=()=>current()?.fingerprint===view.fingerprint&&attempt===activationGeneration&&generation===workingGeneration;
  const marker=await readStore('links',workingKey(view.fingerprint));
  if(!sameView())return;
  if(matches(active)){setReaderRole(active.state.metadata,active.state.remote,active.state.pending);return;}
  if(!marker){window.ATRNotebook?.setPermissions?.({fingerprint:view.fingerprint,role:'local'});return;}
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
async function stopSession(){active=null;epoch++;clearTimeout(timer);if(running)await new Promise(resolve=>idleWaiters.push(resolve));}
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
    const text=button.querySelector('span'); if(text) text.textContent=label;
    button.title=message || t('로그인·동기화','Sign in & sync');button.setAttribute('aria-label',button.title);
  }
  if (message && lastStatus !== message) {live.textContent=message;lastStatus=message;}
  const node=dialog?.querySelector('[data-cloud-status]');if(node) node.textContent=message || '';
}
function help(cause) {
  if (cause?.name === 'NotAllowedError' || cause?.name === 'AbortError') return t('패스키 확인을 취소했습니다. 다시 시도할 수 있습니다.','Passkey confirmation was cancelled. You can try again.');
  if (cause.status === 401) return t('다시 로그인해 주세요. 기기 필기는 보관되어 있습니다.','Sign in again. Your device notes are retained.');
  if (cause.status === 410) return t('초대 링크가 만료되었거나 이미 사용되었습니다. 소유자에게 새 초대 링크를 요청해 주세요.','This invitation has expired or was already used. Ask the owner for a new invitation link.');
  if (cause.status === 403 || cause.status === 404) return t('이 노트에 접근할 수 없습니다. 기기 필기는 보관되어 있습니다.','This notebook is unavailable to your account. Device notes are retained.');
  if (cause.message === 'PASSKEY_UNAVAILABLE') return t('이 브라우저에서 패스키를 사용할 수 없습니다. Safari나 최신 브라우저에서 열어 주세요.','Passkeys are unavailable in this browser. Open Safari or another current browser.');
  if (cause.message === 'SYNC_STORAGE_UNAVAILABLE') return t('동기화 대기열을 저장할 수 없습니다. 기기 저장 상태를 확인해 주세요.','The sync queue could not be saved. Check this browser’s storage.');
  if (cause.message === 'FINGERPRINT_MISMATCH') return t('이 노트와 같은 PDF를 열어 주세요. 파일은 서버로 전송하지 않습니다.','Open the identical PDF for this notebook. The file is not uploaded.');
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
  const header=el('header',undefined,'cloud-header');const title=el('h2',t('내 학습 노트','My study notes'));title.id='study-cloud-title';
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
  ensureDialog();opener=document.activeElement;content.replaceChildren();feedbackText('');
  if(!dialog.open)dialog.showModal();
  await render();
}
async function render() {
  if(!dialog?.open)return;
  const generation=++renderGeneration, renderedAccount=account?.id;
  content.replaceChildren();feedbackText('');
  if(!account){
    content.append(el('p',t('패스키로 로그인하면 다른 기기에서도 필기를 이어서 읽을 수 있습니다.','Sign in with a passkey to continue your notes on another device.'),'cloud-intro'));
    const label=el('label',t('이름','Display name'),'cloud-field');const input=el('input');input.type='text';input.maxLength=100;input.autocomplete='nickname';input.placeholder=t('노트에 표시할 이름','Name for your notebooks');label.append(input);content.append(label);
    const actions=el('div',undefined,'cloud-actions');actions.append(
      action(t('패스키 만들기','Create passkey'),()=>authenticate('register',input.value.trim()),'cloud-action cloud-primary'),
      action(t('패스키로 로그인','Sign in with passkey'),()=>authenticate('login')));content.append(actions);
    content.append(el('p',t('Face ID·Touch ID 또는 기기에 저장한 패스키로 확인합니다. 노트는 선택한 뒤 동기화를 시작합니다.','Confirm with Face ID, Touch ID or a saved passkey. Notes sync only after you choose a notebook.'),'cloud-muted'));
    if(inviteToken)content.append(el('p',t('초대받은 노트에 참여하려면 먼저 로그인해 주세요.','Sign in to accept the notebook invitation.'),'cloud-invite-note'));
    return;
  }
  const accountRow=el('div',undefined,'cloud-account');accountRow.append(el('strong',account.displayName),action(t('로그아웃','Sign out'),logout,'cloud-text-button'));content.append(accountRow);
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
    const section=el('section',undefined,'cloud-section');section.append(el('h3',document.title));
    const summary=el('p',matches(active)?lastStatus:t('기기 필기를 클라우드 노트와 연결합니다. PDF 파일은 전송하지 않습니다.','Connect the device notes to your cloud notebook. The PDF file is not uploaded.'),'cloud-muted');summary.dataset.cloudStatus='';section.append(summary);
    if(matches(active)){
      const permissionNode=el('p',roleLabel(active.state.metadata.role)+' · '+roleDescription(active.state.metadata.role),'cloud-permission-note');permissionNode.dataset.cloudPermission='';section.append(permissionNode);
      const actions=el('div',undefined,'cloud-actions');actions.append(action(t('지금 동기화','Sync now'),()=>syncNow()));
      if(active.state.metadata.role==='owner')actions.append(action(t('공유·구성원','Share & members'),()=>sharing(active.state.metadata)));
      actions.append(action(t('이 기기 연결 해제','Disconnect this device'),disconnect,'cloud-text-button'));section.append(actions);
      if(active.state.blockedLocal)section.append(action(t('전송되지 않은 기기 필기 백업','Export unsent device notes'),()=>downloadBlocked(active.state),'cloud-text-button'));
    }else section.append(action(t('이 노트 동기화','Sync this notebook'),enableCurrent,'cloud-action cloud-primary'));
    content.append(section);
  }
  const library=el('section',undefined,'cloud-section');library.append(el('h3',t('클라우드 노트','Cloud notebooks')));content.append(library);
  const loading=el('p',t('불러오는 중…','Loading…'),'cloud-muted');library.append(loading);
  const result=await api(path+'/notebooks');if(!dialog.open||!account||account.id!==renderedAccount||generation!==renderGeneration)return;
  if(!Array.isArray(result.notebooks)||result.notebooks.length>1000)throw error('INVALID_RESPONSE');
  const notebooks=result.notebooks.map(safeMetadata);loading.remove();
  if(!notebooks.length)library.append(el('p',t('PDF를 연 뒤 ‘이 노트 동기화’를 누르세요.','Open a PDF, then choose “Sync this notebook”.'),'cloud-muted'));
  const list=el('ul',undefined,'cloud-notebooks');
  for(const notebook of notebooks){
    const row=el('li');const text=el('div');text.append(el('strong',notebook.title),el('small',notebook.pageCount+t('쪽 · ',' pages · ')+roleLabel(notebook.role)));
    const actions=el('div',undefined,'cloud-row-actions');actions.append(action(t('열기','Open'),()=>openNotebook(notebook)));
    if(notebook.role==='owner')actions.append(action(t('공유','Share'),()=>sharing(notebook),'cloud-text-button'));
    row.append(text,actions);list.append(row);
  }
  library.append(list);
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
  const local=await exported(), result=await api(path+'/notebooks');
  if(!Array.isArray(result.notebooks))throw error('INVALID_RESPONSE');
  let notebook=result.notebooks.map(safeMetadata).find(item=>item.fingerprint===document.fingerprint&&item.role==='owner');
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
  if(dialog.open)dialog.close();
  window.dispatchEvent(new CustomEvent('atr:cloud-open-local',{detail:{fingerprint:notebook.fingerprint,title:notebook.title}}));
  status('pending',t('보관함에서 같은 원본 PDF 파일을 선택해 주세요. 파일은 업로드하지 않습니다.','Choose the identical original PDF from the library. The file is not uploaded.'));
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
  setReaderRole(state.metadata,state.remote,state.pending);
  await writeStore('links',{key:linkKey(owner,notebook.fingerprint),notebookId:notebook.id});
  selection=null;requestedId=null;status('syncing',t('클라우드 노트를 연결하는 중…','Connecting the cloud notebook…'));
  await syncNow();
}
async function restoreBinding(previousSession){
  if(previousSession&&account?.id===previousSession.accountId&&current()?.fingerprint===previousSession.state.fingerprint){
    const saved=await readStore('states',previousSession.state.key);if(saved)previousSession.state=saved;
    previousSession.epoch=++epoch;previousSession.dirty=true;active=previousSession;schedule(500);
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
    status(session.state.pending.length?'pending':'synced',session.state.pending.length?
      t('기기에 저장됨 · 클라우드 저장 대기','Saved on device · cloud save pending'):
      roleLabel(session.state.metadata.role)+' · '+(session.state.blockedLocal?
        t('전송되지 않은 필기는 동기화 화면에서 백업할 수 있습니다.','Export unsent device notes from the sync panel.'):
        t('기기·클라우드에 저장됨 · 주기적으로 동기화','Saved on device and cloud · periodically synchronized')));
  }catch(cause){
    if(matches(session)){
      if(cause.status===401){account=null;active=null;epoch++;lockReader();}
      else if(cause.status===403||cause.status===404){active=null;epoch++;lockReader();}
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
    session.state.remote=snapshot;session.state.remoteCursor=metadata.revision;changed=true;save=true;
  }else{
    for(let page=0;page<4;page++){
      const delta=await api(path+'/notebooks/'+encodeURIComponent(session.state.notebookId)+'/pages?since='+session.state.remoteCursor);
      if(!matches(session))throw error('READER_BUSY');
      const previous=session.state.remoteCursor;
      session.state.remote=applyRemoteChanges(session.state.remote,delta,previous);session.state.remoteCursor=delta.revision;
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
  const document=current();if(!document?.fingerprint)return;
  const attempt=notebookOpenGeneration,owner=account.id;
  const stillRequested=()=>attempt===notebookOpenGeneration&&account?.id===owner&&current()?.fingerprint===document.fingerprint;
  if(requestedId&&idPattern.test(requestedId)){
    const target=requestedId,result=await api(path+'/notebooks/'+encodeURIComponent(target));
    if(!stillRequested()||requestedId!==target)return;
    await openNotebook(safeMetadata(result.notebook));return;
  }
  if(selection){await openNotebook(selection);return;}
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
  try{const me=await api(path+'/me');if(initialAuth===authGeneration)account=safeAccount(me.account);}
  catch{if(initialAuth===authGeneration)status('idle',t('기기에서 계속 읽을 수 있습니다. 동기화에서 로그인해 주세요.','Continue reading on this device. Open Sync to sign in.'));}
  initialized=true;
  try{await restoreDisplayedPermissions();}catch(cause){status('error',help(cause));}
  // Invitation consent must not wait behind an unrelated notebook resume, or
  // disappear if that resume is temporarily busy while the PDF is rendering.
  if(inviteToken){try{await show();}catch(cause){feedbackText(help(cause),true);}return;}
  try{await resume();}catch(cause){status('error',help(cause));}
  if(requestedId)try{await show();}catch(cause){feedbackText(help(cause),true);}
}
await initializeCloud();
