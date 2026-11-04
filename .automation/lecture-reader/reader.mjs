import * as pdfjs from './vendor/pdf.mjs';
import { clamp, normalizedPoint, eraseStrokes, splitStroke, STROKE_CHUNK_POINTS, pdfPoint, validateNotebook, NOTEBOOK_FORMAT, MAX_PAGES } from './ink-core.mjs';
import * as storage from './storage.mjs';

const $ = id => document.getElementById(id);
const rootURL = new URL('../../', import.meta.url);
const params = new URLSearchParams(location.search);
const initialLocal = new URLSearchParams(location.hash.slice(1)).get('local');
const en = params.get('lang') === 'en';
const strings = {
  lectures: ['렉처 노트', 'Lecture notes'], studyNotebook: ['PDF 학습 노트', 'PDF study notebook'], choosePDF: ['공부할 PDF를 열어주세요', 'Open a PDF to begin'],
  ready: ['준비됨', 'Ready'], cloud: ['로그인·동기화', 'Sign in and sync'], sync: ['동기화', 'Sync'], library: ['보관함', 'Library'], myLibrary: ['내 보관함', 'My library'],
  inkTools: ['필기 도구', 'Writing tools'], pen: ['펜', 'Pen'], eraser: ['지우개', 'Eraser'], move: ['읽기', 'Read'], penColor: ['펜 색상', 'Pen color'],
  black: ['검정', 'Black'], green: ['초록', 'Green'], red: ['빨강', 'Red'], blue: ['파랑', 'Blue'], width: ['굵기', 'Width'], penWidth: ['펜 굵기', 'Pen width'],
  undo: ['실행 취소', 'Undo'], redo: ['다시 실행', 'Redo'], finger: ['손가락 필기', 'Finger ink'], options: ['저장·가져오기·도움말', 'Export, import and help'],
  welcome: ['읽던 곳에서, 쓰던 필기 그대로.', 'Pick up where you left off.'], welcomeBody: ['렉처 PDF를 열거나 내 PDF를 가져와 공부하세요. 펜 필기와 읽던 위치를 이 기기에 자동 저장합니다.', 'Open lecture notes or bring your own PDF. Ink and your reading position are saved automatically on this device.'],
  openPDF: ['PDF 열기', 'Open a PDF'], privateFiles: ['내 PDF는 업로드 없이 이 브라우저에서 열립니다.', 'Your own PDFs open in this browser without an upload.'], loading: ['PDF를 여는 중입니다…', 'Opening your PDF…'],
  pdfPage: ['PDF 페이지', 'PDF page'], pdfContent: ['PDF 본문', 'PDF content'], inkCanvas: ['펜 필기 영역', 'Handwriting canvas'], cannotOpen: ['PDF를 열지 못했습니다', 'Could not open this PDF'], retry: ['다시 열기', 'Try again'], openOriginal: ['원본 PDF 열기', 'Open original PDF'],
  previous: ['이전 페이지', 'Previous page'], next: ['다음 페이지', 'Next page'], pageNumber: ['페이지 번호', 'Page number'], bookmark: ['이 페이지 책갈피', 'Bookmark this page'], goBookmark: ['책갈피 이동', 'Go to bookmark'], bookmarks: ['책갈피', 'Bookmarks'], zoom: ['확대', 'Zoom'], fitWidth: ['너비 맞춤', 'Fit width'],
  personalLearning: ['나의 학습', 'Personal study'], libraryBody: ['읽던 페이지와 필기가 이 브라우저에 보관됩니다. 중요한 필기는 백업 파일로도 보관하세요.', 'Your place and notes stay in this browser. Keep a backup of important notes too.'], importPDF: ['내 PDF 가져오기', 'Bring your own PDF'], localOnly: ['업로드 없이 이 기기에 보관', 'Keep on this device without uploading'], recent: ['이어서 공부하기', 'Continue studying'], publishedLectures: ['렉처 자료', 'Published lectures'], close: ['닫기', 'Close'],
  exportPDF: ['필기한 PDF 내보내기', 'Export PDF with ink'], exportBackup: ['수정 가능한 필기 백업', 'Export editable notes backup'], importBackup: ['필기 백업 가져오기', 'Import notes backup'],
  drawingHelp: ['펜으로 쓰고, 손가락으로 넘기세요', 'Write with Pencil, scroll with a finger'], drawingHelpBody: ['Apple Pencil은 바로 필기할 수 있습니다. 손가락으로 화면을 움직이고 두 손가락으로 확대할 수 있습니다. 마우스로도 쓸 수 있으며 손가락 필기는 도구에서 켤 수 있습니다. 지우개는 닿은 획을 지웁니다.', 'Write with Apple Pencil, scroll with a finger, and pinch to zoom. A mouse works too. Enable Finger ink to draw with a finger. The eraser removes strokes it touches.'],
  savingHelp: ['필기는 자동 저장됩니다', 'Your notes save automatically'], savingHelpBody: ['이 기기·브라우저에 필기와 읽던 페이지를 저장합니다. 브라우저 데이터를 지우거나 비공개 모드를 종료하면 사라질 수 있습니다. 로그인 동기화는 선택한 노트에 적용됩니다. 기기를 옮길 때에는 원본 PDF와 필기 백업을 함께 가져가세요.', 'Ink and your place are saved in this device and browser. Clearing browser data or ending a private session may remove them. Signed-in sync applies to notebooks you choose. To move devices, take the original PDF and a notes backup together.'],
  exportHelp: ['필기 PDF는 다른 앱에서 읽거나 공유하는 사본입니다. 필기를 계속 수정하려면 백업 파일도 보관하세요.', 'The inked PDF is a copy for reading and sharing in other apps. Keep the editable backup to continue editing strokes.'], retainStorage: ['이 기기에 보관 유지 요청', 'Request persistent device storage'], clearPage: ['현재 페이지의 필기 지우기', 'Clear ink on this page'], shortcuts: ['단축키: P 펜 · E 지우개 · H 읽기 · ← → 페이지 · ⌘/Ctrl+Z 실행 취소', 'Keys: P pen · E eraser · H read · ← → pages · ⌘/Ctrl+Z undo'],
  saving: ['저장 중…', 'Saving…'], saved: ['이 기기에 저장됨', 'Saved on this device'], saveFailed: ['저장 실패 · 백업 필요', 'Save failed · back up'],
  storageError: ['이 브라우저에서 저장하지 못했습니다. 필기를 백업해 주세요. 저장이 복구될 때까지 현재 PDF를 유지합니다.', 'This browser could not save your notes. Export a backup. Keep this PDF open until saving is restored.'],
  noRecent: ['아직 보관한 PDF가 없습니다.', 'No PDFs saved yet.'], noCatalog: ['렉처 목록을 불러오지 못했습니다. 내 PDF는 계속 열 수 있습니다.', 'The lecture catalog is unavailable. You can still open a local PDF.'],
  pdfLimit: ['PDF는 50 MB 이하의 파일을 열 수 있습니다.', 'Choose a PDF up to 50 MB.'], notPDF: ['PDF 파일을 선택해 주세요.', 'Please choose a PDF file.'], unknownPDF: ['등록된 렉처 PDF를 찾을 수 없습니다. 보관함에서 자료를 골라 주세요.', 'This lecture PDF is not registered. Choose one from the library.'],
  hashMismatch: ['PDF 판본이 목록과 다릅니다. 새로고침 후 다시 열어주세요.', 'The PDF version differs from the catalog. Refresh and try again.'],
  loadError: ['파일을 불러오지 못했습니다. 인터넷 연결 또는 PDF 파일을 확인해 주세요.', 'Could not load the file. Check the connection or PDF.'],
  pageLimit: ['페이지 수가 너무 많습니다. 10,000쪽 이하 PDF를 선택해 주세요.', 'Choose a PDF of no more than 10,000 pages.'],
  backupReady: ['수정 가능한 필기 백업을 저장했습니다.', 'Your editable notes backup is ready.'], exported: ['필기한 PDF를 저장했습니다.', 'Your PDF with ink is ready.'], exporting: ['PDF에 필기를 옮기는 중…', 'Preparing your inked PDF…'],
  exportFailed: ['PDF를 내보내지 못했습니다. 암호화된 PDF라면 원본 잠금을 해제한 뒤 다시 시도해 주세요. 필기 백업은 사용할 수 있습니다.', 'Could not export this PDF. If it is encrypted, unlock the original and try again. The editable notes backup remains available.'],
  backupInvalid: ['이 필기 백업을 읽을 수 없습니다. 지원하는 백업 파일인지 확인해 주세요.', 'This is not a valid supported notes backup.'], fingerprintMismatch: ['다른 PDF의 필기입니다. 백업을 만든 것과 같은 원본 PDF를 먼저 열어주세요.', 'These notes belong to a different PDF. Open the exact original PDF used for this backup first.'],
  replaceConfirm: ['백업으로 이 PDF의 현재 필기를 바꿀까요? 기존 필기는 먼저 백업해 주세요.', 'Replace this PDF’s current notes with the backup? Export your current notes first.'], imported: ['필기를 가져왔습니다.', 'Notes imported.'], clearConfirm: ['현재 페이지의 필기를 모두 지울까요? 실행 취소로 되돌릴 수 있습니다.', 'Clear all ink on this page? You can undo this.'],
  persistentYes: ['이 브라우저가 보관 유지 요청을 허용했습니다. 백업도 함께 보관하세요.', 'This browser granted persistent storage. Keep backups too.'], persistentNo: ['이 브라우저에서는 보관 유지를 보장할 수 없습니다. 중요한 필기는 백업해 주세요.', 'This browser cannot guarantee persistent storage. Back up important notes.'],
  password: ['PDF 암호를 입력하세요. 암호는 저장하지 않습니다.', 'Enter the PDF password. It will not be saved.'], openFirst: ['먼저 PDF를 열어주세요.', 'Open a PDF first.'], busy: ['현재 작업이 끝난 뒤 다시 시도해 주세요.', 'Please wait for the current operation.'], cloudSetup: ['로그인·동기화 화면을 준비하지 못했습니다. 이 기기 자동 저장은 계속 사용할 수 있습니다.', 'Sign-in and sync are unavailable. Device autosave still works.']
};
const t = key => strings[key]?.[Number(en)] || key;
document.documentElement.lang = en ? 'en' : 'ko';
document.querySelectorAll('[data-i18n]').forEach(e => { e.textContent = t(e.dataset.i18n); });
document.querySelectorAll('[data-i18n-title]').forEach(e => { e.title = t(e.dataset.i18nTitle); e.setAttribute('aria-label', e.title); });
document.querySelectorAll('[data-i18n-aria]').forEach(e => e.setAttribute('aria-label', t(e.dataset.i18nAria)));
$('lecture-link').href = en ? '../en/' : '../';
pdfjs.GlobalWorkerOptions.workerSrc = new URL('./vendor/pdf.worker.mjs', import.meta.url).href;

let catalog = [], pdf = null, pdfLoadingTask = null, pdfBytes = null, current = null, pageNumber = 1, baseWidth = 595, pageAspect = 1.414;
let tool = 'pen', color = '#243746', active = null, busy = false, renderSequence = 0, renderTask = null, saveTimer = null, toastTimer;
let writeQueue = Promise.resolve(true), metaVersion = 0, metaSaved = 0, drawingFrame = 0, lastStorageError = 0, mutationRevision = 0;
let explicitSelection = false;
const pages = new Map(), dirty = new Map(), versions = new Map(), histories = new Map(), retiredIds = new Set();
const pdfCanvas = $('pdf-canvas'), inkCanvas = $('ink-canvas'), sheet = $('page-sheet');
let cssWidth = 595, cssHeight = 842, pixelRatio = 1, retry = null;
const uid = () => crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + '-' + Math.random().toString(36).slice(2);
const clone = value => JSON.parse(JSON.stringify(value));
function signal(name, detail) { window.dispatchEvent(new CustomEvent(name, { detail })); }
function status(kind) { const e = $('save-state'); e.dataset.state = kind; e.textContent = t({ pending: 'saving', saved: 'saved', error: 'saveFailed', ready: 'ready' }[kind]); }
function toast(message, duration = 5000) { clearTimeout(toastTimer); $('toast').textContent = message; $('toast').hidden = false; toastTimer = setTimeout(() => { $('toast').hidden = true; }, duration); }
function storageFailure() { status('error'); if (Date.now() - lastStorageError > 12000) { toast(t('storageError'), 10000); lastStorageError = Date.now(); } }
function currentInfo() { return current ? { fingerprint: current.fingerprint, title: current.title, pageCount: current.pageCount, publicId: current.publicId || null, isLocal: !current.publicId, drawing: Boolean(active), busy, mutationRevision } : null; }
function state() { return pages.get(pageNumber) || []; }
function history() { if (!histories.has(pageNumber)) histories.set(pageNumber, { undo: [], redo: [] }); return histories.get(pageNumber); }
function controls() {
  $('undo').disabled = !current || !history().undo.length || busy;
  $('redo').disabled = !current || !history().redo.length || busy;
  $('previous-page').disabled = !current || pageNumber <= 1 || busy;
  $('next-page').disabled = !current || pageNumber >= current.pageCount || busy;
  ['export-pdf', 'export-backup', 'import-backup', 'clear-page', 'bookmark'].forEach(id => { $(id).disabled = !current || busy; });
  $('page-number').disabled = !current || busy;
  $('page-number').value = pageNumber;
  $('page-count').textContent = current?.pageCount || '—';
  $('page-number').max = current?.pageCount || 1;
  $('bookmark').setAttribute('aria-pressed', String(Boolean(current?.bookmarks?.includes(pageNumber))));
}
function markDirty(number = pageNumber) {
  mutationRevision++;
  const version = (versions.get(number) || 0) + 1;
  versions.set(number, version); dirty.set(number, version); status('pending');
  clearTimeout(saveTimer); saveTimer = setTimeout(flush, 350);
}
function markMeta() { mutationRevision++; metaVersion++; status('pending'); clearTimeout(saveTimer); saveTimer = setTimeout(flush, 250); }
async function flush() {
  clearTimeout(saveTimer);
  if (!current || (!dirty.size && metaSaved === metaVersion)) return writeQueue;
  const document = current, snapshots = [...dirty].map(([number, version]) => ({ number, version, strokes: clone(pages.get(number) || []) }));
  const mv = metaVersion, meta = { position: pageNumber, bookmarks: [...(current.bookmarks || [])] };
  writeQueue = writeQueue.catch(() => false).then(async () => {
    try {
      for (const snapshot of snapshots) {
        await storage.savePage(document.fingerprint, snapshot.number, snapshot.strokes, meta);
        if (current?.fingerprint === document.fingerprint && dirty.get(snapshot.number) === snapshot.version) dirty.delete(snapshot.number);
      }
      if (!snapshots.length) await storage.saveMetadata(document.fingerprint, meta);
      if (current?.fingerprint === document.fingerprint) {
        const metadataChanged = mv > metaSaved;
        metaSaved = Math.max(metaSaved, mv);
        if (!dirty.size && metaSaved === metaVersion) status('saved');
        if (snapshots.length || metadataChanged) signal('atr:notes-saved', { ...currentInfo(), page: pageNumber, metadataOnly: !snapshots.length });
      }
      return true;
    } catch { storageFailure(); return false; }
  });
  return writeQueue;
}
function drawStroke(ctx, stroke) {
  if (!stroke.points.length) return;
  ctx.strokeStyle = stroke.color; ctx.fillStyle = stroke.color; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const points = stroke.points;
  if (points.length === 1) { const p = points[0]; ctx.beginPath(); ctx.arc(p.x * cssWidth, p.y * cssHeight, Math.max(.4, stroke.width * cssWidth * .5), 0, Math.PI * 2); ctx.fill(); return; }
  for (let i = 1; i < points.length; i++) {
    const a = points[i - 1], b = points[i];
    ctx.lineWidth = Math.max(.35, stroke.width * cssWidth * (.45 + .95 * (a.p + b.p) / 2));
    ctx.beginPath(); ctx.moveTo(a.x * cssWidth, a.y * cssHeight); ctx.lineTo(b.x * cssWidth, b.y * cssHeight); ctx.stroke();
  }
}
function drawInk() {
  drawingFrame = 0; const ctx = inkCanvas.getContext('2d');
  ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0); ctx.clearRect(0, 0, cssWidth, cssHeight);
  state().forEach(stroke => drawStroke(ctx, stroke));
}
function requestInk() { if (!drawingFrame) drawingFrame = requestAnimationFrame(drawInk); }
function historyEntry(before, after) {
  if (JSON.stringify(before) === JSON.stringify(after)) return;
  const h = history(); h.undo.push({ before, after: clone(after) }); if (h.undo.length > 80) h.undo.shift(); h.redo.length = 0; controls();
}
function finishStroke() {
  if (!active) return;
  const before = active.before, number = active.page, pointerId = active.id;
  active = null;
  try { inkCanvas.releasePointerCapture(pointerId); } catch { /* capture may already have ended */ }
  inkCanvas.style.touchAction = $('finger-draw').checked && tool !== 'read' ? 'none' : 'pan-x pan-y pinch-zoom';
  if (number === pageNumber) { historyEntry(before, state()); markDirty(); void flush(); }
  requestInk();
}
function chooseTool(next) {
  finishStroke(); tool = next; sheet.dataset.tool = next;
  document.querySelectorAll('[data-tool]').forEach(e => { if (e.tagName === 'BUTTON') { e.classList.toggle('active', e.dataset.tool === next); e.setAttribute('aria-pressed', String(e.dataset.tool === next)); } });
  sheet.classList.toggle('finger-drawing', $('finger-draw').checked && tool !== 'read');
  inkCanvas.style.touchAction = $('finger-draw').checked && tool !== 'read' ? 'none' : 'pan-x pan-y pinch-zoom';
}
function pointerPoint(event) { return normalizedPoint(event.clientX, event.clientY, inkCanvas.getBoundingClientRect(), event.pressure); }
function eraseAt(from, to) {
  const before = state(); const after = eraseStrokes(before, from, to, 10, cssWidth, cssHeight);
  if (after.length !== before.length) {
    const kept = new Set(after.map(s => s.id)); before.forEach(s => { if (!kept.has(s.id)) retiredIds.add(s.id); });
    pages.set(pageNumber, after); markDirty(); requestInk();
  }
}
inkCanvas.addEventListener('pointerover', event => { if (event.pointerType === 'pen' && tool !== 'read') inkCanvas.style.touchAction = 'none'; });
for (const name of ['pointerout', 'pointerleave']) inkCanvas.addEventListener(name, () => {
  if (!active) inkCanvas.style.touchAction = $('finger-draw').checked && tool !== 'read' ? 'none' : 'pan-x pan-y pinch-zoom';
});
function appendActivePoint(point) {
  if (active.stroke.points.length >= STROKE_CHUNK_POINTS) {
    const previous = active.stroke;
    active.stroke = { ...previous, id: uid(), points: [previous.points[previous.points.length - 1]] };
    state().push(active.stroke);
  }
  active.stroke.points.push(point); markDirty(); requestInk();
}
inkCanvas.addEventListener('pointerdown', event => {
  if (!current || busy || tool === 'read' || active || (event.pointerType === 'mouse' && event.button !== 0) ||
      (event.pointerType === 'touch' && !$('finger-draw').checked)) return;
  event.preventDefault(); inkCanvas.setPointerCapture(event.pointerId); inkCanvas.style.touchAction = 'none';
  const point = pointerPoint(event), kind = event.button === 5 || event.buttons === 32 ? 'eraser' : tool;
  active = { id: event.pointerId, type: event.pointerType, page: pageNumber, before: clone(state()), point, kind };
  if (kind === 'pen') { active.stroke = { id: uid(), color, width: Number($('pen-width').value) / baseWidth, points: [point] }; state().push(active.stroke); markDirty(); requestInk(); }
  else eraseAt(point, point);
});
inkCanvas.addEventListener('pointermove', event => {
  if (!active || active.id !== event.pointerId) return;
  event.preventDefault();
  const samples = typeof event.getCoalescedEvents === 'function' ? event.getCoalescedEvents() : [event];
  for (const sample of samples.length ? samples : [event]) {
    const point = pointerPoint(sample);
    if (active.kind === 'eraser') eraseAt(active.point, point);
    else if (Math.hypot((point.x - active.point.x) * cssWidth, (point.y - active.point.y) * cssHeight) > .35) appendActivePoint(point);
    active.point = point;
  }
});
['pointerup', 'pointercancel', 'lostpointercapture'].forEach(name => inkCanvas.addEventListener(name, event => {
  if (active?.id !== event.pointerId) return;
  if (name === 'pointerup' && active.kind === 'pen') {
    const point = pointerPoint(event);
    if (Math.hypot((point.x - active.point.x) * cssWidth, (point.y - active.point.y) * cssHeight) > .35) appendActivePoint(point);
  }
  finishStroke();
}));
// Safari exposes Pencil touchType; cancel only Pencil gestures, leaving finger scroll/pinch native.
for (const name of ['touchstart', 'touchmove']) inkCanvas.addEventListener(name, event => {
  if (tool !== 'read' && ($('finger-draw').checked || active?.type === 'pen' || [...event.touches].some(touch => touch.touchType === 'stylus'))) event.preventDefault();
}, { passive: false });

async function renderPage(scroll = true) {
  if (!pdf || !current) return;
  const sequence = ++renderSequence; busy = true; controls();
  if (renderTask) { try { renderTask.cancel(); } catch {} }
  const page = await pdf.getPage(pageNumber);
  if (sequence !== renderSequence) return;
  const natural = page.getViewport({ scale: 1 }); baseWidth = natural.width; pageAspect = natural.height / natural.width;
  $('page-area').hidden = false;
  const available = Math.max(240, Math.min(1100, $('page-area').clientWidth - (innerWidth <= 590 ? 20 : innerWidth <= 900 ? 36 : 48)));
  const scale = available / natural.width * Number($('zoom').value);
  const viewport = page.getViewport({ scale }); cssWidth = viewport.width; cssHeight = viewport.height;
  pixelRatio = Math.min(devicePixelRatio || 1, 2, 4096 / Math.max(cssWidth, cssHeight), Math.sqrt(10000000 / (cssWidth * cssHeight)));
  pixelRatio = Math.max(.2, pixelRatio);
  sheet.style.width = cssWidth + 'px'; sheet.style.height = cssHeight + 'px';
  for (const canvas of [pdfCanvas, inkCanvas]) { canvas.width = Math.ceil(cssWidth * pixelRatio); canvas.height = Math.ceil(cssHeight * pixelRatio); canvas.style.width = cssWidth + 'px'; canvas.style.height = cssHeight + 'px'; }
  $('page-area').hidden = false; $('loading-state').hidden = true;
  const ctx = pdfCanvas.getContext('2d', { alpha: false });
  renderTask = page.render({ canvasContext: ctx, viewport, transform: [pixelRatio, 0, 0, pixelRatio, 0, 0] });
  try { await renderTask.promise; } catch (error) { if (error.name !== 'RenderingCancelledException') throw error; }
  if (sequence !== renderSequence) return;
  drawInk(); busy = false; controls();
  if (scroll) { window.scrollTo({ top: 0, behavior: 'instant' }); $('page-area').scrollLeft = 0; }
}
async function ensurePage(number) {
  if (!pages.has(number)) {
    let strokes = [];
    try { strokes = await storage.loadPage(current.fingerprint, number); } catch (error) { storageFailure(); throw error; }
    let changed = false;
    strokes.forEach(s => { if (!s.id) { s.id = uid(); changed = true; } });
    strokes = strokes.flatMap(s => { if (s.points.length > 5000) { changed = true; return splitStroke(s, uid); } return [s]; });
    pages.set(number, strokes); if (changed) markDirty(number);
  }
}
async function goPage(value) {
  if (!current || busy) return;
  finishStroke(); const target = clamp(Math.trunc(Number(value)) || 1, 1, current.pageCount);
  if (target === pageNumber) { controls(); return; }
  busy = true; controls();
  try { await ensurePage(target); pageNumber = target; markMeta(); await renderPage(); }
  catch { showError(t('loadError')); }
}
function renderBookmarks() {
  $('bookmarks').replaceChildren(new Option(t('bookmarks'), ''));
  for (const number of [...(current?.bookmarks || [])].sort((a, b) => a - b)) $('bookmarks').add(new Option(en ? `Page ${number}` : `${number}쪽`, String(number)));
  controls();
}
async function openBytes(bytes, metadata) {
  if (busy) return false;
  finishStroke(); busy = true; controls();
  if (current && !(await flush()) && (dirty.size || metaSaved !== metaVersion)) { busy = false; controls(); storageFailure(); return false; }
  mutationRevision++;
  $('empty-state').hidden = true; $('error-state').hidden = true; $('loading-state').hidden = false; $('page-area').hidden = true;
  let nextLoadingTask = null;
  try {
    if (bytes.byteLength > 50 * 1024 * 1024) throw new Error('PDF_TOO_LARGE');
    const fingerprint = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(b => b.toString(16).padStart(2, '0')).join('');
    if (metadata.sha256 && metadata.sha256 !== fingerprint) throw new Error('HASH_MISMATCH');
    const task = pdfjs.getDocument({ data: new Uint8Array(bytes).slice(), cMapUrl: new URL('./vendor/cmaps/', import.meta.url).href, cMapPacked: true,
      standardFontDataUrl: new URL('./vendor/standard_fonts/', import.meta.url).href, wasmUrl: new URL('./vendor/wasm/', import.meta.url).href,
      isEvalSupported: false, enableXfa: false, disableFontFace: false, useSystemFonts: true });
    nextLoadingTask = task;
    task.onPassword = callback => { const password = prompt(t('password')); if (password === null) task.destroy(); else callback(password); };
    const nextPDF = await task.promise;
    if (nextPDF.numPages > MAX_PAGES) { await task.destroy(); throw new Error('PAGE_LIMIT'); }
    // PDF.js 6 owns worker cleanup on the loading task; its document proxy no
    // longer exposes destroy(). Keep the old document until the new one loads.
    if (pdfLoadingTask) await pdfLoadingTask.destroy();
    pdf = nextPDF; pdfLoadingTask = task; pdfBytes = new Uint8Array(bytes).slice();
    let previous;
    try { previous = await storage.getDocument(fingerprint); } catch { /* loading remains available without persistence */ }
    current = { ...previous, fingerprint, title: metadata.title, publicId: metadata.publicId || null,
      pageCount: pdf.numPages, pdf: new Blob([pdfBytes], { type: 'application/pdf' }), position: previous?.position || 1,
      bookmarks: previous?.bookmarks || [], annotatedPages: previous?.annotatedPages || [], updatedAt: Date.now() };
    pages.clear(); histories.clear(); dirty.clear(); versions.clear(); retiredIds.clear(); metaVersion = 0; metaSaved = 0;
    pageNumber = clamp(current.position, 1, current.pageCount); await ensurePage(pageNumber);
    let saved = true; try { await storage.putDocument(current); } catch { saved = false; storageFailure(); }
    $('document-title').textContent = current.title;
    // Local filenames stay out of the browser title and network-visible query.
    document.title = `${t('studyNotebook')} | AI Tech Review Letters`;
    const url = new URL(location.href), fragment = new URLSearchParams();
    const invitation = new URLSearchParams(url.hash.slice(1)).get('invite');
    // The cloud module consumes a private invitation after the PDF module loads.
    // Keep it until explicit acceptance, even when a cached PDF opens first.
    if (invitation && /^[A-Za-z0-9_-]{20,512}$/.test(invitation)) fragment.set('invite', invitation);
    if (metadata.publicId) url.searchParams.set('id', metadata.publicId);
    else { url.searchParams.delete('id'); fragment.set('local', fingerprint); }
    url.hash = fragment.toString(); historyReplace(url);
    renderBookmarks(); $('page-controls').hidden = false; busy = false; await renderPage();
    if (saved) status(dirty.size ? 'pending' : 'saved');
    signal('atr:document-open', currentInfo()); return true;
  } catch (error) {
    if (nextLoadingTask && nextLoadingTask !== pdfLoadingTask) { try { await nextLoadingTask.destroy(); } catch {} }
    busy = false; showError(t(error.message === 'PDF_TOO_LARGE' ? 'pdfLimit' : error.message === 'PAGE_LIMIT' ? 'pageLimit' : error.message === 'HASH_MISMATCH' ? 'hashMismatch' : 'loadError')); return false;
  }
}
function historyReplace(url) { try { window.history.replaceState(null, '', url); } catch {} }
function showError(message) { $('loading-state').hidden = true; $('error-state').hidden = false; $('error-message').textContent = message; busy = false; controls(); }
async function openPublished(id) {
  const doc = catalog.find(d => d.id === id);
  if (!doc) { showError(t('unknownPDF')); return false; }
  retry = () => openPublished(id); $('original-link').href = new URL(doc.href, rootURL).href;
  try {
    const response = await fetch(new URL(doc.href, rootURL), { credentials: 'omit' });
    if (!response.ok) throw new Error('NETWORK');
    return await openBytes(await response.arrayBuffer(), { title: en && doc.title_en ? doc.title_en : doc.title, publicId: doc.id, sha256: doc.sha256 });
  } catch {
    try { const cached = (await storage.listDocuments()).find(d => d.publicId === id && d.pdf); if (cached) return openStored(cached.fingerprint); } catch {}
    showError(t('loadError')); return false;
  }
}
async function openStored(fingerprint) {
  try { const doc = await storage.getDocument(fingerprint); if (!doc?.pdf) throw new Error('MISSING'); return openBytes(await doc.pdf.arrayBuffer(), { title: doc.title, publicId: doc.publicId, sha256: doc.fingerprint }); }
  catch { showError(t('loadError')); return false; }
}
function closeDialogs() { document.querySelectorAll('dialog[open]').forEach(d => d.close()); }
async function showLibrary() {
  finishStroke(); $('library-dialog').showModal();
  const saved = $('saved-documents'); saved.replaceChildren();
  try {
    const docs = await storage.listDocuments();
    if (!docs.length) { const p = document.createElement('p'); p.className = 'empty-list'; p.textContent = t('noRecent'); saved.append(p); }
    docs.forEach(doc => {
      const button = document.createElement('button'); button.className = 'library-document'; button.type = 'button';
      const title = document.createElement('strong'); title.textContent = doc.title;
      const detail = document.createElement('span'); const notes = doc.annotatedPages?.length || 0;
      detail.textContent = en ? `Page ${doc.position || 1} / ${doc.pageCount} · ${notes} annotated pages${doc.publicId ? '' : ' · Personal PDF'}` : `${doc.position || 1} / ${doc.pageCount}쪽 · 필기 ${notes}쪽${doc.publicId ? '' : ' · 내 PDF'}`;
      button.append(title, detail); button.addEventListener('click', () => { explicitSelection = true; closeDialogs(); openStored(doc.fingerprint); }); saved.append(button);
    });
  } catch { const p = document.createElement('p'); p.className = 'empty-list'; p.textContent = t('storageError'); saved.append(p); }
  const published = $('published-documents'); published.replaceChildren();
  if (!catalog.length) { const p = document.createElement('p'); p.className = 'empty-list'; p.textContent = t('noCatalog'); published.append(p); }
  for (const doc of catalog) {
    const button = document.createElement('button'); button.className = 'library-document'; button.type = 'button';
    const title = document.createElement('strong'); title.textContent = en && doc.title_en ? doc.title_en : doc.title;
    const detail = document.createElement('span'); detail.textContent = doc.date + ' · PDF'; button.append(title, detail);
    button.addEventListener('click', () => { explicitSelection = true; closeDialogs(); openPublished(doc.id); }); published.append(button);
  }
}
function download(data, filename, type) {
  const blob = data instanceof Blob ? data : new Blob([data], { type });
  const url = URL.createObjectURL(blob), link = document.createElement('a'); link.href = url; link.download = filename; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 60000);
}
function safeName(title) { return title.replace(/[\\/:*?"<>|\u0000-\u001f]/g, '-').slice(0, 100) || 'study-notes'; }
async function notebook() {
  if (!current) throw new Error('NO_DOCUMENT');
  if (active || busy) throw new Error('READER_BUSY');
  if (!(await flush()) && (dirty.size || metaSaved !== metaVersion)) throw new Error('SAVE_FAILED');
  if (active || busy) throw new Error('READER_BUSY');
  const all = await storage.loadPages(current.fingerprint);
  if (active || busy) throw new Error('READER_BUSY');
  const merged = new Map(all.map(p => [p.number, p.strokes])); pages.forEach((strokes, number) => merged.set(number, strokes));
  return { format: NOTEBOOK_FORMAT, version: 1,
    document: { fingerprint: current.fingerprint, title: current.title, pageCount: current.pageCount },
    pages: [...merged].filter(([, strokes]) => strokes.length).sort((a, b) => a[0] - b[0]).map(([number, strokes]) => ({ number, strokes: clone(strokes) })),
    bookmarks: [...(current.bookmarks || [])], position: pageNumber };
}
async function applyNotebook(value, options = {}) {
  if (!current) throw new Error('NO_DOCUMENT');
  if (active || busy) throw new Error('READER_BUSY');
  const backup = validateNotebook(value, current.fingerprint);
  if (backup.document.pageCount !== current.pageCount) throw new Error('FINGERPRINT_MISMATCH');
  if (options.confirmReplace && !confirm(t('replaceConfirm'))) return false;
  // Hold the edit lock across storage awaits so incoming Pencil events cannot
  // be overwritten by a remote snapshot after the initial drawing check.
  busy = true; controls();
  try {
    if (!(await flush()) && (dirty.size || metaSaved !== metaVersion)) throw new Error('SAVE_FAILED');
    const position = options.preservePosition ? pageNumber : backup.position;
    const importedPages = backup.pages.map(p => ({ ...p, strokes: p.strokes.flatMap(s => {
      // An explicit backup restore is a new edit. Fresh IDs let restored ink
      // survive permanent cloud tombstones from an earlier erasure.
      const stroke = { ...s, id: options.confirmReplace ? uid() : s.id || uid() };
      return stroke.points.length > 5000 ? splitStroke(stroke, uid) : [stroke];
    }) }));
    await storage.importPages(current.fingerprint, importedPages, backup.bookmarks, position);
    mutationRevision++;
    pages.clear(); importedPages.forEach(p => pages.set(p.number, p.strokes));
    histories.clear(); dirty.clear(); current.bookmarks = backup.bookmarks; pageNumber = position; await ensurePage(pageNumber);
    renderBookmarks(); await renderPage(!options.silent); status('saved');
    if (!options.silent) signal('atr:notes-saved', { ...currentInfo(), page: pageNumber });
    return true;
  } finally { busy = false; controls(); }
}
async function exportPDF() {
  if (!current || busy) return;
  try {
    const backup = await notebook(); busy = true; controls(); toast(t('exporting'), 60000);
    if (!window.PDFLib?.PDFDocument) throw new Error('EXPORT_LIBRARY_UNAVAILABLE');
    const { PDFDocument, rgb } = window.PDFLib;
    const result = await PDFDocument.load(pdfBytes.slice()); const outputPages = result.getPages();
    for (const annotation of backup.pages) {
      const page = outputPages[annotation.number - 1]; const crop = page.getCropBox(), media = page.getMediaBox();
      const originX = Math.max(crop.x, media.x), originY = Math.max(crop.y, media.y);
      const width = Math.min(crop.x + crop.width, media.x + media.width) - originX;
      const height = Math.min(crop.y + crop.height, media.y + media.height) - originY;
      const rotation = ((page.getRotation().angle % 360) + 360) % 360;
      // Draw in the PDF.js rotated display frame, then rotate the overlay into PDF space.
      const displayW = rotation % 180 ? height : width, displayH = rotation % 180 ? width : height;
      const coordinate = p => pdfPoint(p, { x: originX, y: originY, width, height }, rotation);
      for (const stroke of annotation.strokes) {
        const hex = stroke.color.slice(1); const c = rgb(parseInt(hex.slice(0, 2), 16) / 255, parseInt(hex.slice(2, 4), 16) / 255, parseInt(hex.slice(4, 6), 16) / 255);
        if (stroke.points.length === 1) { const point = coordinate(stroke.points[0]); page.drawCircle({ x: point.x, y: point.y, size: Math.max(.25, stroke.width * displayW / 2), color: c }); }
        for (let i = 1; i < stroke.points.length; i++) {
          const a = stroke.points[i - 1], b = stroke.points[i]; page.drawLine({ start: coordinate(a), end: coordinate(b), thickness: Math.max(.3, stroke.width * displayW * (.45 + .95 * (a.p + b.p) / 2)), color: c, lineCap: 1 });
        }
      }
    }
    result.setTitle(current.title); result.setSubject('Personal study copy with handwritten notes');
    download(await result.save(), safeName(current.title) + '-notes.pdf', 'application/pdf'); toast(t('exported'));
  } catch { toast(t('exportFailed'), 10000); }
  finally { busy = false; controls(); }
}
function undo(redo = false) {
  if (!current || busy) return; finishStroke(); const h = history(); const source = redo ? h.redo : h.undo, destination = redo ? h.undo : h.redo;
  const item = source.pop(); if (!item) return;
  const previous = state(), next = clone(redo ? item.after : item.before), nextIds = new Set(next.map(s => s.id));
  previous.forEach(s => { if (!nextIds.has(s.id)) retiredIds.add(s.id); });
  const currentIds = new Set(previous.map(s => s.id)); next.forEach(s => { if (retiredIds.has(s.id) && !currentIds.has(s.id)) s.id = uid(); });
  destination.push(item); pages.set(pageNumber, next); markDirty(); drawInk(); controls();
}

document.querySelectorAll('button[data-tool]').forEach(button => button.addEventListener('click', () => chooseTool(button.dataset.tool)));
document.querySelectorAll('[data-color]').forEach(button => button.addEventListener('click', () => {
  color = button.dataset.color; document.querySelectorAll('[data-color]').forEach(b => { b.classList.toggle('active', b === button); b.setAttribute('aria-pressed', String(b === button)); }); chooseTool('pen');
}));
$('finger-draw').addEventListener('change', () => chooseTool(tool)); $('pen-width').addEventListener('input', () => { $('width-value').value = $('pen-width').value; });
$('undo').addEventListener('click', () => undo()); $('redo').addEventListener('click', () => undo(true));
$('previous-page').addEventListener('click', () => goPage(pageNumber - 1)); $('next-page').addEventListener('click', () => goPage(pageNumber + 1));
$('page-number').addEventListener('change', event => goPage(event.target.value)); $('page-number').addEventListener('keydown', event => { if (event.key === 'Enter') { event.target.blur(); goPage(event.target.value); } });
$('zoom').addEventListener('change', () => { finishStroke(); if (pdf && !busy) renderPage(false).catch(() => showError(t('loadError'))); });
$('bookmark').addEventListener('click', () => {
  if (!current) return; const marks = new Set(current.bookmarks || []); if (marks.has(pageNumber)) marks.delete(pageNumber); else marks.add(pageNumber);
  current.bookmarks = [...marks].sort((a, b) => a - b); renderBookmarks(); markMeta();
});
$('bookmarks').addEventListener('change', event => { if (event.target.value) goPage(Number(event.target.value)); event.target.value = ''; });
$('open-library').addEventListener('click', showLibrary); $('choose-document').addEventListener('click', showLibrary);
$('open-options').addEventListener('click', () => { finishStroke(); controls(); $('options-dialog').showModal(); });
document.querySelectorAll('.close-dialog').forEach(b => b.addEventListener('click', () => b.closest('dialog').close()));
document.querySelectorAll('dialog').forEach(dialog => dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } }));
$('import-pdf').addEventListener('click', () => $('pdf-input').click());
$('pdf-input').addEventListener('change', async event => {
  const file = event.target.files[0]; event.target.value = ''; if (!file) return;
  if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') return toast(t('notPDF'));
  if (file.size > 50 * 1024 * 1024) return toast(t('pdfLimit'));
  explicitSelection = true;
  closeDialogs(); const bytes = await file.arrayBuffer(); retry = () => openBytes(bytes.slice(0), { title: file.name.replace(/\.pdf$/i, '') });
  $('original-link').hidden = true; await retry();
});
$('retry-open').addEventListener('click', () => retry ? retry() : showLibrary());
$('export-backup').addEventListener('click', async () => {
  if (!current) return toast(t('openFirst'));
  try { download(JSON.stringify(await notebook()), safeName(current.title) + '-notes.json', 'application/json'); toast(t('backupReady')); }
  catch { toast(t('exportFailed'), 10000); }
});
$('import-backup').addEventListener('click', () => { if (current) $('backup-input').click(); else toast(t('openFirst')); });
$('backup-input').addEventListener('change', async event => {
  const file = event.target.files[0]; event.target.value = ''; if (!file || !current) return;
  try { if (file.size > 30 * 1024 * 1024) throw new Error('INVALID'); const value = JSON.parse(await file.text()); if (await applyNotebook(value, { confirmReplace: true })) { closeDialogs(); toast(t('imported')); } }
  catch (error) { toast(t(error.message === 'FINGERPRINT_MISMATCH' ? 'fingerprintMismatch' : 'backupInvalid'), 9000); }
});
$('export-pdf').addEventListener('click', exportPDF);
$('clear-page').addEventListener('click', () => {
  if (!current || !state().length || !confirm(t('clearConfirm'))) return;
  finishStroke(); const before = clone(state()); before.forEach(s => retiredIds.add(s.id)); pages.set(pageNumber, []); historyEntry(before, []); markDirty(); drawInk(); closeDialogs();
});
$('persistent-storage').addEventListener('click', async () => { try { toast(t(await navigator.storage?.persist?.() ? 'persistentYes' : 'persistentNo'), 8000); } catch { toast(t('persistentNo')); } });
$('cloud-sync').addEventListener('click', () => {
  const event = new CustomEvent('atr:cloud-request', { cancelable: true }); if (window.dispatchEvent(event)) toast(t('cloudSetup'));
});
document.addEventListener('keydown', event => {
  if (/INPUT|TEXTAREA|SELECT/.test(event.target.tagName) || document.querySelector('dialog[open]')) return;
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'z') { event.preventDefault(); undo(event.shiftKey); }
  else if (event.key.toLowerCase() === 'p') chooseTool('pen'); else if (event.key.toLowerCase() === 'e') chooseTool('eraser'); else if (event.key.toLowerCase() === 'h') chooseTool('read');
  else if (event.key === 'ArrowLeft') { event.preventDefault(); goPage(pageNumber - 1); } else if (event.key === 'ArrowRight') { event.preventDefault(); goPage(pageNumber + 1); }
});
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') { finishStroke(); flush(); } });
window.addEventListener('pagehide', () => { finishStroke(); flush(); });
window.addEventListener('beforeunload', event => { if (dirty.size) { finishStroke(); flush(); event.preventDefault(); event.returnValue = ''; } });
let resizeTimer; window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => { if (pdf && !active && !busy) renderPage(false).catch(() => {}); }, 180); });
window.ATRNotebook = Object.freeze({ current: currentInfo, exportNotebook: notebook, applyNotebook, openPublic: openPublished, openStored,
  pdfBlob: () => current?.pdf || null, flush, language: en ? 'en' : 'ko' });

async function init() {
  controls(); chooseTool('pen');
  try {
    const response = await fetch(new URL('archive-manifest.json', rootURL), { credentials: 'omit' }); if (!response.ok) throw new Error('CATALOG');
    const value = await response.json();
    catalog = value.documents.filter(d => d.series === 'lecture-notes' && /^[a-z0-9-]+$/.test(d.id) &&
      d.href === 'archive/files/' + d.id + '.pdf' && /^[a-f0-9]{64}$/.test(d.sha256));
  } catch { /* personal and previously cached PDFs remain usable */ }
  const id = params.get('id');
  // A selection made while the catalog loads takes precedence over startup restore.
  if (!explicitSelection && !current && !busy) {
    if (id) await openPublished(id);
    else if (/^[a-f0-9]{64}$/.test(initialLocal || '')) await openStored(initialLocal);
  }
  signal('atr:reader-ready', currentInfo());
}
init().catch(() => showError(t('loadError')));
