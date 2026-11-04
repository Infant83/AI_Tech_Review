import test from 'node:test';
import assert from 'node:assert/strict';
import {emptyNotebook,diffOperations,mergeNotebook,pendingAfterSnapshot,compactOperations,operationBatches,applyRemoteChanges,switchNotebookView} from './cloud-core.mjs';
const doc={fingerprint:'a'.repeat(64),title:'Lecture',pageCount:3};
const stroke=id=>({id,color:'#0d7c66',width:.003,points:[{x:.1,y:.2,p:.5},{x:.3,y:.4,p:.7}]});
const notes=(...ids)=>({...emptyNotebook(doc),pages:[{number:1,strokes:ids.map(stroke)}]});
const remote=(ids=[],deleted=[])=>({notebook:{id:'book',...doc},pages:[{number:1,strokes:ids.map(stroke)}],deleted:deleted.map(id=>({page:1,id})),bookmarks:[],position:{page:1}});
const ids=value=>value.pages.flatMap(page=>page.strokes.map(item=>item.id)).sort();

test('two writers retain both independent additions in either synchronization order',()=>{
  const a=diffOperations(emptyNotebook(doc),notes('a'));
  const b=diffOperations(emptyNotebook(doc),notes('b'));
  assert.deepEqual(ids(mergeNotebook(remote(['a']),notes('b'),b)),['a','b']);
  assert.deepEqual(ids(mergeNotebook(remote(['b']),notes('a'),a)),['a','b']);
});
test('offline erasure only deletes previously observed ink, preserving new remote strokes',()=>{
  const operations=diffOperations(notes('known'),notes());
  assert.deepEqual(operations,[{type:'delete',page:1,id:'known'}]);
  assert.deepEqual(ids(mergeNotebook(remote(['known','unknown']),notes(),operations)),['unknown']);
});
test('permanent remote tombstones win over stale offline additions and retries',()=>{
  const pending=diffOperations(emptyNotebook(doc),notes('erased','new'));
  assert.deepEqual(ids(mergeNotebook(remote([],['erased']),notes('erased','new'),pending)),['new']);
  assert.deepEqual(pendingAfterSnapshot(pending,remote(['new'],['erased'])),[]);
  assert.deepEqual(compactOperations([{type:'delete',page:1,id:'a'},{type:'put',page:1,stroke:stroke('a')}]),[{type:'delete',page:1,id:'a'}]);
});
test('missing remote stroke is not enough to acknowledge an erasure without a tombstone',()=>{
  const operation={type:'delete',page:1,id:'late-offline-stroke'};
  assert.deepEqual(pendingAfterSnapshot([operation],remote()),[operation]);
  assert.deepEqual(pendingAfterSnapshot([operation],remote([],['late-offline-stroke'])),[]);
});
test('poll merge preserves local reading position/bookmarks and refuses another PDF',()=>{
  const local={...notes('a'),position:{page:3},bookmarks:[2,3]};
  const merged=mergeNotebook(remote(['a','b']),local,[]);
  assert.deepEqual(merged.position,{page:3}); assert.deepEqual(merged.bookmarks,[2,3]);
  assert.throws(()=>mergeNotebook({...remote(),notebook:{...doc,fingerprint:'b'.repeat(64)}},local,[]),/FINGERPRINT/);
});
test('immutable stroke ID collisions fail without overwriting local or remote data',()=>{
  const changed=notes('a'); changed.pages[0].strokes[0].width=.02;
  assert.throws(()=>diffOperations(notes('a'),changed),/STROKE_ID_CONFLICT/);
  assert.throws(()=>mergeNotebook(remote(['a']),changed,[{type:'put',page:1,stroke:changed.pages[0].strokes[0]}]),/STROKE_ID_CONFLICT/);
});
test('operations are bounded and an oversized stroke is retained for an explicit sync error',()=>{
  const operations=Array.from({length:205},(_,i)=>({type:'put',page:1,stroke:stroke('s'+i)}));
  assert.deepEqual(operationBatches(operations).map(batch=>batch.length),[100,100,5]);
  const original=structuredClone(operations);
  assert.throws(()=>operationBatches(operations,20),/STROKE_TOO_LARGE/);
  assert.deepEqual(operations,original);
});
test('incremental pages preserve unknown ink and keep tombstones across later stale puts',()=>{
  const first=applyRemoteChanges(remote(['a','unrelated']),{changes:[
    {revision:1,type:'delete',page:1,id:'a',stroke:null},{revision:2,type:'put',page:1,id:'b',stroke:stroke('b')},
  ],revision:2,notebookRevision:2,more:false},0);
  assert.deepEqual(ids(remoteNotebookForTest(first)),['b','unrelated']);
  const second=applyRemoteChanges(first,{changes:[{revision:3,type:'put',page:1,id:'a',stroke:stroke('a')}],revision:3,notebookRevision:3,more:false},2);
  assert.deepEqual(ids(remoteNotebookForTest(second)),['b','unrelated']);
  assert.deepEqual(second.deleted,[{page:1,id:'a'}]);
  assert.throws(()=>applyRemoteChanges(first,{changes:[],revision:1,notebookRevision:2,more:false},2),/INVALID_REMOTE/);
});
function remoteNotebookForTest(value){return{document:doc,pages:value.pages};}
test('same-PDF account and notebook switches restore the target before computing edits',()=>{
  for(const [currentKey,targetKey]of[['accountA:bookA','accountA:bookB'],['accountA:bookA','accountB:bookB']]){
    const plan=switchNotebookView({current:notes('private-A'),currentKey,targetKey,target:notes('private-B'),allowUpload:true});
    assert.deepEqual(ids(plan.notebook),['private-B']);assert.deepEqual(plan.added,[]);
    assert.deepEqual(diffOperations(notes('private-B'),plan.notebook),[]);
  }
});
test('only unbound device ink can be explicitly merged, without deleting existing target ink',()=>{
  assert.throws(()=>switchNotebookView({current:notes('local'),currentKey:null,targetKey:'B',target:notes('remote')}),/CONSENT/);
  const plan=switchNotebookView({current:notes('local'),currentKey:null,targetKey:'B',target:notes('remote'),allowUpload:true});
  assert.deepEqual(ids(plan.notebook),['local','remote']);assert.deepEqual(plan.added.map(op=>op.type),['put']);
});
