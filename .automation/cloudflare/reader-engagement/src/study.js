import {
  generateRegistrationOptions, verifyRegistrationResponse,
  generateAuthenticationOptions, verifyAuthenticationResponse,
} from '@simplewebauthn/server';
import {ApiError,SITE_ORIGIN,assertOrigin,base64url,object,randomToken,readJson,sha256,responseHeaders} from './security.js';

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
  const body=object(await readJson(request,1024),kind==='register'?['displayName']:[]);
  const {origin,rpID}=rp(request,env);
  const next=kind==='register'?{id:crypto.randomUUID(),displayName:displayName(body.displayName),userID:crypto.getRandomValues(new Uint8Array(32))}:null;
  const options=kind==='register'?await generateRegistrationOptions({
    rpName:'AI Tech Review',rpID,userID:next.userID,userName:next.id,userDisplayName:next.displayName,
    attestationType:'none',timeout:120_000,supportedAlgorithmIDs:[-7,-257],
    authenticatorSelection:{residentKey:'required',userVerification:'required'},
  }):await generateAuthenticationOptions({rpID,userVerification:'required',timeout:120_000});
  const bind=randomToken();
  const previous=token(request,env,'challenge');
  if(previous) await run(env,'DELETE FROM study_challenges WHERE token_hash=?',await sha256(previous));
  await run(env,`INSERT INTO study_challenges(token_hash,kind,challenge,origin,rp_id,account_id,display_name,user_handle,expires_at) VALUES(?,?,?,?,?,?,?,?,?)`,
    await sha256(bind),kind,options.challenge,origin,rpID,next?.id||null,next?.displayName||null,next?base64url(next.userID):null,Date.now()+5*60_000);
  return json(request,env,{options},200,cookie(request,env,bind,'challenge',300));
}
async function authVerify(request,env,kind) {
  await limit(request,env,'auth-verify',60);
  const body=object(await readJson(request,64_000),['response']);
  const bind=token(request,env,'challenge');
  if(!bind) throw new ApiError('challenge_expired',401);
  const expected=await first(env,'DELETE FROM study_challenges WHERE token_hash=? AND kind=? AND expires_at>? RETURNING *',await sha256(bind),kind,Date.now());
  if(!expected || expected.origin!==assertOrigin(request,env,true)) throw new ApiError('challenge_expired',401);
  // This application has no embedded login flow. Reject cross-origin frames
  // even on browsers that omit WebAuthn's newer topOrigin field.
  try {
    const client=JSON.parse(new TextDecoder().decode(decode(body.response?.response?.clientDataJSON)));
    if(client.crossOrigin===true||client.topOrigin) throw new Error('embedded_authentication');
  } catch {throw new ApiError('passkey_verification_failed',401);}
  let owner;
  if(kind==='register') {
    let result;
    try {result=await verifyRegistrationResponse({response:body.response,expectedChallenge:expected.challenge,expectedOrigin:expected.origin,expectedRPID:expected.rp_id,requireUserVerification:true,supportedAlgorithmIDs:[-7,-257]});}
    catch {throw new ApiError('passkey_verification_failed',401);}
    if(!result.verified||!result.registrationInfo) throw new ApiError('passkey_verification_failed',401);
    const credential=result.registrationInfo.credential;
    const transports=Array.isArray(credential.transports)?credential.transports.filter(v=>typeof v==='string').slice(0,8):[];
    owner={id:expected.account_id,displayName:expected.display_name};
    try {await env.DB.batch([
      stmt(env,'INSERT INTO study_accounts(id,display_name,created_at) VALUES(?,?,?)',owner.id,owner.displayName,Date.now()),
      stmt(env,'INSERT INTO study_credentials(id,account_id,public_key,counter,user_handle,transports,created_at) VALUES(?,?,?,?,?,?,?)',credential.id,owner.id,base64url(credential.publicKey),credential.counter,expected.user_handle,JSON.stringify(transports),Date.now()),
    ]);}catch {throw new ApiError('credential_already_registered',409);}
  } else {
    const id=body.response?.id;
    if(typeof id!=='string'||id.length>2048) throw new ApiError('passkey_verification_failed',401);
    const credential=await first(env,'SELECT c.*,a.display_name FROM study_credentials c JOIN study_accounts a ON a.id=c.account_id WHERE c.id=?',id);
    if(!credential) throw new ApiError('passkey_verification_failed',401);
    if(body.response?.response?.userHandle && body.response.response.userHandle!==credential.user_handle) throw new ApiError('passkey_verification_failed',401);
    let result;
    try {result=await verifyAuthenticationResponse({response:body.response,expectedChallenge:expected.challenge,expectedOrigin:expected.origin,expectedRPID:expected.rp_id,requireUserVerification:true,
      credential:{id:credential.id,publicKey:decode(credential.public_key),counter:credential.counter,transports:JSON.parse(credential.transports)}});}
    catch {throw new ApiError('passkey_verification_failed',401);}
    if(!result.verified) throw new ApiError('passkey_verification_failed',401);
    await run(env,'UPDATE study_credentials SET counter=? WHERE id=? AND counter<=?',result.authenticationInfo.newCounter,id,result.authenticationInfo.newCounter);
    owner={id:credential.account_id,displayName:credential.display_name};
  }
  const session=randomToken();
  const old=token(request,env);
  const commands=[];
  if(old) commands.push(stmt(env,'DELETE FROM study_sessions WHERE token_hash=?',await sha256(old)));
  commands.push(stmt(env,'INSERT INTO study_sessions(token_hash,account_id,expires_at) VALUES(?,?,?)',await sha256(session),owner.id,Date.now()+30*DAY));
  await env.DB.batch(commands);
  return json(request,env,{account:owner},200,cookie(request,env,session));
}
function id(value) {
  if(typeof value!=='string'||!/^[A-Za-z0-9_-]{8,100}$/.test(value)) throw new ApiError('invalid_study_id');
  return value;
}
function notebookView(row) {
  return {id:row.id,title:row.title,fingerprint:row.fingerprint,pageCount:row.page_count,publicId:row.public_id,
    ownerId:row.owner_id,role:row.role,revision:row.revision,updatedAt:row.updated_at};
}
async function member(env,notebookId,accountId,ownerOnly=false) {
  id(notebookId);
  const row=await first(env,`SELECT n.*,m.role,m.position,m.bookmarks FROM study_notebooks n JOIN study_members m ON m.notebook_id=n.id WHERE n.id=? AND m.account_id=?`,notebookId,accountId);
  if(!row) throw new ApiError('notebook_not_found',404);
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
  const previous=await first(env,`SELECT n.*,m.role FROM study_notebooks n JOIN study_members m ON m.notebook_id=n.id AND m.account_id=? WHERE n.owner_id=? AND n.fingerprint=?`,current.id,current.id,body.fingerprint);
  if(previous) return json(request,env,{notebook:notebookView(previous)});
  if((await first(env,'SELECT count(*) n FROM study_notebooks WHERE owner_id=?',current.id)).n>=100) throw new ApiError('notebook_limit',413);
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
  const commands=[],now=Date.now();
  let extraBytes=0,extraRows=0;
  const known=new Map();
  for(const operation of body.operations) {
    object(operation,operation?.type==='put'?['type','page','stroke']:['type','page','id']);
    const page=pageNumber(operation.page,row);
    if(operation.type==='put') {
      const value=validateStroke(operation.stroke),data=JSON.stringify(value);
      const key=`${page}:${value.id}`;
      if(!known.has(key)) known.set(key,await first(env,'SELECT deleted,data FROM study_strokes WHERE notebook_id=? AND page=? AND id=?',notebookId,page,value.id));
      if(!known.get(key)) {extraBytes+=data.length;extraRows++;known.set(key,{deleted:0,data});}
      // Immutable ids and permanent tombstones make retries and stale offline writes safe.
      commands.push(stmt(env,`INSERT OR IGNORE INTO study_strokes(notebook_id,page,id,data,deleted,updated_at)
        SELECT ?,?,?,?,0,? WHERE EXISTS(SELECT 1 FROM study_members WHERE notebook_id=? AND account_id=?)`,notebookId,page,value.id,data,now,notebookId,current.id));
    } else if(operation.type==='delete') {
      const key=`${page}:${strokeId(operation.id)}`;
      if(!known.has(key)) known.set(key,await first(env,'SELECT deleted,data FROM study_strokes WHERE notebook_id=? AND page=? AND id=?',notebookId,page,operation.id));
      if(!known.get(key)) extraRows++;
      else if(known.get(key).data) extraBytes-=known.get(key).data.length;
      known.set(key,{deleted:1,data:null});
      commands.push(stmt(env,`INSERT INTO study_strokes(notebook_id,page,id,data,deleted,updated_at)
        SELECT ?,?,?,NULL,1,? WHERE EXISTS(SELECT 1 FROM study_members WHERE notebook_id=? AND account_id=?)
        ON CONFLICT(notebook_id,page,id) DO UPDATE SET data=NULL,deleted=1,updated_at=excluded.updated_at WHERE study_strokes.deleted=0`,notebookId,page,strokeId(operation.id),now,notebookId,current.id));
    } else throw new ApiError('invalid_operation');
  }
  const capacity=await first(env,'SELECT count(*) n,COALESCE(sum(length(data)),0) bytes FROM study_strokes WHERE notebook_id=?',notebookId);
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
  if(commands.length) await env.DB.batch(commands);
  const latest=await member(env,notebookId,current.id);
  return json(request,env,{revision:latest.revision});
}
async function snapshot(request,env,current,notebookId) {
  const row=await member(env,notebookId,current.id);
  const strokes=await all(env,`SELECT page,id,data,deleted FROM study_strokes WHERE notebook_id=? AND EXISTS(SELECT 1 FROM study_members WHERE notebook_id=? AND account_id=?) ORDER BY page,id`,notebookId,notebookId,current.id);
  const pages=new Map(),deleted=[];
  for(const s of strokes) {
    if(s.deleted) {deleted.push({page:s.page,id:s.id});continue;}
    if(!pages.has(s.page)) pages.set(s.page,[]);
    pages.get(s.page).push(JSON.parse(s.data));
  }
  return json(request,env,{notebook:notebookView(row),pages:[...pages].map(([number,values])=>({number,strokes:values})),deleted,position:{page:row.position},bookmarks:JSON.parse(row.bookmarks)});
}
async function changes(request,env,current,notebookId,url) {
  const row=await member(env,notebookId,current.id);
  if([...url.searchParams.keys()].some(k=>k!=='since')) throw new ApiError('invalid_fields');
  const since=Number(url.searchParams.get('since')||0);
  if(!Number.isSafeInteger(since)||since<0) throw new ApiError('invalid_revision');
  const rows=await all(env,`SELECT revision,page,stroke_id,kind,data FROM study_changes WHERE notebook_id=? AND revision>? AND EXISTS(SELECT 1 FROM study_members WHERE notebook_id=? AND account_id=?) ORDER BY revision LIMIT 101`,notebookId,since,notebookId,current.id);
  const more=rows.length>100,selected=rows.slice(0,100);
  const revision=selected.length?selected[selected.length-1].revision:row.revision;
  return json(request,env,{changes:selected.map(r=>({revision:r.revision,type:r.kind,page:r.page,id:r.stroke_id,stroke:r.data?JSON.parse(r.data):null})),revision,more,notebookRevision:row.revision});
}
async function createInvite(request,env,current,notebookId) {
  await member(env,notebookId,current.id,true);
  object(await readJson(request,256),[]);
  await limit(request,env,'invite-create',30,HOUR,current.id);
  const value=randomToken(),expiresAt=Date.now()+DAY;
  await run(env,'INSERT INTO study_invites(token_hash,notebook_id,created_by,expires_at) VALUES(?,?,?,?)',await sha256(value),notebookId,current.id,expiresAt);
  return json(request,env,{token:value,expiresAt},201);
}
async function acceptInvite(request,env,current) {
  const body=object(await readJson(request,256),['token']);
  if(typeof body.token!=='string'||!/^[A-Za-z0-9_-]{43}$/.test(body.token)) throw new ApiError('invalid_invite');
  await limit(request,env,'invite-accept',60,HOUR,current.id);
  const hash=await sha256(body.token),now=Date.now();
  const invitation=await first(env,'SELECT * FROM study_invites WHERE token_hash=? AND expires_at>?',hash,now);
  if(!invitation||invitation.used_by) throw new ApiError('invite_expired',410);
  await env.DB.batch([
    stmt(env,'UPDATE study_invites SET used_by=? WHERE token_hash=? AND used_by IS NULL AND expires_at>?',current.id,hash,now),
    stmt(env,`INSERT OR IGNORE INTO study_members(notebook_id,account_id,role,joined_at)
      SELECT notebook_id,?,'editor',? FROM study_invites WHERE token_hash=? AND used_by=? AND expires_at>?`,current.id,now,hash,current.id,now),
  ]);
  const claimed=await first(env,'SELECT used_by FROM study_invites WHERE token_hash=?',hash);
  if(claimed.used_by!==current.id) throw new ApiError('invite_expired',410);
  return json(request,env,{notebook:notebookView(await member(env,invitation.notebook_id,current.id))});
}

export async function studyRoute(request,env,url=new URL(request.url)) {
  if(!url.pathname.startsWith('/v1/study/')) return null;
  assertOrigin(request,env,true);
  const route=url.pathname.slice('/v1/study/'.length),method=request.method;
  if(route==='me'&&method==='GET') return json(request,env,{account:await account(request,env,false)});
  const auth=route.match(/^auth\/(register|login)\/(options|verify)$/);
  if(auth&&method==='POST') return auth[2]==='options'?authOptions(request,env,auth[1]):authVerify(request,env,auth[1]);
  if(route==='logout'&&method==='POST') {
    object(await readJson(request,256),[]);
    const current=token(request,env);
    if(current) await run(env,'DELETE FROM study_sessions WHERE token_hash=?',await sha256(current));
    return json(request,env,{},200,cookie(request,env,'','session',0));
  }
  const current=await account(request,env);
  if(route==='notebooks'&&method==='GET') {
    const rows=await all(env,`SELECT n.*,m.role FROM study_notebooks n JOIN study_members m ON m.notebook_id=n.id WHERE m.account_id=? ORDER BY n.updated_at DESC LIMIT 200`,current.id);
    return json(request,env,{notebooks:rows.map(notebookView)});
  }
  if(route==='notebooks'&&method==='POST') return createNotebook(request,env,current);
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
        const rows=await all(env,'SELECT a.id,a.display_name,m.role FROM study_members m JOIN study_accounts a ON a.id=m.account_id WHERE m.notebook_id=? ORDER BY m.role DESC,m.joined_at',notebookId);
        return json(request,env,{members:rows.map(r=>({accountId:r.id,displayName:r.display_name,role:r.role}))});
      }
      if(method==='DELETE'&&memberId) {
        if(memberId===current.id) throw new ApiError('cannot_revoke_owner');
        await run(env,"DELETE FROM study_members WHERE notebook_id=? AND account_id=? AND role='editor'",notebookId,id(memberId));
        return json(request,env,{});
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
}
