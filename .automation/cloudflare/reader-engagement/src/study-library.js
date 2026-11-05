import {ApiError,object,readJson,responseHeaders} from './security.js';

const HOUR=3_600_000;
export const DOCUMENT_LIMIT=50*1024*1024;
export const ACCOUNT_DOCUMENT_LIMIT=500*1024*1024;
const stmt=(env,sql,...args)=>env.DB.prepare(sql).bind(...args);
const first=(env,sql,...args)=>stmt(env,sql,...args).first();
const all=async(env,sql,...args)=>(await stmt(env,sql,...args).all()).results;
const run=(env,sql,...args)=>stmt(env,sql,...args).run();
const changed=result=>Number(result.meta?.changes||0)>0;
const title=value=>{
  if(typeof value!=='string'||!value.trim()||value.trim().length>240||/[\u0000-\u001f\u007f]/.test(value))throw new ApiError('invalid_notebook_title');
  return value.trim();
};
const text=(value,maximum)=>{
  if(typeof value!=='string'||value.length>maximum||/\u0000/.test(value))throw new ApiError('invalid_draft_text');
  return value;
};
function notebookQuota(error){
  const message=String(error?.message||error);
  if(message.includes('study_notebook_quota'))throw new ApiError('notebook_limit',413);
  if(message.includes('study_retention_quota'))throw new ApiError('notebook_retention_limit',413);
  throw error;
}
export function studyFeatures(env){return{documentStorage:Boolean(env.STUDY_DOCUMENTS),drafts:true,presenter:true,additionalPasskeys:true};}
export async function studyUsage(env,accountId){
  if(!accountId)return null;
  const usage=await first(env,`SELECT COALESCE(sum(byte_size),0) bytes,count(*) n FROM study_documents WHERE owner_id=?`,accountId);
  const notebooks=await first(env,`SELECT count(*) n,COALESCE(sum(deleted_at IS NOT NULL),0) trash FROM study_notebooks WHERE owner_id=?`,accountId);
  return{documentBytes:usage.bytes,documentCount:usage.n,quotaBytes:ACCOUNT_DOCUMENT_LIMIT,notebookCount:notebooks.n,trashCount:notebooks.trash};
}
export async function notebookPresentation(env,notebookId){
  const row=await first(env,`SELECT p.*,a.display_name FROM study_presentations p JOIN study_accounts a ON a.id=p.presenter_id
    JOIN study_members m ON m.notebook_id=p.notebook_id AND m.account_id=p.presenter_id
    WHERE p.notebook_id=? AND p.expires_at>? AND m.role IN ('owner','editor')`,notebookId,Date.now());
  return row?{id:row.id,presenterId:row.presenter_id,presenterName:row.display_name,page:row.page,updatedAt:row.updated_at,expiresAt:row.expires_at}:null;
}

async function duplicate(request,env,current,notebookId,reset,api){
  const source=await api.member(env,notebookId,current.id);
  await api.limit(request,env,'copy-note',30,HOUR,current.id);
  const body=object(await readJson(request,2048),reset?['title']:['title','includeInk'],[]);
  if(body.includeInk!==undefined&&typeof body.includeInk!=='boolean')throw new ApiError('invalid_fields');
  const includeInk=!reset&&body.includeInk!==false,id=crypto.randomUUID(),now=Date.now();
  const name=title(body.title||source.title+(reset?' · 새 학습본':' · 사본'));
  const commands=[
    stmt(env,`INSERT INTO study_notebooks(id,owner_id,public_id,title,fingerprint,page_count,created_at,updated_at,document_id,document_bytes,source_notebook_id,created_from)
      SELECT ?,?,public_id,?,fingerprint,page_count,?,?,CASE WHEN owner_id=? THEN document_id ELSE NULL END,
        CASE WHEN owner_id=? THEN document_bytes ELSE 0 END,id,? FROM study_notebooks
      WHERE id=? AND deleted_at IS NULL AND EXISTS(SELECT 1 FROM study_members WHERE notebook_id=? AND account_id=?)`,
      id,current.id,name,now,now,current.id,current.id,reset?'reset':'copy',notebookId,notebookId,current.id),
    stmt(env,"INSERT INTO study_members(notebook_id,account_id,role,joined_at) VALUES(?,?,'owner',?)",id,current.id,now),
  ];
  if(includeInk)commands.push(stmt(env,`WITH copies AS MATERIALIZED (
      SELECT page,lower(hex(randomblob(16))) new_id,data FROM study_strokes WHERE notebook_id=? AND deleted=0
    ) INSERT INTO study_strokes(notebook_id,page,id,data,deleted,updated_at,author_id,actor_id)
      SELECT ?,page,new_id,json_set(data,'$.id',new_id),0,?,?,? FROM copies`,notebookId,id,now,current.id,current.id));
  try{await env.DB.batch(commands);}catch(error){notebookQuota(error);}
  return api.json(request,env,{notebook:api.notebookView(await api.member(env,id,current.id)),sourceNotebookId:notebookId,sourcePreserved:true},201);
}
async function trash(request,env,current,notebookId,restore,api){
  const row=await api.member(env,notebookId,current.id,true,true);
  object(await readJson(request,256),[]);
  if(restore){
    if((await first(env,'SELECT count(*) n FROM study_notebooks WHERE owner_id=? AND deleted_at IS NULL',current.id)).n>=100&&row.deleted_at)throw new ApiError('notebook_limit',413);
    try{await run(env,'UPDATE study_notebooks SET deleted_at=NULL,updated_at=? WHERE id=? AND owner_id=?',Date.now(),notebookId,current.id);}catch(error){notebookQuota(error);}
  }else{
    const now=Date.now();
    await env.DB.batch([
      stmt(env,'UPDATE study_notebooks SET deleted_at=COALESCE(deleted_at,?),updated_at=? WHERE id=? AND owner_id=?',now,now,notebookId,current.id),
      stmt(env,'DELETE FROM study_presentations WHERE notebook_id=?',notebookId),
      stmt(env,"UPDATE study_submissions SET status='withdrawn' WHERE notebook_id=? AND status IN ('submitted','approved')",notebookId),
      stmt(env,"UPDATE study_drafts SET status='draft',updated_at=? WHERE notebook_id=? AND status IN ('submitted','approved')",now,notebookId),
    ]);
  }
  return api.json(request,env,{notebook:api.notebookView(await api.member(env,notebookId,current.id,true,true))});
}

async function uploadedDocument(env,row){
  if(!row.document_id)return null;
  return first(env,"SELECT * FROM study_documents WHERE id=? AND state='ready'",row.document_id);
}
async function documentGet(request,env,current,notebookId,api){
  if(!env.STUDY_DOCUMENTS)throw new ApiError('document_storage_unavailable',503);
  const row=await api.member(env,notebookId,current.id),document=await uploadedDocument(env,row);
  if(!document)throw new ApiError('document_not_uploaded',404);
  const stored=await env.STUDY_DOCUMENTS.get(document.object_key);
  if(!stored)throw new ApiError('document_unavailable',503);
  // Membership can change while the object is being fetched.
  await api.member(env,notebookId,current.id);
  const headers=responseHeaders(request,env);
  headers.set('Content-Type','application/pdf');headers.set('Content-Disposition','attachment; filename="study-source.pdf"');
  headers.set('Content-Length',String(stored.size));headers.set('Cache-Control','private, no-store');headers.set('X-Content-Type-Options','nosniff');
  headers.set('ETag','"sha256-'+document.fingerprint+'"');
  return new Response(stored.body,{headers});
}
async function attachDocument(env,row,document,current){
  const result=await run(env,`UPDATE study_notebooks SET document_id=?,document_bytes=?,updated_at=?
    WHERE id=? AND owner_id=? AND deleted_at IS NULL AND fingerprint=?`,document.id,document.byte_size,Date.now(),row.id,current.id,document.fingerprint);
  if(!changed(result))throw new ApiError('notebook_not_found',404);
}
async function verifyPdfBody(request,size,sink=null){
  const digest=new crypto.DigestStream('SHA-256'),hash=digest.getWriter(),reader=request.body.getReader();
  const digestResult=digest.digest.catch(()=>null);let count=0,prefix=[];
  try{
    while(true){
      const {done,value}=await reader.read();if(done)break;
      count+=value.byteLength;if(count>size||count>DOCUMENT_LIMIT)throw new ApiError('document_length_mismatch');
      if(prefix.length<5)prefix.push(...value.slice(0,5-prefix.length));
      await hash.write(value);if(sink)await sink.write(value);
    }
    if(count!==size)throw new ApiError('document_length_mismatch');
    await hash.close();if(sink)await sink.close();
    const result=await digestResult;
    if(String.fromCharCode(...prefix)!=='%PDF-'||!result)throw new ApiError('pdf_required');
    return [...new Uint8Array(result)].map(byte=>byte.toString(16).padStart(2,'0')).join('');
  }catch(error){await Promise.allSettled([reader.cancel(error),hash.abort(error),...(sink?[sink.abort(error)]:[])]);throw error;}
}
async function documentPut(request,env,current,notebookId,url,api){
  if(!env.STUDY_DOCUMENTS)throw new ApiError('document_storage_unavailable',503);
  const row=await api.member(env,notebookId,current.id,true);
  await api.limit(request,env,'document-upload',20,HOUR,current.id);
  if(request.headers.get('Content-Type')?.split(';')[0].trim()!=='application/pdf')throw new ApiError('pdf_required',415);
  if([...url.searchParams.keys()].some(key=>key!=='size'))throw new ApiError('invalid_fields');
  const header=request.headers.get('Content-Length'),declared=url.searchParams.get('size')||header;
  if(!declared||!/^\d+$/.test(declared))throw new ApiError('document_length_required',411);
  const size=Number(declared);
  if(!Number.isSafeInteger(size)||size<5||size>DOCUMENT_LIMIT)throw new ApiError('document_too_large',413);
  if(header!==null&&(!/^\d+$/.test(header)||Number(header)!==size))throw new ApiError('document_length_mismatch');
  if(!request.body)throw new ApiError('pdf_required');
  const previous=await first(env,'SELECT * FROM study_documents WHERE owner_id=? AND fingerprint=?',current.id,row.fingerprint);
  if(previous){
    if(previous.state!=='ready')throw new ApiError('document_upload_in_progress',409);
    if(previous.byte_size!==size)throw new ApiError('document_fingerprint_mismatch',409);
    if(await verifyPdfBody(request,size)!==row.fingerprint)throw new ApiError('document_fingerprint_mismatch',409);
    await attachDocument(env,row,previous,current);
    return api.json(request,env,{notebook:api.notebookView(await api.member(env,notebookId,current.id)),document:{fingerprint:row.fingerprint,bytes:size,immutable:true},usage:await studyUsage(env,current.id)});
  }
  const document={id:crypto.randomUUID(),owner_id:current.id,fingerprint:row.fingerprint,object_key:'private/'+current.id+'/'+row.fingerprint+'.pdf',byte_size:size};
  const temporary='pending/'+document.id+'.pdf';
  try{await run(env,"INSERT INTO study_documents(id,owner_id,fingerprint,object_key,byte_size,state,created_at,expires_at) VALUES(?,?,?,?,?,'uploading',?,?)",
    document.id,current.id,row.fingerprint,document.object_key,size,Date.now(),Date.now()+HOUR);
  }catch(error){
    if(String(error?.message||error).includes('study_document_quota'))throw new ApiError('document_quota_exceeded',413);
    if(String(error?.message||error).includes('UNIQUE'))throw new ApiError('document_upload_in_progress',409);
    throw error;
  }
  let finalCreated=false,committed=false,upload=null;
  const fixed=new FixedLengthStream(size),writer=fixed.writable.getWriter(),pumping=verifyPdfBody(request,size,writer);
  try{
    upload=env.STUDY_DOCUMENTS.put(temporary,fixed.readable,{httpMetadata:{contentType:'application/pdf'}});
    const [actual]=await Promise.all([pumping,upload]);
    if(actual!==row.fingerprint)throw new ApiError('document_fingerprint_mismatch',409);
    await api.member(env,notebookId,current.id,true);
    const staged=await env.STUDY_DOCUMENTS.get(temporary);if(!staged)throw new ApiError('document_unavailable',503);
    const stored=await env.STUDY_DOCUMENTS.put(document.object_key,staged.body,{onlyIf:{etagDoesNotMatch:'*'},httpMetadata:{contentType:'application/pdf'},customMetadata:{fingerprint:actual,ownerId:current.id}});
    finalCreated=Boolean(stored);
    if(!stored){
      const original=await env.STUDY_DOCUMENTS.head(document.object_key);
      if(original?.size!==size||original.customMetadata?.fingerprint!==actual||original.customMetadata?.ownerId!==current.id)throw new ApiError('document_fingerprint_mismatch',409);
    }
    await env.DB.batch([
      stmt(env,`UPDATE study_documents SET state='ready',expires_at=NULL WHERE id=? AND owner_id=?
        AND EXISTS(SELECT 1 FROM study_notebooks WHERE id=? AND owner_id=? AND deleted_at IS NULL)`,document.id,current.id,notebookId,current.id),
      stmt(env,`UPDATE study_notebooks SET document_id=?,document_bytes=?,updated_at=?
        WHERE id=? AND owner_id=? AND deleted_at IS NULL AND fingerprint=?
          AND EXISTS(SELECT 1 FROM study_documents WHERE id=? AND state='ready')`,document.id,size,Date.now(),notebookId,current.id,actual,document.id),
    ]);
    committed=Boolean(await first(env,"SELECT id FROM study_documents WHERE id=? AND state='ready'",document.id));
    await env.STUDY_DOCUMENTS.delete(temporary).catch(()=>{});
    const latest=await api.member(env,notebookId,current.id,true);
    if(latest.document_id!==document.id)throw new ApiError('notebook_not_found',404);
    return api.json(request,env,{notebook:api.notebookView(latest),document:{fingerprint:actual,bytes:size,immutable:true},usage:await studyUsage(env,current.id)},201);
  }catch(error){
    await writer.abort(error).catch(()=>{});
    await pumping.catch(()=>{});
    if(upload)await upload.catch(()=>{});
    if(!committed){
      await env.STUDY_DOCUMENTS.delete(finalCreated?[temporary,document.object_key]:temporary).catch(()=>{});
      await run(env,"DELETE FROM study_documents WHERE id=? AND state='uploading'",document.id);
    }
    if(error instanceof ApiError)throw error;
    throw new ApiError('document_upload_failed',503);
  }
}

function draftView(row){return{id:row.id,title:row.title,summary:row.summary,body:row.body,notebookId:row.notebook_id,status:row.status,submissionId:row.submission_id,createdAt:row.created_at,updatedAt:row.updated_at};}
async function ownDraft(env,id,current){
  const row=await first(env,'SELECT * FROM study_drafts WHERE id=? AND owner_id=?',id,current.id);
  if(!row)throw new ApiError('draft_not_found',404);return row;
}
async function draftValues(env,current,body,api,previous=null){
  const values={title:title(body.title??previous?.title),summary:text(body.summary??previous?.summary??'',4000),body:text(body.body??previous?.body??'',100000),notebookId:body.notebookId===undefined?previous?.notebook_id||null:body.notebookId};
  if(values.notebookId!==null)await api.member(env,values.notebookId,current.id,true);
  return values;
}
async function drafts(request,env,current,route,api){
  if(route==='drafts'&&request.method==='GET')return api.json(request,env,{drafts:(await all(env,'SELECT * FROM study_drafts WHERE owner_id=? ORDER BY updated_at DESC LIMIT 200',current.id)).map(draftView)});
  const match=route.match(/^drafts\/([A-Za-z0-9_-]+)(?:\/(submit|withdraw))?$/),method=request.method;
  if(route==='drafts'&&method==='POST'){
    if((await first(env,'SELECT count(*) n FROM study_drafts WHERE owner_id=?',current.id)).n>=100)throw new ApiError('draft_limit',413);
    const body=object(await readJson(request,120000),['title','summary','body','notebookId'],['title']),v=await draftValues(env,current,body,api),id=crypto.randomUUID(),now=Date.now();
    await run(env,'INSERT INTO study_drafts(id,owner_id,notebook_id,title,summary,body,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)',id,current.id,v.notebookId,v.title,v.summary,v.body,now,now);
    return api.json(request,env,{draft:draftView(await ownDraft(env,id,current))},201);
  }
  if(!match)return null;
  const [,id,action]=match,row=await ownDraft(env,id,current);
  if(!action&&method==='GET')return api.json(request,env,{draft:draftView(row)});
  if(!action&&method==='PATCH'){
    if(row.status==='submitted')throw new ApiError('draft_locked_for_review',409);
    const body=object(await readJson(request,120000),['title','summary','body','notebookId'],[]),v=await draftValues(env,current,body,api,row);
    const result=await run(env,"UPDATE study_drafts SET notebook_id=?,title=?,summary=?,body=?,status='draft',updated_at=? WHERE id=? AND owner_id=? AND status!='submitted'",v.notebookId,v.title,v.summary,v.body,Date.now(),id,current.id);
    if(!changed(result))throw new ApiError('draft_locked_for_review',409);
    return api.json(request,env,{draft:draftView(await ownDraft(env,id,current))});
  }
  if(action==='submit'&&method==='POST'){
    const body=object(await readJson(request,256),['rightsConfirmed']);
    if(body.rightsConfirmed!==true)throw new ApiError('publication_rights_confirmation_required');
    if(row.status==='submitted')throw new ApiError('draft_locked_for_review',409);
    const source=row.notebook_id?await api.member(env,row.notebook_id,current.id,true):null;
    if(!row.body.trim()&&!source?.document_id)throw new ApiError('draft_content_required');
    const submission=crypto.randomUUID(),now=Date.now();
    try{await env.DB.batch([
      stmt(env,`INSERT INTO study_submissions(id,draft_id,owner_id,notebook_id,document_id,title,summary,body,fingerprint,submitted_at)
        VALUES(?,?,?,?,?,?,?,?,?,?)`,submission,id,current.id,row.notebook_id,source?.document_id||null,row.title,row.summary,row.body,source?.fingerprint||null,now),
      stmt(env,"UPDATE study_drafts SET status='submitted',submission_id=?,updated_at=? WHERE id=? AND owner_id=?",submission,now,id,current.id),
    ]);}catch(error){
      if(String(error?.message||error).includes('draft_locked_for_review'))throw new ApiError('draft_locked_for_review',409);
      if(String(error?.message||error).includes('draft_source_unavailable'))throw new ApiError('notebook_not_found',404);
      throw error;
    }
    return api.json(request,env,{draft:draftView(await ownDraft(env,id,current)),submission:{id:submission,status:'submitted',published:false}},201);
  }
  if(action==='withdraw'&&method==='POST'){
    object(await readJson(request,256),[]);
    await env.DB.batch([stmt(env,"UPDATE study_submissions SET status='withdrawn' WHERE id=? AND owner_id=? AND status='submitted'",row.submission_id,current.id),stmt(env,"UPDATE study_drafts SET status='draft',updated_at=? WHERE id=? AND owner_id=?",Date.now(),id,current.id)]);
    return api.json(request,env,{draft:draftView(await ownDraft(env,id,current))});
  }
  return null;
}
function isReviewer(env,current){return String(env.STUDY_REVIEWER_ACCOUNT_IDS||'').split(',').map(id=>id.trim()).filter(Boolean).includes(current.id);}
async function review(request,env,current,route,api){
  if(!route.startsWith('review/'))return null;
  if(!isReviewer(env,current))throw new ApiError('editorial_reviewer_required',403);
  if(route==='review/submissions'&&request.method==='GET'){
    const rows=await all(env,"SELECT id,draft_id,owner_id,title,summary,status,submitted_at FROM study_submissions WHERE status!='withdrawn' ORDER BY submitted_at DESC LIMIT 200");
    return api.json(request,env,{submissions:rows.map(row=>({id:row.id,draftId:row.draft_id,ownerId:row.owner_id,title:row.title,summary:row.summary,status:row.status,submittedAt:row.submitted_at,published:false}))});
  }
  const match=route.match(/^review\/submissions\/([A-Za-z0-9_-]+)(?:\/(document))?$/);if(!match)return null;
  const row=await first(env,'SELECT * FROM study_submissions WHERE id=?',match[1]);if(!row||row.status==='withdrawn')throw new ApiError('submission_not_found',404);
  if(match[2]==='document'&&request.method==='GET'){
    if(!row.document_id||row.status==='withdrawn')throw new ApiError('document_not_uploaded',404);
    if(!env.STUDY_DOCUMENTS)throw new ApiError('document_storage_unavailable',503);
    const document=await first(env,"SELECT * FROM study_documents WHERE id=? AND state='ready'",row.document_id),stored=document?await env.STUDY_DOCUMENTS.get(document.object_key):null;
    if(!stored)throw new ApiError('document_unavailable',503);
    // Withdrawal/trash can revoke the review grant while R2 is being fetched.
    const latest=await first(env,"SELECT document_id FROM study_submissions WHERE id=? AND status<>'withdrawn'",row.id);
    if(!latest||latest.document_id!==row.document_id)throw new ApiError('submission_not_found',404);
    const headers=responseHeaders(request,env);headers.set('Content-Type','application/pdf');headers.set('Content-Disposition','attachment; filename="submitted-source.pdf"');headers.set('Cache-Control','private, no-store');
    return new Response(stored.body,{headers});
  }
  if(request.method==='GET')return api.json(request,env,{submission:{id:row.id,draftId:row.draft_id,title:row.title,summary:row.summary,body:row.body,status:row.status,submittedAt:row.submitted_at,fingerprint:row.fingerprint,documentAvailable:Boolean(row.document_id),published:false}});
  if(request.method==='POST'){
    const body=object(await readJson(request,6000),['decision','note'],['decision']);
    if(!['approved','rejected'].includes(body.decision)||row.status!=='submitted')throw new ApiError('invalid_review_transition',409);
    const note=text(body.note||'',4000),now=Date.now();
    await env.DB.batch([stmt(env,"UPDATE study_submissions SET status=?,reviewer_id=?,reviewed_at=?,review_note=? WHERE id=? AND status='submitted'",body.decision,current.id,now,note,row.id),stmt(env,'UPDATE study_drafts SET status=?,updated_at=? WHERE id=? AND submission_id=? AND EXISTS(SELECT 1 FROM study_submissions WHERE id=? AND status=? AND reviewer_id=? AND reviewed_at=?)',body.decision,now,row.draft_id,row.id,row.id,body.decision,current.id,now)]);
    const latest=await first(env,'SELECT status,reviewer_id,reviewed_at FROM study_submissions WHERE id=?',row.id);
    if(latest.status!==body.decision||latest.reviewer_id!==current.id||latest.reviewed_at!==now)throw new ApiError('invalid_review_transition',409);
    return api.json(request,env,{submission:{id:row.id,status:latest.status,published:false,editorialExportRequired:true}});
  }
  return null;
}
async function presentation(request,env,current,notebookId,api){
  const row=await api.member(env,notebookId,current.id),method=request.method;
  if(method==='GET')return api.json(request,env,{presentation:await notebookPresentation(env,notebookId)});
  if(!['owner','editor'].includes(row.role))throw new ApiError('presentation_presenter_required',403);
  const previous=await notebookPresentation(env,notebookId);
  if(previous&&previous.presenterId!==current.id&&row.role!=='owner')throw new ApiError('presentation_in_use',409);
  const allowed=`EXISTS(SELECT 1 FROM study_members m JOIN study_notebooks n ON n.id=m.notebook_id
    WHERE m.notebook_id=? AND m.account_id=? AND n.deleted_at IS NULL AND m.role IN ('owner','editor'))`;
  const owner=`EXISTS(SELECT 1 FROM study_members WHERE notebook_id=? AND account_id=? AND role='owner')`;
  if(method==='DELETE'){
    object(await readJson(request,256),[]);
    const result=await run(env,`DELETE FROM study_presentations WHERE notebook_id=? AND id=? AND ${allowed}
      AND (presenter_id=? OR ${owner})`,notebookId,previous?.id||'',notebookId,current.id,current.id,notebookId,current.id);
    if(!changed(result)){
      const latest=await api.member(env,notebookId,current.id);if(!['owner','editor'].includes(latest.role))throw new ApiError('presentation_presenter_required',403);
      if(await notebookPresentation(env,notebookId))throw new ApiError('presentation_in_use',409);
    }
    return api.json(request,env,{presentation:null});
  }
  const body=object(await readJson(request,256),['page']),page=api.pageNumber(body.page,row),now=Date.now();
  if(method==='PATCH'&&!previous)throw new ApiError('presentation_not_found',404);
  const id=previous?.id||crypto.randomUUID();
  let result;
  if(method==='PATCH')result=await run(env,`UPDATE study_presentations SET presenter_id=?,page=?,updated_at=?,expires_at=?
    WHERE notebook_id=? AND id=? AND expires_at>? AND ${allowed} AND (presenter_id=? OR ${owner})`,current.id,page,now,now+4*HOUR,notebookId,previous.id,now,notebookId,current.id,current.id,notebookId,current.id);
  else result=await run(env,`INSERT INTO study_presentations(notebook_id,id,presenter_id,page,created_at,updated_at,expires_at)
    SELECT ?,?,?,?,?,?,? WHERE ${allowed}
    ON CONFLICT(notebook_id) DO UPDATE SET
      id=CASE WHEN study_presentations.expires_at>? THEN study_presentations.id ELSE excluded.id END,
      presenter_id=excluded.presenter_id,page=excluded.page,updated_at=excluded.updated_at,expires_at=excluded.expires_at
    WHERE study_presentations.expires_at<=? OR study_presentations.presenter_id=? OR ${owner}
      OR NOT EXISTS(SELECT 1 FROM study_members WHERE notebook_id=study_presentations.notebook_id
        AND account_id=study_presentations.presenter_id AND role IN ('owner','editor'))`,notebookId,id,current.id,page,now,now,now+4*HOUR,notebookId,current.id,now,now,current.id,notebookId,current.id);
  if(!changed(result)){
    const latest=await api.member(env,notebookId,current.id);if(!['owner','editor'].includes(latest.role))throw new ApiError('presentation_presenter_required',403);
    throw new ApiError('presentation_in_use',409);
  }
  return api.json(request,env,{presentation:await notebookPresentation(env,notebookId)});
}

export async function libraryRoute(request,env,current,route,url,api){
  if(route==='usage'&&request.method==='GET')return api.json(request,env,{usage:await studyUsage(env,current.id),limits:{documentBytes:DOCUMENT_LIMIT,accountDocumentBytes:ACCOUNT_DOCUMENT_LIMIT}});
  if(route==='drafts'||route.startsWith('drafts/'))return drafts(request,env,current,route,api);
  if(route.startsWith('review/'))return review(request,env,current,route,api);
  const match=route.match(/^notebooks\/([A-Za-z0-9_-]+)(?:\/(copy|reset|restore|document|presentation))?$/);if(!match)return null;
  const [,id,action]=match,method=request.method;
  if(action==='copy'&&method==='POST')return duplicate(request,env,current,id,false,api);
  if(action==='reset'&&method==='POST')return duplicate(request,env,current,id,true,api);
  if(!action&&method==='DELETE')return trash(request,env,current,id,false,api);
  if(action==='restore'&&method==='POST')return trash(request,env,current,id,true,api);
  if(action==='document'&&method==='GET')return documentGet(request,env,current,id,api);
  if(action==='document'&&method==='POST')return documentPut(request,env,current,id,url,api);
  if(action==='presentation'&&['GET','POST','PATCH','DELETE'].includes(method))return presentation(request,env,current,id,api);
  return null;
}
export async function pruneLibrary(env){
  if(env.STUDY_DOCUMENTS){
    const expired=await all(env,"SELECT id FROM study_documents WHERE state='uploading' AND expires_at<? LIMIT 20",Date.now());
    for(const document of expired){await env.STUDY_DOCUMENTS.delete('pending/'+document.id+'.pdf');await run(env,"DELETE FROM study_documents WHERE id=? AND state='uploading'",document.id);}
  }
  await run(env,'DELETE FROM study_presentations WHERE expires_at<?',Date.now());
}
