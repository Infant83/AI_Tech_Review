import test from 'node:test';
import assert from 'node:assert/strict';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {Miniflare,createFetchMock,Log,LogLevel} from 'miniflare';
import worker from '../src/worker.js';
import {insightsRange,readingInsights,INSIGHTS_LIMITS} from '../src/insights.js';

const ROOT=dirname(dirname(fileURLToPath(import.meta.url)));
const NOW=Date.parse('2026-11-15T02:00:00.000Z');
const URL_BASE='https://api.infant83.io/v1/insights';
const range=(query='',now=NOW)=>insightsRange(new URL(URL_BASE+query),now);
const state={since:'2026-10-25T05:12:00.000Z',discovery_activity_since:'2026-10-26'};
const active=[{id:'review-b'},{id:'lecture:notes-a'},{id:'review-a'}];
function dbFixture({states=[state],articles=active,rows=[]}={}) {
  const calls=[];
  const env={DB:{
    prepare(sql) {
      assert.match(sql,/^SELECT\s/);
      const statement={sql,values:[],bind(...values) { this.values=values; return this; }};
      return statement;
    },
    async batch(statements) {
      calls.push(statements);
      assert.equal(statements.length,3);
      return [states,articles,rows].map(results=>({success:true,results}));
    },
  }};
  return {env,calls};
}
const unavailable=promise=>assert.rejects(promise,error=>error.status===503);

test('insights accepts only a bounded period with inclusive KST midnight boundaries',()=>{
  assert.deepEqual(range(),{period:'7d',from:'2026-11-09',to:'2026-11-15'});
  assert.deepEqual(range('?period=30d'),{period:'30d',from:'2026-10-17',to:'2026-11-15'});
  assert.deepEqual(range('?period=90d'),{period:'90d',from:'2026-08-18',to:'2026-11-15'});
  assert.deepEqual(range('',Date.parse('2026-11-14T14:59:59Z')),{period:'7d',from:'2026-11-08',to:'2026-11-14'});
  assert.deepEqual(range('',Date.parse('2026-11-14T15:00:00Z')),{period:'7d',from:'2026-11-09',to:'2026-11-15'});
  for (const query of ['?period=','?period=all','?period=91d','?period=7D','?period=7d&period=7d',
    '?%70eriod=7d&period=30d','?from=2026-11-01&to=2026-11-15','?to=2099-01-01','?period=7d&articleId=private','?topic=review']) {
    assert.throws(()=>range(query),error=>error.status===400,query);
  }
});

test('same snapshot exposes only sorted public IDs/recorded daily opens and exact scoped sums',async()=>{
  const f=dbFixture({rows:[
    {day:'2026-11-10',article_id:'review-b',opens:2,visitor_hash:'never expose'},
    {day:'2026-11-09',article_id:'review-b',opens:3},
    {day:'2026-11-10',article_id:'lecture:notes-a',opens:1},
    {day:'2026-11-15',article_id:'review-b',opens:0},
  ]});
  const body=await readingInsights(f.env,range(),NOW);
  assert.equal(f.calls.length,1);
  assert.deepEqual(f.calls[0][2].values,['2026-11-09','2026-11-15']);
  assert.match(f.calls[0][1].sql,/active=1.*LIMIT 501/);
  assert.match(f.calls[0][2].sql,/JOIN articles a ON a.id=d.article_id/);
  assert.match(f.calls[0][2].sql,/a.active=1/);
  assert.match(f.calls[0][2].sql,/LIMIT 10001/);
  assert.deepEqual(body.articles,[{id:'lecture:notes-a',periodOpens:1},{id:'review-a',periodOpens:0},{id:'review-b',periodOpens:5}]);
  assert.deepEqual(body.daily,[
    {day:'2026-11-09',articleId:'review-b',opens:3},
    {day:'2026-11-10',articleId:'lecture:notes-a',opens:1},
    {day:'2026-11-10',articleId:'review-b',opens:2},
    {day:'2026-11-15',articleId:'review-b',opens:0},
  ]);
  assert.equal(body.generatedAt,'2026-11-15T02:00:00.000Z');
  assert.deepEqual(body.coverage,{timezone:'Asia/Seoul',collectionStartedOn:'2026-10-25',activityRecordedFrom:'2026-10-26',
    firstDayMayBePartial:true,todayPartial:true,outageHistoryAvailable:false});
  assert.deepEqual(body.limits,INSIGHTS_LIMITS);
  assert.deepEqual(Object.keys(body),['ok','since','activitySince','generatedAt','range','coverage','articles','daily','limits']);
  assert.doesNotMatch(JSON.stringify(body),/visitor_hash|never expose|subscription|deviceId|endpoint|userId/);
});

test('sparse absence stays absent and real retained rows before coverage remain recorded',async()=>{
  const f=dbFixture({states:[{...state,discovery_activity_since:'2026-11-12'}],rows:[{day:'2026-11-10',article_id:'review-a',opens:2}]});
  const body=await readingInsights(f.env,range(),NOW);
  assert.equal(body.daily.length,1);
  assert.equal(body.daily[0].day,'2026-11-10');
  assert.equal(body.coverage.activityRecordedFrom,'2026-11-12');
  assert.equal(body.articles.find(row=>row.id==='review-a').periodOpens,2);
  const empty=await readingInsights(dbFixture({articles:[]}).env,range(),NOW);
  assert.deepEqual(empty.articles,[]); assert.deepEqual(empty.daily,[]);
});

test('missing/incomplete collection state fails instead of inventing coverage',async()=>{
  for (const states of [[],[null],[{}],[{since:state.since}], [{...state,discovery_activity_since:null}],
    [{...state,discovery_activity_since:'2026-02-30'}],[{...state,discovery_activity_since:'2099-01-01'}],
    [{...state,since:'not-a-date'}],[{...state,since:'2026-02-30T00:00:00Z'}],[{...state,since:'2099-01-01T00:00:00Z'}],[state,state]]) {
    await unavailable(readingInsights(dbFixture({states}).env,range(),NOW));
  }
});

test('article and sparse-row caps fail closed rather than returning a partial catalog',async()=>{
  const articles=Array.from({length:501},(_,i)=>({id:`article-${i}`}));
  await assert.rejects(readingInsights(dbFixture({articles}).env,range(),NOW),error=>error.status===503 && error.code==='catalog_too_large');
  await assert.rejects(readingInsights(dbFixture({rows:Array(10_001).fill({})}).env,range(),NOW),error=>error.status===503 && error.code==='insights_too_large');
});

test('exact article and row caps remain available when the response fits its byte budget',async()=>{
  const articles=Array.from({length:500},(_,i)=>({id:`a-${String(i).padStart(3,'0')}`}));
  const selected=range('?period=30d'),rows=[];
  for (let i=0;i<20;i++) for (const article of articles) {
    rows.push({day:new Date(Date.parse(selected.from+'T00:00:00Z')+i*86_400_000).toISOString().slice(0,10),article_id:article.id,opens:1});
  }
  const body=await readingInsights(dbFixture({articles,rows}).env,selected,NOW);
  assert.equal(body.articles.length,500); assert.equal(body.daily.length,10_000);
  assert.equal(body.articles.every(row=>row.periodOpens===20),true);
  assert.equal(new TextEncoder().encode(JSON.stringify(body)).byteLength<=INSIGHTS_LIMITS.maxBytes,true);
});

test('response UTF-8 budget also rejects an otherwise bounded valid sparse result',async()=>{
  const articles=Array.from({length:120},(_,i)=>({id:`${'a'.repeat(165)}-${String(i).padStart(3,'0')}`}));
  const selected=range('?period=90d');
  const rows=[];
  for (let i=0;i<90;i++) for (const article of articles.slice(0,100)) {
    rows.push({day:new Date(Date.parse(selected.from+'T00:00:00Z')+i*86_400_000).toISOString().slice(0,10),article_id:article.id,opens:1});
  }
  assert.equal(rows.length,9000);
  await assert.rejects(readingInsights(dbFixture({articles,rows}).env,selected,NOW),error=>error.status===503 && error.code==='insights_too_large');
});

test('invalid/overflow counts, duplicate or mismatched rows never become misleading totals',async()=>{
  const good={day:'2026-11-10',article_id:'review-a',opens:1};
  for (const rows of [[{...good,opens:null}],[{...good,opens:true}],[{...good,opens:'1'}],
    [{...good,opens:-1}],[{...good,opens:0.5}],[{...good,opens:Number.MAX_SAFE_INTEGER+1}],
    [{...good,article_id:'inactive'}],[{...good,day:'2026-11-08'}],[{...good,day:'2026-11-16'}],
    [{...good,day:'2026-02-30'}],[good,good],
    [{...good,opens:Number.MAX_SAFE_INTEGER},{...good,day:'2026-11-11',opens:1}]]) {
    await unavailable(readingInsights(dbFixture({rows}).env,range(),NOW));
  }
  for (const articles of [[{id:'bad/id'}],[{id:'same'},{id:'same'}]]) await unavailable(readingInsights(dbFixture({articles}).env,range(),NOW));
});

test('failed or malformed database reads produce a closed unavailable response',async()=>{
  const broken={DB:{prepare(){ throw new Error('synthetic read outage'); }}};
  await unavailable(readingInsights(broken,range(),NOW));
  const missing={DB:{prepare:()=>({bind(){return this;}}),batch:async()=>[{results:[state]},{results:[]}]}};
  await unavailable(readingInsights(missing,range(),NOW));
  const failure={DB:{prepare:()=>({bind(){return this;}}),batch:async()=>[{results:[state]},{results:[]},{success:false,results:[]}]}};
  await unavailable(readingInsights(failure,range(),NOW));
});

test('public route preserves exact Origin, bounded errors/cache and cookie-free read-only behavior',async()=>{
  const request=(path,origin='https://infant83.io',method='GET')=>new Request(URL_BASE.replace('/v1/insights',path),{method,headers:origin ? {Origin:origin} : {}});
  const f=dbFixture();
  const response=await worker.fetch(request('/v1/insights'),f.env);
  assert.equal(response.status,200); assert.equal(response.headers.get('Set-Cookie'),null);
  assert.equal(response.headers.get('Cache-Control'),'public, max-age=30');
  assert.equal(response.headers.get('Vary'),'Origin');
  assert.equal(response.headers.get('Access-Control-Allow-Origin'),'https://infant83.io');
  assert.equal((await response.json()).ok,true); assert.equal(f.calls.length,1);
  const anonymous=await worker.fetch(request('/v1/insights',null),dbFixture().env);
  assert.equal(anonymous.status,200); assert.equal(anonymous.headers.get('Set-Cookie'),null);
  const rejected=dbFixture();
  assert.equal((await worker.fetch(request('/v1/insights','https://evil.example'),rejected.env)).status,403);
  assert.equal(rejected.calls.length,0);
  for (const path of ['/v1/insights?period=all','/v1/insights?period=7d&period=7d','/v1/insights?to=2099-01-01']) {
    const invalid=dbFixture(),res=await worker.fetch(request(path),invalid.env);
    assert.equal(res.status,400); assert.equal(res.headers.get('Cache-Control'),'private, no-store'); assert.equal(res.headers.get('Set-Cookie'),null); assert.equal(invalid.calls.length,0);
  }
  const missing=await worker.fetch(request('/v1/insights'),dbFixture({states:[]}).env);
  assert.equal(missing.status,503); assert.equal(missing.headers.get('Cache-Control'),'private, no-store');
  assert.equal((await worker.fetch(request('/v1/insights','https://infant83.io','POST'),dbFixture().env)).status,404);
});

test('actual isolated D1 query excludes inactive/out-of-range records without changing any data',async t=>{
  const mock=createFetchMock(); mock.disableNetConnect();
  const mf=new Miniflare({modules:true,scriptPath:join(ROOT,'.wrangler/test-worker.mjs'),compatibilityDate:'2026-08-06',
    d1Databases:['DB'],fetchMock:mock,log:new Log(LogLevel.ERROR)});
  t.after(()=>mf.dispose());
  const db=await mf.getD1Database('DB');
  await db.exec(`CREATE TABLE metrics_state(id INTEGER PRIMARY KEY,since TEXT,discovery_activity_since TEXT);
CREATE TABLE articles(id TEXT PRIMARY KEY,active INTEGER);
CREATE TABLE metrics_article_daily(day TEXT,article_id TEXT,opens INTEGER,PRIMARY KEY(day,article_id));
CREATE TABLE private_fixture(secret TEXT);`);
  const now=Date.now(),current=insightsRange(new URL(URL_BASE),now),yesterday=new Date(Date.parse(current.to+'T00:00:00Z')-86_400_000).toISOString().slice(0,10);
  await db.batch([
    db.prepare('INSERT INTO metrics_state VALUES(1,?,?)').bind(state.since,'2026-10-26'),
    db.prepare("INSERT INTO articles VALUES('review-a',1),('lecture:notes-a',1),('inactive',0)"),
    db.prepare("INSERT INTO private_fixture VALUES('synthetic-private-value')"),
    db.prepare('INSERT INTO metrics_article_daily VALUES(?,?,?),(?,?,?),(?,?,?),(?,?,?)').bind(current.to,'review-a',2,yesterday,'lecture:notes-a',3,current.to,'inactive',999,'2000-01-01','review-a',999),
  ]);
  const before=await db.batch(['metrics_state','articles','metrics_article_daily','private_fixture'].map(name=>db.prepare(`SELECT * FROM ${name} ORDER BY ${name==='private_fixture' ? '1' : '1,2'}`)));
  const response=await mf.dispatchFetch(URL_BASE,{headers:{Origin:'https://infant83.io'}});
  assert.equal(response.status,200); assert.equal(response.headers.get('Set-Cookie'),null);
  const body=await response.json();
  assert.deepEqual(body.articles,[{id:'lecture:notes-a',periodOpens:3},{id:'review-a',periodOpens:2}]);
  assert.equal(body.daily.length,2);
  assert.doesNotMatch(JSON.stringify(body),/inactive|999|synthetic-private-value|secret/);
  const after=await db.batch(['metrics_state','articles','metrics_article_daily','private_fixture'].map(name=>db.prepare(`SELECT * FROM ${name} ORDER BY ${name==='private_fixture' ? '1' : '1,2'}`)));
  assert.deepEqual(after.map(row=>row.results),before.map(row=>row.results));
});
