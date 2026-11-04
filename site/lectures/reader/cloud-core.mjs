/** Deterministic notebook synchronization. No network, identity or storage access. */
const FORMAT = 'ai-tech-review-notebook';
const ID = /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}$/;
const fail = code => { throw new Error(code); };
export const strokeKey = (page, id) => page + ':' + id;
export function positionPage(value) { return Number.isInteger(value) ? value : value?.page; }

/** The reader acquires its edit lock synchronously when apply is invoked. */
export async function applyNotebookIfCurrent(expected,readCurrent,apply) {
  const now=readCurrent();
  if(!expected||!now||Object.keys(expected).some(key=>expected[key]!==now[key]))return false;
  await apply();return true;
}

export function normalizeNotebook(value, expected = null) {
  const doc = value?.document;
  if (value?.format !== FORMAT || value.version !== 1 || !doc || !/^[a-f0-9]{64}$/.test(doc.fingerprint) ||
      typeof doc.title !== 'string' || doc.title.length > 500 || !Number.isInteger(doc.pageCount) ||
      doc.pageCount < 1 || doc.pageCount > 10000) fail('INVALID_NOTEBOOK');
  if (expected && (doc.fingerprint !== expected.fingerprint || doc.pageCount !== expected.pageCount)) fail('FINGERPRINT_MISMATCH');
  if (!Array.isArray(value.pages) || value.pages.length > doc.pageCount) fail('INVALID_NOTEBOOK');
  const pagesSeen = new Set(), ids = new Set(); let pointCount = 0;
  const pages = value.pages.map(page => {
    if (!Number.isInteger(page?.number) || page.number < 1 || page.number > doc.pageCount || pagesSeen.has(page.number) ||
        !Array.isArray(page.strokes) || page.strokes.length > 50000) fail('INVALID_NOTEBOOK');
    pagesSeen.add(page.number);
    const strokes = page.strokes.map(stroke => {
      if (!ID.test(stroke?.id) || ids.has(strokeKey(page.number, stroke.id)) || !/^#[a-f0-9]{6}$/i.test(stroke.color) ||
          !Number.isFinite(stroke.width) || stroke.width <= 0 || stroke.width > .1 || !Array.isArray(stroke.points) ||
          !stroke.points.length || stroke.points.length > 100000) fail('INVALID_NOTEBOOK');
      ids.add(strokeKey(page.number, stroke.id)); pointCount += stroke.points.length;
      if (pointCount > 1000000) fail('NOTEBOOK_TOO_LARGE');
      const points = stroke.points.map(point => {
        if (!point || !['x', 'y', 'p'].every(key => Number.isFinite(point[key]) && point[key] >= 0 && point[key] <= 1)) fail('INVALID_NOTEBOOK');
        return {x:point.x, y:point.y, p:point.p};
      });
      return {id:stroke.id, color:stroke.color.toLowerCase(), width:stroke.width, points};
    });
    return {number:page.number, strokes};
  }).sort((a,b) => a.number-b.number);
  const bookmarks = value.bookmarks ?? [];
  if (!Array.isArray(bookmarks) || bookmarks.length > doc.pageCount || bookmarks.some(page => !Number.isInteger(page) || page < 1 || page > doc.pageCount)) fail('INVALID_NOTEBOOK');
  const page = positionPage(value.position) ?? 1;
  if (!Number.isInteger(page) || page < 1 || page > doc.pageCount) fail('INVALID_NOTEBOOK');
  return {format:FORMAT, version:1, document:{fingerprint:doc.fingerprint,title:doc.title,pageCount:doc.pageCount},
    pages, bookmarks:[...new Set(bookmarks)].sort((a,b) => a-b), position:{page}};
}

function strokeMap(notebook) {
  return new Map(notebook.pages.flatMap(page => page.strokes.map(stroke => [strokeKey(page.number,stroke.id),{page:page.number,stroke}])));
}
function sameStroke(a,b) { return JSON.stringify(a) === JSON.stringify(b); }

/** Only strokes previously observed on this device may become delete operations. */
export function diffOperations(previous, current) {
  const before = normalizeNotebook(previous), after = normalizeNotebook(current, before.document);
  const known = strokeMap(before), present = strokeMap(after), operations = [];
  for (const [key,item] of present) {
    if (!known.has(key)) operations.push({type:'put',page:item.page,stroke:item.stroke});
    else if (!sameStroke(known.get(key).stroke,item.stroke)) fail('STROKE_ID_CONFLICT');
  }
  for (const [key,item] of known) if (!present.has(key)) operations.push({type:'delete',page:item.page,id:item.stroke.id});
  return operations;
}

export function tombstoneSet(deleted, pageCount) {
  if (!Array.isArray(deleted) || deleted.length > 1000000) fail('INVALID_REMOTE_NOTEBOOK');
  return new Set(deleted.map(item => {
    if (!Number.isInteger(item?.page) || item.page < 1 || item.page > pageCount || !ID.test(item.id)) fail('INVALID_REMOTE_NOTEBOOK');
    return strokeKey(item.page,item.id);
  }));
}

export function compactOperations(operations, deleted = new Set()) {
  const result = new Map();
  for (const operation of operations) {
    const id = operation.type === 'put' ? operation.stroke.id : operation.id;
    const key = strokeKey(operation.page,id);
    if (deleted.has(key)) continue;
    // Once an ID has been erased, an offline redo cannot resurrect that ID.
    if (result.get(key)?.type === 'delete') continue;
    result.set(key,operation);
  }
  return [...result.values()];
}

export function remoteNotebook(snapshot) {
  const metadata = snapshot?.notebook;
  if (!metadata) fail('INVALID_REMOTE_NOTEBOOK');
  const notebook = normalizeNotebook({format:FORMAT,version:1,
    document:{fingerprint:metadata.fingerprint,title:metadata.title,pageCount:metadata.pageCount},
    pages:snapshot.pages,bookmarks:snapshot.bookmarks ?? [],position:snapshot.position ?? {page:1}});
  const deleted = tombstoneSet(snapshot.deleted ?? [],notebook.document.pageCount);
  return {notebook,deleted};
}

/** Apply an ordered incremental feed to the cached authoritative snapshot. */
export function applyRemoteChanges(snapshot, delta, since) {
  const {notebook,deleted}=remoteNotebook(snapshot), strokes=strokeMap(notebook);
  if(!delta||!Array.isArray(delta.changes)||delta.changes.length>1000||!Number.isSafeInteger(delta.revision)||delta.revision<since||
      typeof delta.more!=='boolean'||!Number.isSafeInteger(delta.notebookRevision)||delta.notebookRevision<delta.revision)fail('INVALID_REMOTE_NOTEBOOK');
  let cursor=since;
  const tombstones=new Map((snapshot.deleted||[]).map(item=>[strokeKey(item.page,item.id),item]));
  for(const change of delta.changes){
    if(!Number.isSafeInteger(change?.revision)||change.revision<=cursor||change.revision>delta.revision||
        !Number.isInteger(change.page)||change.page<1||change.page>notebook.document.pageCount||!ID.test(change.id)||
        !['put','delete'].includes(change.type))fail('INVALID_REMOTE_NOTEBOOK');
    cursor=change.revision;const key=strokeKey(change.page,change.id);
    if(change.type==='delete'){deleted.add(key);tombstones.set(key,{page:change.page,id:change.id});strokes.delete(key);}
    else if(!deleted.has(key)){
      const checked=normalizeNotebook({...emptyNotebook(notebook.document),pages:[{number:change.page,strokes:[change.stroke]}]});
      const stroke=checked.pages[0].strokes[0];if(stroke.id!==change.id)fail('INVALID_REMOTE_NOTEBOOK');
      if(strokes.has(key)&&!sameStroke(strokes.get(key).stroke,stroke))fail('STROKE_ID_CONFLICT');
      strokes.set(key,{page:change.page,stroke});
    }
  }
  const pages=new Map();
  for(const item of strokes.values()){if(!pages.has(item.page))pages.set(item.page,[]);pages.get(item.page).push(item.stroke);}
  const merged=normalizeNotebook({...notebook,pages:[...pages].map(([number,items])=>({number,strokes:items}))});
  return {...snapshot,notebook:{...snapshot.notebook,revision:delta.notebookRevision},pages:merged.pages,
    deleted:[...tombstones.values()],position:merged.position,bookmarks:merged.bookmarks};
}

export function pendingAfterSnapshot(operations, snapshot) {
  const {notebook,deleted} = remoteNotebook(snapshot), remote = strokeMap(notebook);
  return compactOperations(operations).filter(operation => {
    const key = strokeKey(operation.page,operation.type === 'put' ? operation.stroke.id : operation.id);
    if (deleted.has(key)) return false;
    if (operation.type === 'delete') return true;
    const found = remote.get(key);
    if (found && !sameStroke(found.stroke,operation.stroke)) fail('STROKE_ID_CONFLICT');
    return !found;
  });
}

/** Remote unknown strokes survive; local intent is represented only by queued operations. */
export function mergeNotebook(snapshot, local, pending) {
  const {notebook:remote,deleted} = remoteNotebook(snapshot), current = normalizeNotebook(local,remote.document);
  const strokes = strokeMap(remote);
  for (const key of deleted) strokes.delete(key);
  for (const operation of compactOperations(pending,deleted)) {
    const key = strokeKey(operation.page,operation.type === 'put' ? operation.stroke.id : operation.id);
    if (operation.type === 'delete') strokes.delete(key);
    else {
      if (strokes.has(key) && !sameStroke(strokes.get(key).stroke,operation.stroke)) fail('STROKE_ID_CONFLICT');
      strokes.set(key,{page:operation.page,stroke:operation.stroke});
    }
  }
  const pages = new Map();
  for (const item of strokes.values()) {
    if (!pages.has(item.page)) pages.set(item.page,[]);
    pages.get(item.page).push(item.stroke);
  }
  return normalizeNotebook({...current,pages:[...pages].sort((a,b)=>a[0]-b[0]).map(([number,items])=>({number,strokes:items}))},remote.document);
}

export function emptyNotebook(document) {
  return normalizeNotebook({format:FORMAT,version:1,document,pages:[],bookmarks:[],position:{page:1}});
}

/** Account/notebook working views are separate even when the PDF is identical. */
export function switchNotebookView({current,currentKey,targetKey,target,allowUpload=false}) {
  const next=normalizeNotebook(target),local=normalizeNotebook(current,next.document);
  if(currentKey===targetKey)return{notebook:local,added:diffOperations(next,local)};
  if(currentKey)return{notebook:next,added:[]};
  if(!local.pages.some(page=>page.strokes.length))return{notebook:next,added:[]};
  if(!allowUpload)fail('UNBOUND_NOTES_REQUIRE_CONSENT');
  const strokes=strokeMap(next);
  for(const [key,item] of strokeMap(local)){
    if(strokes.has(key)&&!sameStroke(strokes.get(key).stroke,item.stroke))fail('STROKE_ID_CONFLICT');
    strokes.set(key,item);
  }
  const pages=new Map();for(const item of strokes.values()){if(!pages.has(item.page))pages.set(item.page,[]);pages.get(item.page).push(item.stroke);}
  const merged=normalizeNotebook({...local,pages:[...pages].map(([number,items])=>({number,strokes:items}))});
  return{notebook:merged,added:diffOperations(next,merged)};
}

export function operationBatches(operations, byteLimit = 950000) {
  const encoder = new TextEncoder(), batches = []; let current = [];
  for (const operation of operations) {
    if (encoder.encode(JSON.stringify({operations:[operation]})).byteLength > byteLimit) fail('STROKE_TOO_LARGE');
    const next = [...current,operation];
    if (current.length && (next.length > 100 || encoder.encode(JSON.stringify({operations:next})).byteLength > byteLimit)) {
      batches.push(current); current = [];
    }
    current.push(operation);
  }
  if (current.length) batches.push(current);
  return batches;
}
