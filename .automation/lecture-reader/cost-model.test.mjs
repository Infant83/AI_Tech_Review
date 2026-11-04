import test from 'node:test';
import assert from 'node:assert/strict';
import {estimate,simulateSchedule,workerPaidCost,estimateDurableTransport,PRICES} from './cost-model.mjs';
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-7,`${a} != ${b}`);

test('uniform three-second edits reset four-second idle timer instead of double-counting 450 idle polls',()=>{
  const s=simulateSchedule();assert.equal(s.operations,600);assert.equal(s.writeBatches,600);
  assert.equal(s.idleReadOnlyPolls,450);assert.equal(s.idlePolls,0);
  assert.equal(s.deltaRequests,1200);assert.equal(s.additiveUpperDeltaRequests,1650);
});
test('ten-operation bursts include actual idle polls; max100 is not the default batching assumption',()=>{
  const s=simulateSchedule({operationsPerBatch:10});
  assert.equal(s.writeBatches,60);assert.equal(s.idlePolls,420);assert.equal(s.deltaRequests,540);
  assert.throws(()=>simulateSchedule({operationsPerBatch:101}));
});
test('Workers included usage boundaries and arithmetic match official 15M requests/7ms example',()=>{
  assert.deepEqual(workerPaidCost(10e6,30e6),{minimumUSD:5,requestsUSD:0,cpuUSD:0});
  const c=workerPaidCost(15e6,105e6);near(c.minimumUSD+c.requestsUSD+c.cpuUSD,8);
});
test('one user month retains live ink plus all original put payloads in changelog',()=>{
  const x=estimate({dau:1,storageOverheadMultiplier:1,metadataBytesPerUser:0,initialDatabaseBytes:0});
  assert.equal(x.storage.activeInkEndBytes,12e6);assert.equal(x.storage.changelogInkEndBytes,15e6);
  assert.equal(x.storage.strokeRows,15000);assert.equal(x.storage.changeRows,18000);
  near(x.storage.estimatedEndGB,.027);near(x.storage.estimatedGBMonths,.01395);
});
test('counter optimization removes triangular full-book scans rather than treating them as current paid reads',()=>{
  const x=estimate({dau:1});assert.equal(x.legacyFullScanExtraReadRowsRemoved,141731100);
  assert.ok(x.monthlyReadRows<1e6);assert.ok(x.monthlyReadRows<x.legacyFullScanExtraReadRowsRemoved/100);
});
test('index and trigger amplification counts more writes than strokes or requests',()=>{
  const x=estimate({dau:1});assert.equal(x.monthlyWriteRows,107733);
  assert.ok(x.monthlyWriteRows>15000*5);assert.equal(x.monthlyRequests,55206);
});
test('at100 DAU Free requests/writes fail even while Paid read allowance remains sufficient',()=>{
  const x=estimate();assert.equal(x.firstLimitDay.freeWorkerRequests,1);
  assert.equal(x.firstLimitDay.freeD1Writes,1);assert.equal(x.firstLimitDay.freeDatabase,5);
  assert.equal(x.paidProjection.d1.readUSD,0);assert.equal(x.paidProjection.executableOnOneDatabase,true);
  assert.equal(x.firstLimitDay.notebookActiveInk,30);
});
test('1000 and10000 DAU hit onePaidDB capacity before month ends; theoreticalprice is not feasibility',()=>{
  assert.equal(estimate({dau:1000}).firstLimitDay.paidDatabase,9);
  assert.equal(estimate({dau:10000}).firstLimitDay.paidDatabase,1);
  assert.equal(estimate({dau:1000}).paidProjection.executableOnOneDatabase,false);
  assert.equal(estimate({dau:1000}).paidProjection.actualPlanConfirmed,false);
});
test('uncapped retention grows nextmonth; app12MB and25k limits are surfaced separately',()=>{
  const x=estimate({dau:1,days:60});assert.equal(x.firstLimitDay.notebookRows,50);
  assert.equal(x.firstLimitDay.notebookActiveInk,30);assert.equal(x.storage.changelogInkEndBytes,30e6);
});
test('DO hibernating transport accounts20 incomingmessages perrequest and rounds billable units',()=>{
  const x=estimateDurableTransport({dau:10000});
  assert.equal(x.billedRequestUnits,9.3e6);near(x.durationGBSeconds,230400);
  near(x.requestUSD,1.35);assert.equal(x.durationUSD,0);
  near(estimateDurableTransport({dau:10000,handlerWallMs:100}).durationUSD,25);
});
test('nonhibernating socket duration charges allocatedmemory throughall30minutes',()=>{
  const x=estimateDurableTransport({dau:1000,hibernation:false});
  near(x.durationGBSeconds,6912000);near(x.durationUSD,87.5);
});
test('rates useOctober30 D1allowance andcurrentperdatabase limits',()=>{
  assert.equal(PRICES.d1.includedReadRows,25e9);assert.equal(PRICES.d1.freeDatabaseBytes,500e6);
  assert.equal(PRICES.d1.paidDatabaseBytes,10e9);assert.equal(PRICES.r2Standard.egressUSD,0);
});
