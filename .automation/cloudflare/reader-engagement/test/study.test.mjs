import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {randomBytes,generateKeyPairSync,createHash,sign} from 'node:crypto';
import {encodeCBOR} from '@levischuck/tiny-cbor';
import {Miniflare,Log,LogLevel} from 'miniflare';
import {sha256} from '../src/security.js';

const ROOT=dirname(dirname(fileURLToPath(import.meta.url)));
const ORIGIN='https://infant83.io';
const API='https://api.infant83.io';
const hash=data=>createHash('sha256').update(data).digest();
const b64=data=>Buffer.from(data).toString('base64url');
const pref='/v1/study/';
const stroke=(id='stroke-a')=>({id,color:'#182b35',width:0.002,points:[{x:0.1,y:0.2,p:0.5},{x:0.8,y:0.7,p:0.7}]});
const put=(id,page=1)=>({type:'put',page,stroke:stroke(id)});
const erase=(id,page=1)=>({type:'delete',page,id});

async function fixture(t) {
  const mf=new Miniflare({modules:true,scriptPath:join(ROOT,'.wrangler/test-worker.mjs'),compatibilityDate:'2026-08-06',
    d1Databases:['DB'],bindings:{RATE_LIMIT_SALT:randomBytes(32).toString('hex')},log:new Log(LogLevel.ERROR)});
  t.after(()=>mf.dispose());
  const db=await mf.getD1Database('DB');
  for(const name of (await readdir(join(ROOT,'migrations'))).filter(n=>n.endsWith('.sql')).sort()) {
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
  const invitation=await (await f.request(path+'/invites',{method:'POST',cookie:a.cookie,body:{}})).json();
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
  assert.equal(Object.keys(row).some(k=>/pdf|blob|bytes|url/i.test(k)),false);
});

test('at row or byte capacity existing erasures, immutable retries and position saves remain allowed',async t=>{
  const f=await fixture(t),a=await f.register('Capacity learner');
  const n=await create(f,a),path=`notebooks/${n.id}/operations`;
  assert.equal((await f.request(path,{method:'POST',cookie:a.cookie,body:{operations:[put('retained')]}})).status,200);
  await f.db.prepare(`WITH RECURSIVE seq(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM seq WHERE x<24999)
    INSERT INTO study_strokes(notebook_id,page,id,data,deleted,updated_at)
      SELECT ?,1,'quota-'||x,NULL,1,1 FROM seq`).bind(n.id).run();
  assert.equal((await f.db.prepare('SELECT count(*) n FROM study_strokes WHERE notebook_id=?').bind(n.id).first()).n,25000);
  assert.equal((await f.request(path,{method:'POST',cookie:a.cookie,body:{operations:[put('new-at-capacity')]}})).status,413);
  const unchanged=await f.request(path,{method:'POST',cookie:a.cookie,body:{operations:[put('retained'),put('quota-1')],position:{page:3}}});
  assert.equal(unchanged.status,200,await unchanged.clone().text());
  const erased=await f.request(path,{method:'POST',cookie:a.cookie,body:{operations:[erase('retained')]}});
  assert.equal(erased.status,200,await erased.clone().text());
  assert.equal((await f.request(path,{method:'POST',cookie:a.cookie,body:{operations:[put('retained'),erase('retained')]}})).status,200);
  assert.equal((await f.db.prepare("SELECT deleted FROM study_strokes WHERE notebook_id=? AND id='retained'").bind(n.id).first()).deleted,1);
  assert.equal((await f.db.prepare('SELECT position FROM study_members WHERE notebook_id=? AND account_id=?').bind(n.id,a.account.id).first()).position,3);

  const bytes=await create(f,a,{fingerprint:'b'.repeat(64)}),bytePath=`notebooks/${bytes.id}/operations`;
  assert.equal((await f.request(bytePath,{method:'POST',cookie:a.cookie,body:{operations:[put('small')]}})).status,200);
  // Seed real-shaped JSON strokes efficiently. No large request or quota
  // bypass endpoint is added to the application to construct this fixture.
  const large={...stroke('large'),points:Array.from({length:5000},()=>({x:0.1234567890123456,y:0.2345678901234567,p:0.3456789012345678}))};
  const payload=JSON.stringify(large),count=Math.ceil(12_000_000/payload.length);
  await f.db.prepare(`WITH RECURSIVE seq(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM seq WHERE x<?)
    INSERT INTO study_strokes(notebook_id,page,id,data,deleted,updated_at)
      SELECT ?,1,'bytes-'||x,?,0,1 FROM seq`).bind(count,bytes.id,payload).run();
  assert.ok((await f.db.prepare('SELECT sum(length(data)) bytes FROM study_strokes WHERE notebook_id=?').bind(bytes.id).first()).bytes>12_000_000);
  assert.equal((await f.request(bytePath,{method:'POST',cookie:a.cookie,body:{operations:[put('new-over-bytes')]}})).status,413);
  assert.equal((await f.request(bytePath,{method:'POST',cookie:a.cookie,body:{operations:[put('small')]}})).status,200);
  assert.equal((await f.request(bytePath,{method:'POST',cookie:a.cookie,body:{operations:[erase('small')],bookmarks:[1]}})).status,200);
  assert.equal((await f.request(bytePath,{method:'POST',cookie:a.cookie,body:{operations:[],position:{page:8}}})).status,200);
});
