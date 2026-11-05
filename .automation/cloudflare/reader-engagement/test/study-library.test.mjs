import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {randomBytes,generateKeyPairSync,createHash,sign} from 'node:crypto';
import {encodeCBOR} from '@levischuck/tiny-cbor';
import {Miniflare,Log,LogLevel} from 'miniflare';
import {sha256} from '../src/security.js';
import {studyRoute} from '../src/study.js';
const ROOT=dirname(dirname(fileURLToPath(import.meta.url))),ORIGIN='https://infant83.io',API='https://api.infant83.io/v1/study/';
const hash=data=>createHash('sha256').update(data).digest(),hex=data=>createHash('sha256').update(data).digest('hex'),b64=data=>Buffer.from(data).toString('base64url');
const stroke=id=>({id,color:'#2468ab',width:.003,points:[{x:.1,y:.2,p:.5}]}),put=id=>({type:'put',page:1,stroke:stroke(id)});
const pdf=Buffer.from('%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 600 800]>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF');
async function statements(db,name){const commands=[];let sql='';for(const line of(await readFile(join(ROOT,'migrations',name),'utf8')).split('\n')){const content=line.replace(/--.*$/,'').trim();if(!content)continue;sql+=content+'\n';if(/^CREATE TRIGGER\b/i.test(sql)?/^END;$/i.test(content):/;$/.test(content)){commands.push(db.prepare(sql));sql='';}}assert.equal(sql,'');return commands;}
function authenticator(options){const pair=generateKeyPairSync('ec',{namedCurve:'prime256v1'}),jwk=pair.publicKey.export({format:'jwk'}),credentialId=randomBytes(32),length=Buffer.alloc(2);length.writeUInt16BE(credentialId.length);
 const cose=new Map([[1,2],[3,-7],[-1,1],[-2,new Uint8Array(Buffer.from(jwk.x,'base64url'))],[-3,new Uint8Array(Buffer.from(jwk.y,'base64url'))]]),authData=Buffer.concat([hash(options.rp.id),Buffer.from([0x45]),Buffer.alloc(4),Buffer.alloc(16),length,credentialId,Buffer.from(encodeCBOR(cose))]);
 const clientData=Buffer.from(JSON.stringify({type:'webauthn.create',challenge:options.challenge,origin:ORIGIN,crossOrigin:false}));let counter=0;
 return{id:b64(credentialId),userHandle:options.user.id,registration:{id:b64(credentialId),rawId:b64(credentialId),type:'public-key',clientExtensionResults:{},response:{clientDataJSON:b64(clientData),attestationObject:b64(encodeCBOR(new Map([['fmt','none'],['attStmt',new Map()],['authData',new Uint8Array(authData)]]))),transports:['internal']}},
 authenticate(settings){const count=Buffer.alloc(4);count.writeUInt32BE(++counter);const auth=Buffer.concat([hash(settings.rpId),Buffer.from([5]),count]),client=Buffer.from(JSON.stringify({type:'webauthn.get',challenge:settings.challenge,origin:ORIGIN,crossOrigin:false}));return{id:b64(credentialId),rawId:b64(credentialId),type:'public-key',clientExtensionResults:{},response:{authenticatorData:b64(auth),clientDataJSON:b64(client),signature:b64(sign('sha256',Buffer.concat([auth,hash(client)]),pair.privateKey)),userHandle:options.user.id}};}};
}
async function fixture(t,{storage=true,through='9999',bindings={}}={}){
 const mf=new Miniflare({modules:true,scriptPath:join(ROOT,'.wrangler/test-worker.mjs'),compatibilityDate:'2026-08-06',d1Databases:['DB'],...(storage?{r2Buckets:['STUDY_DOCUMENTS']}:{}),bindings:{RATE_LIMIT_SALT:'x'.repeat(32),...bindings},log:new Log(LogLevel.ERROR)});t.after(()=>mf.dispose());
 const db=await mf.getD1Database('DB');for(const name of(await readdir(join(ROOT,'migrations'))).filter(n=>n.endsWith('.sql')&&n.slice(0,4)<=through).sort())await db.batch(await statements(db,name));
 const request=(path,{method='GET',body,bytes,cookie,headers={},origin=ORIGIN}={})=>mf.dispatchFetch(API+path,{method,headers:{...(origin?{Origin:origin}:{}),...(cookie?{Cookie:cookie}:{}),...(body!==undefined?{'Content-Type':'application/json'}:{}),...headers},...(body!==undefined?{body:JSON.stringify(body)}:{}),...(bytes?{body:bytes}:{})});
 const register=async(name='Learner')=>{const response=await request('auth/register/options',{method:'POST',body:{displayName:name}});assert.equal(response.status,200,await response.clone().text());const browser=authenticator((await response.json()).options),verify=await request('auth/register/verify',{method:'POST',body:{response:browser.registration},cookie:response.headers.get('Set-Cookie').split(';')[0]});assert.equal(verify.status,200,await verify.clone().text());return{...browser,account:(await verify.json()).account,cookie:verify.headers.get('Set-Cookie').split(';')[0]};};
 const synthetic=async(id,name=id)=>{const value=randomBytes(32).toString('base64url');await db.batch([db.prepare('INSERT INTO study_accounts(id,display_name,created_at) VALUES(?,?,1)').bind(id,name),db.prepare('INSERT INTO study_sessions(token_hash,account_id,expires_at) VALUES(?,?,?)').bind(await sha256(value),id,Date.now()+3600000)]);return{account:{id,displayName:name},cookie:'__Host-study_session='+value};};
 return{mf,db,request,register,synthetic,bucket:storage?await mf.getR2Bucket('STUDY_DOCUMENTS'):null};
}
async function notebook(f,a,extra={}){const response=await f.request('notebooks',{method:'POST',cookie:a.cookie,body:{publicId:null,title:'Personal study',fingerprint:hex(pdf),pageCount:2,...extra}});assert.equal(response.status,201,await response.clone().text());return(await response.json()).notebook;}
async function share(f,a,n,b,role){const invite=await(await f.request(`notebooks/${n.id}/invites`,{method:'POST',cookie:a.cookie,body:{role}})).json(),response=await f.request('invites/accept',{method:'POST',cookie:b.cookie,body:{token:invite.token}});assert.equal(response.status,200,await response.clone().text());}
async function reauth(f,a,browser=a){const options=await f.request('auth/reauth/options',{method:'POST',cookie:a.cookie,body:{}});assert.equal(options.status,200,await options.clone().text());const response=await f.request('auth/reauth/verify',{method:'POST',cookie:a.cookie+'; '+options.headers.get('Set-Cookie').split(';')[0],body:{response:browser.authenticate((await options.json()).options)}});assert.equal(response.status,200,await response.clone().text());return response.json();}
async function upload(f,a,n,bytes=pdf,extra={}){return f.request(`notebooks/${n.id}/document?size=${bytes.length}`,{method:'POST',cookie:a.cookie,bytes,headers:{'Content-Type':'application/pdf',...extra}});}

test('private documents stream to R2 with exact fingerprint, immutable original and per-request membership',async t=>{
 const f=await fixture(t),owner=await f.register('Owner'),viewer=await f.register('Reader'),other=await f.register('Other'),n=await notebook(f,owner);await share(f,owner,n,viewer,'viewer');
 const before=await(await f.request('me',{cookie:owner.cookie})).json();assert.equal(before.features.documentStorage,true);assert.equal(before.usage.documentBytes,0);
 assert.equal((await upload(f,viewer,n)).status,403);
 const uploaded=await upload(f,owner,n);assert.equal(uploaded.status,201,await uploaded.clone().text());const result=await uploaded.json();assert.equal(result.notebook.documentAvailable,true);assert.equal(result.usage.documentBytes,pdf.length);
 const read=await f.request(`notebooks/${n.id}/document`,{cookie:viewer.cookie});assert.equal(read.status,200);assert.equal(read.headers.get('Content-Type'),'application/pdf');assert.equal(read.headers.get('Cache-Control'),'private, no-store');assert.deepEqual(Buffer.from(await read.arrayBuffer()),pdf);
 assert.equal((await f.request(`notebooks/${n.id}/document`,{cookie:other.cookie})).status,404);assert.equal((await f.request(`notebooks/${n.id}/document`)).status,401);
 const altered=Buffer.from(pdf);altered[20]^=1;assert.equal((await upload(f,owner,n,altered)).status,409);assert.deepEqual(Buffer.from(await(await f.request(`notebooks/${n.id}/document`,{cookie:owner.cookie})).arrayBuffer()),pdf);
 assert.equal((await upload(f,owner,n)).status,200,'Verified identical retries reuse the immutable original');
 assert.equal((await f.bucket.list({prefix:'private/'})).objects.length,1);
 const env={DB:f.db,RATE_LIMIT_SALT:'x'.repeat(32),STUDY_DOCUMENTS:{get:async key=>{const object=await f.bucket.get(key);await f.db.prepare('DELETE FROM study_members WHERE notebook_id=? AND account_id=?').bind(n.id,viewer.account.id).run();return object;}}};
 await assert.rejects(studyRoute(new Request(API+`notebooks/${n.id}/document`,{headers:{Origin:ORIGIN,Cookie:viewer.cookie}}),env),error=>error.status===404);
});

test('document size/hash/magic/quota checks reject uploads and missing storage fails immediately',async t=>{
 const f=await fixture(t),owner=await f.register(),wrong=await notebook(f,owner,{fingerprint:'b'.repeat(64)});
 assert.equal((await upload(f,owner,wrong)).status,409);
 assert.equal((await f.db.prepare('SELECT count(*) n FROM study_documents').first()).n,0);assert.equal((await f.bucket.list()).objects.length,0);
 assert.equal((await f.request(`notebooks/${wrong.id}/document?size=52428801`,{method:'POST',cookie:owner.cookie,bytes:pdf,headers:{'Content-Type':'application/pdf'}})).status,413);
 const nonpdf=Buffer.from('hello not a PDF'),invalid=await notebook(f,owner,{fingerprint:hex(nonpdf)});assert.equal((await upload(f,owner,invalid,nonpdf)).status,400);
 const n=await notebook(f,owner);for(let i=0;i<10;i++)await f.db.prepare("INSERT INTO study_documents(id,owner_id,fingerprint,object_key,byte_size,state,created_at) VALUES(?,?,?,?,52428800,'ready',1)").bind('quota-'+i,owner.account.id,hex('quota-'+i),'quota/'+i).run();
 assert.equal((await upload(f,owner,n)).status,413);assert.equal((await f.bucket.list()).objects.length,0);
 const off=await fixture(t,{storage:false}),a=await off.register(),note=await notebook(off,a);assert.equal((await(await off.request('me',{cookie:a.cookie})).json()).features.documentStorage,false);assert.equal((await upload(off,a,note)).status,503);
});

test('all reading roles can create independent copies or fresh study notebooks without changing the shared source',async t=>{
 const f=await fixture(t),owner=await f.register('Source owner'),viewer=await f.register('Viewer'),n=await notebook(f,owner);await share(f,owner,n,viewer,'viewer');
 await f.request(`notebooks/${n.id}/operations`,{method:'POST',cookie:owner.cookie,body:{operations:[put('source-ink')],position:{page:2}}});assert.equal((await upload(f,owner,n)).status,201);
 const source=await(await f.request(`notebooks/${n.id}`,{cookie:owner.cookie})).json();
 const copied=await f.request(`notebooks/${n.id}/copy`,{method:'POST',cookie:viewer.cookie,body:{title:'My independent copy'}});assert.equal(copied.status,201,await copied.clone().text());const copy=(await copied.json()).notebook;
 assert.equal(copy.ownerId,viewer.account.id);assert.equal(copy.ownerName,'Viewer');assert.equal(copy.role,'owner');assert.equal(copy.documentAvailable,false);
 const ownCopy=await(await f.request(`notebooks/${copy.id}`,{cookie:viewer.cookie})).json();assert.equal(ownCopy.pages[0].strokes.length,1);assert.notEqual(ownCopy.pages[0].strokes[0].id,'source-ink');assert.equal((await f.request(`notebooks/${copy.id}`,{cookie:owner.cookie})).status,404);
 const reset=await f.request(`notebooks/${n.id}/reset`,{method:'POST',cookie:viewer.cookie,body:{}});assert.equal(reset.status,201,await reset.clone().text());const blank=(await reset.json()).notebook;assert.equal((await(await f.request(`notebooks/${blank.id}`,{cookie:viewer.cookie})).json()).pages.length,0);
 const ownerCopy=(await(await f.request(`notebooks/${n.id}/copy`,{method:'POST',cookie:owner.cookie,body:{}})).json()).notebook;assert.equal(ownerCopy.documentAvailable,true);assert.deepEqual(Buffer.from(await(await f.request(`notebooks/${ownerCopy.id}/document`,{cookie:owner.cookie})).arrayBuffer()),pdf);
 assert.deepEqual((await(await f.request(`notebooks/${n.id}`,{cookie:owner.cookie})).json()).pages,source.pages);
 assert.equal((await f.request(`notebooks/${n.id}`,{method:'DELETE',cookie:viewer.cookie,body:{}})).status,403);
 assert.equal((await f.request(`notebooks/${n.id}`,{method:'DELETE',cookie:owner.cookie,body:{}})).status,200);assert.equal((await f.request(`notebooks/${n.id}`,{cookie:viewer.cookie})).status,404);
 const list=await(await f.request('notebooks?includeDeleted=1',{cookie:owner.cookie})).json();assert.ok(list.notebooks.find(item=>item.id===n.id).deletedAt);
 assert.equal((await f.request(`notebooks/${n.id}/restore`,{method:'POST',cookie:owner.cookie,body:{}})).status,200);assert.deepEqual((await(await f.request(`notebooks/${n.id}`,{cookie:viewer.cookie})).json()).pages,source.pages);
});

test('trash blocks unused invitations and the active notebook quota is atomic on restore',async t=>{
 const f=await fixture(t),owner=await f.register(),recipient=await f.register(),n=await notebook(f,owner);
 const invite=(await(await f.request(`notebooks/${n.id}/invites`,{method:'POST',cookie:owner.cookie,body:{role:'viewer'}})).json()).token;
 await f.request(`notebooks/${n.id}`,{method:'DELETE',cookie:owner.cookie,body:{}});
 assert.equal((await f.request('invites/preview',{method:'POST',cookie:recipient.cookie,body:{token:invite}})).status,410);
 assert.equal((await f.request('invites/accept',{method:'POST',cookie:recipient.cookie,body:{token:invite}})).status,410);
 assert.equal((await f.db.prepare('SELECT count(*) n FROM study_members WHERE notebook_id=? AND account_id=?').bind(n.id,recipient.account.id).first()).n,0);
 const seeded=Array.from({length:100},(_,i)=>f.db.prepare('INSERT INTO study_notebooks(id,owner_id,title,fingerprint,page_count,created_at,updated_at) VALUES(?,?,?,?,2,1,1)').bind('capacity-'+i,owner.account.id,'Capacity fixture',hex('capacity-'+i)));await f.db.batch(seeded);
 assert.equal((await f.request(`notebooks/${n.id}/restore`,{method:'POST',cookie:owner.cookie,body:{}})).status,413);
 await assert.rejects(f.db.prepare('UPDATE study_notebooks SET deleted_at=NULL WHERE id=?').bind(n.id).run(),/study_notebook_quota/,'Database rejects a stale or bypassed restore over the active quota');
 assert.ok((await f.db.prepare('SELECT deleted_at FROM study_notebooks WHERE id=?').bind(n.id).first()).deleted_at);
 await f.db.prepare('UPDATE study_notebooks SET deleted_at=1 WHERE id=?').bind('capacity-0').run();
 assert.equal((await f.request(`notebooks/${n.id}/restore`,{method:'POST',cookie:owner.cookie,body:{}})).status,200);
 assert.equal((await f.request('invites/accept',{method:'POST',cookie:recipient.cookie,body:{token:invite}})).status,200,'Unused invitation is available again only after its owner restores the source');
});

test('additional passkeys require existing-key UV and remain attached to the same account',async t=>{
 const f=await fixture(t),owner=await f.register('Existing learner');
 assert.equal((await f.request('auth/credential/options',{method:'POST',cookie:owner.cookie,body:{label:'Backup'}})).status,403);
 await reauth(f,owner);
 const options=await f.request('auth/credential/options',{method:'POST',cookie:owner.cookie,body:{label:'Backup'}});assert.equal(options.status,200,await options.clone().text());const settings=(await options.json()).options;assert.equal(settings.user.id,owner.userHandle);assert.equal(settings.excludeCredentials[0].id,owner.id);
 const second=authenticator(settings),added=await f.request('auth/credential/verify',{method:'POST',cookie:owner.cookie+'; '+options.headers.get('Set-Cookie').split(';')[0],body:{response:second.registration}});assert.equal(added.status,200,await added.clone().text());assert.equal((await added.json()).account.id,owner.account.id);assert.equal((await f.db.prepare('SELECT count(*) n FROM study_accounts').first()).n,1);
 const login=await f.request('auth/login/options',{method:'POST',body:{}}),verified=await f.request('auth/login/verify',{method:'POST',cookie:login.headers.get('Set-Cookie').split(';')[0],body:{response:second.authenticate((await login.json()).options)}});assert.equal(verified.status,200,await verified.clone().text());assert.equal((await verified.json()).account.id,owner.account.id);
 const list=await(await f.request('credentials',{cookie:owner.cookie})).json();assert.equal(list.credentials.length,2);assert.ok(list.credentials.some(key=>key.label==='Backup'));
 await reauth(f,owner);assert.equal((await f.request('credentials/'+second.id,{method:'DELETE',cookie:owner.cookie,body:{}})).status,200);
 await reauth(f,owner);assert.equal((await f.request('credentials/'+owner.id,{method:'DELETE',cookie:owner.cookie,body:{}})).status,409);assert.equal((await f.db.prepare('SELECT count(*) n FROM study_credentials').first()).n,1);
});

test('drafts and reviewed submission snapshots stay private, immutable and separate from publication',async t=>{
 const f=await fixture(t,{bindings:{STUDY_REVIEWER_ACCOUNT_IDS:'editorial-reviewer'}}),owner=await f.register('Author'),other=await f.register('Other'),reviewer=await f.synthetic('editorial-reviewer');
 const made=await f.request('drafts',{method:'POST',cookie:owner.cookie,body:{title:'A personal note',summary:'Short summary',body:'Original private text',notebookId:null}});assert.equal(made.status,201,await made.clone().text());let draft=(await made.json()).draft;
 assert.equal((await f.request('drafts/'+draft.id,{cookie:other.cookie})).status,404);assert.equal((await f.request('review/submissions',{cookie:owner.cookie})).status,403);
 assert.equal((await f.request(`drafts/${draft.id}/submit`,{method:'POST',cookie:owner.cookie,body:{rightsConfirmed:false}})).status,400);
 const submitted=await f.request(`drafts/${draft.id}/submit`,{method:'POST',cookie:owner.cookie,body:{rightsConfirmed:true}});assert.equal(submitted.status,201,await submitted.clone().text());const submission=(await submitted.json()).submission;assert.equal(submission.published,false);
 assert.equal((await f.request('drafts/'+draft.id,{method:'PATCH',cookie:owner.cookie,body:{body:'Changed while pending'}})).status,409);
 const reviewed=await(await f.request('review/submissions/'+submission.id,{cookie:reviewer.cookie})).json();assert.equal(reviewed.submission.body,'Original private text');
 const accepted=await f.request('review/submissions/'+submission.id,{method:'POST',cookie:reviewer.cookie,body:{decision:'approved',note:'Ready for separate editorial export'}});assert.equal(accepted.status,200,await accepted.clone().text());assert.equal((await accepted.json()).submission.published,false);
 assert.equal((await f.request('drafts/'+draft.id,{method:'PATCH',cookie:owner.cookie,body:{body:'A new revision'}})).status,200);assert.equal((await(await f.request('review/submissions/'+submission.id,{cookie:reviewer.cookie})).json()).submission.body,'Original private text');
 const next=await(await f.request(`drafts/${draft.id}/submit`,{method:'POST',cookie:owner.cookie,body:{rightsConfirmed:true}})).json();assert.notEqual(next.submission.id,submission.id);
 assert.equal((await f.request(`drafts/${draft.id}/withdraw`,{method:'POST',cookie:owner.cookie,body:{}})).status,200);assert.equal((await f.request('review/submissions/'+next.submission.id,{cookie:reviewer.cookie})).status,404);
 assert.equal((await f.db.prepare('SELECT count(*) n FROM articles').first()).n,0,'Approval cannot create a public article or notification');
});

test('presentation pages are opt-in metadata and do not overwrite any member reading position',async t=>{
 const f=await fixture(t),owner=await f.register('Presenter'),viewer=await f.register('Student'),editor=await f.register('Co-editor'),n=await notebook(f,owner);await share(f,owner,n,viewer,'viewer');await share(f,owner,n,editor,'editor');
 assert.equal((await f.request(`notebooks/${n.id}/presentation`,{method:'POST',cookie:viewer.cookie,body:{page:2}})).status,403);
 const started=await f.request(`notebooks/${n.id}/presentation`,{method:'POST',cookie:owner.cookie,body:{page:2}});assert.equal(started.status,200,await started.clone().text());assert.equal((await started.json()).presentation.presenterName,'Presenter');
 assert.equal((await f.request(`notebooks/${n.id}/presentation`,{method:'POST',cookie:editor.cookie,body:{page:1}})).status,409);
 const followed=await(await f.request(`notebooks/${n.id}/pages?since=0&follow=1`,{cookie:viewer.cookie})).json();assert.equal(followed.presentation.page,2);assert.equal((await(await f.request(`notebooks/${n.id}`,{cookie:viewer.cookie})).json()).position.page,1);
 assert.equal((await f.request(`notebooks/${n.id}/presentation`,{method:'DELETE',cookie:owner.cookie,body:{}})).status,200);
 assert.equal((await f.request(`notebooks/${n.id}/presentation`,{method:'POST',cookie:editor.cookie,body:{page:2}})).status,200);
 await f.request(`notebooks/${n.id}/members/${editor.account.id}`,{method:'PATCH',cookie:owner.cookie,body:{role:'viewer'}});assert.equal((await(await f.request(`notebooks/${n.id}/presentation`,{cookie:viewer.cookie})).json()).presentation,null);
});

test('presentation writes atomically reject stale editor grants and competing presenter takeovers',async t=>{
 const f=await fixture(t),owner=await f.register('Owner'),editor=await f.register('Editor'),other=await f.register('Other editor'),n=await notebook(f,owner);await share(f,owner,n,editor,'editor');await share(f,owner,n,other,'editor');
 const route=`notebooks/${n.id}/presentation`;
 const intercepted=action=>{
   let fired=false;
   const wrap=(statement,sql)=>new Proxy(statement,{get(target,key){if(key==='bind')return(...args)=>wrap(target.bind(...args),sql);if(key==='run')return async()=>{if(!fired&&/^(?:DELETE FROM|UPDATE|INSERT INTO) study_presentations/.test(sql.trim())){fired=true;await action();}return target.run();};const value=target[key];return typeof value==='function'?value.bind(target):value;}});
   return{DB:{prepare:sql=>wrap(f.db.prepare(sql),sql),batch:commands=>f.db.batch(commands)},RATE_LIMIT_SALT:'x'.repeat(32)};
 };
 for(const method of ['DELETE','PATCH']){
   await f.db.prepare("UPDATE study_members SET role='editor' WHERE notebook_id=? AND account_id=?").bind(n.id,editor.account.id).run();
   await f.db.prepare('DELETE FROM study_presentations WHERE notebook_id=?').bind(n.id).run();
   assert.equal((await f.request(route,{method:'POST',cookie:editor.cookie,body:{page:1}})).status,200);
   const env=intercepted(async()=>{await f.db.batch([f.db.prepare("UPDATE study_members SET role='viewer' WHERE notebook_id=? AND account_id=?").bind(n.id,editor.account.id),f.db.prepare('UPDATE study_presentations SET id=?,presenter_id=?,page=2 WHERE notebook_id=?').bind('owner-session-'+method,owner.account.id,n.id)]);});
   await assert.rejects(studyRoute(new Request(API+route,{method,headers:{Origin:ORIGIN,Cookie:editor.cookie,'Content-Type':'application/json'},body:JSON.stringify(method==='PATCH'?{page:1}:{})}),env),error=>error.status===403);
   const active=await f.db.prepare('SELECT id,presenter_id,page FROM study_presentations WHERE notebook_id=?').bind(n.id).first();assert.deepEqual(active,{id:'owner-session-'+method,presenter_id:owner.account.id,page:2});
 }
 await f.db.prepare("UPDATE study_members SET role='editor' WHERE notebook_id=? AND account_id=?").bind(n.id,editor.account.id).run();await f.db.prepare('DELETE FROM study_presentations WHERE notebook_id=?').bind(n.id).run();
 const env=intercepted(async()=>{await f.db.prepare('INSERT INTO study_presentations VALUES(?,?,?,?,?,?,?)').bind(n.id,'first-editor-session',other.account.id,2,Date.now(),Date.now(),Date.now()+3600000).run();});
 await assert.rejects(studyRoute(new Request(API+route,{method:'POST',headers:{Origin:ORIGIN,Cookie:editor.cookie,'Content-Type':'application/json'},body:JSON.stringify({page:1})}),env),error=>error.status===409);
 assert.equal((await f.db.prepare('SELECT presenter_id FROM study_presentations WHERE notebook_id=?').bind(n.id).first()).presenter_id,other.account.id);
 await f.db.prepare("UPDATE study_members SET role='viewer' WHERE notebook_id=? AND account_id=?").bind(n.id,other.account.id).run();
 assert.equal((await f.request(route,{method:'POST',cookie:editor.cookie,body:{page:1}})).status,200,'A valid editor can reclaim a hidden presentation from a revoked presenter');
 assert.equal((await f.db.prepare('SELECT presenter_id FROM study_presentations WHERE notebook_id=?').bind(n.id).first()).presenter_id,editor.account.id);
});

test('review document responses recheck withdrawal and trash after the private R2 read',async t=>{
 const f=await fixture(t,{bindings:{STUDY_REVIEWER_ACCOUNT_IDS:'editorial-reviewer'}}),owner=await f.register('Author'),reviewer=await f.synthetic('editorial-reviewer'),n=await notebook(f,owner);assert.equal((await upload(f,owner,n)).status,201);
 for(const action of ['withdraw','trash']){
   const draft=(await(await f.request('drafts',{method:'POST',cookie:owner.cookie,body:{title:'Private source',body:'Review text',notebookId:n.id}})).json()).draft;
   const submission=(await(await f.request(`drafts/${draft.id}/submit`,{method:'POST',cookie:owner.cookie,body:{rightsConfirmed:true}})).json()).submission;
   assert.deepEqual(Buffer.from(await(await f.request(`review/submissions/${submission.id}/document`,{cookie:reviewer.cookie})).arrayBuffer()),pdf);
   const env={DB:f.db,RATE_LIMIT_SALT:'x'.repeat(32),STUDY_REVIEWER_ACCOUNT_IDS:'editorial-reviewer',STUDY_DOCUMENTS:{get:async key=>{const stored=await f.bucket.get(key);const response=await f.request(action==='trash'?`notebooks/${n.id}`:`drafts/${draft.id}/withdraw`,{method:action==='trash'?'DELETE':'POST',cookie:owner.cookie,body:{}});assert.equal(response.status,200);return stored;}}};
   await assert.rejects(studyRoute(new Request(API+`review/submissions/${submission.id}/document`,{headers:{Origin:ORIGIN,Cookie:reviewer.cookie}}),env),error=>error.status===404);
 }
});

test('library migration preserves populated legacy rows, child grants and counters and rolls back a failed rebuild',async t=>{
 const f=await fixture(t,{through:'0005',storage:false}),db=f.db;
 await db.batch([db.prepare("INSERT INTO study_accounts VALUES('legacy-owner','Owner',1),('legacy-reader','Reader',1),('legacy-editor','Editor',1),('legacy-add','Contributor',1)"),db.prepare("INSERT INTO study_notebooks(id,owner_id,title,fingerprint,page_count,created_at,updated_at) VALUES('legacy-note','legacy-owner','Before upgrade',?,2,1,1)").bind('a'.repeat(64)),db.prepare("INSERT INTO study_members(notebook_id,account_id,role,joined_at) VALUES('legacy-note','legacy-owner','owner',1),('legacy-note','legacy-reader','viewer',2),('legacy-note','legacy-editor','editor',3),('legacy-note','legacy-add','contributor',4)"),db.prepare("INSERT INTO study_strokes(notebook_id,page,id,data,deleted,updated_at,author_id,actor_id) VALUES('legacy-note',1,'original-ink',?,0,1,'legacy-owner','legacy-owner')").bind(JSON.stringify(stroke('original-ink'))),db.prepare("INSERT INTO study_invites(token_hash,notebook_id,created_by,expires_at,role) VALUES('private-hash','legacy-note','legacy-owner',9999999999999,'viewer')"),db.prepare("INSERT INTO study_credentials(id,account_id,public_key,user_handle,created_at) VALUES('legacy-key','legacy-owner','synthetic-public-key','synthetic-user-handle',1)"),db.prepare("INSERT INTO study_sessions(token_hash,account_id,expires_at) VALUES('synthetic-session-hash','legacy-owner',9999999999999)"),db.prepare("INSERT INTO study_challenges(token_hash,kind,challenge,origin,rp_id,account_id,expires_at) VALUES('synthetic-challenge-hash','login','synthetic-challenge','https://infant83.io','infant83.io','legacy-owner',9999999999999)")]);
 const tables=['study_accounts','study_credentials','study_sessions','study_challenges','study_notebooks','study_members','study_strokes','study_changes','study_invites'],before={};for(const table of tables)before[table]=(await db.prepare('SELECT * FROM '+table).all()).results;
 const commands=await statements(db,'0006_study_library.sql');await assert.rejects(db.batch([...commands,db.prepare('INSERT INTO deliberately_missing_audit_table VALUES(1)')]));
 for(const table of tables)assert.deepEqual((await db.prepare('SELECT * FROM '+table).all()).results,before[table]);
 await db.batch(await statements(db,'0006_study_library.sql'));
 for(const table of tables){const columns=Object.keys(before[table][0]);assert.deepEqual((await db.prepare('SELECT '+columns.join(',')+' FROM '+table).all()).results,before[table]);}
 assert.deepEqual((await db.prepare('PRAGMA foreign_key_check').all()).results,[]);assert.equal((await db.prepare("SELECT count(*) n FROM sqlite_master WHERE name LIKE '%backup_0006'").first()).n,0);
 await db.prepare("INSERT INTO study_notebooks(id,owner_id,title,fingerprint,page_count,created_at,updated_at) VALUES('independent-copy','legacy-owner','Second study',?,2,3,3)").bind('a'.repeat(64)).run();
 assert.equal((await db.prepare("SELECT count(*) n FROM study_notebooks WHERE owner_id='legacy-owner'").first()).n,2);
});
