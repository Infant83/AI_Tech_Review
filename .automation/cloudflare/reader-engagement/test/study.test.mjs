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

const ROOT=dirname(dirname(fileURLToPath(import.meta.url)));
const ORIGIN='https://infant83.io';
const API='https://api.infant83.io';
const hash=data=>createHash('sha256').update(data).digest();
const b64=data=>Buffer.from(data).toString('base64url');
const pref='/v1/study/';
const stroke=(id='stroke-a')=>({id,color:'#182b35',width:0.002,points:[{x:0.1,y:0.2,p:0.5},{x:0.8,y:0.7,p:0.7}]});
const put=(id,page=1)=>({type:'put',page,stroke:stroke(id)});
const erase=(id,page=1)=>({type:'delete',page,id});

async function fixture(t,beforePermissions=null) {
  const mf=new Miniflare({modules:true,scriptPath:join(ROOT,'.wrangler/test-worker.mjs'),compatibilityDate:'2026-08-06',
    d1Databases:['DB'],bindings:{RATE_LIMIT_SALT:randomBytes(32).toString('hex')},log:new Log(LogLevel.ERROR)});
  t.after(()=>mf.dispose());
  const db=await mf.getD1Database('DB');
  for(const name of (await readdir(join(ROOT,'migrations'))).filter(n=>n.endsWith('.sql')).sort()) {
    if(name.startsWith('0005_')&&beforePermissions) await beforePermissions(db);
    const statements=[];let sql='';
    for(const line of (await readFile(join(ROOT,'migrations',name),'utf8')).split('\n')) {
      const content=line.replace(/--.*$/,'').trim();if(!content)continue;sql+=content+'\n';
      if(/^CREATE TRIGGER\b/i.test(sql)?/^END;$/i.test(content):/;$/.test(content)){statements.push(db.prepare(sql));sql='';}
    }
    assert.equal(sql,'');await db.batch(statements);
  }
  await db.prepare("INSERT INTO articles(id,path,title,published_at,topic,created_at,updated_at) VALUES('lecture:2026-11-04-test-notes','/AI_Tech_Review/archive/files/2026-11-04-test-notes.pdf','Test','2026-11-04','lecture',1,1)").run();
  const request=(path,{method='GET',body,cookie,origin=ORIGIN}={})=>{
    const headers={'CF-Connecting-IP':'192.0.2.10'};
    if(origin!==null)headers.Origin=origin;
    if(cookie)headers.Cookie=cookie;
    if(body!==undefined)headers['Content-Type']='application/json';
    return mf.dispatchFetch(API+pref+path,{method,headers,...(body===undefined?{}:{body:JSON.stringify(body)})});
  };
  const register=async(name='Learner')=>{
    const options=await request('auth/register/options',{method:'POST',body:{displayName:name}});
    assert.equal(options.status,200,await options.clone().text());
    const settings=(await options.json()).options;
    const browser=authenticator(settings);
    const response=await request('auth/register/verify',{method:'POST',body:{response:browser.registration},cookie:options.headers.get('Set-Cookie').split(';')[0]});
    assert.equal(response.status,200,await response.clone().text());
    const body=await response.json();
    return {...browser,account:body.account,cookie:response.headers.get('Set-Cookie').split(';')[0],rawCookie:response.headers.get('Set-Cookie')};
  };
  return {mf,db,request,register};
}

async function share(f,owner,notebook,guest,role) {
  const issued=await f.request(`notebooks/${notebook.id}/invites`,{method:'POST',cookie:owner.cookie,body:{role}});
  assert.equal(issued.status,201,await issued.clone().text());
  const invitation=await issued.json();assert.equal(invitation.role,role);
  const accepted=await f.request('invites/accept',{method:'POST',cookie:guest.cookie,body:{token:invitation.token}});
  assert.equal(accepted.status,200,await accepted.clone().text());
  return (await accepted.json()).notebook;
}

async function counters(f,notebookId) {
  const row=await f.db.prepare(`SELECT stroke_count,ink_bytes,
    (SELECT count(*) FROM study_strokes WHERE notebook_id=study_notebooks.id) actual_rows,
    (SELECT COALESCE(sum(length(data)),0) FROM study_strokes WHERE notebook_id=study_notebooks.id) actual_bytes
    FROM study_notebooks WHERE id=?`).bind(notebookId).first();
  assert.equal(row.stroke_count,row.actual_rows);assert.equal(row.ink_bytes,row.actual_bytes);
  return row;
}

function authenticator(options) {
  const pair=generateKeyPairSync('ec',{namedCurve:'prime256v1'});
  const jwk=pair.publicKey.export({format:'jwk'}),credentialId=randomBytes(32);
  const cose=new Map([[1,2],[3,-7],[-1,1],[-2,new Uint8Array(Buffer.from(jwk.x,'base64url'))],[-3,new Uint8Array(Buffer.from(jwk.y,'base64url'))]]);
  const length=Buffer.alloc(2);length.writeUInt16BE(credentialId.length);
  const authData=Buffer.concat([hash(options.rp.id),Buffer.from([0x45]),Buffer.alloc(4),Buffer.alloc(16),length,credentialId,Buffer.from(encodeCBOR(cose))]);
  const clientData=Buffer.from(JSON.stringify({type:'webauthn.create',challenge:options.challenge,origin:ORIGIN,crossOrigin:false}));
  const registration={id:b64(credentialId),rawId:b64(credentialId),type:'public-key',clientExtensionResults:{},
    response:{clientDataJSON:b64(clientData),attestationObject:b64(encodeCBOR(new Map([['fmt','none'],['attStmt',new Map()],['authData',new Uint8Array(authData)]]))),transports:['internal']}};
  let counter=0;
  return {registration,userHandle:options.user.id,authenticate(settings,{origin=ORIGIN,uv=true,corrupt=false}={}) {
    const count=Buffer.alloc(4);count.writeUInt32BE(++counter);
    const auth=Buffer.concat([hash(settings.rpId),Buffer.from([uv?5:1]),count]);
    const client=Buffer.from(JSON.stringify({type:'webauthn.get',challenge:settings.challenge,origin,crossOrigin:false}));
    const signature=sign('sha256',Buffer.concat([auth,hash(client)]),pair.privateKey);
    if(corrupt)signature[signature.length-1]^=1;
    return {id:b64(credentialId),rawId:b64(credentialId),type:'public-key',clientExtensionResults:{},
      response:{authenticatorData:b64(auth),clientDataJSON:b64(client),signature:b64(signature),userHandle:options.user.id}};
  }};
}

async function create(f,current,extra={}) {
  const response=await f.request('notebooks',{method:'POST',cookie:current.cookie,body:{publicId:'2026-11-04-test-notes',title:'Private lecture study',fingerprint:'a'.repeat(64),pageCount:114,...extra}});
  assert.equal(response.status,201,await response.clone().text());
  return (await response.json()).notebook;
}

test('WebAuthn registration and signed cross-device login require UV, origin and one-use browser-bound challenge',async t=>{
  const f=await fixture(t),current=await f.register('Passkey learner');
  for(const part of ['HttpOnly','Secure','SameSite=Strict','Path=/','Max-Age=2592000'])assert.ok(current.rawCookie.includes(part));
  const sessions=await f.db.prepare('SELECT * FROM study_sessions').all();
  assert.equal(sessions.results[0].token_hash,await sha256(current.cookie.split('=')[1]));
  assert.equal(JSON.stringify(sessions).includes(current.cookie.split('=')[1]),false);
  assert.equal((await (await f.request('me',{cookie:current.cookie})).json()).account.displayName,'Passkey learner');
  assert.equal((await f.request('me',{cookie:current.cookie,origin:'https://evil.example'})).status,403);
  assert.equal((await f.request('me',{cookie:current.cookie,origin:null})).status,403);
  for(const invalid of [{origin:'https://evil.example'},{uv:false},{corrupt:true}]) {
    const options=await f.request('auth/login/options',{method:'POST',body:{}}),body=await options.json();
    const assertion=current.authenticate(body.options,invalid);
    const noBinding=await f.request('auth/login/verify',{method:'POST',body:{response:assertion}});
    assert.equal(noBinding.status,401);
    const rejected=await f.request('auth/login/verify',{method:'POST',cookie:options.headers.get('Set-Cookie').split(';')[0],body:{response:assertion}});
    assert.equal(rejected.status,401);
  }
  const options=await f.request('auth/login/options',{method:'POST',body:{}}),settings=(await options.json()).options;
  const challengeCookie=options.headers.get('Set-Cookie').split(';')[0],body={response:current.authenticate(settings)};
  const signed=await f.request('auth/login/verify',{method:'POST',cookie:challengeCookie,body});
  assert.equal(signed.status,200,await signed.clone().text());
  assert.equal((await signed.json()).account.id,current.account.id);
  assert.equal((await f.request('auth/login/verify',{method:'POST',cookie:challengeCookie,body})).status,401);
  const logout=await f.request('logout',{method:'POST',cookie:current.cookie,body:{}});
  assert.equal(logout.status,200);
  assert.equal((await (await f.request('me',{cookie:current.cookie})).json()).account,null);
});

test('private notebook authorization, catalog validation and per-account reading state',async t=>{
  const f=await fixture(t),a=await f.register('Owner'),b=await f.register('Other');
  const notebook=await create(f,a);
  assert.equal(notebook.role,'owner');
  const bad=await f.request('notebooks',{method:'POST',cookie:a.cookie,body:{publicId:'2026-11-04-not-in-catalog',title:'Bad',fingerprint:'b'.repeat(64),pageCount:1}});
  assert.equal(bad.status,404);
  assert.equal((await f.request(`notebooks/${notebook.id}`,{cookie:b.cookie})).status,404);
  assert.equal((await f.request(`notebooks/${notebook.id}/pages`,{cookie:b.cookie})).status,404);
  assert.equal((await f.request(`notebooks/${notebook.id}/operations`,{method:'POST',cookie:b.cookie,body:{operations:[put('x')]}})).status,404);
  assert.equal((await f.request('notebooks')).status,401);
  assert.equal((await (await f.request('notebooks',{cookie:b.cookie})).json()).notebooks.length,0);
  const written=await f.request(`notebooks/${notebook.id}/operations`,{method:'POST',cookie:a.cookie,body:{operations:[put('first')],position:{page:22},bookmarks:[22,4,22]}});
  assert.equal(written.status,200,await written.clone().text());
  const snapshot=await (await f.request(`notebooks/${notebook.id}`,{cookie:a.cookie})).json();
  assert.equal(snapshot.pages[0].strokes[0].id,'first');
  assert.deepEqual(snapshot.position,{page:22});assert.deepEqual(snapshot.bookmarks,[4,22]);
  assert.equal((await f.request(`notebooks/${notebook.id}/operations`,{method:'POST',cookie:a.cookie,body:{operations:[put('bad',115)]}})).status,400);
  const invalid=put('bad');invalid.stroke.points[0].x=2;
  assert.equal((await f.request(`notebooks/${notebook.id}/operations`,{method:'POST',cookie:a.cookie,body:{operations:[invalid]}})).status,400);
});

test('single-use shared-account invitations grant editing, concurrent ink survives and erasure cannot be resurrected',async t=>{
  const f=await fixture(t),a=await f.register('Owner'),b=await f.register('Editor'),c=await f.register('Outsider');
  const n=await create(f,a),path=`notebooks/${n.id}`;
  const invitation=await (await f.request(path+'/invites',{method:'POST',cookie:a.cookie,body:{role:'editor'}})).json();
  assert.equal(JSON.stringify(await f.db.prepare('SELECT * FROM study_invites').all()).includes(invitation.token),false);
  assert.equal((await f.request('invites/accept',{method:'POST',cookie:b.cookie,body:{token:invitation.token}})).status,200);
  assert.equal((await f.request('invites/accept',{method:'POST',cookie:c.cookie,body:{token:invitation.token}})).status,410);
  assert.equal((await f.request(path+'/invites',{method:'POST',cookie:b.cookie,body:{}})).status,403);
  const writes=await Promise.all([a,b].map((current,i)=>f.request(path+'/operations',{method:'POST',cookie:current.cookie,body:{operations:[put(`concurrent-${i}`)],position:{page:i+1},bookmarks:[i+1]}})));
  assert.deepEqual(writes.map(r=>r.status),[200,200]);
  const initial=await (await f.request(path,{cookie:a.cookie})).json();
  assert.equal(initial.pages[0].strokes.length,2);
  await f.request(path+'/operations',{method:'POST',cookie:b.cookie,body:{operations:[erase('concurrent-0'),erase('future-stale')]}});
  await f.request(path+'/operations',{method:'POST',cookie:a.cookie,body:{operations:[put('concurrent-0'),put('future-stale')]}});
  const after=await (await f.request(path,{cookie:a.cookie})).json();
  assert.deepEqual(after.pages[0].strokes.map(s=>s.id),['concurrent-1']);
  assert.deepEqual(after.deleted.map(s=>s.id).sort(),['concurrent-0','future-stale']);
  const revision=after.notebook.revision;
  await f.request(path+'/operations',{method:'POST',cookie:a.cookie,body:{operations:[put('concurrent-1'),erase('concurrent-0')]}});
  const same=await (await f.request(path,{cookie:a.cookie})).json();assert.equal(same.notebook.revision,revision);
  const delta=await (await f.request(path+`/pages?since=${initial.notebook.revision}`,{cookie:b.cookie})).json();
  assert.deepEqual(delta.changes.map(c=>c.type),['delete','delete']);
  assert.equal((await (await f.request(path,{cookie:b.cookie})).json()).position.page,2);
  assert.equal(after.position.page,1);
  const members=await (await f.request(path+'/members',{cookie:a.cookie})).json();assert.equal(members.members.length,2);
  assert.equal((await f.request(path+`/members/${b.account.id}`,{method:'DELETE',cookie:a.cookie})).status,200);
  assert.equal((await f.request(path,{cookie:b.cookie})).status,404);
  assert.equal((await f.request(path+'/operations',{method:'POST',cookie:b.cookie,body:{operations:[put('revoked')]}})).status,404);
});

test('expired challenges and invitations are rejected; local PDFs store metadata only',async t=>{
  const f=await fixture(t),a=await f.register('Private learner'),b=await f.register('Guest');
  const n=await create(f,a,{publicId:null,title:'My personal local PDF'});
  const invitation=await (await f.request(`notebooks/${n.id}/invites`,{method:'POST',cookie:a.cookie,body:{}})).json();
  await f.db.prepare('UPDATE study_invites SET expires_at=1').run();
  assert.equal((await f.request('invites/accept',{method:'POST',cookie:b.cookie,body:{token:invitation.token}})).status,410);
  const response=await f.request('auth/register/options',{method:'POST',body:{displayName:'Expired'}});
  const options=(await response.json()).options;
  const browser=authenticator(options);await f.db.prepare('UPDATE study_challenges SET expires_at=1').run();
  assert.equal((await f.request('auth/register/verify',{method:'POST',cookie:response.headers.get('Set-Cookie').split(';')[0],body:{response:browser.registration}})).status,401);
  const row=await f.db.prepare('SELECT * FROM study_notebooks WHERE id=?').bind(n.id).first();
  assert.equal(row.public_id,null);
  assert.equal(Object.keys(row).some(k=>/pdf|blob|url/i.test(k)),false);
  assert.equal(row.ink_bytes,0,'This is an ink counter, not uploaded PDF content');
});

test('at row or byte capacity existing erasures, immutable retries and position saves remain allowed',async t=>{
  const f=await fixture(t),a=await f.register('Capacity learner');
  const n=await create(f,a),path=`notebooks/${n.id}/operations`;
  assert.equal((await f.request(path,{method:'POST',cookie:a.cookie,body:{operations:[put('retained')]}})).status,200);
  await f.db.prepare(`WITH RECURSIVE seq(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM seq WHERE x<24999)
    INSERT INTO study_strokes(notebook_id,page,id,data,deleted,updated_at,actor_id)
      SELECT ?,1,'quota-'||x,NULL,1,1,? FROM seq`).bind(n.id,a.account.id).run();
  assert.equal((await f.db.prepare('SELECT count(*) n FROM study_strokes WHERE notebook_id=?').bind(n.id).first()).n,25000);
  assert.equal((await counters(f,n.id)).stroke_count,25000);
  assert.equal((await f.request(path,{method:'POST',cookie:a.cookie,body:{operations:[put('new-at-capacity')]}})).status,413);
  const unchanged=await f.request(path,{method:'POST',cookie:a.cookie,body:{operations:[put('retained'),put('quota-1')],position:{page:3}}});
  assert.equal(unchanged.status,200,await unchanged.clone().text());
  const erased=await f.request(path,{method:'POST',cookie:a.cookie,body:{operations:[erase('retained')]}});
  assert.equal(erased.status,200,await erased.clone().text());
  assert.equal((await f.request(path,{method:'POST',cookie:a.cookie,body:{operations:[put('retained'),erase('retained')]}})).status,200);
  assert.equal((await f.db.prepare("SELECT deleted FROM study_strokes WHERE notebook_id=? AND id='retained'").bind(n.id).first()).deleted,1);
  assert.equal((await f.db.prepare('SELECT position FROM study_members WHERE notebook_id=? AND account_id=?').bind(n.id,a.account.id).first()).position,3);
  assert.equal((await counters(f,n.id)).stroke_count,25000);

  const bytes=await create(f,a,{fingerprint:'b'.repeat(64)}),bytePath=`notebooks/${bytes.id}/operations`;
  assert.equal((await f.request(bytePath,{method:'POST',cookie:a.cookie,body:{operations:[put('small')]}})).status,200);
  // Seed real-shaped JSON strokes efficiently. No large request or quota
  // bypass endpoint is added to the application to construct this fixture.
  const large={...stroke('large'),points:Array.from({length:5000},()=>({x:0.1234567890123456,y:0.2345678901234567,p:0.3456789012345678}))};
  const payload=JSON.stringify(large),count=Math.ceil(12_000_000/payload.length);
  await f.db.prepare(`WITH RECURSIVE seq(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM seq WHERE x<?)
    INSERT INTO study_strokes(notebook_id,page,id,data,deleted,updated_at,actor_id,author_id)
      SELECT ?,1,'bytes-'||x,?,0,1,?,? FROM seq`).bind(count,bytes.id,payload,a.account.id,a.account.id).run();
  assert.ok((await f.db.prepare('SELECT sum(length(data)) bytes FROM study_strokes WHERE notebook_id=?').bind(bytes.id).first()).bytes>12_000_000);
  assert.equal((await f.request(bytePath,{method:'POST',cookie:a.cookie,body:{operations:[put('new-over-bytes')]}})).status,413);
  assert.equal((await f.request(bytePath,{method:'POST',cookie:a.cookie,body:{operations:[put('small')]}})).status,200);
  assert.equal((await f.request(bytePath,{method:'POST',cookie:a.cookie,body:{operations:[erase('small')],bookmarks:[1]}})).status,200);
  assert.equal((await f.request(bytePath,{method:'POST',cookie:a.cookie,body:{operations:[],position:{page:8}}})).status,200);
  await counters(f,bytes.id);
});

test('viewer grants preview their scope, preserve personal progress, and reject ink or forged authorship',async t=>{
  const f=await fixture(t),owner=await f.register('Owner'),viewer=await f.register('Reader');
  const n=await create(f,owner),path=`notebooks/${n.id}`;
  await f.request(path+'/operations',{method:'POST',cookie:owner.cookie,body:{operations:[put('owner-baseline')]}});
  const issued=await (await f.request(path+'/invites',{method:'POST',cookie:owner.cookie,body:{}})).json();
  assert.equal(issued.role,'viewer','A missing sharing choice must default to the least privilege');
  assert.equal((await f.request('invites/preview',{method:'POST',body:{token:issued.token}})).status,401);
  const preview=await (await f.request('invites/preview',{method:'POST',cookie:viewer.cookie,body:{token:issued.token}})).json();
  assert.equal(preview.invitation.role,'viewer');assert.equal(preview.invitation.title,n.title);
  assert.equal((await f.request(path,{cookie:viewer.cookie})).status,404,'Preview cannot create membership');
  const accepted=await (await f.request('invites/accept',{method:'POST',cookie:viewer.cookie,body:{token:issued.token}})).json();
  assert.deepEqual(accepted.notebook.capabilities,{canRead:true,canAdd:false,canDeleteOwn:false,canEditAll:false,canManageMembers:false});
  const snap=await (await f.request(path,{cookie:viewer.cookie})).json();
  assert.equal(snap.pages[0].strokes[0].id,'owner-baseline');
  assert.deepEqual(snap.strokeAuthors,[{page:1,id:'owner-baseline',accountId:owner.account.id}]);
  assert.equal((await f.request(path+'/operations',{method:'POST',cookie:viewer.cookie,body:{operations:[],position:{page:7},bookmarks:[7]}})).status,200);
  for(const operation of [put('forbidden'),erase('owner-baseline')]) {
    assert.equal((await f.request(path+'/operations',{method:'POST',cookie:viewer.cookie,body:{operations:[operation],position:{page:99}}})).status,403);
  }
  const untouched=await (await f.request(path,{cookie:viewer.cookie})).json();assert.equal(untouched.position.page,7);assert.equal(untouched.pages[0].strokes.length,1);
  assert.equal((await f.request(path+'/invites',{method:'POST',cookie:owner.cookie,body:{role:'owner'}})).status,400);
  assert.equal((await f.request(path+'/invites',{method:'POST',cookie:viewer.cookie,body:{role:'editor'}})).status,403);
  const forged=put('spoofed');forged.stroke.authorId=owner.account.id;
  assert.equal((await f.request(path+'/operations',{method:'POST',cookie:owner.cookie,body:{operations:[forged]}})).status,400);
});

test('contributors add their own layer and erase only their own ink; legacy and other writers remain protected',async t=>{
  const f=await fixture(t),owner=await f.register('Owner'),add=await f.register('Contributor'),editor=await f.register('Editor');
  const n=await create(f,owner),path=`notebooks/${n.id}`;
  await f.request(path+'/operations',{method:'POST',cookie:owner.cookie,body:{operations:[put('baseline')]}});
  const grant=await share(f,owner,n,add,'contributor');assert.equal(grant.capabilities.canAdd,true);assert.equal(grant.capabilities.canEditAll,false);
  await share(f,owner,n,editor,'editor');
  assert.equal((await f.request(path+'/operations',{method:'POST',cookie:add.cookie,body:{operations:[put('mine')]}})).status,200);
  const before=await (await f.request(path,{cookie:add.cookie})).json();
  assert.equal(before.strokeAuthors.find(s=>s.id==='mine').accountId,add.account.id);
  for(const operation of [erase('baseline'),erase('unknown-poison'),put('baseline')]) {
    assert.equal((await f.request(path+'/operations',{method:'POST',cookie:add.cookie,body:{operations:[put('mixed-new'),operation]}})).status,403);
    assert.equal((await f.db.prepare("SELECT count(*) n FROM study_strokes WHERE notebook_id=? AND id='mixed-new'").bind(n.id).first()).n,0);
  }
  const changed=put('mine');changed.stroke.color='#ff0000';
  assert.equal((await f.request(path+'/operations',{method:'POST',cookie:add.cookie,body:{operations:[changed]}})).status,200);
  assert.equal((await (await f.request(path,{cookie:add.cookie})).json()).pages[0].strokes.find(s=>s.id==='mine').color,'#182b35','Immutable IDs cannot overwrite a saved stroke');
  assert.equal((await f.request(path+'/operations',{method:'POST',cookie:add.cookie,body:{operations:[erase('mine')]}})).status,200);
  assert.equal((await f.request(path+'/operations',{method:'POST',cookie:editor.cookie,body:{operations:[erase('baseline')]}})).status,200);
  const delta=await (await f.request(path+`/pages?since=${before.notebook.revision}`,{cookie:add.cookie})).json();
  assert.equal(delta.changes.find(c=>c.id==='mine').authorId,add.account.id);
  assert.equal(delta.changes.find(c=>c.id==='baseline').authorId,owner.account.id);
  assert.equal((await (await f.request(path,{cookie:owner.cookie})).json()).pages.length,0);
  const capacity=await counters(f,n.id);assert.equal(capacity.stroke_count,2);assert.equal(capacity.ink_bytes,0);
});

test('owners change each non-owner grant; metadata-only polls reflect downgrades and older invitations cannot escalate',async t=>{
  const f=await fixture(t),owner=await f.register('Owner'),guest=await f.register('Guest');
  const n=await create(f,owner),path=`notebooks/${n.id}`;
  await share(f,owner,n,guest,'editor');
  const oldEditorInvite=await (await f.request(path+'/invites',{method:'POST',cookie:owner.cookie,body:{role:'editor'}})).json();
  const initial=await (await f.request(path,{cookie:guest.cookie})).json();
  for(const role of ['viewer','contributor','editor','viewer']) {
    const changed=await f.request(path+`/members/${guest.account.id}`,{method:'PATCH',cookie:owner.cookie,body:{role}});
    assert.equal(changed.status,200,await changed.clone().text());
    const delta=await (await f.request(path+`/pages?since=${initial.notebook.revision}`,{cookie:guest.cookie})).json();
    assert.equal(delta.notebook.role,role);assert.equal(delta.changes.length,0);
  }
  const reused=await (await f.request('invites/accept',{method:'POST',cookie:guest.cookie,body:{token:oldEditorInvite.token}})).json();
  assert.equal(reused.notebook.role,'viewer','An existing grant changes only through the owner role control');
  assert.equal((await f.request(path+`/members/${guest.account.id}`,{method:'PATCH',cookie:guest.cookie,body:{role:'editor'}})).status,403);
  assert.equal((await f.request(path+`/members/${owner.account.id}`,{method:'PATCH',cookie:owner.cookie,body:{role:'viewer'}})).status,400);
  assert.equal((await f.request(path+`/members/${guest.account.id}`,{method:'PATCH',cookie:owner.cookie,body:{role:'owner'}})).status,400);
  const members=await (await f.request(path+'/members',{cookie:owner.cookie})).json();assert.equal(members.members[0].role,'owner');
  assert.equal((await f.request(path+`/members/${guest.account.id}`,{method:'DELETE',cookie:owner.cookie})).status,200);
  assert.equal((await f.request(path,{cookie:guest.cookie})).status,404);
});

test('transactional permission guards roll back a mixed ink batch and recheck a role changed after application validation',async t=>{
  const f=await fixture(t),owner=await f.register('Owner'),guest=await f.register('Contributor');
  const n=await create(f,owner),path=`notebooks/${n.id}`;await share(f,owner,n,guest,'contributor');
  const before=await (await f.request(path,{cookie:owner.cookie})).json();
  await assert.rejects(f.db.batch([
    f.db.prepare('INSERT INTO study_strokes(notebook_id,page,id,data,deleted,updated_at,author_id,actor_id) VALUES(?,1,?,?,0,1,?,?)').bind(n.id,'first-valid',JSON.stringify(stroke('first-valid')),guest.account.id,guest.account.id),
    f.db.prepare('INSERT INTO study_strokes(notebook_id,page,id,data,deleted,updated_at,actor_id) VALUES(?,1,?,NULL,1,1,?)').bind(n.id,'unknown-tombstone',guest.account.id),
  ]),/study_permission_denied/);
  const after=await (await f.request(path,{cookie:owner.cookie})).json();assert.equal(after.notebook.revision,before.notebook.revision);assert.equal(after.pages.length,0);assert.equal(after.deleted.length,0);
  const env={RATE_LIMIT_SALT:'x'.repeat(32),DB:{prepare:sql=>f.db.prepare(sql),batch:async commands=>{
    await f.db.prepare("UPDATE study_members SET role='viewer' WHERE notebook_id=? AND account_id=?").bind(n.id,guest.account.id).run();
    return f.db.batch(commands);
  }}};
  const request=new Request(API+pref+path+'/operations',{method:'POST',headers:{Origin:ORIGIN,Cookie:guest.cookie,'Content-Type':'application/json'},body:JSON.stringify({operations:[put('raced-put')]})});
  await assert.rejects(studyRoute(request,env),error=>error.status===403&&error.code==='notebook_permission_changed');
  assert.equal((await f.db.prepare('SELECT count(*) n FROM study_strokes WHERE notebook_id=?').bind(n.id).first()).n,0);
  const capacity=await counters(f,n.id);assert.equal(capacity.stroke_count,0);assert.equal(capacity.ink_bytes,0);
});

test('permission migration preserves owner/editor grants and keeps pre-attribution strokes protected from contributors',async t=>{
  const f=await fixture(t,async db=>{
    await db.batch([
      db.prepare("INSERT INTO study_accounts(id,display_name,created_at) VALUES('legacy-owner','Owner',1),('legacy-editor','Editor',1)"),
      db.prepare("INSERT INTO study_notebooks(id,owner_id,title,fingerprint,page_count,created_at,updated_at) VALUES('legacy-note','legacy-owner','Legacy',?,2,1,1)").bind('b'.repeat(64)),
      db.prepare("INSERT INTO study_members(notebook_id,account_id,role,joined_at) VALUES('legacy-note','legacy-owner','owner',1),('legacy-note','legacy-editor','editor',1)"),
      db.prepare("INSERT INTO study_strokes(notebook_id,page,id,data,deleted,updated_at) VALUES('legacy-note',1,'legacy-ink',?,0,1)").bind(JSON.stringify(stroke('legacy-ink'))),
    ]);
  });
  const members=await f.db.prepare("SELECT role,account_id FROM study_members WHERE notebook_id='legacy-note' ORDER BY account_id").all();
  assert.deepEqual(members.results,[{role:'editor',account_id:'legacy-editor'},{role:'owner',account_id:'legacy-owner'}]);
  assert.equal((await f.db.prepare("SELECT author_id FROM study_strokes WHERE notebook_id='legacy-note'").first()).author_id,null);
  const capacity=await counters(f,'legacy-note');assert.equal(capacity.stroke_count,1);assert.equal(capacity.ink_bytes,JSON.stringify(stroke('legacy-ink')).length);
  await f.db.prepare("UPDATE study_members SET role='contributor' WHERE account_id='legacy-editor'").run();
  await assert.rejects(f.db.prepare("INSERT INTO study_strokes(notebook_id,page,id,data,deleted,updated_at,actor_id) VALUES('legacy-note',1,'legacy-ink',NULL,1,2,'legacy-editor') ON CONFLICT(notebook_id,page,id) DO UPDATE SET data=NULL,deleted=1,actor_id=excluded.actor_id").run(),/study_permission_denied/);
  assert.equal((await f.db.prepare("SELECT deleted FROM study_strokes WHERE notebook_id='legacy-note'").first()).deleted,0);
});

test('a 100-operation sync uses bounded D1 calls and indexed JSON-key prefetch while preserving retries and sequential edits',async t=>{
  const f=await fixture(t),owner=await f.register('Batch learner'),n=await create(f,owner),path=`notebooks/${n.id}/operations`;
  const operations=Array.from({length:100},(_,i)=>put(`batch-${i}`,i%2+1));
  const written=await f.request(path,{method:'POST',cookie:owner.cookie,body:{operations,position:{page:2}}});
  assert.equal(written.status,200,await written.clone().text());assert.equal((await counters(f,n.id)).stroke_count,100);
  const original=new WeakMap();let bindingCalls=0,prefetchCalls=0,batches=0;
  function wrapped(statement) {
    const value={bind:(...args)=>wrapped(statement.bind(...args)),
      first:(...args)=>{bindingCalls++;return statement.first(...args);},
      all:(...args)=>{bindingCalls++;prefetchCalls++;return statement.all(...args);},
      run:(...args)=>{bindingCalls++;return statement.run(...args);}};
    original.set(value,statement);return value;
  }
  const env={RATE_LIMIT_SALT:'q'.repeat(32),DB:{prepare:sql=>wrapped(f.db.prepare(sql)),batch:commands=>{
    bindingCalls++;batches++;return f.db.batch(commands.map(command=>original.get(command)));
  }}};
  const request=new Request(API+pref+path,{method:'POST',headers:{Origin:ORIGIN,Cookie:owner.cookie,'Content-Type':'application/json'},body:JSON.stringify({operations})});
  const replay=await studyRoute(request,env);assert.equal(replay.status,200);
  assert.ok(bindingCalls<=10,`${bindingCalls} D1 calls exceeds the bounded batch budget`);assert.equal(prefetchCalls,1);assert.equal(batches,1);
  assert.equal((await counters(f,n.id)).stroke_count,100,'A full replay must not duplicate counters or ink');
  const source=await readFile(join(ROOT,'src/study.js'),'utf8'),sql=source.match(/const stored=await all\(env,`([^`]+)`/)[1];
  const plan=await f.db.prepare('EXPLAIN QUERY PLAN '+sql).bind(JSON.stringify([{page:1,id:'batch-0'},{page:2,id:'batch-1'}]),n.id).all();
  const details=plan.results.map(row=>row.detail).join('\n');
  assert.match(details,/SEARCH s USING INDEX .*\(notebook_id=\? AND page=\? AND id=\?\)/);assert.doesNotMatch(details,/SCAN s\b/);
  bindingCalls=0;prefetchCalls=0;batches=0;
  const progress=new Request(API+pref+path,{method:'POST',headers:{Origin:ORIGIN,Cookie:owner.cookie,'Content-Type':'application/json'},body:JSON.stringify({operations:[],position:{page:4}})});
  assert.equal((await studyRoute(progress,env)).status,200);assert.equal(prefetchCalls,0,'Progress-only saves do not prefetch ink');assert.ok(bindingCalls<=10);
  const edits=await f.request(path,{method:'POST',cookie:owner.cookie,body:{operations:[put('within-batch'),erase('within-batch'),put('within-batch')]}});
  assert.equal(edits.status,200,await edits.clone().text());
  const tombstone=await f.db.prepare("SELECT deleted FROM study_strokes WHERE notebook_id=? AND id='within-batch'").bind(n.id).first();assert.equal(tombstone.deleted,1);
  await counters(f,n.id);
});

test('delta feeds redact erased historical ink for newly invited readers while preserving live ink, pagination and offline erasures',async t=>{
  const f=await fixture(t),owner=await f.register('Owner'),viewer=await f.register('New reader'),n=await create(f,owner),path=`notebooks/${n.id}`;
  const additions=Array.from({length:99},(_,index)=>{
    const operation=put(`erased-${index}`);operation.stroke.color='#abcdef';return operation;
  });
  const visible=put('still-visible');visible.stroke.color='#2468ab';additions.push(visible);
  assert.equal((await f.request(path+'/operations',{method:'POST',cookie:owner.cookie,body:{operations:additions}})).status,200);
  const offline=await (await f.request(path,{cookie:owner.cookie})).json();
  assert.equal(offline.pages[0].strokes.length,100);
  assert.equal((await f.request(path+'/operations',{method:'POST',cookie:owner.cookie,body:{operations:additions.slice(0,99).map(item=>erase(item.stroke.id))}})).status,200);
  await share(f,owner,n,viewer,'viewer');
  const current=await (await f.request(path,{cookie:viewer.cookie})).json();
  assert.deepEqual(current.pages[0].strokes.map(item=>item.id),['still-visible']);
  const first=await (await f.request(path+'/pages?since=0',{cookie:viewer.cookie})).json();
  assert.equal(first.more,true);assert.equal(first.changes.length,100);
  assert.equal(first.changes.filter(item=>item.type==='put').length,1);
  assert.deepEqual(first.changes.find(item=>item.type==='put').stroke,visible.stroke);
  for(const change of first.changes.filter(item=>item.id.startsWith('erased-'))){assert.equal(change.type,'delete');assert.equal(change.stroke,null);}
  assert.equal(JSON.stringify(first).includes('#abcdef'),false,'Deleted geometry must not leak through old put payloads');
  const second=await (await f.request(path+`/pages?since=${first.revision}`,{cookie:viewer.cookie})).json();
  assert.equal(second.more,false);assert.equal(second.changes.length,99);
  assert.ok(second.changes.every(item=>item.type==='delete'&&item.stroke===null));
  assert.equal(second.revision,current.notebook.revision);
  const end=await (await f.request(path+`/pages?since=${second.revision}`,{cookie:viewer.cookie})).json();assert.deepEqual(end.changes,[]);assert.equal(end.revision,second.revision);
  const delta=await (await f.request(path+`/pages?since=${offline.notebook.revision}`,{cookie:owner.cookie})).json();
  const {applyRemoteChanges}=await import('../../../lecture-reader/cloud-core.mjs');
  const recovered=applyRemoteChanges(offline,delta,offline.notebook.revision);
  assert.deepEqual(recovered.pages[0].strokes.map(item=>item.id),['still-visible']);
  assert.equal(recovered.deleted.length,99,'A client that was offline still receives every erasure');
  const source=await readFile(join(ROOT,'src/study.js'),'utf8'),section=source.slice(source.indexOf('async function changes('),source.indexOf('async function createInvite('));
  const sql=section.match(/const rows=await all\(env,`([^`]+)`/)[1];
  const plan=await f.db.prepare('EXPLAIN QUERY PLAN '+sql).bind(n.id,0,n.id,viewer.account.id).all();
  assert.match(plan.results.map(row=>row.detail).join('\n'),/SEARCH s USING INDEX .*\(notebook_id=\? AND page=\? AND id=\?\)/);
});
