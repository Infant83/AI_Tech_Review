import {
  ApiError, SITE_ORIGIN, SITE_ROOT, TOPICS, allowedOrigins, article, assertOrigin,
  decode64, equalSecret, object, pushSubscription, randomToken, readJson, readToken,
  responseHeaders, sessionCookie, sha256, topics, validArticleId,
} from './security.js';
import {webPushRequest} from './web-push.js';
import {metricsArticleQuery,metricsSummary,pruneMetrics,recordMetrics} from './metrics.js';

const PUBLIC_FEED = `${SITE_ORIGIN}${SITE_ROOT}reader-publications.json`;
const MAX_CATALOG = 500;
const FANOUT_PAGE = 20;
const MAX_ATTEMPTS = 6;
const HOUR = 3_600_000;
const DAY = 86_400_000;
const LEASE = 120_000;

const statement = (env, sql, ...values) => env.DB.prepare(sql).bind(...values);
const first = (env, sql, ...values) => statement(env,sql,...values).first();
const run = (env, sql, ...values) => statement(env,sql,...values).run();
const all = async (env, sql, ...values) => (await statement(env,sql,...values).all()).results;
const changed = result => Number(result.meta?.changes || 0) > 0;

function json(request, env, value, status = 200, extra = {}) {
  const headers = responseHeaders(request,env);
  for (const [key,val] of Object.entries(extra)) headers.set(key,val);
  return new Response(JSON.stringify(value),{status,headers});
}

async function device(request, env, required = true) {
  const token = readToken(request,env);
  const row = token ? await first(env,'SELECT id, user_id FROM devices WHERE token_hash = ? AND created_at > ?',await sha256(token),Date.now()-365*DAY) : null;
  if (required && !row) throw new ApiError('device_session_required',401);
  return row;
}

async function limit(env, key, window, maximum, now = Date.now()) {
  const bucket = Math.floor(now/window);
  const result = await run(env,`INSERT INTO rate_limits(key,hits,expires_at) VALUES(?,1,?)
    ON CONFLICT(key) DO UPDATE SET hits=hits+1 WHERE hits < ?`,`${key}:${bucket}`,(bucket+1)*window,maximum);
  if (!changed(result)) throw new ApiError('rate_limited',429);
}

async function cooldown(env,key,milliseconds) {
  const now = Date.now();
  const result = await run(env,`INSERT INTO rate_limits(key,hits,expires_at) VALUES(?,1,?)
    ON CONFLICT(key) DO UPDATE SET hits=1,expires_at=excluded.expires_at WHERE rate_limits.expires_at<=?`,key,now+milliseconds,now);
  if (!changed(result)) throw new ApiError('rate_limited',429);
}

async function ipLimit(request, env, scope, window, maximum) {
  if (!env.RATE_LIMIT_SALT || env.RATE_LIMIT_SALT.length < 32) throw new ApiError('server_not_configured',503);
  const day = Math.floor(Date.now()/DAY);
  // CF overwrites this header at the edge. Only a rotating hash is persisted.
  const address = request.headers.get('CF-Connecting-IP') || 'unknown';
  const hash = await sha256(`${env.RATE_LIMIT_SALT}:${day}:${address}`);
  await limit(env,`${scope}:${hash}`,window,maximum);
}

async function registerDevice(request, env) {
  object(await readJson(request,256),[]);
  const previous = await device(request,env,false);
  if (previous) return json(request,env,{ok:true,deviceId:previous.id});
  await ipLimit(request,env,'create-hour',HOUR,20);
  await ipLimit(request,env,'create-day',DAY,80);
  const token = randomToken();
  const id = crypto.randomUUID();
  await run(env,'INSERT INTO devices(id,token_hash,user_id,created_at) VALUES(?,?,NULL,?)',id,await sha256(token),Date.now());
  return json(request,env,{ok:true,deviceId:id},201,{'Set-Cookie':sessionCookie(request,env,token)});
}

async function activeArticle(env,id) {
  validArticleId(id);
  const row = await first(env,'SELECT * FROM articles WHERE id=? AND active=1',id);
  if (!row) throw new ApiError('article_not_found',404);
  return row;
}

async function likeState(env,id,deviceId) {
  const row = await first(env,`SELECT COUNT(*) AS count,
    COALESCE(MAX(CASE WHEN device_id=? THEN 1 ELSE 0 END),0) AS liked
    FROM likes WHERE article_id=?`,deviceId || '',id);
  return {ok:true,count:Number(row.count),liked:!!row.liked};
}

async function likes(request,env,id) {
  await activeArticle(env,id);
  const current = await device(request,env,request.method === 'PUT');
  if (request.method === 'PUT') {
    const body = object(await readJson(request,256),['liked']);
    if (typeof body.liked !== 'boolean') throw new ApiError('invalid_liked');
    await limit(env,`like:${current.id}`,HOUR,120);
    await ipLimit(request,env,'like-ip',HOUR,300);
    if (body.liked) await run(env,'INSERT OR IGNORE INTO likes(article_id,device_id,user_id,created_at) VALUES(?,?,?,?)',id,current.id,current.user_id,Date.now());
    else await run(env,'DELETE FROM likes WHERE article_id=? AND device_id=?',id,current.id);
  }
  return json(request,env,await likeState(env,id,current?.id));
}

function subscriptionView(row) {
  if (!row || (row.expiration_time !== null && row.expiration_time <= Date.now())) return {ok:true,subscribed:false,subscription:null,topics:[]};
  return {
    ok:true,subscribed:true,
    subscription:{endpoint:row.endpoint,expirationTime:row.expiration_time,keys:{p256dh:row.p256dh,auth:row.auth}},
    topics:TOPICS.filter(topic => row[`${topic}_enabled`]),
  };
}

async function subscriptions(request,env) {
  const current = await device(request,env);
  if (request.method === 'PUT') {
    const body = object(await readJson(request,4096),['subscription','topics']);
    const subscription = pushSubscription(body.subscription);
    const selected = topics(body.topics);
    // Importing also rejects malformed/off-curve ECDH public keys before storing.
    try { await crypto.subtle.importKey('raw',decode64(subscription.keys.p256dh,65),{name:'ECDH',namedCurve:'P-256'},false,[]); }
    catch { throw new ApiError('invalid_key'); }
    await limit(env,`subscribe:${current.id}`,HOUR,20);
    await ipLimit(request,env,'subscribe-ip',HOUR,100);
    const endpointHash = await sha256(subscription.endpoint);
    const [previous,other] = await Promise.all([
      first(env,'SELECT * FROM subscriptions WHERE device_id=?',current.id),
      first(env,'SELECT * FROM subscriptions WHERE endpoint_hash=?',endpointHash),
    ]);
    if (other && other.device_id !== current.id && (other.p256dh !== subscription.keys.p256dh || other.auth !== subscription.keys.auth)) throw new ApiError('endpoint_in_use',409);
    const same = previous && previous.endpoint_hash === endpointHash && previous.p256dh === subscription.keys.p256dh && previous.auth === subscription.keys.auth;
    const now = Date.now();
    const statements = [statement(env,`UPDATE metrics_state SET subscription_registrations=subscription_registrations+1
      WHERE id=1 AND NOT EXISTS (SELECT 1 FROM subscriptions
        WHERE (device_id=? OR endpoint_hash=?) AND (expiration_time IS NULL OR expiration_time>?)
          AND (review_enabled=1 OR lecture_enabled=1))`,current.id,endpointHash,now)];
    if (other && other.device_id !== current.id) statements.push(statement(env,'DELETE FROM subscriptions WHERE device_id=? AND endpoint_hash=?',other.device_id,endpointHash));
    statements.push(statement(env,`INSERT INTO subscriptions(device_id,endpoint_hash,endpoint,p256dh,auth,expiration_time,review_enabled,lecture_enabled,version,created_at,updated_at)
      VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(device_id) DO UPDATE SET
      endpoint_hash=excluded.endpoint_hash,endpoint=excluded.endpoint,p256dh=excluded.p256dh,auth=excluded.auth,
      expiration_time=excluded.expiration_time,review_enabled=excluded.review_enabled,lecture_enabled=excluded.lecture_enabled,
      version=excluded.version,updated_at=excluded.updated_at`,
      current.id,endpointHash,subscription.endpoint,subscription.keys.p256dh,subscription.keys.auth,subscription.expirationTime,
      Number(selected.includes('review')),Number(selected.includes('lecture')),same ? previous.version : crypto.randomUUID(),previous?.created_at || now,now));
    await env.DB.batch(statements);
  } else if (request.method === 'DELETE') {
    await limit(env,`subscribe:${current.id}`,HOUR,20);
    await run(env,'DELETE FROM subscriptions WHERE device_id=?',current.id);
  }
  return json(request,env,subscriptionView(await first(env,'SELECT * FROM subscriptions WHERE device_id=?',current.id)));
}

export function normalizeFeed(value) {
  object(value,['revision','articles']);
  if (typeof value.revision !== 'string' || !/^[a-f0-9]{40,64}$/.test(value.revision)) throw new ApiError('invalid_revision');
  if (!Array.isArray(value.articles) || !value.articles.length || value.articles.length > MAX_CATALOG) throw new ApiError('invalid_article_catalog');
  const articles = value.articles.map(article).sort((a,b) => a.id.localeCompare(b.id)).map(v => ({id:v.id,path:v.path,title:v.title,publishedAt:v.publishedAt,topic:v.topic}));
  if (new Set(articles.map(v => v.id)).size !== articles.length || new Set(articles.map(v => v.path)).size !== articles.length) throw new ApiError('duplicate_article');
  return {revision:value.revision,articles};
}

async function publisher(request,env) {
  const authorization = request.headers.get('Authorization') || '';
  if (!authorization.startsWith('Bearer ') || !await equalSecret(authorization.slice(7),env.READER_PUBLISH_TOKEN)) throw new ApiError('publisher_unauthorized',401);
}

async function currentPublicFeed(expected, transport) {
  let response;
  try {
    // Workers supports manual/follow, not redirect:error. A redirect is rejected
    // below and cannot change this fixed fetch target. A server nonce avoids
    // replaying a cached feed for a caller-selected older source revision.
    response = await transport(`${PUBLIC_FEED}?reader_revision=${expected.revision}&nonce=${crypto.randomUUID()}`,{
      redirect:'manual',signal:AbortSignal.timeout(10_000),headers:{'Accept':'application/json','Cache-Control':'no-cache, no-store'},cf:{cacheTtl:0,cacheEverything:false},
    });
  } catch { throw new ApiError('public_feed_unavailable',409); }
  if (!response.ok) { await response.body?.cancel(); throw new ApiError('public_feed_unavailable',409); }
  let actual;
  try { actual = normalizeFeed(await readJson(response,300_000)); }
  catch { throw new ApiError('public_feed_not_ready',409); }
  if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new ApiError('public_feed_mismatch',409);
}

async function acquireLock(env,name,owner) {
  const now = Date.now();
  return changed(await run(env,`INSERT INTO operation_locks(name,owner,expires_at) VALUES(?,?,?)
    ON CONFLICT(name) DO UPDATE SET owner=excluded.owner,expires_at=excluded.expires_at
    WHERE operation_locks.expires_at < ?`,name,owner,now+LEASE,now));
}

export async function syncPublications(request,env,transport=fetch) {
  await publisher(request,env);
  const feed = normalizeFeed(await readJson(request,300_000));
  const feedHash = await sha256(JSON.stringify(feed));
  const prior = await first(env,'SELECT feed_hash FROM sync_revisions WHERE revision=?',feed.revision);
  if (prior) {
    if (prior.feed_hash !== feedHash) throw new ApiError('revision_conflict',409);
    await currentPublicFeed(feed,transport);
    const queued = await recoverOutbox(env);
    return json(request,env,{ok:true,replay:true,revision:feed.revision,newArticles:0,queuedEvents:queued});
  }
  const owner = crypto.randomUUID();
  if (!await acquireLock(env,'publication-sync',owner)) throw new ApiError('sync_in_progress',409);
  try {
    // Revalidate while holding the writer lock. This closes the race in which
    // an older request verified before a newer sync but acquired the lock later.
    await currentPublicFeed(feed,transport);
    // A second check under the lock makes concurrent/retried syncs idempotent.
    if (await first(env,'SELECT revision FROM sync_revisions WHERE revision=?',feed.revision)) return json(request,env,{ok:true,replay:true,revision:feed.revision,newArticles:0});
    const initial = !await first(env,'SELECT id FROM publication_state WHERE id=1');
    const existing = new Set((await all(env,'SELECT id FROM articles')).map(row => row.id));
    const fresh = initial ? [] : feed.articles.filter(item => !existing.has(item.id));
    const now = Date.now();
    // json_each keeps SQL generation and transfer constant as the catalog grows.
    // D1 counts the entire transactional batch as one binding API call.
    const events = await Promise.all(fresh.map(async item => ({
      id:await sha256(`article:${item.id}`),articleId:item.id,title:item.title,
      body:item.topic === 'lecture' ? '새 렉처 노트가 발행되었습니다.' : '새로운 심층 리뷰가 발행되었습니다.',
      path:item.path,topic:item.topic,
    })));
    const statements = [
      statement(env,'UPDATE articles SET active=0,updated_at=?',now),
      statement(env,`INSERT INTO articles(id,path,title,published_at,topic,active,created_at,updated_at)
        SELECT json_extract(value,'$.id'),json_extract(value,'$.path'),json_extract(value,'$.title'),
          json_extract(value,'$.publishedAt'),json_extract(value,'$.topic'),1,?,? FROM json_each(?) WHERE 1
        ON CONFLICT(id) DO UPDATE SET path=excluded.path,title=excluded.title,published_at=excluded.published_at,
          topic=excluded.topic,active=1,updated_at=excluded.updated_at`,now,now,JSON.stringify(feed.articles)),
      statement(env,`INSERT OR IGNORE INTO publication_events(id,kind,article_id,revision,title,body,path,topic,created_at)
        SELECT json_extract(value,'$.id'),'article',json_extract(value,'$.articleId'),?,
          json_extract(value,'$.title'),json_extract(value,'$.body'),json_extract(value,'$.path'),
          json_extract(value,'$.topic'),? FROM json_each(?)`,feed.revision,now,JSON.stringify(events)),
    ];
    statements.push(statement(env,`INSERT INTO publication_state(id,revision,initialized_at,updated_at) VALUES(1,?,?,?)
      ON CONFLICT(id) DO UPDATE SET revision=excluded.revision,updated_at=excluded.updated_at`,feed.revision,now,now));
    statements.push(statement(env,'INSERT INTO sync_revisions(revision,feed_hash,applied_at) VALUES(?,?,?)',feed.revision,feedHash,now));
    await env.DB.batch(statements);
    const queued = await recoverOutbox(env);
    return json(request,env,{ok:true,baseline:initial,revision:feed.revision,newArticles:fresh.length,queuedEvents:queued});
  } finally { await run(env,'DELETE FROM operation_locks WHERE name=? AND owner=?','publication-sync',owner); }
}

async function testSubscription(request,env) {
  const current = await device(request,env);
  object(await readJson(request,256),[]);
  const sub = await first(env,'SELECT * FROM subscriptions WHERE device_id=?',current.id);
  if (!subscriptionView(sub).subscribed) throw new ApiError('subscription_required',409);
  await cooldown(env,`test-minute:${current.id}`,60_000);
  await limit(env,`test-day:${current.id}`,DAY,5);
  const now = Date.now();
  const id = `test-${crypto.randomUUID()}`;
  await env.DB.batch([
    statement(env,`INSERT INTO publication_events(id,kind,title,body,path,created_at,fanout_completed)
      VALUES(?,'test',?,?,?,?,1)`,id,'AI Tech Review 알림 테스트','이 기기에서 새 글 알림을 받을 준비가 되었습니다.',SITE_ROOT,now),
    statement(env,'INSERT INTO deliveries(event_id,device_id,subscription_version,created_at) VALUES(?,?,?,?)',id,current.id,sub.version,now),
  ]);
  await env.READER_QUEUE.send({type:'push',eventId:id,deviceId:current.id},{contentType:'json'});
  return json(request,env,{ok:true,queued:true},202);
}

export async function recoverOutbox(env) {
  const now = Date.now();
  const [events,deliveries] = await Promise.all([
    all(env,'SELECT id FROM publication_events WHERE kind=\'article\' AND fanout_completed=0 AND lease_until<? ORDER BY created_at LIMIT 10',now),
    all(env,`SELECT event_id,device_id FROM deliveries WHERE
      ((status IN ('pending','retry') AND retry_at<=?) OR (status='sending' AND lease_until<?))
      AND attempts < ? ORDER BY created_at LIMIT 40`,now,now,MAX_ATTEMPTS),
  ]);
  const messages = [
    ...events.map(row => ({body:{type:'fanout',eventId:row.id},contentType:'json'})),
    ...deliveries.map(row => ({body:{type:'push',eventId:row.event_id,deviceId:row.device_id},contentType:'json'})),
  ];
  if (messages.length) await env.READER_QUEUE.sendBatch(messages);
  return messages.length;
}

export async function fanout(env,eventId) {
  const owner = crypto.randomUUID();
  const now = Date.now();
  const claim = await run(env,`UPDATE publication_events SET lease_owner=?,lease_until=?
    WHERE id=? AND kind='article' AND fanout_completed=0 AND lease_until<?`,owner,now+LEASE,eventId,now);
  if (!changed(claim)) return;
  try {
    const event = await first(env,'SELECT * FROM publication_events WHERE id=?',eventId);
    const active = await first(env,'SELECT active FROM articles WHERE id=?',event.article_id);
    if (!active?.active) {
      await run(env,'UPDATE publication_events SET fanout_completed=1,lease_until=0,lease_owner=NULL WHERE id=? AND lease_owner=?',eventId,owner);
      return;
    }
    // Topic is a trusted enum from the validated catalog; no client SQL fragments.
    const sql = event.topic === 'lecture'
      ? 'SELECT * FROM subscriptions WHERE lecture_enabled=1 AND device_id>? AND created_at<=? AND (expiration_time IS NULL OR expiration_time>?) ORDER BY device_id LIMIT ?'
      : 'SELECT * FROM subscriptions WHERE review_enabled=1 AND device_id>? AND created_at<=? AND (expiration_time IS NULL OR expiration_time>?) ORDER BY device_id LIMIT ?';
    const subscriptions = await all(env,sql,event.fanout_cursor,event.created_at,now,FANOUT_PAGE);
    if (!subscriptions.length) {
      await run(env,'UPDATE publication_events SET fanout_completed=1,lease_until=0,lease_owner=NULL WHERE id=? AND lease_owner=?',eventId,owner);
      return;
    }
    await run(env,`INSERT OR IGNORE INTO deliveries(event_id,device_id,subscription_version,created_at)
      SELECT ?,json_extract(value,'$.device_id'),json_extract(value,'$.version'),? FROM json_each(?)`,
      eventId,now,JSON.stringify(subscriptions.map(({device_id,version})=>({device_id,version}))));
    await env.READER_QUEUE.sendBatch(subscriptions.map(sub => ({body:{type:'push',eventId,deviceId:sub.device_id},contentType:'json'})));
    const completed = subscriptions.length < FANOUT_PAGE;
    await run(env,'UPDATE publication_events SET fanout_cursor=?,fanout_completed=?,lease_owner=NULL,lease_until=0 WHERE id=? AND lease_owner=?',subscriptions.at(-1).device_id,Number(completed),eventId,owner);
    if (!completed) await env.READER_QUEUE.send({type:'fanout',eventId},{contentType:'json'});
  } catch (error) {
    await run(env,'UPDATE publication_events SET lease_owner=NULL,lease_until=0 WHERE id=? AND lease_owner=?',eventId,owner);
    throw error;
  }
}

class RetryDelivery extends Error {
  constructor(delay) { super('retry_delivery'); this.delay = delay; }
}

function retryDelay(response,attempts) {
  const raw = response?.headers.get('Retry-After');
  const seconds = raw && /^\d+$/.test(raw) ? Number(raw) : raw ? Math.ceil((Date.parse(raw)-Date.now())/1000) : 0;
  return Math.max(30,Math.min(3600,Number.isFinite(seconds) && seconds > 0 ? seconds : 30*2**Math.min(attempts,6)));
}

export async function deliver(env,eventId,deviceId,transport=fetch) {
  const owner = crypto.randomUUID();
  const now = Date.now();
  const claim = await run(env,`UPDATE deliveries SET status='sending',lease_owner=?,lease_until=?,attempts=attempts+1
    WHERE event_id=? AND device_id=? AND attempts<? AND
    ((status IN ('pending','retry') AND retry_at<=?) OR (status='sending' AND lease_until<?))`,owner,now+LEASE,eventId,deviceId,MAX_ATTEMPTS,now,now);
  if (!changed(claim)) return;
  const [delivery,event,sub] = await Promise.all([
    first(env,'SELECT * FROM deliveries WHERE event_id=? AND device_id=?',eventId,deviceId),
    first(env,'SELECT * FROM publication_events WHERE id=?',eventId),
    first(env,'SELECT * FROM subscriptions WHERE device_id=?',deviceId),
  ]);
  let allowed = !!event && !!sub && sub.version === delivery.subscription_version && subscriptionView(sub).subscribed;
  if (allowed && event.kind === 'article') {
    const active = await first(env,'SELECT active FROM articles WHERE id=?',event.article_id);
    allowed = !!active?.active && !!sub[`${event.topic}_enabled`];
  }
  if (!allowed) {
    await run(env,"UPDATE deliveries SET status='suppressed',lease_owner=NULL,lease_until=0 WHERE event_id=? AND device_id=? AND lease_owner=?",eventId,deviceId,owner);
    return;
  }
  let response;
  try {
    const subscription = pushSubscription({endpoint:sub.endpoint,expirationTime:sub.expiration_time,keys:{p256dh:sub.p256dh,auth:sub.auth}});
    const payload = {title:event.title,body:event.body,url:`${SITE_ORIGIN}${event.path}`,articleId:event.article_id,tag:event.id};
    response = await transport(new Request(await webPushRequest(subscription,payload,env),{signal:AbortSignal.timeout(10_000)}));
    await response.body?.cancel();
  } catch {
    const delay = retryDelay(null,delivery.attempts);
    await retryRecord(env,eventId,deviceId,owner,delivery.attempts,delay,null,'push_transport_failed');
    if (delivery.attempts < MAX_ATTEMPTS) throw new RetryDelivery(delay);
    return;
  }
  if (response.ok) {
    await run(env,"UPDATE deliveries SET status='sent',sent_at=?,last_http_status=?,lease_owner=NULL,lease_until=0,last_error=NULL WHERE event_id=? AND device_id=? AND lease_owner=?",Date.now(),response.status,eventId,deviceId,owner);
  } else if (response.status === 404 || response.status === 410) {
    await env.DB.batch([
      statement(env,'DELETE FROM subscriptions WHERE device_id=? AND version=?',deviceId,sub.version),
      statement(env,"UPDATE deliveries SET status='dead',last_http_status=?,lease_owner=NULL,lease_until=0 WHERE event_id=? AND device_id=? AND lease_owner=?",response.status,eventId,deviceId,owner),
    ]);
  } else if (response.status === 429 || response.status >= 500 || response.status === 401 || response.status === 403) {
    const delay = retryDelay(response,delivery.attempts);
    await retryRecord(env,eventId,deviceId,owner,delivery.attempts,delay,response.status,'push_provider_retry');
    if (delivery.attempts < MAX_ATTEMPTS) throw new RetryDelivery(delay);
  } else {
    await run(env,"UPDATE deliveries SET status='failed',last_http_status=?,last_error='push_provider_rejected',lease_owner=NULL,lease_until=0 WHERE event_id=? AND device_id=? AND lease_owner=?",response.status,eventId,deviceId,owner);
  }
}

async function retryRecord(env,eventId,deviceId,owner,attempts,delay,status,error) {
  await run(env,'UPDATE deliveries SET status=?,retry_at=?,last_http_status=?,last_error=?,lease_owner=NULL,lease_until=0 WHERE event_id=? AND device_id=? AND lease_owner=?',attempts >= MAX_ATTEMPTS ? 'failed' : 'retry',Date.now()+delay*1000,status,error,eventId,deviceId,owner);
}

export default {
  async fetch(request,env) {
    try {
      allowedOrigins(env);
      const url = new URL(request.url);
      if (url.pathname === '/v1/publications/sync' && request.method === 'POST') {
        assertOrigin(request,env,false);
        return await syncPublications(request,env);
      }
      assertOrigin(request,env,!['GET','OPTIONS'].includes(request.method));
      if (request.method === 'OPTIONS') {
        assertOrigin(request,env,true);
        return new Response(null,{status:204,headers:responseHeaders(request,env)});
      }
      if (url.pathname === '/v1/config' && request.method === 'GET') {
        let publicKey = null;
        try { if (decode64(env.VAPID_PUBLIC_KEY,65)[0] === 4) publicKey = env.VAPID_PUBLIC_KEY; } catch {}
        return json(request,env,{ok:true,vapidPublicKey:publicKey,pushEnabled:!!publicKey && !!env.VAPID_PRIVATE_KEY && !!env.VAPID_SUBJECT,topics:TOPICS});
      }
      if (url.pathname === '/v1/devices' && request.method === 'POST') return await registerDevice(request,env);
      if (url.pathname === '/v1/metrics' && request.method === 'GET') return json(request,env,await metricsSummary(env,metricsArticleQuery(url)));
      if (url.pathname === '/v1/metrics/events' && request.method === 'POST') {
        if (url.search) throw new ApiError('invalid_fields');
        return json(request,env,await recordMetrics(request,env));
      }
      const match = url.pathname.match(/^\/v1\/articles\/([^/]+)\/like$/);
      if (match && ['GET','PUT'].includes(request.method)) {
        let id;
        try { id = decodeURIComponent(match[1]); } catch { throw new ApiError('invalid_article_id'); }
        return await likes(request,env,id);
      }
      if (url.pathname === '/v1/subscription' && ['GET','PUT','DELETE'].includes(request.method)) return await subscriptions(request,env);
      if (url.pathname === '/v1/subscription/test' && request.method === 'POST') return await testSubscription(request,env);
      throw new ApiError('not_found',404);
    } catch (error) {
      if (!(error instanceof ApiError)) console.error('reader-engagement request failure',error?.name || 'Error');
      const status = error instanceof ApiError ? error.status : 500;
      const headers = status === 429 ? {'Retry-After':'60'} : {};
      return json(request,env,{ok:false,error:error instanceof ApiError ? error.code : 'server_error'},status,headers);
    }
  },
  async queue(batch,env) {
    for (const message of batch.messages) {
      try {
        const body = message.body;
        if (body?.type === 'fanout' && typeof body.eventId === 'string') await fanout(env,body.eventId);
        else if (body?.type === 'push' && typeof body.eventId === 'string' && typeof body.deviceId === 'string') await deliver(env,body.eventId,body.deviceId);
        else { console.error('reader-engagement invalid queue message'); message.ack(); continue; }
        message.ack();
      } catch (error) {
        console.error('reader-engagement queue retry',error instanceof RetryDelivery ? 'provider_retry' : 'processing_failure');
        message.retry({delaySeconds:error instanceof RetryDelivery ? error.delay : 60});
      }
    }
  },
  async scheduled(_controller,env,ctx) {
    ctx.waitUntil((async () => {
      await recoverOutbox(env);
      await run(env,'DELETE FROM rate_limits WHERE expires_at<?',Date.now()-DAY);
      // Test notification history is disposable; publication history remains durable.
      await run(env,"DELETE FROM publication_events WHERE kind='test' AND created_at<?",Date.now()-7*DAY);
      await pruneMetrics(env);
    })());
  },
};
