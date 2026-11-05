/** Private, same-origin browser storage. Never sends documents or ink over a network. */
const DATABASE = 'atr-lecture-notebooks';
const VERSION = 2;
const META = 'document_metadata';
const PDFS = 'pdf_originals';
let dbPromise;
export function openDatabase() {
  if (!dbPromise) dbPromise = new Promise((resolve, reject) => {
    if (!globalThis.indexedDB) return reject(new Error('STORAGE_UNAVAILABLE'));
    const request = indexedDB.open(DATABASE, VERSION);
    request.onupgradeneeded = event => {
      const db = request.result;
      if (!db.objectStoreNames.contains('documents')) db.createObjectStore('documents', { keyPath: 'fingerprint' });
      if (!db.objectStoreNames.contains('pages')) db.createObjectStore('pages', { keyPath: 'key' });
      if (!db.objectStoreNames.contains(META)) db.createObjectStore(META, { keyPath: 'fingerprint' });
      if (!db.objectStoreNames.contains(PDFS)) db.createObjectStore(PDFS, { keyPath: 'fingerprint' });
      if (event.oldVersion < VERSION) {
        // Keep v1 PDF records intact as immutable legacy originals. Copy only
        // their small metadata into the new working store. This avoids both a
        // second full PDF copy and a Blob conversion during an upgrade txn.
        const cursor = request.transaction.objectStore('documents').openCursor();
        cursor.onsuccess = () => {
          const row = cursor.result;
          if (!row) return;
          request.transaction.objectStore(META).put(metadata(row.value, Boolean(row.value.pdf)));
          row.continue();
        };
      }
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
function metadata(document, hasPDF = document.hasPDF) {
  const { pdf, ...small } = document;
  return { ...small, hasPDF: Boolean(hasPDF) };
}
function pageKey(fingerprint, page) { return fingerprint + ':' + String(page).padStart(5, '0'); }
export async function getDocument(fingerprint) {
  const db = await openDatabase();
  const tx = db.transaction([META, PDFS]);
  const [document, original] = await Promise.all([
    result(tx.objectStore(META).get(fingerprint)),
    result(tx.objectStore(PDFS).get(fingerprint)),
  ]);
  if (!document) return null;
  if (original) return hydrateDocument({ ...document, pdf: original.data });
  if (!document.hasPDF) return document;
  const legacy = await result(db.transaction('documents').objectStore('documents').get(fingerprint));
  return hydrateDocument({ ...document, pdf: legacy?.pdf });
}
export async function listDocuments({ includeTrash = false } = {}) {
  const db = await openDatabase();
  const docs = await result(db.transaction(META).objectStore(META).getAll());
  return docs.filter(doc => includeTrash || !doc.deletedAt).sort((a, b) => b.updatedAt - a.updatedAt);
}
export async function putDocument(document) {
  // Some WebKit environments cannot prepare Blob/File data for IndexedDB.
  // ArrayBuffer structured cloning works there and also avoids that Blob path
  // in subsequent page/meta transactions. Keep the public API returning Blobs.
  const db = await openDatabase();
  const previous = await result(db.transaction(META).objectStore(META).get(document.fingerprint));
  let bytes = null;
  if (!previous?.hasPDF && document.pdf) {
    bytes = document.pdf instanceof Blob ? await document.pdf.arrayBuffer() : document.pdf;
    if (ArrayBuffer.isView(bytes)) bytes = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
    if (!(bytes instanceof ArrayBuffer)) throw new Error('INVALID_PDF_BYTES');
  }
  const tx = db.transaction([META, PDFS], 'readwrite'), done = complete(tx), docs = tx.objectStore(META);
  docs.get(document.fingerprint).onsuccess = event => {
    const current = event.target.result;
    // Concurrent openings of an identical fingerprint never replace bytes.
    if (!current?.hasPDF && bytes) tx.objectStore(PDFS).add({ fingerprint: document.fingerprint, data: bytes });
    docs.put(metadata({ ...current, ...document }, Boolean(current?.hasPDF || bytes)));
  };
  await done;
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
  const db = await openDatabase(); const tx = db.transaction([META, 'pages'], 'readwrite'); const done = complete(tx);
  const docs = tx.objectStore(META);
  docs.get(fingerprint).onsuccess = event => {
    const document = event.target.result;
    if (!document) { tx.abort(); return; }
    const annotated = new Set(document.annotatedPages || []);
    if (strokes.length) annotated.add(page); else annotated.delete(page);
    docs.put(metadata({ ...document, ...meta, annotatedPages: [...annotated].sort((a, b) => a - b), updatedAt: Date.now() }, document.hasPDF));
    tx.objectStore('pages').put({ key: pageKey(fingerprint, page), fingerprint, number: page, strokes, updatedAt: Date.now() });
  };
  await done;
}
export async function saveMetadata(fingerprint, meta) {
  const db = await openDatabase(); const tx = db.transaction(META, 'readwrite'); const done = complete(tx);
  const docs = tx.objectStore(META);
  docs.get(fingerprint).onsuccess = event => {
    if (event.target.result) docs.put(metadata({ ...event.target.result, ...meta, updatedAt: Date.now() }, event.target.result.hasPDF));
    else tx.abort();
  };
  await done;
}
export async function importPages(fingerprint, pages, bookmarks, position) {
  const db = await openDatabase(); const tx = db.transaction([META, 'pages'], 'readwrite'); const done = complete(tx);
  const docs = tx.objectStore(META);
  docs.get(fingerprint).onsuccess = event => {
    const document = event.target.result;
    if (!document) { tx.abort(); return; }
    const store = tx.objectStore('pages');
    const range = IDBKeyRange.bound(pageKey(fingerprint, 0), pageKey(fingerprint, 99999));
    store.delete(range);
    pages.forEach(page => store.put({ key: pageKey(fingerprint, page.number), fingerprint, number: page.number, strokes: page.strokes, updatedAt: Date.now() }));
    docs.put(metadata({ ...document, bookmarks, position, annotatedPages: pages.filter(p => p.strokes.length).map(p => p.number), updatedAt: Date.now() }));
  };
  await done;
}
export async function trashDocument(fingerprint) { return saveMetadata(fingerprint, { deletedAt: Date.now() }); }
export async function restoreDocument(fingerprint) { return saveMetadata(fingerprint, { deletedAt: null }); }
