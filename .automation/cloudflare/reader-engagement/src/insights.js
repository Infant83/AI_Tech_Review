import {ApiError,validArticleId} from './security.js';
import {kstDay} from './metrics.js';

const DAY=86_400_000;
const encoder=new TextEncoder();
export const INSIGHTS_LIMITS=Object.freeze({maxArticles:500,maxDays:90,maxRows:10_000,maxBytes:750_000});

function calendarDay(value) {
  if (typeof value!=='string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
  const time=Date.parse(`${value}T00:00:00.000Z`);
  return Number.isFinite(time) && new Date(time).toISOString().slice(0,10)===value ? time : null;
}

export function insightsRange(url,now=Date.now()) {
  const params=url.searchParams;
  for (const key of params.keys()) {
    if (key!=='period' || params.getAll(key).length!==1) throw new ApiError('invalid_fields');
  }
  const period=params.has('period') ? params.get('period') : '7d';
  if (!['7d','30d','90d'].includes(period)) throw new ApiError('invalid_period');
  const to=kstDay(now),days=Number(period.slice(0,-1));
  return {period,from:new Date(calendarDay(to)-(days-1)*DAY).toISOString().slice(0,10),to};
}

function unavailable(code='insights_unavailable') { throw new ApiError(code,503); }
function validId(value) {
  try { return validArticleId(value); } catch { return unavailable(); }
}

// No device, session, visitor, subscription or event tables are read here.
// D1 batch keeps the catalog, state and selected recorded counts in one snapshot.
export async function readingInsights(env,range,now=Date.now()) {
  const expected=insightsRange(new URL(`https://insights.invalid/?period=${encodeURIComponent(range?.period || '')}`),now);
  if (range?.from!==expected.from || range?.to!==expected.to) throw new ApiError('invalid_range');
  let results;
  try { results=await env.DB.batch([
    env.DB.prepare('SELECT since,discovery_activity_since FROM metrics_state WHERE id=1'),
    env.DB.prepare(`SELECT id FROM articles WHERE active=1 ORDER BY id LIMIT ${INSIGHTS_LIMITS.maxArticles+1}`),
    env.DB.prepare(`SELECT d.day,d.article_id,d.opens FROM metrics_article_daily d
      JOIN articles a ON a.id=d.article_id
      WHERE a.active=1 AND d.day>=? AND d.day<=?
      ORDER BY d.day,d.article_id LIMIT ${INSIGHTS_LIMITS.maxRows+1}`).bind(range.from,range.to),
  ]); } catch { unavailable(); }
  if (!Array.isArray(results) || results.length!==3 || results.some(row=>row?.success===false || !Array.isArray(row?.results))) unavailable();
  const [states,active,rows]=results.map(row=>row.results);
  if (states.length!==1) unavailable('insights_not_configured');
  if (active.length>INSIGHTS_LIMITS.maxArticles) unavailable('catalog_too_large');
  if (rows.length>INSIGHTS_LIMITS.maxRows) unavailable('insights_too_large');
  if (!states[0] || typeof states[0]!=='object') unavailable('insights_not_configured');
  const {since,discovery_activity_since:activitySince}=states[0];
  const sinceTime=typeof since==='string' ? Date.parse(since) : NaN;
  if (!Number.isFinite(sinceTime) || sinceTime>now || !/^\d{4}-\d{2}-\d{2}T/.test(since)
      || calendarDay(since.slice(0,10))===null
      || calendarDay(activitySince)===null || activitySince>range.to) unavailable('insights_not_configured');
  const collectionStartedOn=kstDay(sinceTime);
  if (activitySince<collectionStartedOn) unavailable('insights_not_configured');
  const totals=new Map();
  for (const row of active) {
    const id=validId(row?.id);
    if (totals.has(id)) unavailable();
    totals.set(id,0);
  }
  const keys=new Set();
  const daily=rows.map(row=>{
    const id=validId(row?.article_id),day=row.day,opens=row.opens;
    if (!totals.has(id) || calendarDay(day)===null || day<range.from || day>range.to || day<collectionStartedOn
        || !Number.isSafeInteger(opens) || opens<0) unavailable();
    const key=`${day}:${id}`;
    if (keys.has(key)) unavailable();
    keys.add(key);
    const total=totals.get(id)+opens;
    if (!Number.isSafeInteger(total)) unavailable();
    totals.set(id,total);
    return {day,articleId:id,opens};
  }).sort((a,b)=>a.day<b.day ? -1 : a.day>b.day ? 1 : a.articleId<b.articleId ? -1 : a.articleId>b.articleId ? 1 : 0);
  const articles=[...totals].sort(([a],[b])=>a<b ? -1 : a>b ? 1 : 0).map(([id,periodOpens])=>({id,periodOpens}));
  const result={ok:true,since,activitySince,generatedAt:new Date(now).toISOString(),range:{...expected},
    coverage:{timezone:'Asia/Seoul',collectionStartedOn,activityRecordedFrom:activitySince,
      firstDayMayBePartial:true,todayPartial:true,outageHistoryAvailable:false},
    articles,daily,limits:{...INSIGHTS_LIMITS}};
  // Fail explicitly rather than silently truncating recorded activity.
  if (encoder.encode(JSON.stringify(result)).byteLength>INSIGHTS_LIMITS.maxBytes) unavailable('insights_too_large');
  return result;
}
