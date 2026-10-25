import {ApiError} from './security.js';
import {kstDay} from './metrics.js';

const DAY=86_400_000;
const MAX_DAYS=3660;
const MAX_ARTICLES=500;

function calendarDay(value) {
  if (typeof value!=='string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new ApiError('invalid_date');
  const time=Date.parse(`${value}T00:00:00.000Z`);
  if (!Number.isFinite(time) || new Date(time).toISOString().slice(0,10)!==value) throw new ApiError('invalid_date');
  return time;
}

export function discoveryRange(url,now=Date.now()) {
  const params=url.searchParams;
  for(const key of params.keys()) if (!['period','from','to'].includes(key) || params.getAll(key).length!==1) throw new ApiError('invalid_fields');
  if (params.has('from') || params.has('to')) {
    if (params.has('period') || !params.has('from') || !params.has('to')) throw new ApiError('invalid_range');
    const from=params.get('from'),to=params.get('to');
    const difference=calendarDay(to)-calendarDay(from);
    if (difference<0 || difference/DAY+1>MAX_DAYS) throw new ApiError('invalid_range');
    return {from,to,period:'custom'};
  }
  const period=params.has('period') ? params.get('period') : 'all';
  if (!['all','7d','30d','90d'].includes(period)) throw new ApiError('invalid_period');
  if (period==='all') return {from:null,to:null,period};
  const to=kstDay(now),days=Number(period.slice(0,-1));
  const from=new Date(calendarDay(to)-(days-1)*DAY).toISOString().slice(0,10);
  return {from,to,period};
}

export async function reviewDiscovery(env,range) {
  const common=`SELECT a.id,COALESCE(m.opens,0) AS opens,COALESCE(m.likes,0) AS likes,
    COALESCE(m.shares,0) AS shares,COALESCE(m.copies,0) AS copies,`;
  const end=`FROM articles a LEFT JOIN metrics_articles m ON m.article_id=a.id
    ${range.period==='all' ? '' : 'LEFT JOIN activity p ON p.article_id=a.id'}
    WHERE a.active=1 ORDER BY a.id LIMIT ${MAX_ARTICLES+1}`;
  const sql=range.period==='all' ? `${common} COALESCE(m.opens,0) AS period_opens,COALESCE(m.likes,0) AS period_likes ${end}` :
    `WITH activity AS (SELECT article_id,SUM(opens) AS opens,SUM(likes) AS likes
      FROM metrics_article_daily WHERE day>=? AND day<=? GROUP BY article_id)
    ${common} COALESCE(p.opens,0) AS period_opens,COALESCE(p.likes,0) AS period_likes ${end}`;
  const query=env.DB.prepare(sql);
  const results=await env.DB.batch([
    env.DB.prepare('SELECT since,discovery_activity_since FROM metrics_state WHERE id=1'),
    range.period==='all' ? query : query.bind(range.from,range.to),
  ]);
  const state=results[0].results[0],rows=results[1].results;
  if (!state) throw new ApiError('discovery_not_configured',503);
  if (rows.length>MAX_ARTICLES) throw new ApiError('catalog_too_large',503);
  return {ok:true,since:state.since,activitySince:state.discovery_activity_since,range,articles:rows.map(row=>({
    id:row.id,opens:Number(row.opens),likes:Number(row.likes),shares:Number(row.shares),copies:Number(row.copies),
    periodOpens:Number(row.period_opens),periodLikes:Number(row.period_likes),
  }))};
}
