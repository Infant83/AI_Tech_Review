/** Private, same-origin browser storage. Never sends documents or ink over a network. */
const DATABASE = 'atr-lecture-notebooks';
let dbPromise;
export function openDatabase() {
  if (!dbPromise) dbPromise = new Promise((resolve, reject) => {
    if (!globalThis.indexedDB) return reject(new Error('STORAGE_UNAVAILABLE'));
    const request = indexedDB.open(DATABASE, 1);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains('documents')) db.createObjectStore('documents', { keyPath: 'fingerprint' });
      if (!db.objectStoreNames.contains('pages')) db.createObjectStore('pages', { keyPath: 'key' });
    };
    request.onsuccess = () => {
      const db = request.result;
      db.onversionchange = () => { db.close(); dbPromise = null; };
      resolve(db);
    };
    request.onerror = () => reject(request.error || new Error('STORAGE_UNAVAILABLE'));
    request.onblocked = () => reject(new Error('STORAGE_BLOCKED'));
  });
  return dbPromise;
}
function result(request) {
  return new Promise((resolve, reject) => { request.onsuccess = () => resolve(request.result); request.onerror = () => reject(request.error); });
}
function complete(transaction) {
  return new Promise((resolve, reject) => {
    let requestError = null;
    // WebKit can report a request failure before transaction.error is populated.
    transaction.onerror = event => { requestError = event.target?.error || transaction.error || new Error('SAVE_FAILED'); };
    transaction.oncomplete = () => requestError ? reject(requestError) : resolve();
    transaction.onabort = () => reject(requestError || transaction.error || new Error('SAVE_ABORTED'));
  });
}
function hydrateDocument(document) {
  if (!document) return document;
  const value = document.pdf;
  if (value instanceof ArrayBuffer || ArrayBuffer.isView(value)) {
    return { ...document, pdf: new Blob([value], { type: 'application/pdf' }) };
  }
  return document;
}
function pageKey(fingerprint, page) { return fingerprint + ':' + String(page).padStart(5, '0'); }
export async function getDocument(fingerprint) {
  const db = await openDatabase();
  return hydrateDocument(await result(db.transaction('documents').objectStore('documents').get(fingerprint)));
}
export async function listDocuments() {
  const db = await openDatabase();
  const docs = await result(db.transaction('documents').objectStore('documents').getAll());
  return docs.map(hydrateDocument).sort((a, b) => b.updatedAt - a.updatedAt);
}
export async function putDocument(document) {
  // Some WebKit environments cannot prepare Blob/File data for IndexedDB.
  // ArrayBuffer structured cloning works there and also avoids that Blob path
  // in subsequent page/meta transactions. Keep the public API returning Blobs.
  const stored = document.pdf instanceof Blob ? { ...document, pdf: await document.pdf.arrayBuffer() } : document;
  const db = await openDatabase(); const tx = db.transaction('documents', 'readwrite'); const done = complete(tx);
  tx.objectStore('documents').put(stored); await done;
}
export async function loadPage(fingerprint, page) {
  const db = await openDatabase();
  return (await result(db.transaction('pages').objectStore('pages').get(pageKey(fingerprint, page))))?.strokes || [];
}
export async function loadPages(fingerprint) {
  const db = await openDatabase();
  const range = IDBKeyRange.bound(pageKey(fingerprint, 0), pageKey(fingerprint, 99999));
  return result(db.transaction('pages').objectStore('pages').getAll(range));
}
export async function savePage(fingerprint, page, strokes, meta = {}) {
  const db = await openDatabase(); const tx = db.transaction(['documents', 'pages'], 'readwrite'); const done = complete(tx);
  const docs = tx.objectStore('documents');
  docs.get(fingerprint).onsuccess = event => {
    const document = event.target.result;
    if (!document) { tx.abort(); return; }
    const annotated = new Set(document.annotatedPages || []);
    if (strokes.length) annotated.add(page); else annotated.delete(page);
    docs.put({ ...document, ...meta, annotatedPages: [...annotated].sort((a, b) => a - b), updatedAt: Date.now() });
    tx.objectStore('pages').put({ key: pageKey(fingerprint, page), fingerprint, number: page, strokes, updatedAt: Date.now() });
  };
  await done;
}
export async function saveMetadata(fingerprint, meta) {
  const db = await openDatabase(); const tx = db.transaction('documents', 'readwrite'); const done = complete(tx);
  const docs = tx.objectStore('documents');
  docs.get(fingerprint).onsuccess = event => {
    if (event.target.result) docs.put({ ...event.target.result, ...meta, updatedAt: Date.now() });
    else tx.abort();
  };
  await done;
}
export async function importPages(fingerprint, pages, bookmarks, position) {
  const db = await openDatabase(); const tx = db.transaction(['documents', 'pages'], 'readwrite'); const done = complete(tx);
  const docs = tx.objectStore('documents');
  docs.get(fingerprint).onsuccess = event => {
    const document = event.target.result;
    if (!document) { tx.abort(); return; }
    const store = tx.objectStore('pages');
    const range = IDBKeyRange.bound(pageKey(fingerprint, 0), pageKey(fingerprint, 99999));
    store.delete(range);
    pages.forEach(page => store.put({ key: pageKey(fingerprint, page.number), fingerprint, number: page.number, strokes: page.strokes, updatedAt: Date.now() }));
    docs.put({ ...document, bookmarks, position, annotatedPages: pages.filter(p => p.strokes.length).map(p => p.number), updatedAt: Date.now() });
  };
  await done;
}
