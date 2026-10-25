import {ApiError,object,readJson,sha256,validArticleId} from './security.js';

const HOUR=3_600_000;
const DAY=86_400_000;
const UUID4=/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const statement=(env,sql,...values)=>env.DB.prepare(sql).bind(...values);

export function kstDay(now=Date.now()) {
  return new Date(now+9*HOUR).toISOString().slice(0,10);
}

async function activeArticle(env,id) {
  validArticleId(id);
  if (!await statement(env,'SELECT id FROM articles WHERE id=? AND active=1',id).first()) throw new ApiError('article_not_found',404);
}

export function metricsArticleQuery(url) {
  if ([...url.searchParams.keys()].some(key=>key!=='articleId') || url.searchParams.getAll('articleId').length>1) throw new ApiError('invalid_fields');
  const id=url.searchParams.has('articleId') ? url.searchParams.get('articleId') : null;
  if (id!==null) validArticleId(id);
  return id;
}

export async function metricsSummary(env,id=null,now=Date.now(),validate=true) {
  if (id!==null && validate) await activeArticle(env,id);
  const row=await statement(env,`SELECT m.*,
    COALESCE((SELECT visitors FROM metrics_daily_counts WHERE day=?),0) AS today_visitors,
    (SELECT COUNT(*) FROM subscriptions WHERE (expiration_time IS NULL OR expiration_time>?)
      AND (review_enabled=1 OR lecture_enabled=1)) AS active_subscribers,
    COALESCE(a.opens,0) AS article_opens,COALESCE(a.shares,0) AS article_shares,COALESCE(a.copies,0) AS article_copies
    FROM metrics_state m LEFT JOIN metrics_articles a ON a.article_id=? WHERE m.id=1`,kstDay(now),now,id).first();
  if (!row) throw new ApiError('metrics_not_configured',503);
  return {ok:true,since:row.since,site:{
    visitors:Number(row.visitors),todayVisitors:Number(row.today_visitors),opens:Number(row.opens),
    shares:Number(row.shares),copies:Number(row.copies),activeSubscribers:Number(row.active_subscribers),
    subscriptionRegistrations:Number(row.subscription_registrations),articleNotificationsSent:Number(row.article_notifications_sent),
  },article:id===null ? null : {id,opens:Number(row.article_opens),shares:Number(row.article_shares),copies:Number(row.article_copies)}};
}

async function limit(env,key,window,maximum,now) {
  const bucket=Math.floor(now/window);
  const result=await statement(env,`INSERT INTO rate_limits(key,hits,expires_at) VALUES(?,1,?)
    ON CONFLICT(key) DO UPDATE SET hits=hits+1 WHERE hits<?`,`${key}:${bucket}`,(bucket+1)*window,maximum).run();
  if (!Number(result.meta?.changes || 0)) throw new ApiError('rate_limited',429);
}

function excludedRequest(request) {
  const purpose=`${request.headers.get('Sec-Purpose') || ''} ${request.headers.get('Purpose') || ''}`;
  return /prefetch|prerender/i.test(purpose) || /bot\b|spider|crawler|headlesschrome|lighthouse|facebookexternalhit|preview/i.test(request.headers.get('User-Agent') || '') ||
    request.headers.get('Sec-GPC')==='1' || request.headers.get('DNT')==='1';
}

export async function recordMetrics(request,env) {
  const body=object(await readJson(request,512),['type','visitorId','eventId','articleId']);
  if (!['open','share','copy'].includes(body.type) || typeof body.visitorId!=='string' || typeof body.eventId!=='string' || !UUID4.test(body.visitorId) || !UUID4.test(body.eventId)) throw new ApiError('invalid_metrics_event');
  if (body.articleId!==null) await activeArticle(env,body.articleId);
  else if (body.type!=='open') throw new ApiError('article_required');
  if (excludedRequest(request)) return metricsSummary(env,body.articleId,Date.now(),false);
  if (typeof env.RATE_LIMIT_SALT!=='string' || env.RATE_LIMIT_SALT.length<32) throw new ApiError('server_not_configured',503);
  const now=Date.now();
  const [visitorHash,eventHash,ipHash]=await Promise.all([
    sha256(`${env.RATE_LIMIT_SALT}:metrics-visitor:${body.visitorId.toLowerCase()}`),
    sha256(`${env.RATE_LIMIT_SALT}:metrics-event:${body.eventId.toLowerCase()}`),
    sha256(`${env.RATE_LIMIT_SALT}:metrics-ip:${Math.floor(now/DAY)}:${request.headers.get('CF-Connecting-IP') || 'unknown'}`),
  ]);
  await limit(env,`metrics-visitor:${visitorHash}`,HOUR,120,now);
  await limit(env,`metrics-ip:${ipHash}`,HOUR,600,now);
  if (body.type!=='open') await limit(env,`metrics-action:${visitorHash}`,DAY,60,now);
  const day=kstDay(now);
  const statements=[
    statement(env,'INSERT OR IGNORE INTO metrics_visitors(visitor_hash) VALUES(?)',visitorHash),
    statement(env,'INSERT OR IGNORE INTO metrics_daily_visitors(day,visitor_hash,expires_at) VALUES(?,?,?)',day,visitorHash,now+2*DAY),
  ];
  if (body.type==='open' && body.articleId!==null) statements.push(statement(env,
    'INSERT OR IGNORE INTO metrics_daily_opens(day,visitor_hash,article_id,expires_at) VALUES(?,?,?,?)',day,visitorHash,body.articleId,now+2*DAY));
  if (body.type!=='open') statements.push(statement(env,
    'INSERT OR IGNORE INTO metrics_actions(event_hash,article_id,kind,expires_at) VALUES(?,?,?,?)',eventHash,body.articleId,body.type,now+7*DAY));
  // D1 batch transactions plus insert triggers keep deduplication and counters atomic.
  await env.DB.batch(statements);
  return metricsSummary(env,body.articleId,now,false);
}

export async function pruneMetrics(env,now=Date.now()) {
  await env.DB.batch(['metrics_daily_visitors','metrics_daily_opens','metrics_actions'].map(table=>statement(env,`DELETE FROM ${table} WHERE expires_at<?`,now)));
}
