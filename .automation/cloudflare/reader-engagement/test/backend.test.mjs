import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import {createECDH,generateKeyPairSync,randomBytes,verify,createPublicKey} from 'node:crypto';
import {Miniflare,createFetchMock,Log,LogLevel} from 'miniflare';
import ece from 'http_ece';
import worker,{deliver,fanout,recoverOutbox,normalizeFeed} from '../src/worker.js';
import {sha256} from '../src/security.js';
import {webPushRequest} from '../src/web-push.js';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const ORIGIN = 'https://infant83.io';
const API = 'https://api.infant83.io';
const revision = letter => letter.repeat(40);
const item = (id='2026-10-25_first-review',topic='review') => ({
  id:topic === 'lecture' ? `lecture:${id}` : id,
  path:`/AI_Tech_Review/${topic === 'lecture' ? 'lectures' : 'reviews'}/${id}/`,
  title:`검증용 ${id}`,publishedAt:'2026-10-25',topic,
});

function keys() {
  const pair = generateKeyPairSync('ec',{namedCurve:'prime256v1'});
  const privateKey = pair.privateKey.export({format:'jwk'});
  const publicKey = Buffer.concat([Buffer.from([4]),Buffer.from(privateKey.x,'base64url'),Buffer.from(privateKey.y,'base64url')]);
  return {VAPID_PUBLIC_KEY:publicKey.toString('base64url'),VAPID_PRIVATE_KEY:privateKey.d,VAPID_SUBJECT:'mailto:reader-tests@example.com'};
}

function browserSubscription(label='test-endpoint') {
  const client = createECDH('prime256v1');
  client.generateKeys();
  const auth = randomBytes(16);
  return {client,auth,subscription:{endpoint:`https://web.push.apple.com/${label}`,expirationTime:null,
    keys:{p256dh:client.getPublicKey().toString('base64url'),auth:auth.toString('base64url')}}};
}

async function fixture(t,extraBindings={}) {
  const bindings = {...keys(),RATE_LIMIT_SALT:randomBytes(32).toString('hex'),READER_PUBLISH_TOKEN:randomBytes(32).toString('hex'),...extraBindings};
  let feed = {revision:revision('a'),articles:[item()]};
  const mock = createFetchMock();
  mock.disableNetConnect();
  mock.get(ORIGIN).intercept({path:path=>{
    const url=new URL(path,ORIGIN);
    return url.pathname==='/AI_Tech_Review/reader-publications.json' && /^[a-f0-9]{40,64}$/.test(url.searchParams.get('reader_revision')) && /^[a-f0-9-]{36}$/.test(url.searchParams.get('nonce'));
  },method:'GET'})
    .reply(200,() => JSON.stringify(feed),{headers:{'Content-Type':'application/json'}}).persist();
  const mf = new Miniflare({
    modules:true,scriptPath:join(ROOT,'src/worker.js'),modulesRules:[{type:'ESModule',include:['**/*.js']}],compatibilityDate:'2026-08-06',
    d1Databases:['DB'],queueProducers:{READER_QUEUE:'test-reader-notifications'},bindings,fetchMock:mock,
    log:new Log(LogLevel.ERROR),
  });
  t.after(() => mf.dispose());
  const db = await mf.getD1Database('DB');
  const migration=await readFile(join(ROOT,'migrations/0001_reader_engagement.sql'),'utf8');
  await db.batch(migration.split(';').map(sql=>sql.trim()).filter(Boolean).map(sql=>db.prepare(sql)));
  const queued = [];
  const env = {...bindings,DB:db,READER_QUEUE:{
    async send(body) { queued.push(body); },
    async sendBatch(batch) { queued.push(...batch.map(message => message.body)); },
  }};
  const request = (path,{method='GET',body,cookie,origin=ORIGIN,headers={}}={}) => {
    const combined = {'CF-Connecting-IP':'198.51.100.10',...headers};
    if (origin !== null) combined.Origin=origin;
    if (cookie) combined.Cookie=cookie;
    if (body !== undefined) combined['Content-Type']='application/json';
    return mf.dispatchFetch(`${API}${path}`,{method,headers:combined,...(body !== undefined ? {body:JSON.stringify(body)} : {})});
  };
  const register = async (ip='198.51.100.10') => {
    const response = await request('/v1/devices',{method:'POST',body:{},headers:{'CF-Connecting-IP':ip}});
    assert.equal(response.status,201);
    const body = await response.json();
    assert.equal(body.ok,true);
    return {id:body.deviceId,cookie:response.headers.get('Set-Cookie').split(';')[0],response,body};
  };
  const sync = async (next=feed,extra={}) => {
    feed=next;
    return request('/v1/publications/sync',{method:'POST',body:next,origin:null,headers:{Authorization:`Bearer ${bindings.READER_PUBLISH_TOKEN}`},...extra});
  };
  return {mf,db,env,request,register,sync,queued,setFeed:value => {feed=value;},getFeed:() => feed};
}

test('real Web Push encryption decrypts with independent http_ece and VAPID signature verifies',async () => {
  const browser = browserSubscription();
  const env = keys();
  const payload = {title:'알림 암호화 검증',body:'새 글',url:`${ORIGIN}/AI_Tech_Review/`,tag:'a'.repeat(64)};
  const request = await webPushRequest(browser.subscription,payload,env);
  assert.equal(request.method,'POST');
  assert.equal(request.redirect,'manual');
  assert.equal(request.headers.get('Content-Encoding'),'aes128gcm');
  const decrypted = ece.decrypt(Buffer.from(await request.arrayBuffer()),{version:'aes128gcm',privateKey:browser.client,authSecret:browser.auth});
  assert.deepEqual(JSON.parse(decrypted.toString()),payload);
  const authorization = request.headers.get('Authorization');
  const jwt = /^vapid t=([^,]+), k=/.exec(authorization)[1];
  const [header,claims,signature] = jwt.split('.');
  assert.equal(JSON.parse(Buffer.from(header,'base64url')).alg,'ES256');
  assert.equal(JSON.parse(Buffer.from(claims,'base64url')).aud,'https://web.push.apple.com');
  const raw = Buffer.from(env.VAPID_PUBLIC_KEY,'base64url');
  const key = createPublicKey({key:{kty:'EC',crv:'P-256',x:raw.subarray(1,33).toString('base64url'),y:raw.subarray(33,65).toString('base64url')},format:'jwk'});
  assert.equal(verify('sha256',Buffer.from(`${header}.${claims}`),{key,dsaEncoding:'ieee-p1363'},Buffer.from(signature,'base64url')),true);
});

test('device sessions are HttpOnly, hashed in D1, reused, and protected by exact Origin',async t => {
  const f=await fixture(t);
  assert.equal((await f.request('/v1/devices',{method:'POST',body:{},origin:null})).status,403);
  assert.equal((await f.request('/v1/devices',{method:'POST',body:{},origin:'https://infant83.io.evil.example'})).status,403);
  const current=await f.register();
  const cookie=current.response.headers.get('Set-Cookie');
  assert.match(cookie,/^__Host-reader_session=/);
  for (const value of ['HttpOnly','Secure','SameSite=Strict','Path=/']) assert.ok(cookie.includes(value));
  assert.equal('token' in current.body,false);
  assert.equal('deviceToken' in current.body,false);
  assert.equal(current.response.headers.get('Access-Control-Allow-Origin'),ORIGIN);
  assert.equal(current.response.headers.get('Access-Control-Allow-Credentials'),'true');
  const stored=await f.db.prepare('SELECT * FROM devices').first();
  const token=current.cookie.split('=')[1];
  assert.equal(stored.token_hash,await sha256(token));
  assert.equal(JSON.stringify(stored).includes(token),false);
  const reused=await f.request('/v1/devices',{method:'POST',body:{},cookie:current.cookie});
  assert.equal((await reused.json()).deviceId,current.id);
  assert.equal((await f.db.prepare('SELECT count(*) n FROM devices').first()).n,1);
  assert.equal((await f.request('/v1/config',{method:'OPTIONS',origin:ORIGIN})).status,204);
  const bad=await f.request('/v1/config',{origin:'https://example.com'});
  assert.equal(bad.status,403);
  assert.equal(bad.headers.has('Access-Control-Allow-Origin'),false);
});

test('baseline catalog sends nothing and likes are per-device, repeatable state updates',async t => {
  const f=await fixture(t);
  const seed=await f.sync();
  assert.equal(seed.status,200,await seed.clone().text());
  assert.equal((await seed.json()).baseline,true);
  assert.equal((await f.db.prepare('SELECT count(*) n FROM publication_events').first()).n,0);
  const a=await f.register(),b=await f.register();
  const path=`/v1/articles/${encodeURIComponent(item().id)}/like`;
  assert.deepEqual(await (await f.request(path)).json(),{ok:true,count:0,liked:false});
  assert.equal((await f.request(path,{method:'PUT',body:{liked:true}})).status,401);
  for(let i=0;i<2;i++) assert.deepEqual(await (await f.request(path,{method:'PUT',cookie:a.cookie,body:{liked:true}})).json(),{ok:true,count:1,liked:true});
  assert.deepEqual(await (await f.request(path,{method:'PUT',cookie:b.cookie,body:{liked:true}})).json(),{ok:true,count:2,liked:true});
  assert.deepEqual(await (await f.request(path,{method:'PUT',cookie:a.cookie,body:{liked:false}})).json(),{ok:true,count:1,liked:false});
  assert.equal((await f.request('/v1/articles/not-in-catalog/like',{method:'PUT',cookie:a.cookie,body:{liked:true}})).status,404);
  assert.equal((await f.request(path,{method:'PUT',cookie:a.cookie,body:{liked:'true'}})).status,400);
  assert.equal((await f.request(path,{method:'PUT',cookie:a.cookie,body:{liked:true,extra:'ignored?'}})).status,400);
});

test('subscription validation rejects SSRF endpoints and keeps device ownership isolated',async t => {
  const f=await fixture(t);
  const a=await f.register(),b=await f.register();
  const browser=browserSubscription();
  for(const endpoint of ['http://web.push.apple.com/test','https://127.0.0.1/internal','https://web.push.apple.com.evil.example/test','https://web.push.apple.com:8443/test','https://user:pass@web.push.apple.com/test']) {
    const response=await f.request('/v1/subscription',{method:'PUT',cookie:a.cookie,body:{subscription:{...browser.subscription,endpoint},topics:['review']}});
    assert.equal(response.status,400);
  }
  assert.equal((await f.request('/v1/subscription',{method:'PUT',cookie:a.cookie,body:{subscription:browser.subscription,topics:['anything']}})).status,400);
  const saved=await f.request('/v1/subscription',{method:'PUT',cookie:a.cookie,body:{subscription:browser.subscription,topics:['review']}});
  assert.equal(saved.status,200);
  assert.deepEqual((await saved.json()).topics,['review']);
  assert.equal((await (await f.request('/v1/subscription',{cookie:b.cookie})).json()).subscribed,false);
  await f.request('/v1/subscription',{method:'DELETE',cookie:b.cookie});
  assert.equal((await (await f.request('/v1/subscription',{cookie:a.cookie})).json()).subscribed,true);
  await f.request('/v1/subscription',{method:'DELETE',cookie:a.cookie});
  assert.equal((await (await f.request('/v1/subscription',{cookie:a.cookie})).json()).subscribed,false);
});

test('public feed verification, initial baseline, edits, new IDs and replay are distinct',async t => {
  const f=await fixture(t);
  const unauthorized=await f.request('/v1/publications/sync',{method:'POST',body:f.getFeed(),origin:null});
  assert.equal(unauthorized.status,401);
  const forged={revision:revision('b'),articles:[{...item(),title:'not public'}]};
  const mismatch=await f.request('/v1/publications/sync',{method:'POST',body:forged,origin:null,headers:{Authorization:`Bearer ${f.env.READER_PUBLISH_TOKEN}`}});
  assert.equal(mismatch.status,409);
  const initial=f.getFeed();
  assert.equal((await f.sync(initial)).status,200);
  const edited={revision:revision('b'),articles:[{...item(),title:'교정된 제목'}]};
  assert.equal((await (await f.sync(edited)).json()).newArticles,0);
  const latest={revision:revision('c'),articles:[...edited.articles,item('2026-10-26_second-review'),item('quantum-course','lecture')]};
  assert.equal((await (await f.sync(latest)).json()).newArticles,2);
  assert.equal((await f.db.prepare('SELECT count(*) n FROM publication_events').first()).n,2);
  assert.equal((await (await f.sync(initial)).json()).replay,true);
  assert.equal((await f.db.prepare('SELECT count(*) n FROM articles WHERE active=1').first()).n,3);
  const conflict=await f.sync({...initial,articles:[{...item(),title:'same SHA different content'}]});
  assert.equal(conflict.status,409);
  assert.equal((await f.db.prepare('SELECT count(*) n FROM publication_events').first()).n,2);
});

test('creation rate limiting stores rotating hashes, without plaintext IP addresses',async t => {
  const f=await fixture(t);
  for(let i=0;i<20;i++) await f.register('198.51.100.200');
  const response=await f.request('/v1/devices',{method:'POST',body:{},headers:{'CF-Connecting-IP':'198.51.100.200'}});
  assert.equal(response.status,429);
  assert.equal(response.headers.get('Retry-After'),'60');
  const values=(await f.db.prepare('SELECT key FROM rate_limits').all()).results;
  assert.equal(JSON.stringify(values).includes('198.51.100.200'),false);
  assert.equal((await f.db.prepare('SELECT count(*) n FROM devices').first()).n,20);
});

async function seedSubscriber(f,label,selected=['review'],created=Date.now()-10_000) {
  const browser=browserSubscription(`endpoint-${label}`);
  const id=`device-${String(label).padStart(3,'0')}`;
  const version=`version-${label}`;
  await f.db.batch([
    f.db.prepare('INSERT INTO devices(id,token_hash,created_at) VALUES(?,?,?)').bind(id,await sha256(id),created),
    f.db.prepare(`INSERT INTO subscriptions(device_id,endpoint_hash,endpoint,p256dh,auth,expiration_time,review_enabled,lecture_enabled,version,created_at,updated_at)
      VALUES(?,?,?,?,?,NULL,?,?,?,?,?)`).bind(id,await sha256(browser.subscription.endpoint),browser.subscription.endpoint,browser.subscription.keys.p256dh,browser.subscription.keys.auth,Number(selected.includes('review')),Number(selected.includes('lecture')),version,created,created),
  ]);
  return {id,version,...browser};
}

async function newEvent(f) {
  await f.sync();
  const feed={revision:revision('b'),articles:[item(),item('2026-10-26_new')]};
  await f.sync(feed);
  return f.db.prepare('SELECT * FROM publication_events').first();
}

test('fanout is paginated and topic-filtered; users joining later are not notified',async t => {
  const f=await fixture(t);
  for(let i=0;i<23;i++) await seedSubscriber(f,i);
  await seedSubscriber(f,100,['lecture']);
  const event=await newEvent(f);
  await seedSubscriber(f,101,['review'],event.created_at+1);
  await fanout(f.env,event.id);
  assert.equal(f.queued.filter(v=>v.type==='push').length,20);
  assert.equal(f.queued.filter(v=>v.type==='fanout').length,1);
  await fanout(f.env,event.id);
  assert.equal(f.queued.filter(v=>v.type==='push').length,23);
  await fanout(f.env,event.id);
  assert.equal((await f.db.prepare('SELECT count(*) n FROM deliveries').first()).n,23);
  assert.equal((await f.db.prepare('SELECT fanout_completed FROM publication_events').first()).fanout_completed,1);
});

test('delivery sends encrypted payload once, honors concurrent redelivery and prunes 410',async t => {
  const f=await fixture(t);
  const subscriber=await seedSubscriber(f,1);
  const event=await newEvent(f);
  await fanout(f.env,event.id);
  let calls=0;
  const transport=async request => {
    calls++;
    const plaintext=ece.decrypt(Buffer.from(await request.arrayBuffer()),{version:'aes128gcm',privateKey:subscriber.client,authSecret:subscriber.auth});
    const payload=JSON.parse(plaintext.toString());
    assert.equal(payload.url,`${ORIGIN}${event.path}`);
    assert.equal(payload.articleId,event.article_id);
    return new Response(null,{status:201});
  };
  await Promise.all([deliver(f.env,event.id,subscriber.id,transport),deliver(f.env,event.id,subscriber.id,transport)]);
  await deliver(f.env,event.id,subscriber.id,transport);
  assert.equal(calls,1);
  assert.equal((await f.db.prepare('SELECT status FROM deliveries').first()).status,'sent');
  const gone=await seedSubscriber(f,2);
  await f.db.prepare('INSERT INTO deliveries(event_id,device_id,subscription_version,created_at) VALUES(?,?,?,?)').bind(event.id,gone.id,gone.version,Date.now()).run();
  await deliver(f.env,event.id,gone.id,async()=>new Response(null,{status:410}));
  assert.equal(await f.db.prepare('SELECT * FROM subscriptions WHERE device_id=?').bind(gone.id).first(),null);
  assert.equal((await f.db.prepare('SELECT status FROM deliveries WHERE device_id=?').bind(gone.id).first()).status,'dead');
});

test('unsubscription, changed endpoint version, and topic opt-out suppress pending delivery',async t => {
  const f=await fixture(t);
  const a=await seedSubscriber(f,1),b=await seedSubscriber(f,2),c=await seedSubscriber(f,3);
  const event=await newEvent(f);
  await fanout(f.env,event.id);
  await f.db.prepare('DELETE FROM subscriptions WHERE device_id=?').bind(a.id).run();
  await f.db.prepare('UPDATE subscriptions SET version=? WHERE device_id=?').bind('changed',b.id).run();
  await f.db.prepare('UPDATE subscriptions SET review_enabled=0 WHERE device_id=?').bind(c.id).run();
  let calls=0;
  for(const sub of [a,b,c]) await deliver(f.env,event.id,sub.id,async()=>{calls++;return new Response(null,{status:201});});
  assert.equal(calls,0);
  assert.equal((await f.db.prepare("SELECT count(*) n FROM deliveries WHERE status='suppressed'").first()).n,3);
});

test('429 retries remain durable and outbox recovery requeues unfinished work',async t => {
  const f=await fixture(t);
  const subscriber=await seedSubscriber(f,1);
  const event=await newEvent(f);
  await fanout(f.env,event.id);
  await assert.rejects(deliver(f.env,event.id,subscriber.id,async()=>new Response(null,{status:429,headers:{'Retry-After':'120'}})),/retry_delivery/);
  const row=await f.db.prepare('SELECT * FROM deliveries').first();
  assert.equal(row.status,'retry');
  assert.ok(row.retry_at>Date.now()+110_000);
  await f.db.prepare('UPDATE deliveries SET retry_at=0').run();
  assert.equal(await recoverOutbox(f.env),1);
  assert.deepEqual(f.queued.at(-1),{type:'push',eventId:event.id,deviceId:subscriber.id});
  await deliver(f.env,event.id,subscriber.id,async()=>new Response(null,{status:201}));
  assert.equal((await f.db.prepare('SELECT status FROM deliveries').first()).status,'sent');
});

test('test push targets only the current device, with 60-second and five-per-day limits',async t => {
  const f=await fixture(t);
  const a=await f.register(),b=await f.register();
  const browser=browserSubscription('test-own-endpoint');
  assert.equal((await f.request('/v1/subscription/test',{method:'POST',cookie:a.cookie,body:{}})).status,409);
  await f.request('/v1/subscription',{method:'PUT',cookie:a.cookie,body:{subscription:browser.subscription,topics:['review']}});
  const accepted=await f.request('/v1/subscription/test',{method:'POST',cookie:a.cookie,body:{}});
  assert.equal(accepted.status,202);
  assert.deepEqual(await accepted.json(),{ok:true,queued:true});
  assert.equal((await f.request('/v1/subscription/test',{method:'POST',cookie:a.cookie,body:{}})).status,429);
  assert.equal((await f.request('/v1/subscription/test',{method:'POST',cookie:b.cookie,body:{}})).status,409);
  for(let i=0;i<4;i++) {
    await f.db.prepare('UPDATE rate_limits SET expires_at=0 WHERE key=?').bind(`test-minute:${a.id}`).run();
    assert.equal((await f.request('/v1/subscription/test',{method:'POST',cookie:a.cookie,body:{}})).status,202);
  }
  await f.db.prepare('UPDATE rate_limits SET expires_at=0 WHERE key=?').bind(`test-minute:${a.id}`).run();
  assert.equal((await f.request('/v1/subscription/test',{method:'POST',cookie:a.cookie,body:{}})).status,429);
  const deliveries=(await f.db.prepare('SELECT * FROM deliveries').all()).results;
  assert.equal(deliveries.length,5);
  assert.ok(deliveries.every(row=>row.device_id===a.id));
  const event=await f.db.prepare('SELECT * FROM publication_events LIMIT 1').first();
  assert.equal(event.title,'AI Tech Review 알림 테스트');
  assert.equal(event.path,'/AI_Tech_Review/');
});

test('queue consumer acknowledges terminal/successful messages without retrying a whole batch',async t => {
  const f=await fixture(t);
  let acknowledgements=0,retries=0;
  await worker.queue({messages:[{body:{type:'invalid'},ack(){acknowledgements++;},retry(){retries++;}},{body:{type:'push',eventId:'missing',deviceId:'missing'},ack(){acknowledgements++;},retry(){retries++;}}]},f.env);
  assert.equal(acknowledgements,2);
  assert.equal(retries,0);
});

test('existing published catalog preserves lecture IDs, web slugs and PDF-only lectures',async t => {
  let feed;
  try { feed=JSON.parse(await readFile(join(ROOT,'../../../site/reader-publications.json'),'utf8')); }
  catch(error) { if(error.code==='ENOENT') {t.skip('generated site catalog is absent');return;} throw error; }
  const normalized=normalizeFeed(feed);
  assert.equal(normalized.articles.length,feed.articles.length);
  assert.ok(normalized.articles.some(article=>article.topic==='lecture' && article.path.endsWith('.pdf')));
  for(const path of ['/AI_Tech_Review/lectures/../private/','https://example.com/lectures/test/','/AI_Tech_Review/archive/files/../../private.pdf']) {
    assert.throws(()=>normalizeFeed({revision:revision('d'),articles:[{...item('notes','lecture'),path}]}),/invalid_article_path/);
  }
});

test('full 500-article catalog updates remain one transactional SQL batch',async t => {
  const f=await fixture(t);
  const articles=Array.from({length:500},(_,i)=>item(`catalog-${i}`));
  const initial=await f.sync({revision:revision('d'),articles});
  assert.equal(initial.status,200,await initial.clone().text());
  assert.equal((await f.db.prepare('SELECT count(*) n FROM articles WHERE active=1').first()).n,500);
  const updated=await f.sync({revision:revision('e'),articles:articles.map(article=>({...article,title:'수정 제목'}))});
  assert.equal(updated.status,200,await updated.clone().text());
  assert.equal((await updated.json()).newArticles,0);
  assert.equal((await f.db.prepare('SELECT count(*) n FROM publication_events').first()).n,0);
  assert.equal((await f.sync({revision:revision('f'),articles:[...articles,item('too-many')]})).status,400);
});

test('development cookies require both explicit local settings and a loopback API host',async t => {
  const f=await fixture(t,{DEV_ALLOWED_ORIGINS:'http://localhost:8000',DEV_ALLOW_INSECURE_COOKIE:'true'});
  const local=await f.mf.dispatchFetch('http://localhost:8787/v1/devices',{method:'POST',headers:{Origin:'http://localhost:8000','Content-Type':'application/json'},body:'{}'});
  assert.equal(local.status,201);
  const cookie=local.headers.get('Set-Cookie');
  assert.match(cookie,/^reader_session=/);
  assert.equal(cookie.includes('; Secure'),false);
  assert.equal(local.headers.get('Access-Control-Allow-Origin'),'http://localhost:8000');
  const production=await f.request('/v1/devices',{method:'POST',body:{},origin:'http://localhost:8000'});
  assert.match(production.headers.get('Set-Cookie'),/^__Host-reader_session=/);
  assert.ok(production.headers.get('Set-Cookie').includes('; Secure'));
});

test('server expires year-old device tokens, and invalid development configuration stays closed',async t => {
  const f=await fixture(t);
  const current=await f.register();
  await f.db.prepare('UPDATE devices SET created_at=? WHERE id=?').bind(Date.now()-366*86_400_000,current.id).run();
  assert.equal((await f.request('/v1/subscription',{cookie:current.cookie})).status,401);
  const bad=await fixture(t,{DEV_ALLOWED_ORIGINS:'https://evil.example'});
  const response=await bad.request('/v1/config');
  assert.equal(response.status,503);
  assert.equal(response.headers.has('Access-Control-Allow-Origin'),false);
  assert.equal((await response.json()).error,'invalid_development_config');
});
