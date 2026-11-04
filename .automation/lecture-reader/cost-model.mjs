/** Planning model, not measured billing. USD prices checked 2026-11-04.
 * Run: node .automation/lecture-reader/cost-model.mjs
 * Existing backend/frontend files are intentionally neither imported nor changed.
 */
import {pathToFileURL} from 'node:url';

export const AS_OF = '2026-11-04';
export const SOURCES = Object.freeze({
  workers: 'https://developers.cloudflare.com/workers/platform/pricing/',
  workersLimits: 'https://developers.cloudflare.com/workers/platform/limits/',
  d1: 'https://developers.cloudflare.com/d1/platform/pricing/',
  d1Limits: 'https://developers.cloudflare.com/d1/platform/limits/',
  durableObjects: 'https://developers.cloudflare.com/durable-objects/platform/pricing/',
  r2: 'https://developers.cloudflare.com/r2/pricing/',
  staticAssets: 'https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/',
  pages: 'https://developers.cloudflare.com/pages/functions/pricing/',
});
export const PRICES = Object.freeze({
  workers: {minimumMonthlyUSD:5, includedRequests:10e6, requestPerMillionUSD:.30,
    includedCpuMs:30e6, cpuPerMillionMsUSD:.02, freeRequestsPerDay:100000, freeCpuMsPerRequest:10},
  d1: {includedReadRows:25e9, includedWriteRows:50e6, readPerMillionUSD:.001,
    writePerMillionUSD:1, includedStorageGB:5, storagePerGBMonthUSD:.75,
    freeReadsPerDay:5e6, freeWritesPerDay:100000, freeDatabaseBytes:500e6,
    freeAccountStorageBytes:5e9, paidDatabaseBytes:10e9, paidAccountStorageBytes:1e12,
    includedPaidDatabases:100000, additionalDatabaseMonthlyUSD:.10},
  durableObjects: {includedRequests:1e6, requestPerMillionUSD:.15, incomingMessagesPerRequest:20,
    includedDurationGBSeconds:400000, durationPerMillionGBSecondsUSD:12.50,
    allocatedGB:.128, sqliteIncludedStorageGB:5, sqliteStoragePerGBMonthUSD:.20},
  r2Standard: {includedStorageGB:10, storagePerGBMonthUSD:.015, includedClassA:1e6,
    classAPerMillionUSD:4.50, includedClassB:10e6, classBPerMillionUSD:.36, egressUSD:0},
});

export const DEFAULTS = Object.freeze({
  dau:100, days:30, minutesPerDay:30, pollSeconds:4, eventDebounceSeconds:.25,
  strokesPerUserDay:500, eraseFraction:.20, strokeBytes:1000, operationsPerBatch:1,
  progressSavesPerUserDay:30, snapshotsPerUserDay:1, dailyLoginRequests:2,
  openingRequests:3, preflightRequestsPerUserDay:5, onboardingRequestsPerUser:6,
  // D1 billing counts physical rows/index changes, not just HTTP operations.
  // 3 logical writes per put + 2 index writes; existing-stroke deletion is 3+1.
  writeRowsPerPut:5, writeRowsPerErase:4, rateWriteRowsPerMutationRequest:1,
  progressWriteRows:1, activeRateBucketsPerDay:1, rateBucketInsertAndCleanupExtraRows:5,
  authAndCleanupWriteRowsPerUserDay:25, onboardingWriteRowsPerUser:33,
  pollFixedReadRows:6, mutationFixedReadRows:8, operationReadRows:6,
  snapshotFixedReadRows:5, authAndOpeningReadRowsPerUserDay:30,
  onboardingReadRowsPerUser:20,
  storageOverheadMultiplier:1.25, metadataBytesPerUser:8000,
  initialDatabaseBytes:364544, averageCpuMs:5,
  notebookMaxRows:25000, notebookMaxActiveBytes:12e6,
});

const M = 1e6;
const GB = 1e9;
const positive = (v,name,allowZero=false) => {
  if(!Number.isFinite(v)||(allowZero?v<0:v<=0))throw new TypeError(`Invalid ${name}`);
};
const excess = (used,included) => Math.max(0,used-included);
const costPerMillion = (used,included,price) => excess(used,included)/M*price;
const roundedMillionCost = (used,included,price) => Math.ceil(excess(used,included)/M)*price;

/** Uniform synthetic writing bursts; each saved burst resets the idle timer.
 * Zero network latency is a request-count assumption, not a performance claim.
 * A mutation cycle does GET changes, POST operations, then GET changes again.
 */
export function simulateSchedule(options={}) {
  const {minutesPerDay,pollSeconds,eventDebounceSeconds,operationsPerBatch,
    strokesPerUserDay,eraseFraction}={...DEFAULTS,...options};
  for(const [k,v] of Object.entries({minutesPerDay,pollSeconds,operationsPerBatch,strokesPerUserDay}))positive(v,k);
  if(!Number.isInteger(operationsPerBatch)||operationsPerBatch>100)throw new TypeError('Batch must be 1..100');
  if(eraseFraction<0||eraseFraction>1)throw new TypeError('Invalid eraseFraction');
  const duration=minutesPerDay*60,operations=strokesPerUserDay*(1+eraseFraction);
  const writeBatches=Math.ceil(operations/operationsPerBatch);
  let idlePolls=0,nextIdle=Infinity;
  for(let i=0;i<writeBatches;i++) {
    const eventTime=i*duration/writeBatches;
    while(nextIdle<eventTime){idlePolls++;nextIdle+=pollSeconds;}
    nextIdle=eventTime+eventDebounceSeconds+pollSeconds;
  }
  while(nextIdle<duration){idlePolls++;nextIdle+=pollSeconds;}
  return {operations,writeBatches,idlePolls,preAndPostWriteReads:2*writeBatches,
    deltaRequests:idlePolls+2*writeBatches,
    idleReadOnlyPolls:Math.floor(duration/pollSeconds),
    additiveUpperDeltaRequests:Math.floor(duration/pollSeconds)+2*writeBatches};
}

export function workerPaidCost(requests,cpuMs) {
  const p=PRICES.workers;
  return {minimumUSD:p.minimumMonthlyUSD,
    requestsUSD:costPerMillion(requests,p.includedRequests,p.requestPerMillionUSD),
    cpuUSD:costPerMillion(cpuMs,p.includedCpuMs,p.cpuPerMillionMsUSD)};
}

/** Counter-based final implementation: no per-save full-book COUNT/SUM scan.
 * Storage and D1 physical-row estimates are tunable until live metrics exist.
 * A 30-day projection is NOT executable on one database once capacity is hit.
 */
export function estimate(options={}) {
  const a={...DEFAULTS,...options};
  for(const [name,value] of Object.entries(a))positive(value,name,
    ['eraseFraction','eventDebounceSeconds','initialDatabaseBytes','metadataBytesPerUser',
      'progressSavesPerUserDay','snapshotsPerUserDay','averageCpuMs'].includes(name));
  if(!Number.isInteger(a.days)||!Number.isInteger(a.dau)||a.eraseFraction>1)throw new TypeError('Invalid cohort');
  const schedule=simulateSchedule(a),erasures=a.strokesPerUserDay*a.eraseFraction;
  // Progress is normally piggybacked onto existing sync cycles. If there are
  // fewer cycles, budget a pre-read for each remaining progress-only cycle.
  const progressExtraReads=Math.max(0,a.progressSavesPerUserDay-schedule.writeBatches);
  const deltaRequests=schedule.deltaRequests+progressExtraReads;
  const mutationRequests=schedule.writeBatches+a.progressSavesPerUserDay;
  const dailyRequestsPerUser=deltaRequests+mutationRequests+a.dailyLoginRequests+
    a.openingRequests+a.preflightRequestsPerUserDay;
  const monthlyRequests=a.dau*(a.days*dailyRequestsPerUser+a.onboardingRequestsPerUser);
  const dailyWritesPerUser=a.strokesPerUserDay*a.writeRowsPerPut+erasures*a.writeRowsPerErase+
    mutationRequests*a.rateWriteRowsPerMutationRequest+a.progressSavesPerUserDay*a.progressWriteRows+
    a.activeRateBucketsPerDay*a.rateBucketInsertAndCleanupExtraRows+a.authAndCleanupWriteRowsPerUserDay;
  let monthlyReads=0,legacyFullScanExtraReads=0,storageGBMonths=0;
  const daily=[];
  const baseBytes=a.initialDatabaseBytes+a.dau*a.metadataBytesPerUser;
  for(let day=1;day<=a.days;day++) {
    const startRows=(day-1)*a.strokesPerUserDay;
    const averageRows=startRows+a.strokesPerUserDay/2;
    const readsPerUser=deltaRequests*a.pollFixedReadRows+
      mutationRequests*a.mutationFixedReadRows+schedule.operations*a.operationReadRows+
      schedule.operations+a.snapshotsPerUserDay*(startRows+a.snapshotFixedReadRows)+
      a.authAndOpeningReadRowsPerUserDay;
    const reads=a.dau*(readsPerUser+(day===1?a.onboardingReadRowsPerUser:0));
    const writes=a.dau*(dailyWritesPerUser+(day===1?a.onboardingWriteRowsPerUser:0));
    const activeJson=day*a.strokesPerUserDay*(1-a.eraseFraction)*a.strokeBytes;
    const changelogJson=day*a.strokesPerUserDay*a.strokeBytes;
    const storageBytes=baseBytes+a.dau*(activeJson+changelogJson)*a.storageOverheadMultiplier;
    monthlyReads+=reads;
    // Compare the old book scan with the one-row capacity counter lookup.
    legacyFullScanExtraReads+=a.dau*mutationRequests*Math.max(0,averageRows-1);
    // Mean end-of-day holdings approximates GB-month; it is not a live size metric.
    storageGBMonths+=storageBytes/GB/a.days;
    daily.push({day,requests:a.dau*(dailyRequestsPerUser+(day===1?a.onboardingRequestsPerUser:0)),
      readRows:reads,writeRows:writes,estimatedStorageBytes:storageBytes,
      perNotebookRows:day*a.strokesPerUserDay,perNotebookActiveBytes:activeJson});
  }
  const monthlyWrites=daily.reduce((sum,d)=>sum+d.writeRows,0);
  const end=daily.at(-1),p=PRICES.d1;
  const worker=workerPaidCost(monthlyRequests,monthlyRequests*a.averageCpuMs);
  const d1={readUSD:costPerMillion(monthlyReads,p.includedReadRows,p.readPerMillionUSD),
    writeUSD:costPerMillion(monthlyWrites,p.includedWriteRows,p.writePerMillionUSD),
    storageUSD:excess(storageGBMonths,p.includedStorageGB)*p.storagePerGBMonthUSD};
  const totalUSD=Object.values(worker).reduce((s,v)=>s+v,0)+Object.values(d1).reduce((s,v)=>s+v,0);
  const firstDay=predicate=>daily.find(predicate)?.day??null;
  return {asOf:AS_OF,assumptions:a,schedule:{...schedule,progressExtraReads},
    dailyRequestsPerUser,monthlyRequests,monthlyReadRows:monthlyReads,monthlyWriteRows:monthlyWrites,
    legacyFullScanExtraReadRowsRemoved:legacyFullScanExtraReads,
    storage:{estimatedEndGB:end.estimatedStorageBytes/GB,estimatedGBMonths:storageGBMonths,
      activeInkEndBytes:a.dau*end.perNotebookActiveBytes,
      changelogInkEndBytes:a.dau*a.days*a.strokesPerUserDay*a.strokeBytes,
      strokeRows:a.dau*a.days*a.strokesPerUserDay,
      changeRows:a.dau*a.days*schedule.operations,
      estimateMultiplier:a.storageOverheadMultiplier},
    firstLimitDay:{freeWorkerRequests:firstDay(d=>d.requests>PRICES.workers.freeRequestsPerDay),
      freeD1Reads:firstDay(d=>d.readRows>p.freeReadsPerDay),
      freeD1Writes:firstDay(d=>d.writeRows>p.freeWritesPerDay),
      freeDatabase:firstDay(d=>d.estimatedStorageBytes>p.freeDatabaseBytes),
      paidDatabase:firstDay(d=>d.estimatedStorageBytes>p.paidDatabaseBytes),
      notebookActiveInk:firstDay(d=>d.perNotebookActiveBytes>=a.notebookMaxActiveBytes),
      notebookRows:firstDay(d=>d.perNotebookRows>=a.notebookMaxRows)},
    paidProjection:{worker,d1,totalUSD,incrementalIfAlreadyPaidUSD:totalUSD-worker.minimumUSD,
      executableOnOneDatabase:!daily.some(d=>d.estimatedStorageBytes>p.paidDatabaseBytes),
      actualPlanConfirmed:false},
    daily};
}

/** Future transport-only comparison; no migration or deployment is performed.
 * Keeps database/storage charges OUT of this number. They do not disappear
 * merely because polling becomes WebSockets. Duration includes unmeasured I/O.
 */
export function estimateDurableTransport({dau=100,days=30,minutesPerDay=30,
  messagesPerUserDay=600,handlerWallMs=10,hibernation=true}={}) {
  const p=PRICES.durableObjects;
  const connections=dau*days,messages=dau*days*messagesPerUserDay;
  const billedRequestUnits=connections+messages/p.incomingMessagesPerRequest;
  const activeSeconds=hibernation?messages*handlerWallMs/1000:dau*days*minutesPerDay*60;
  const durationGBSeconds=activeSeconds*p.allocatedGB;
  return {architecture:'future comparison only',connections,incomingMessages:messages,
    billedRequestUnits,durationGBSeconds,
    requestUSD:roundedMillionCost(billedRequestUnits,p.includedRequests,p.requestPerMillionUSD),
    durationUSD:roundedMillionCost(durationGBSeconds,p.includedDurationGBSeconds,p.durationPerMillionGBSecondsUSD),
    excludes:['Worker connection/authentication CPU and requests','D1 or DO SQLite storage/rows','existing notification traffic']};
}

export function reportRows() {
  return [100,1000,10000].map(dau=>{
    const x=estimate({dau});
    const cpuUSD=[1,5,20].map(averageCpuMs=>({averageCpuMs,
      totalUSD:estimate({dau,averageCpuMs}).paidProjection.totalUSD}));
    return {dau,monthlyRequests:x.monthlyRequests,monthlyReadRows:x.monthlyReadRows,
      monthlyWriteRows:x.monthlyWriteRows,endGB:x.storage.estimatedEndGB,
      storageGBMonths:x.storage.estimatedGBMonths,limits:x.firstLimitDay,
      paidUSD:cpuUSD,oneDatabaseFeasible:x.paidProjection.executableOnOneDatabase,
      batch10Requests:estimate({dau,operationsPerBatch:10}).monthlyRequests,
      futureDO10ms:estimateDurableTransport({dau}),futureDO100ms:estimateDurableTransport({dau,handlerWallMs:100})};
  });
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)
  console.log(JSON.stringify({asOf:AS_OF,sources:SOURCES,rows:reportRows()},null,2));
