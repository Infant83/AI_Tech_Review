import {
  generateRegistrationOptions, verifyRegistrationResponse,
  generateAuthenticationOptions, verifyAuthenticationResponse,
} from '@simplewebauthn/server';
import {ApiError,SITE_ORIGIN,assertOrigin,base64url,object,randomToken,readJson,sha256,responseHeaders} from './security.js';
import {libraryRoute,pruneLibrary,studyFeatures,studyUsage,notebookPresentation,DOCUMENT_LIMIT,ACCOUNT_DOCUMENT_LIMIT} from './study-library.js';

const DAY=86_400_000;
const HOUR=3_600_000;
const MAX_STROKES=25000;
const MAX_NOTE_BYTES=12_000_000;
const stmt=(env,sql,...values)=>env.DB.prepare(sql).bind(...values);
const first=(env,sql,...values)=>stmt(env,sql,...values).first();
const all=async(env,sql,...values)=>(await stmt(env,sql,...values).all()).results;
const run=(env,sql,...values)=>stmt(env,sql,...values).run();
const changed=r=>Number(r.meta?.changes||0)>0;

function json(request,env,value,status=200,cookie=null) {
  const headers=responseHeaders(request,env);
  if(cookie) headers.set('Set-Cookie',cookie);
  return new Response(JSON.stringify({ok:true,...value}),{status,headers});
}

function cookieName(request,env,kind='session') {
  const host=new URL(request.url).hostname;
  const insecure=env.DEV_ALLOW_INSECURE_COOKIE==='true' && ['localhost','127.0.0.1','[::1]'].includes(host);
  return {name:`${insecure?'':'__Host-'}study_${kind}`,secure:!insecure};
}
function cookie(request,env,token,kind='session',seconds=30*86400) {
  const {name,secure}=cookieName(request,env,kind);
  return `${name}=${token}; Path=/; Max-Age=${seconds}; HttpOnly; SameSite=Strict${secure?'; Secure':''}`;
}
function token(request,env,kind='session') {
  const {name}=cookieName(request,env,kind);
  const values=(request.headers.get('Cookie')||'').split(';').map(s=>s.trim()).filter(s=>s.startsWith(`${name}=`));
  if(values.length!==1) return null;
  const value=values[0].slice(name.length+1);
  return /^[A-Za-z0-9_-]{43}$/.test(value)?value:null;
}
async function account(request,env,required=true) {
  const value=token(request,env);
  const row=value?await first(env,`SELECT a.id,a.display_name FROM study_sessions s JOIN study_accounts a ON a.id=s.account_id WHERE s.token_hash=? AND s.expires_at>?`,await sha256(value),Date.now()):null;
  if(required&&!row) throw new ApiError('study_login_required',401);
  return row?{id:row.id,displayName:row.display_name}:null;
}
async function limit(request,env,scope,maximum,window=HOUR,identity=null) {
  if(!env.RATE_LIMIT_SALT || env.RATE_LIMIT_SALT.length<32) throw new ApiError('server_not_configured',503);
  const now=Date.now();
  const hash=await sha256(`${env.RATE_LIMIT_SALT}:${Math.floor(now/DAY)}:${identity||request.headers.get('CF-Connecting-IP')||'unknown'}`);
  const key=`study:${scope}:${hash}:${Math.floor(now/window)}`;
  const r=await run(env,`INSERT INTO rate_limits(key,hits,expires_at) VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET hits=hits+1 WHERE hits<?`,key,(Math.floor(now/window)+1)*window,maximum);
  if(!changed(r)) throw new ApiError('rate_limited',429);
}
function rp(request,env) {
  const origin=assertOrigin(request,env,true);
  const url=new URL(origin);
  return {origin,rpID:origin===SITE_ORIGIN?'infant83.io':url.hostname};
}
function displayName(value) {
  if(typeof value!=='string'||!value.trim()||value.trim().length>80||/[\u0000-\u001f\u007f]/.test(value)) throw new ApiError('invalid_display_name');
  return value.trim();
}
function decode(value) {
  if(typeof value!=='string'||!/^[A-Za-z0-9_-]+$/.test(value)||value.length>2048) throw new ApiError('invalid_credential');
  return Uint8Array.from(atob(value.replace(/-/g,'+').replace(/_/g,'/')),c=>c.charCodeAt(0));
}
async function authOptions(request,env,kind) {
  await limit(request,env,`auth-${kind}`,kind==='register'?12:40);
  const body=object(await readJson(request,1024),kind==='register'?['displayName']:kind==='add'?['label']:[],kind==='add'?[]:undefined);
  const {origin,rpID}=rp(request,env);
  const current=await account(request,env,kind==='add'||kind==='reauth');
  if(kind==='register'&&current)throw new ApiError('already_signed_in_use_add_passkey',409);
  const credentials=current?await all(env,'SELECT id,transports,user_handle FROM study_credentials WHERE account_id=?',current.id):[];
  if(kind==='add'){
    if(credentials.length>=10)throw new ApiError('credential_limit',413);
    await recentVerification(request,env,current);
  }
  const registering=kind==='register'||kind==='add';
  const next=kind==='register'?{id:crypto.randomUUID(),displayName:displayName(body.displayName),userID:crypto.getRandomValues(new Uint8Array(32))}:
    kind==='add'?{id:current.id,displayName:current.displayName,userID:decode(credentials[0].user_handle)}:null;
  const label=kind==='add'?displayName(body.label||'Passkey'):next?.displayName||null;
  const options=registering?await generateRegistrationOptions({
    rpName:'AI Tech Review',rpID,userID:next.userID,userName:next.id,userDisplayName:next.displayName,
    attestationType:'none',timeout:120_000,supportedAlgorithmIDs:[-7,-257],
    authenticatorSelection:{residentKey:'required',userVerification:'required'},
    ...(kind==='add'?{excludeCredentials:credentials.map(value=>({id:value.id,transports:JSON.parse(value.transports)}))}:{}),
  }):await generateAuthenticationOptions({rpID,userVerification:'required',timeout:120_000,
    ...(kind==='reauth'?{allowCredentials:credentials.map(value=>({id:value.id,transports:JSON.parse(value.transports)}))}:{})});
  const bind=randomToken();
  const previous=token(request,env,'challenge');
  if(previous) await run(env,'DELETE FROM study_challenges WHERE token_hash=?',await sha256(previous));
  await run(env,`INSERT INTO study_challenges(token_hash,kind,challenge,origin,rp_id,account_id,display_name,user_handle,expires_at) VALUES(?,?,?,?,?,?,?,?,?)`,
    await sha256(bind),kind,options.challenge,origin,rpID,next?.id||current?.id||null,label,next?base64url(next.userID):null,Date.now()+5*60_000);
  return json(request,env,{options},200,cookie(request,env,bind,'challenge',300));
}
async function authVerify(request,env,kind) {
  await limit(request,env,'auth-verify',60);
  const body=object(await readJson(request,64_000),['response']);
  const bind=token(request,env,'challenge');
  if(!bind) throw new ApiError('challenge_expired',401);
  const expected=await first(env,'DELETE FROM study_challenges WHERE token_hash=? AND kind=? AND expires_at>? RETURNING *',await sha256(bind),kind,Date.now());
  if(!expected || expected.origin!==assertOrigin(request,env,true)) throw new ApiError('challenge_expired',401);
  const existing=kind==='add'||kind==='reauth'?await account(request,env):null;
  if(existing&&expected.account_id!==existing.id)throw new ApiError('passkey_verification_failed',401);
  // This application has no embedded login flow. Reject cross-origin frames
  // even on browsers that omit WebAuthn's newer topOrigin field.
  try {
    const client=JSON.parse(new TextDecoder().decode(decode(body.response?.response?.clientDataJSON)));
    if(client.crossOrigin===true||client.topOrigin) throw new Error('embedded_authentication');
  } catch {throw new ApiError('passkey_verification_failed',401);}
  let owner;
  if(kind==='register'||kind==='add') {
    let result;
    try {result=await verifyRegistrationResponse({response:body.response,expectedChallenge:expected.challenge,expectedOrigin:expected.origin,expectedRPID:expected.rp_id,requireUserVerification:true,supportedAlgorithmIDs:[-7,-257]});}
    catch {throw new ApiError('passkey_verification_failed',401);}
    if(!result.verified||!result.registrationInfo) throw new ApiError('passkey_verification_failed',401);
    const credential=result.registrationInfo.credential;
    const transports=Array.isArray(credential.transports)?credential.transports.filter(v=>typeof v==='string').slice(0,8):[];
    owner=existing||{id:expected.account_id,displayName:expected.display_name};
    const now=Date.now(),commands=[];
    if(kind==='register')commands.push(stmt(env,'INSERT INTO study_accounts(id,display_name,created_at) VALUES(?,?,?)',owner.id,owner.displayName,now));
    commands.push(stmt(env,'INSERT INTO study_credentials(id,account_id,public_key,counter,user_handle,transports,created_at,label,last_used_at) VALUES(?,?,?,?,?,?,?,?,?)',credential.id,owner.id,base64url(credential.publicKey),credential.counter,expected.user_handle,JSON.stringify(transports),now,kind==='add'?expected.display_name:'Passkey',now));
    try {await env.DB.batch(commands);}catch {throw new ApiError('credential_already_registered',409);}
    if(kind==='add')return json(request,env,{account:owner,credential:{id:credential.id,label:expected.display_name,createdAt:now,lastUsedAt:now}});
  } else {
    const id=body.response?.id;
    if(typeof id!=='string'||id.length>2048) throw new ApiError('passkey_verification_failed',401);
    const credential=await first(env,'SELECT c.*,a.display_name FROM study_credentials c JOIN study_accounts a ON a.id=c.account_id WHERE c.id=?',id);
    if(!credential) throw new ApiError('passkey_verification_failed',401);
    if(existing&&credential.account_id!==existing.id)throw new ApiError('passkey_verification_failed',401);
    if(body.response?.response?.userHandle && body.response.response.userHandle!==credential.user_handle) throw new ApiError('passkey_verification_failed',401);
    let result;
    try {result=await verifyAuthenticationResponse({response:body.response,expectedChallenge:expected.challenge,expectedOrigin:expected.origin,expectedRPID:expected.rp_id,requireUserVerification:true,
      credential:{id:credential.id,publicKey:decode(credential.public_key),counter:credential.counter,transports:JSON.parse(credential.transports)}});}
    catch {throw new ApiError('passkey_verification_failed',401);}
    if(!result.verified) throw new ApiError('passkey_verification_failed',401);
    await run(env,'UPDATE study_credentials SET counter=?,last_used_at=? WHERE id=? AND counter<=?',result.authenticationInfo.newCounter,Date.now(),id,result.authenticationInfo.newCounter);
    owner={id:credential.account_id,displayName:credential.display_name};
    if(kind==='reauth'){
      const verifiedAt=Date.now();await run(env,'UPDATE study_sessions SET verified_at=? WHERE token_hash=? AND account_id=?',verifiedAt,await sha256(token(request,env)),existing.id);
      return json(request,env,{verifiedUntil:verifiedAt+5*60_000,account:owner});
    }
  }
  const session=randomToken();
  const old=token(request,env);
  const commands=[];
  if(old) commands.push(stmt(env,'DELETE FROM study_sessions WHERE token_hash=?',await sha256(old)));
  commands.push(stmt(env,'INSERT INTO study_sessions(token_hash,account_id,expires_at) VALUES(?,?,?)',await sha256(session),owner.id,Date.now()+30*DAY));
  await env.DB.batch(commands);
  return json(request,env,{account:owner},200,cookie(request,env,session));
}
async function recentVerification(request,env,current){
  const row=await first(env,'UPDATE study_sessions SET verified_at=0 WHERE token_hash=? AND account_id=? AND verified_at>? RETURNING account_id',await sha256(token(request,env)),current.id,Date.now()-5*60_000);
  if(!row)throw new ApiError('passkey_reauthentication_required',403);
}
async function credentialsRoute(request,env,current,route){
  if(route==='credentials'&&request.method==='GET'){
    const rows=await all(env,'SELECT id,label,created_at,last_used_at FROM study_credentials WHERE account_id=? ORDER BY created_at',current.id);
    return json(request,env,{credentials:rows.map(row=>({id:row.id,label:row.label,createdAt:row.created_at,lastUsedAt:row.last_used_at}))});
  }
  const match=route.match(/^credentials\/([A-Za-z0-9_-]+)$/);
  if(match&&request.method==='DELETE'){
    object(await readJson(request,256),[]);await recentVerification(request,env,current);
    const row=await first(env,'SELECT id FROM study_credentials WHERE id=? AND account_id=?',match[1],current.id);
    if(!row)throw new ApiError('credential_not_found',404);
    try{await run(env,'DELETE FROM study_credentials WHERE id=? AND account_id=?',row.id,current.id);}catch(error){
      if(String(error?.message||error).includes('last_credential_required'))throw new ApiError('last_credential_required',409);throw error;
    }
    return json(request,env,{});
  }
  return null;
}
function id(value) {
  if(typeof value!=='string'||!/^[A-Za-z0-9_-]{8,100}$/.test(value)) throw new ApiError('invalid_study_id');
  return value;
}
function notebookView(row) {
  return {id:row.id,title:row.title,fingerprint:row.fingerprint,pageCount:row.page_count,publicId:row.public_id,
    ownerId:row.owner_id,ownerName:row.owner_name||'',role:row.role,revision:row.revision,updatedAt:row.updated_at,
    deletedAt:row.deleted_at||null,sourceNotebookId:row.source_notebook_id||null,createdFrom:row.created_from||'original',
    documentAvailable:Boolean(row.document_id),documentBytes:row.document_bytes||0,
    capabilities:{canRead:true,canAdd:['owner','editor','contributor'].includes(row.role),
      canDeleteOwn:['owner','editor','contributor'].includes(row.role),canEditAll:['owner','editor'].includes(row.role),canManageMembers:row.role==='owner'}};
}
function shareRole(value,fallback=null) {
  const role=value===undefined?fallback:value;
  if(!['viewer','contributor','editor'].includes(role)) throw new ApiError('invalid_notebook_role');
  return role;
}
async function member(env,notebookId,accountId,ownerOnly=false,includeDeleted=false) {
  id(notebookId);
  const row=await first(env,`SELECT n.*,m.role,m.position,m.bookmarks,a.display_name owner_name FROM study_notebooks n JOIN study_members m ON m.notebook_id=n.id JOIN study_accounts a ON a.id=n.owner_id WHERE n.id=? AND m.account_id=?`,notebookId,accountId);
  if(!row||(!includeDeleted&&row.deleted_at)) throw new ApiError('notebook_not_found',404);
  if(ownerOnly&&row.role!=='owner') throw new ApiError('notebook_owner_required',403);
  return row;
}
async function createNotebook(request,env,current) {
  await limit(request,env,'create-note',60,HOUR,current.id);
  const body=object(await readJson(request,2048),['publicId','title','fingerprint','pageCount']);
  const title=displayNameForNotebook(body.title);
  if(!/^[a-f0-9]{64}$/.test(body.fingerprint)||!Number.isInteger(body.pageCount)||body.pageCount<1||body.pageCount>10000) throw new ApiError('invalid_document');
  let publicId=body.publicId;
  if(publicId!==null) {
    if(typeof publicId!=='string'||!/^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$/.test(publicId.replace(/^lecture:/,''))) throw new ApiError('invalid_public_document');
    publicId=publicId.replace(/^lecture:/,'');
    const article=await first(env,"SELECT id FROM articles WHERE id=? AND topic='lecture' AND active=1",`lecture:${publicId}`);
    if(!article) throw new ApiError('public_document_not_found',404);
  }
  const previous=await first(env,`SELECT n.*,m.role,a.display_name owner_name FROM study_notebooks n JOIN study_members m ON m.notebook_id=n.id AND m.account_id=? JOIN study_accounts a ON a.id=n.owner_id WHERE n.owner_id=? AND n.fingerprint=? AND n.deleted_at IS NULL ORDER BY n.updated_at DESC LIMIT 1`,current.id,current.id,body.fingerprint);
  if(previous) return json(request,env,{notebook:notebookView(previous)});
  if((await first(env,'SELECT count(*) n FROM study_notebooks WHERE owner_id=? AND deleted_at IS NULL',current.id)).n>=100) throw new ApiError('notebook_limit',413);
  const notebookId=crypto.randomUUID(),now=Date.now();
  await env.DB.batch([
    stmt(env,'INSERT INTO study_notebooks(id,owner_id,public_id,title,fingerprint,page_count,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)',notebookId,current.id,publicId,title,body.fingerprint,body.pageCount,now,now),
    stmt(env,"INSERT INTO study_members(notebook_id,account_id,role,joined_at) VALUES(?,?,'owner',?)",notebookId,current.id,now),
  ]);
  return json(request,env,{notebook:notebookView(await member(env,notebookId,current.id))},201);
}
function displayNameForNotebook(value) {
  if(typeof value!=='string'||!value.trim()||value.trim().length>240||/[\u0000-\u001f\u007f]/.test(value)) throw new ApiError('invalid_notebook_title');
  return value.trim();
}
function pageNumber(value,row) {
  if(!Number.isInteger(value)||value<1||value>row.page_count) throw new ApiError('invalid_page');
  return value;
}
function strokeId(value) {
  if(typeof value!=='string'||!/^[A-Za-z0-9_.:-]{1,100}$/.test(value)) throw new ApiError('invalid_stroke_id');
  return value;
}
export function validateStroke(value) {
  object(value,['id','color','width','points']);
  strokeId(value.id);
  if(typeof value.color!=='string'||!/^#[0-9a-fA-F]{6}$/.test(value.color)||!Number.isFinite(value.width)||value.width<=0||value.width>0.1) throw new ApiError('invalid_stroke');
  if(!Array.isArray(value.points)||!value.points.length||value.points.length>5000) throw new ApiError('invalid_stroke_points');
  const points=value.points.map(point=>{
    object(point,['x','y','p']);
    if(![point.x,point.y,point.p].every(v=>Number.isFinite(v)&&v>=0&&v<=1)) throw new ApiError('invalid_stroke_points');
    return {x:point.x,y:point.y,p:point.p};
  });
  return {id:value.id,color:value.color.toLowerCase(),width:value.width,points};
}
async function operations(request,env,current,notebookId) {
  const row=await member(env,notebookId,current.id);
  await limit(request,env,'note-write',1200,HOUR,current.id);
  const body=object(await readJson(request,1_000_000),['operations','position','bookmarks'],['operations']);
  if(!Array.isArray(body.operations)||body.operations.length>100) throw new ApiError('invalid_operations');
  if(body.operations.length&&row.role==='viewer') throw new ApiError('notebook_read_only',403);
  const commands=[],now=Date.now();
  let extraBytes=0,extraRows=0;
  const normalized=body.operations.map(operation=>{
    object(operation,operation?.type==='put'?['type','page','stroke']:['type','page','id']);
    const page=pageNumber(operation.page,row);
    if(operation.type==='put') return {type:'put',page,stroke:validateStroke(operation.stroke)};
    if(operation.type==='delete') return {type:'delete',page,id:strokeId(operation.id)};
    throw new ApiError('invalid_operation');
  });
  const requested=new Map();
  for(const operation of normalized) {
    const stroke=operation.type==='put'?operation.stroke.id:operation.id;
    requested.set(`${operation.page}:${stroke}`,{page:operation.page,id:stroke});
  }
  const known=new Map([...requested.keys()].map(key=>[key,null]));
  if(requested.size) {
    // One binding read for the whole request, with one bound JSON value instead
    // of up to 200 tuple parameters. CROSS JOIN keeps json_each's <=100 keys
    // outside indexed (notebook_id,page,id) lookups, never a notebook scan.
    const stored=await all(env,`SELECT s.page,s.id,s.deleted,s.data,s.author_id
      FROM json_each(?) AS requested CROSS JOIN study_strokes AS s
      WHERE s.notebook_id=? AND s.page=json_extract(requested.value,'$.page') AND s.id=json_extract(requested.value,'$.id')`,
      JSON.stringify([...requested.values()]),notebookId);
    for(const value of stored) known.set(`${value.page}:${value.id}`,value);
  }
  for(const operation of normalized) {
    const page=operation.page;
    if(operation.type==='put') {
      const value=operation.stroke,data=JSON.stringify(value);
      const key=`${page}:${value.id}`;
      if(row.role==='contributor'&&known.get(key)&&known.get(key).author_id!==current.id) throw new ApiError('notebook_add_only',403);
      if(!known.get(key)) {extraBytes+=data.length;extraRows++;known.set(key,{deleted:0,data,author_id:current.id});}
      // Immutable ids and permanent tombstones make retries and stale offline writes safe.
      commands.push(stmt(env,`INSERT OR IGNORE INTO study_strokes(notebook_id,page,id,data,deleted,updated_at,author_id,actor_id)
        VALUES(?,?,?,?,0,?,?,?)`,notebookId,page,value.id,data,now,current.id,current.id));
    } else if(operation.type==='delete') {
      const key=`${page}:${operation.id}`;
      if(row.role==='contributor'&&known.get(key)?.author_id!==current.id) throw new ApiError('notebook_add_only',403);
      if(!known.get(key)) extraRows++;
      else if(known.get(key).data) extraBytes-=known.get(key).data.length;
      known.set(key,{deleted:1,data:null,author_id:known.get(key)?.author_id||null});
      commands.push(stmt(env,`INSERT INTO study_strokes(notebook_id,page,id,data,deleted,updated_at,author_id,actor_id)
        VALUES(?,?,?,NULL,1,?,NULL,?)
        ON CONFLICT(notebook_id,page,id) DO UPDATE SET data=NULL,deleted=1,updated_at=excluded.updated_at,actor_id=excluded.actor_id WHERE study_strokes.deleted=0`,notebookId,page,operation.id,now,current.id));
    }
  }
  const capacity=await first(env,'SELECT stroke_count n,ink_bytes bytes FROM study_notebooks WHERE id=?',notebookId);
  // Existing erasures/replays and reading-position saves must remain possible
  // even if simultaneous prior batches put a notebook slightly over its limit.
  if((extraRows>0&&capacity.n+extraRows>MAX_STROKES)||(extraBytes>0&&capacity.bytes+extraBytes>MAX_NOTE_BYTES)) throw new ApiError('notebook_storage_limit',413);
  let position=row.position,bookmarks=row.bookmarks;
  if(body.position!==undefined) {object(body.position,['page']);position=pageNumber(body.position.page,row);}
  if(body.bookmarks!==undefined) {
    if(!Array.isArray(body.bookmarks)||body.bookmarks.length>row.page_count) throw new ApiError('invalid_bookmarks');
    bookmarks=JSON.stringify([...new Set(body.bookmarks.map(p=>pageNumber(p,row)))].sort((a,b)=>a-b));
  }
  if(body.position!==undefined||body.bookmarks!==undefined) commands.push(stmt(env,'UPDATE study_members SET position=?,bookmarks=? WHERE notebook_id=? AND account_id=?',position,bookmarks,notebookId,current.id));
  if(commands.length) {
    try {await env.DB.batch(commands);}
    catch(error) {
      if(String(error?.message||error).includes('study_permission_denied')) throw new ApiError('notebook_permission_changed',403);
      throw error;
    }
  }
  const latest=await member(env,notebookId,current.id);
  return json(request,env,{revision:latest.revision});
}
async function snapshot(request,env,current,notebookId) {
  const row=await member(env,notebookId,current.id);
  const strokes=await all(env,`SELECT page,id,data,deleted,author_id FROM study_strokes WHERE notebook_id=? AND EXISTS(SELECT 1 FROM study_members WHERE notebook_id=? AND account_id=?) ORDER BY page,id`,notebookId,notebookId,current.id);
  const pages=new Map(),deleted=[];
  for(const s of strokes) {
    if(s.deleted) {deleted.push({page:s.page,id:s.id});continue;}
    if(!pages.has(s.page)) pages.set(s.page,[]);
    pages.get(s.page).push(JSON.parse(s.data));
  }
  return json(request,env,{notebook:notebookView(row),pages:[...pages].map(([number,values])=>({number,strokes:values})),deleted,
    strokeAuthors:strokes.map(s=>({page:s.page,id:s.id,accountId:s.author_id||null})),position:{page:row.position},bookmarks:JSON.parse(row.bookmarks)});
}
async function changes(request,env,current,notebookId,url) {
  const row=await member(env,notebookId,current.id);
  if([...url.searchParams.keys()].some(k=>!['since','follow'].includes(k))||(url.searchParams.has('follow')&&url.searchParams.get('follow')!=='1')) throw new ApiError('invalid_fields');
  const since=Number(url.searchParams.get('since')||0);
  if(!Number.isSafeInteger(since)||since<0) throw new ApiError('invalid_revision');
  // A new member may request the feed from revision zero. Do not expose the
  // coordinates of ink erased before that request, even in old put events.
  // Keep each revision as a delete event so existing offline clients still
  // advance their cursors and discard stale copies of the erased stroke.
  const rows=await all(env,`SELECT c.revision,c.page,c.stroke_id,c.author_id,
      CASE WHEN s.deleted=0 THEN c.kind ELSE 'delete' END kind,
      CASE WHEN s.deleted=0 THEN c.data ELSE NULL END data
    FROM study_changes c LEFT JOIN study_strokes s ON s.notebook_id=c.notebook_id AND s.page=c.page AND s.id=c.stroke_id
    WHERE c.notebook_id=? AND c.revision>? AND EXISTS(SELECT 1 FROM study_members WHERE notebook_id=? AND account_id=?)
    ORDER BY c.revision LIMIT 101`,notebookId,since,notebookId,current.id);
  const more=rows.length>100,selected=rows.slice(0,100);
  const revision=selected.length?selected[selected.length-1].revision:row.revision;
  return json(request,env,{notebook:notebookView(row),changes:selected.map(r=>({revision:r.revision,type:r.kind,page:r.page,id:r.stroke_id,stroke:r.data?JSON.parse(r.data):null,authorId:r.author_id||null})),revision,more,notebookRevision:row.revision,
    ...(url.searchParams.get('follow')==='1'?{presentation:await notebookPresentation(env,notebookId)}:{})});
}
async function createInvite(request,env,current,notebookId) {
  await member(env,notebookId,current.id,true);
  const body=object(await readJson(request,256),['role'],[]),role=shareRole(body.role,'viewer');
  await limit(request,env,'invite-create',30,HOUR,current.id);
  const value=randomToken(),expiresAt=Date.now()+DAY;
  await run(env,'INSERT INTO study_invites(token_hash,notebook_id,created_by,expires_at,role) VALUES(?,?,?,?,?)',await sha256(value),notebookId,current.id,expiresAt,role);
  return json(request,env,{token:value,expiresAt,role},201);
}
async function invitation(request,env,current) {
  const body=object(await readJson(request,256),['token']);
  if(typeof body.token!=='string'||!/^[A-Za-z0-9_-]{43}$/.test(body.token)) throw new ApiError('invalid_invite');
  await limit(request,env,'invite-preview',120,HOUR,current.id);
  const row=await first(env,`SELECT i.role,i.expires_at,n.title,n.fingerprint,n.page_count,n.public_id FROM study_invites i
    JOIN study_notebooks n ON n.id=i.notebook_id WHERE i.token_hash=? AND i.expires_at>? AND i.used_by IS NULL AND n.deleted_at IS NULL`,await sha256(body.token),Date.now());
  if(!row) throw new ApiError('invite_expired',410);
  return json(request,env,{invitation:{role:row.role,title:row.title,fingerprint:row.fingerprint,pageCount:row.page_count,publicId:row.public_id,expiresAt:row.expires_at}});
}
async function acceptInvite(request,env,current) {
  const body=object(await readJson(request,256),['token']);
  if(typeof body.token!=='string'||!/^[A-Za-z0-9_-]{43}$/.test(body.token)) throw new ApiError('invalid_invite');
  await limit(request,env,'invite-accept',60,HOUR,current.id);
  const hash=await sha256(body.token),now=Date.now();
  const invitation=await first(env,'SELECT i.* FROM study_invites i JOIN study_notebooks n ON n.id=i.notebook_id WHERE i.token_hash=? AND i.expires_at>? AND n.deleted_at IS NULL',hash,now);
  if(!invitation||invitation.used_by) throw new ApiError('invite_expired',410);
  await env.DB.batch([
    stmt(env,'UPDATE study_invites SET used_by=? WHERE token_hash=? AND used_by IS NULL AND expires_at>? AND EXISTS(SELECT 1 FROM study_notebooks WHERE id=study_invites.notebook_id AND deleted_at IS NULL)',current.id,hash,now),
    stmt(env,`INSERT OR IGNORE INTO study_members(notebook_id,account_id,role,joined_at)
      SELECT notebook_id,?,role,? FROM study_invites WHERE token_hash=? AND used_by=? AND expires_at>?
        AND EXISTS(SELECT 1 FROM study_notebooks WHERE id=study_invites.notebook_id AND deleted_at IS NULL)`,current.id,now,hash,current.id,now),
  ]);
  const claimed=await first(env,'SELECT used_by FROM study_invites WHERE token_hash=?',hash);
  if(claimed.used_by!==current.id) throw new ApiError('invite_expired',410);
  return json(request,env,{notebook:notebookView(await member(env,invitation.notebook_id,current.id))});
}

export async function studyRoute(request,env,url=new URL(request.url)) {
  if(!url.pathname.startsWith('/v1/study/')) return null;
  assertOrigin(request,env,true);
  const route=url.pathname.slice('/v1/study/'.length),method=request.method;
  if(route==='me'&&method==='GET') {
    const current=await account(request,env,false);
    return json(request,env,{account:current,features:studyFeatures(env),limits:{documentBytes:DOCUMENT_LIMIT,accountDocumentBytes:ACCOUNT_DOCUMENT_LIMIT},usage:await studyUsage(env,current?.id)});
  }
  const auth=route.match(/^auth\/(register|login|reauth|credential)\/(options|verify)$/);
  if(auth&&method==='POST') {const kind=auth[1]==='credential'?'add':auth[1];return auth[2]==='options'?authOptions(request,env,kind):authVerify(request,env,kind);}
  if(route==='logout'&&method==='POST') {
    object(await readJson(request,256),[]);
    const current=token(request,env);
    if(current) await run(env,'DELETE FROM study_sessions WHERE token_hash=?',await sha256(current));
    return json(request,env,{},200,cookie(request,env,'','session',0));
  }
  const current=await account(request,env);
  if(route==='credentials'||route.startsWith('credentials/')){const response=await credentialsRoute(request,env,current,route);if(response)return response;}
  const library=await libraryRoute(request,env,current,route,url,{json,member,notebookView,limit,pageNumber});if(library)return library;
  if(route==='notebooks'&&method==='GET') {
    if([...url.searchParams.keys()].some(key=>!['includeDeleted','cursor','limit'].includes(key)))throw new ApiError('invalid_fields');
    const includeDeleted=url.searchParams.get('includeDeleted')==='1',cursor=Number(url.searchParams.get('cursor')||0),size=Number(url.searchParams.get('limit')||200);
    if(!Number.isInteger(cursor)||cursor<0||cursor>10000||!Number.isInteger(size)||size<1||size>200)throw new ApiError('invalid_fields');
    const rows=await all(env,`SELECT n.*,m.role,a.display_name owner_name FROM study_notebooks n JOIN study_members m ON m.notebook_id=n.id JOIN study_accounts a ON a.id=n.owner_id
      WHERE m.account_id=? AND (n.deleted_at IS NULL OR (?=1 AND n.owner_id=?)) ORDER BY n.updated_at DESC,n.id LIMIT ? OFFSET ?`,current.id,Number(includeDeleted),current.id,size+1,cursor);
    return json(request,env,{notebooks:rows.slice(0,size).map(notebookView),nextCursor:rows.length>size?cursor+size:null});
  }
  if(route==='notebooks'&&method==='POST') return createNotebook(request,env,current);
  if(route==='invites/preview'&&method==='POST') return invitation(request,env,current);
  if(route==='invites/accept'&&method==='POST') return acceptInvite(request,env,current);
  const match=route.match(/^notebooks\/([A-Za-z0-9_-]+)(?:\/(operations|pages|invites|members)(?:\/([A-Za-z0-9_-]+))?)?$/);
  if(match) {
    const [,notebookId,action,memberId]=match;
    if(!action&&method==='GET') return snapshot(request,env,current,notebookId);
    if(action==='operations'&&method==='POST') return operations(request,env,current,notebookId);
    if(action==='pages'&&method==='GET') return changes(request,env,current,notebookId,url);
    if(action==='invites'&&method==='POST') return createInvite(request,env,current,notebookId);
    if(action==='members') {
      await member(env,notebookId,current.id,true);
      if(method==='GET'&&!memberId) {
        const rows=await all(env,"SELECT a.id,a.display_name,m.role FROM study_members m JOIN study_accounts a ON a.id=m.account_id WHERE m.notebook_id=? ORDER BY CASE m.role WHEN 'owner' THEN 0 ELSE 1 END,m.joined_at",notebookId);
        return json(request,env,{members:rows.map(r=>({accountId:r.id,displayName:r.display_name,role:r.role}))});
      }
      if(method==='DELETE'&&memberId) {
        if(memberId===current.id) throw new ApiError('cannot_revoke_owner');
        await run(env,"DELETE FROM study_members WHERE notebook_id=? AND account_id=? AND role!='owner'",notebookId,id(memberId));
        return json(request,env,{});
      }
      if(method==='PATCH'&&memberId) {
        if(memberId===current.id) throw new ApiError('cannot_change_owner');
        const body=object(await readJson(request,256),['role']),role=shareRole(body.role);
        const result=await run(env,"UPDATE study_members SET role=? WHERE notebook_id=? AND account_id=? AND role!='owner'",role,notebookId,id(memberId));
        if(!changed(result)) throw new ApiError('notebook_member_not_found',404);
        return json(request,env,{member:{accountId:memberId,role}});
      }
    }
  }
  throw new ApiError('not_found',404);
}

export async function pruneStudy(env) {
  const now=Date.now();
  await env.DB.batch([
    stmt(env,'DELETE FROM study_sessions WHERE expires_at<?',now),
    stmt(env,'DELETE FROM study_challenges WHERE expires_at<?',now),
    stmt(env,'DELETE FROM study_invites WHERE expires_at<?',now),
  ]);
  await pruneLibrary(env);
}
