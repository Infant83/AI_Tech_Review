import * as pdfjs from './vendor/pdf.mjs';
import { clamp, normalizedPoint, eraseStrokes, splitStroke, STROKE_CHUNK_POINTS, pdfPoint, validateNotebook, NOTEBOOK_FORMAT, MAX_PAGES } from './ink-core.mjs';
import * as storage from './storage.mjs';
import { roleCapabilities, strokeAuthorMap, strokeKey } from './cloud-core.mjs';
import { editionsFor, selectEdition } from './editions.mjs';

const $ = id => document.getElementById(id);
const rootURL = new URL('../../', import.meta.url);
const params = new URLSearchParams(location.search);
const initialLocal = new URLSearchParams(location.hash.slice(1)).get('local');
const en = params.get('lang') === 'en';
const strings = {
  lectures: ['렉처 노트', 'Lecture notes'], studyNotebook: ['PDF 학습 노트', 'PDF study notebook'], choosePDF: ['공부할 PDF를 열어주세요', 'Open a PDF to begin'],
  ready: ['준비됨', 'Ready'], cloud: ['로그인·동기화', 'Sign in and sync'], sync: ['로그인', 'Sign in'], library: ['내 학습 공간', 'My study space'], myLibrary: ['내 학습 공간', 'My study space'],
  inkTools: ['필기 도구', 'Writing tools'], pen: ['펜', 'Pen'], eraser: ['지우개', 'Eraser'], move: ['읽기', 'Read'], penColor: ['펜 색상', 'Pen color'],
  black: ['검정', 'Black'], green: ['초록', 'Green'], red: ['빨강', 'Red'], blue: ['파랑', 'Blue'], width: ['굵기', 'Width'], penWidth: ['펜 굵기', 'Pen width'],
  undo: ['실행 취소', 'Undo'], redo: ['다시 실행', 'Redo'], finger: ['손가락 필기', 'Finger ink'], options: ['저장·가져오기·도움말', 'Export, import and help'],
  welcome: ['PDF와 나의 학습 노트', 'PDFs and my study notes'], welcomeBody: ['렉처를 읽거나 내 PDF를 가져와 공부하세요. 필기와 읽던 위치를 기기에 저장하고, 로그인 후 선택한 노트를 동기화합니다.', 'Read lecture notes or bring your own PDF. Save ink and your place on this device, and sync selected notebooks after signing in.'],
  openPDF: ['자료 선택', 'Choose study material'], privateFiles: ['PDF 가져오기는 기기에서 열기입니다. 클라우드 보관은 별도로 선택합니다.', 'Import opens a PDF on this device. Cloud file storage is a separate choice.'], loading: ['PDF를 여는 중입니다…', 'Opening your PDF…'],
  pdfPage: ['PDF 페이지', 'PDF page'], pdfContent: ['PDF 본문', 'PDF content'], inkCanvas: ['펜 필기 영역', 'Handwriting canvas'], cannotOpen: ['PDF를 열지 못했습니다', 'Could not open this PDF'], retry: ['다시 열기', 'Try again'], openOriginal: ['원본 PDF 열기', 'Open original PDF'],
  previous: ['이전 페이지', 'Previous page'], next: ['다음 페이지', 'Next page'], pageNumber: ['페이지 번호', 'Page number'], bookmark: ['이 페이지 책갈피', 'Bookmark this page'], goBookmark: ['책갈피 이동', 'Go to bookmark'], bookmarks: ['책갈피', 'Bookmarks'], zoom: ['확대', 'Zoom'], fitWidth: ['너비 맞춤', 'Fit width'],
  personalLearning: ['나의 학습', 'Personal study'], libraryBody: ['읽던 페이지와 필기가 이 브라우저에 보관됩니다. 중요한 필기는 백업 파일로도 보관하세요.', 'Your place and notes stay in this browser. Keep a backup of important notes too.'], importPDF: ['내 PDF 가져오기', 'Bring your own PDF'], localOnly: ['업로드 없이 이 기기에 보관', 'Keep on this device without uploading'], recent: ['이어서 공부하기', 'Continue studying'], publishedLectures: ['렉처 자료', 'Published lectures'], close: ['닫기', 'Close'],
  exportPDF: ['필기한 PDF 내보내기', 'Export PDF with ink'], exportBackup: ['수정 가능한 필기 백업', 'Export editable notes backup'], importBackup: ['필기 백업 가져오기', 'Import notes backup'],
  exportOriginal: ['원본 PDF 내보내기', 'Export original PDF'], sourceHelp: ['PDF 원본은 그대로 두고 필기를 별도로 저장합니다. 원본 PDF와 필기를 포함한 사본을 각각 내보낼 수 있습니다.', 'The original PDF stays unchanged; ink is stored separately. Export either the original PDF or a copy with ink.'], originalReady: ['필기 없는 원본 PDF를 저장했습니다.', 'The original PDF without ink is ready.'],
  drawingHelp: ['스크롤로 읽고, 펜으로 쓰세요', 'Scroll to read, write with your pen'], drawingHelpBody: ['위아래로 스크롤해 페이지를 이어 읽습니다. Apple Pencil로 필기하고 손가락으로 이동하거나 두 손가락으로 확대하세요. 손가락 필기를 꺼두면 두 번 탭해 2배 확대와 너비 맞춤을 전환합니다. 마우스는 읽기 도구에서 두 번 클릭하세요. 손가락 필기는 도구에서 켤 수 있습니다.', 'Scroll up and down through the pages. Write with Apple Pencil, move with a finger, or pinch to zoom. With Finger ink off, double-tap to switch between 2× and fit width. In the Read tool, double-click with a mouse. Enable Finger ink to draw with a finger.'],
  savingHelp: ['필기는 자동 저장됩니다', 'Your notes save automatically'], savingHelpBody: ['이 기기·브라우저에 필기와 읽던 페이지를 저장합니다. 로그인하면 선택한 노트를 동기화합니다. 개인 PDF 원본까지 클라우드 보관한 경우 다른 기기에서도 파일을 열 수 있고, 기기에만 둔 PDF는 같은 원본 파일을 다시 가져와야 합니다. 중요한 필기는 백업 파일로도 보관하세요.', 'Ink and your place are saved on this device. Sign in to sync selected notebooks. A private PDF stored in the cloud can also open on other devices; a device-only PDF needs the identical original file there. Keep a backup of important notes.'],
  exportHelp: ['필기 PDF는 다른 앱에서 읽거나 공유하는 사본입니다. 필기를 계속 수정하려면 백업 파일도 보관하세요.', 'The inked PDF is a copy for reading and sharing in other apps. Keep the editable backup to continue editing strokes.'], retainStorage: ['이 기기에 보관 유지 요청', 'Request persistent device storage'], clearPage: ['현재 페이지의 필기 지우기', 'Clear ink on this page'], shortcuts: ['단축키: P 펜 · E 지우개 · H 읽기 · ← → 페이지 · ⌘/Ctrl+Z 실행 취소', 'Keys: P pen · E eraser · H read · ← → pages · ⌘/Ctrl+Z undo'],
  saving: ['저장 중…', 'Saving…'], saved: ['이 기기에 저장됨', 'Saved on this device'], saveFailed: ['저장 실패 · 백업 필요', 'Save failed · back up'],
  fullscreen: ['전체화면', 'Fullscreen'], exitFullscreen: ['전체화면 나가기', 'Exit fullscreen'],
  storageError: ['이 브라우저에서 저장하지 못했습니다. 필기를 백업해 주세요. 저장이 복구될 때까지 현재 PDF를 유지합니다.', 'This browser could not save your notes. Export a backup. Keep this PDF open until saving is restored.'],
  noRecent: ['아직 보관한 PDF가 없습니다.', 'No PDFs saved yet.'], noCatalog: ['렉처 목록을 불러오지 못했습니다. 내 PDF는 계속 열 수 있습니다.', 'The lecture catalog is unavailable. You can still open a local PDF.'],
  pdfLimit: ['PDF는 50 MB 이하의 파일을 열 수 있습니다.', 'Choose a PDF up to 50 MB.'], notPDF: ['PDF 파일을 선택해 주세요.', 'Please choose a PDF file.'], unknownPDF: ['등록된 렉처 PDF를 찾을 수 없습니다. 보관함에서 자료를 골라 주세요.', 'This lecture PDF is not registered. Choose one from the library.'],
  hashMismatch: ['PDF 판본이 목록과 다릅니다. 새로고침 후 다시 열어주세요.', 'The PDF version differs from the catalog. Refresh and try again.'],
  loadError: ['파일을 불러오지 못했습니다. 인터넷 연결 또는 PDF 파일을 확인해 주세요.', 'Could not load the file. Check the connection or PDF.'],
  pageLimit: ['페이지 수가 너무 많습니다. 10,000쪽 이하 PDF를 선택해 주세요.', 'Choose a PDF of no more than 10,000 pages.'],
  backupReady: ['수정 가능한 필기 백업을 저장했습니다.', 'Your editable notes backup is ready.'], exported: ['필기한 PDF를 저장했습니다.', 'Your PDF with ink is ready.'], exporting: ['PDF에 필기를 옮기는 중…', 'Preparing your inked PDF…'],
  exportFailed: ['PDF를 내보내지 못했습니다. 암호화된 PDF라면 원본 잠금을 해제한 뒤 다시 시도해 주세요. 필기 백업은 사용할 수 있습니다.', 'Could not export this PDF. If it is encrypted, unlock the original and try again. The editable notes backup remains available.'],
  backupInvalid: ['이 필기 백업을 읽을 수 없습니다. 지원하는 백업 파일인지 확인해 주세요.', 'This is not a valid supported notes backup.'], fingerprintMismatch: ['다른 PDF의 필기입니다. 백업을 만든 것과 같은 원본 PDF를 먼저 열어주세요.', 'These notes belong to a different PDF. Open the exact original PDF used for this backup first.'],
  requestedPDFMismatch: ['이 노트의 원본 PDF와 다른 파일입니다. 같은 원본 파일을 다시 선택해 주세요.', 'This file differs from this notebook’s original PDF. Choose the identical original file.'],
  pdfEdition: ['PDF 판본', 'PDF edition'], editionHelp: ['판본마다 필기가 따로 보존됩니다.', 'Each edition keeps its own notes.'],
  replaceConfirm: ['백업으로 이 PDF의 현재 필기를 바꿀까요? 기존 필기는 먼저 백업해 주세요.', 'Replace this PDF’s current notes with the backup? Export your current notes first.'], imported: ['필기를 가져왔습니다.', 'Notes imported.'], clearConfirm: ['현재 페이지의 필기를 모두 지울까요? 실행 취소로 되돌릴 수 있습니다.', 'Clear all ink on this page? You can undo this.'],
  clearSharedConfirm: ['이 노트의 현재 페이지 필기를 모두 지울까요? 공유 중이면 다른 사람의 필기도 함께 지워지고 모두에게 반영됩니다. 지운 직후에는 실행 취소로 되돌릴 수 있습니다.', 'Clear all ink on this notebook’s current page? If shared, other members’ ink is erased too and everyone sees the change. You can undo immediately afterward.'],
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
let requestedLocalPDF = null;
let documentOpenGeneration = 0, readerInkEpoch = 0;
let saveFeedbackTimer = null, saveFeedbackEpoch = 0, saveFeedbackOwner = null, saveFeedbackGeneration = -1, saveFeedbackShownAt = 0, saveFeedbackWanted = 'ready';
let readerFocusGeneration = 0, readerNativeFullscreen = false, readerFocusReturn = null, readerResizePending = false, readerResizeAnchorPending = false, resizeTimer;
let readerFocusAnchor = null, readerFocusInputEpoch = 0, readerExpectedNativeExit = 0;
let permissions = { role: 'local', accountId: null, notebookId: null }, strokeAuthors = new Map(), suspendedTool = null;
const pages = new Map(), dirty = new Map(), versions = new Map(), histories = new Map(), retiredIds = new Set();
let pdfCanvas = $('pdf-canvas'), inkCanvas = $('ink-canvas'), sheet = $('page-sheet');
let cssWidth = 595, cssHeight = 842, pixelRatio = 1, retry = null;
const uid = () => crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + '-' + Math.random().toString(36).slice(2);
const clone = value => JSON.parse(JSON.stringify(value));
function signal(name, detail) { window.dispatchEvent(new CustomEvent(name, { detail })); }
// Cache, network and file reads can finish after the user chooses another PDF.
function beginDocumentOpen({ explicit = false, fingerprint = null } = {}) {
  const intent = ++documentOpenGeneration;
  if (explicit) { explicitSelection = true; signal('atr:document-selection', { fingerprint }); }
  return intent;
}
function isCurrentDocumentOpen(intent) { return intent === documentOpenGeneration; }
function paintSaveStatus(kind) {
  const e = $('save-state'); if (!e) return;
  const text = t({ pending: 'saving', saved: 'saved', error: 'saveFailed', ready: 'ready' }[kind]);
  if (e.dataset.state !== kind) e.dataset.state = kind;
  if (e.textContent !== text) e.textContent = text;
}
function status(kind, owner = current, generation = documentOpenGeneration) {
  if (owner !== current || generation !== documentOpenGeneration) return;
  if (saveFeedbackOwner !== owner || saveFeedbackGeneration !== generation) {
    clearTimeout(saveFeedbackTimer); saveFeedbackTimer = null; saveFeedbackEpoch++;
    saveFeedbackOwner = owner; saveFeedbackGeneration = generation; saveFeedbackShownAt = 0; saveFeedbackWanted = 'ready';
    if (kind === 'pending') paintSaveStatus('ready');
  }
  if (kind === 'pending' && (saveFeedbackWanted === 'pending' || saveFeedbackWanted === 'error')) return;
  clearTimeout(saveFeedbackTimer); saveFeedbackTimer = null;
  const epoch = ++saveFeedbackEpoch; saveFeedbackWanted = kind;
  const valid = () => owner === current && generation === documentOpenGeneration && epoch === saveFeedbackEpoch;
  const later = (delay, callback) => {
    const timer = setTimeout(() => {
      if (saveFeedbackTimer !== timer || !valid()) return;
      saveFeedbackTimer = null; callback();
    }, delay);
    saveFeedbackTimer = timer;
  };
  if (kind === 'pending') {
    if ($('save-state')?.dataset.state === 'pending') return;
    later(600, () => { saveFeedbackShownAt = Date.now(); paintSaveStatus('pending'); });
  } else if (kind === 'saved' && $('save-state')?.dataset.state === 'pending') {
    const remaining = Math.max(0, 300 - (Date.now() - saveFeedbackShownAt));
    if (remaining) later(remaining, () => paintSaveStatus('saved'));
    else paintSaveStatus('saved');
  } else paintSaveStatus(kind);
}
function toast(message, duration = 5000) { clearTimeout(toastTimer); $('toast').textContent = message; $('toast').hidden = false; toastTimer = setTimeout(() => { $('toast').hidden = true; }, duration); }
function storageFailure(owner = current, generation = documentOpenGeneration) {
  if (owner !== current || generation !== documentOpenGeneration) return;
  status('error', owner, generation);
  if (Date.now() - lastStorageError > 12000) { toast(t('storageError'), 10000); lastStorageError = Date.now(); }
}
function currentInfo() { return current ? { fingerprint: current.fingerprint, title: current.title, pageCount: current.pageCount, page: pageNumber, publicId: current.publicId || null, isLocal: !current.publicId, drawing: Boolean(active), busy, mutationRevision, role: permissions.role } : null; }
function canAddInk() { return permissions.role === 'local' || roleCapabilities(permissions.role).canAdd; }
function canEditAllInk() { return permissions.role === 'local' || roleCapabilities(permissions.role).canEditAll; }
function canEraseStroke(stroke, number = pageNumber) { return canEditAllInk() || (permissions.role === 'contributor' && strokeAuthors.get(strokeKey(number, stroke.id)) === permissions.accountId); }
function ownStroke(stroke, number = pageNumber) { if (permissions.accountId) strokeAuthors.set(strokeKey(number, stroke.id), permissions.accountId); }
function setPermissions(value = {}) {
  if (!current || (value.fingerprint && value.fingerprint !== current.fingerprint)) return false;
  const role = value.role || 'viewer'; if (role !== 'local') roleCapabilities(role);
  if (role === 'contributor' && (typeof value.accountId !== 'string' || !value.accountId)) throw new Error('INVALID_ROLE');
  finishStroke();
  const newView = permissions.accountId !== (value.accountId || null) || permissions.notebookId !== (value.notebookId || null);
  const changed = permissions.role !== role || newView;
  permissions = { role, accountId: value.accountId || null, notebookId: value.notebookId || null };
  if (value.strokeAuthors) {
    const incoming = strokeAuthorMap(value.strokeAuthors, current.pageCount);
    if (!newView) for (const [key, owner] of strokeAuthors) if (!incoming.has(key) && owner === permissions.accountId) incoming.set(key, owner);
    strokeAuthors = incoming;
  } else if (changed) strokeAuthors.clear();
  if (changed) { mutationRevision++; histories.clear(); }
  if (!canAddInk()) { if (tool !== 'read') suspendedTool = tool; chooseTool('read'); }
  else if (suspendedTool) { const restored = suspendedTool; suspendedTool = null; chooseTool(restored); }
  sheet.dataset.permission = role; controls(); return true;
}
function state() { return pages.get(pageNumber) || []; }
function history() { if (!histories.has(pageNumber)) histories.set(pageNumber, { undo: [], redo: [] }); return histories.get(pageNumber); }
function controls() {
  $('undo').disabled = !current || !canAddInk() || !history().undo.length || busy;
  $('redo').disabled = !current || !canAddInk() || !history().redo.length || busy;
  $('previous-page').disabled = !current || pageNumber <= 1 || busy;
  $('next-page').disabled = !current || pageNumber >= current.pageCount || busy;
  ['export-original', 'export-pdf', 'export-backup', 'import-backup', 'clear-page', 'bookmark'].forEach(id => { $(id).disabled = !current || busy; });
  ['import-backup', 'clear-page'].forEach(id => { $(id).disabled ||= !canEditAllInk(); });
  document.querySelectorAll('[data-tool="pen"],[data-tool="eraser"],[data-color]').forEach(node => { node.disabled = !current || busy || !canAddInk(); });
  $('finger-draw').disabled = $('pen-width').disabled = !current || busy || !canAddInk();
  $('page-number').disabled = !current || busy;
  if ($('pdf-edition')) $('pdf-edition').disabled = !current || busy;
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
  const document = current, feedbackGeneration = documentOpenGeneration, snapshots = [...dirty].map(([number, version]) => ({ number, version, strokes: clone(pages.get(number) || []) }));
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
        if (!dirty.size && metaSaved === metaVersion) status('saved', document, feedbackGeneration);
        if (snapshots.length || metadataChanged) signal('atr:notes-saved', { ...currentInfo(), page: pageNumber, metadataOnly: !snapshots.length });
      }
      return true;
    } catch { storageFailure(document, feedbackGeneration); return false; }
  });
  return writeQueue;
}
function drawStroke(ctx, stroke, width = cssWidth, height = cssHeight) {
  if (!stroke.points.length) return;
  ctx.strokeStyle = stroke.color; ctx.fillStyle = stroke.color; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const points = stroke.points;
  if (points.length === 1) { const p = points[0]; ctx.beginPath(); ctx.arc(p.x * width, p.y * height, Math.max(.4, stroke.width * width * .5), 0, Math.PI * 2); ctx.fill(); return; }
  for (let i = 1; i < points.length; i++) {
    const a = points[i - 1], b = points[i];
    ctx.lineWidth = Math.max(.35, stroke.width * width * (.45 + .95 * (a.p + b.p) / 2));
    ctx.beginPath(); ctx.moveTo(a.x * width, a.y * height); ctx.lineTo(b.x * width, b.y * height); ctx.stroke();
  }
}
function drawReaderViewInk(view) {
  if (!view.inkCanvas || !view.inkCanvas.width || !view.cssWidth) return;
  const ctx = view.inkCanvas.getContext('2d');
  ctx.setTransform(view.pixelRatio, 0, 0, view.pixelRatio, 0, 0); ctx.clearRect(0, 0, view.cssWidth, view.cssHeight);
  (pages.get(view.number) || []).forEach(stroke => drawStroke(ctx, stroke, view.cssWidth, view.cssHeight));
}
function drawInk() {
  drawingFrame = 0;
  if (readerViews.size) { for (const view of readerMountedViews) if (view.ready || view.number === pageNumber) drawReaderViewInk(view); return; }
  const ctx = inkCanvas.getContext('2d'); ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0); ctx.clearRect(0, 0, cssWidth, cssHeight);
  state().forEach(stroke => drawStroke(ctx, stroke));
}
function requestInk() { if (!drawingFrame) drawingFrame = requestAnimationFrame(drawInk); }
function historyEntry(before, after) {
  const beforeIds = new Set(before.map(stroke => stroke.id)), afterIds = new Set(after.map(stroke => stroke.id));
  const action = { added: clone(after.filter(stroke => !beforeIds.has(stroke.id))), removed: clone(before.filter(stroke => !afterIds.has(stroke.id))) };
  if (!action.added.length && !action.removed.length) return;
  const h = history(); h.undo.push(action); if (h.undo.length > 80) h.undo.shift(); h.redo.length = 0; controls();
}
function finishStroke() {
  if (!active) return;
  const before = active.before, number = active.page, pointerId = active.id, canvas = active.canvas || inkCanvas;
  active = null;
  try { canvas.releasePointerCapture(pointerId); } catch { /* capture may already have ended */ }
  inkCanvas.style.touchAction = $('finger-draw').checked && tool !== 'read' ? 'none' : 'manipulation';
  if (number === pageNumber) { clearTimeout(readerPositionTimer); readerPositionTimer = null; historyEntry(before, state()); markDirty(); void flush(); }
  requestInk();
  if (readerResizePending) scheduleReaderResize();
  if (readerScrollPending) scheduleReaderVisible();
  queueReaderNeighbours();
}
function chooseTool(next) {
  finishStroke(); tool = canAddInk() ? next : 'read'; next = tool; sheet.dataset.tool = next;
  document.querySelectorAll('[data-tool]').forEach(e => { if (e.tagName === 'BUTTON') { e.classList.toggle('active', e.dataset.tool === next); e.setAttribute('aria-pressed', String(e.dataset.tool === next)); } });
  sheet.classList.toggle('finger-drawing', $('finger-draw').checked && tool !== 'read');
  inkCanvas.style.touchAction = $('finger-draw').checked && tool !== 'read' ? 'none' : 'manipulation';
  for (const view of readerMountedViews) readerViewTools(view);
}
function pointerPoint(event) { return normalizedPoint(event.clientX, event.clientY, inkCanvas.getBoundingClientRect(), event.pressure); }
function eraseAt(from, to) {
  const before = state(), editable = before.filter(stroke => canEraseStroke(stroke));
  const retained = new Set(eraseStrokes(editable, from, to, 10, cssWidth, cssHeight).map(stroke => stroke.id));
  const after = before.filter(stroke => !canEraseStroke(stroke) || retained.has(stroke.id));
  if (after.length !== before.length) {
    const kept = new Set(after.map(s => s.id)); before.forEach(s => { if (!kept.has(s.id)) retiredIds.add(s.id); });
    pages.set(pageNumber, after); markDirty(); requestInk();
  }
}
function appendActivePoint(point) {
  if (active.stroke.points.length >= STROKE_CHUNK_POINTS) {
    const previous = active.stroke;
    active.stroke = { ...previous, id: uid(), points: [previous.points[previous.points.length - 1]] };
    ownStroke(active.stroke);
    state().push(active.stroke);
  }
  active.stroke.points.push(point); markDirty(); requestInk();
}
function onInkPointerDown(event) {
  if (!current || busy || !canAddInk() || tool === 'read' || active || (event.pointerType === 'mouse' && event.button !== 0) ||
      (event.pointerType === 'touch' && !$('finger-draw').checked) || !selectReaderInput(event)) return;
  event.preventDefault(); inkCanvas.setPointerCapture(event.pointerId); inkCanvas.style.touchAction = 'none';
  const point = pointerPoint(event), kind = event.button === 5 || event.buttons === 32 ? 'eraser' : tool;
  active = { id: event.pointerId, type: event.pointerType, page: pageNumber, canvas: inkCanvas, before: clone(state()), point, kind };
  if (kind === 'pen') { active.stroke = { id: uid(), color, width: Number($('pen-width').value) / baseWidth, points: [point] }; ownStroke(active.stroke); state().push(active.stroke); markDirty(); requestInk(); }
  else eraseAt(point, point);
}
function onInkPointerMove(event) {
  if (!active || active.id !== event.pointerId || event.currentTarget !== active.canvas) return;
  event.preventDefault();
  const samples = typeof event.getCoalescedEvents === 'function' ? event.getCoalescedEvents() : [event];
  for (const sample of samples.length ? samples : [event]) {
    const point = pointerPoint(sample);
    if (active.kind === 'eraser') eraseAt(active.point, point);
    else if (Math.hypot((point.x - active.point.x) * cssWidth, (point.y - active.point.y) * cssHeight) > .35) appendActivePoint(point);
    active.point = point;
  }
}
function onInkPointerEnd(event) {
  if (active?.id !== event.pointerId || event.currentTarget !== active.canvas) return;
  if (event.type === 'pointerup' && active.kind === 'pen') {
    const point = pointerPoint(event);
    if (Math.hypot((point.x - active.point.x) * cssWidth, (point.y - active.point.y) * cssHeight) > .35) appendActivePoint(point);
  }
  finishStroke();
}
function bindReaderInk(canvas) {
  canvas.addEventListener('pointerover', event => { if (event.pointerType === 'pen' && tool !== 'read') canvas.style.touchAction = 'none'; });
  for (const name of ['pointerout', 'pointerleave']) canvas.addEventListener(name, () => {
    if (!active) canvas.style.touchAction = $('finger-draw').checked && tool !== 'read' ? 'none' : 'manipulation';
  });
  canvas.addEventListener('pointerdown', onInkPointerDown); canvas.addEventListener('pointermove', onInkPointerMove);
  for (const name of ['pointerup', 'pointercancel', 'lostpointercapture']) canvas.addEventListener(name, onInkPointerEnd);
  // Safari exposes Pencil touchType. Keep finger scroll/pinch native otherwise.
  for (const name of ['touchstart', 'touchmove']) canvas.addEventListener(name, event => {
    if (tool !== 'read' && ($('finger-draw').checked || active?.type === 'pen' || [...event.touches].some(touch => touch.touchType === 'stylus'))) event.preventDefault();
  }, { passive: false });
}
bindReaderInk(inkCanvas);

// Continuous reader views keep document geometry, ink and bitmap lifetimes separate.
// Only the active page and its immediate neighbours own canvas backing stores.
const READER_BITMAP_BUDGET = 20_000_000;
const READER_ACTIVE_PIXELS = 8_000_000;
const READER_NEIGHBOUR_PIXELS = 1_000_000;
const readerViews = new Map(), readerCanvasViews = new WeakMap(), readerMountedViews = new Set();
let readerViewsOwner = null, readerViewPDF = null, readerViewEpoch = 0, readerScrollFrame = 0, readerBoundView = null, readerLayoutKey = null;
let readerNeighbourQueue = Promise.resolve(), readerNeighbourRequested = false, readerNeighbourRunning = false, readerNeighbourGeneration = 0, readerPositionTimer = null, readerScrollPending = false;
let readerLastGestureTap = null, readerGestureCandidate = null, readerNonMouseAt = 0;
const readerTouchPointers = new Set();
function readerRasterPlan(width, height, desiredRatio, maximumPixels = READER_ACTIVE_PIXELS) {
  const limit = Math.max(1, Math.floor(maximumPixels));
  let ratio = Math.min(Math.max(.01, desiredRatio || 1), 4096 / Math.max(width, height), Math.sqrt(limit / (width * height)));
  let pixelsW = Math.max(1, Math.ceil(width * ratio)), pixelsH = Math.max(1, Math.ceil(height * ratio));
  while (pixelsW * pixelsH > limit) {
    ratio *= Math.sqrt(limit / (pixelsW * pixelsH)) * .99999;
    pixelsW = Math.max(1, Math.ceil(width * ratio)); pixelsH = Math.max(1, Math.ceil(height * ratio));
  }
  return { ratio, width: pixelsW, height: pixelsH, pixels: pixelsW * pixelsH };
}
function readerDesiredPixelRatio() {
  return Math.max(1, (window.devicePixelRatio || 1) * (window.visualViewport?.scale || 1));
}
function readerBitmapPixels() {
  let total = 0;
  for (const view of readerMountedViews) for (const canvas of [view.pdfCanvas, view.inkCanvas]) if (canvas) total += canvas.width * canvas.height;
  return total;
}
function resetReaderTap() { readerLastGestureTap = null; readerGestureCandidate = null; }
function readerGestureOffsets() {
  return [...readerScrollOffsets(), window.visualViewport?.offsetLeft || 0, window.visualViewport?.offsetTop || 0];
}
function readerGestureScrollMatches(tap) {
  return !!tap && Array.isArray(tap.scroll) && readerGestureOffsets().every((value, index) => value === tap.scroll[index]);
}
function readerGestureScrolled() {
  // A queued scroll event can arrive after the first tap even though the
  // viewport had already reached those offsets before that tap began.
  if ((readerGestureCandidate && !readerGestureScrollMatches(readerGestureCandidate)) ||
      (readerLastGestureTap && !readerGestureScrollMatches(readerLastGestureTap))) resetReaderTap();
}
function readerViewCurrent(view, epoch = readerViewEpoch, owner = current, documentPDF = pdf) {
  return view && readerViews.get(view.number) === view && readerViewsOwner === owner && current === owner &&
    readerViewPDF === documentPDF && pdf === documentPDF && epoch === readerViewEpoch;
}
function readerViewTools(view) {
  view.sheet.dataset.tool = tool; view.sheet.dataset.permission = permissions.role;
  view.sheet.classList.toggle('finger-drawing', $('finger-draw').checked && tool !== 'read');
  if (view.inkCanvas) view.inkCanvas.style.touchAction = $('finger-draw').checked && tool !== 'read' ? 'none' : 'manipulation';
}
function releaseReaderView(view) {
  if (!view || (active && active.page === view.number)) return;
  view.ready = false; view.sheet.dataset.ready = 'false'; view.sheet.setAttribute('aria-busy', 'true');
  const task = view.renderTask; view.renderTask = null; view.renderToken++;
  if (task) { try { task.cancel(); } catch {} }
  for (const canvas of [view.pdfCanvas, view.inkCanvas]) if (canvas) { canvas.width = 0; canvas.height = 0; }
  if (view.number !== pageNumber) {
    view.pdfCanvas?.remove(); view.inkCanvas?.remove(); view.pdfCanvas = null; view.inkCanvas = null; readerMountedViews.delete(view);
  }
  const page = view.pdfPage; view.pdfPage = null;
  if (page) {
    // cleanup only succeeds after PDF.js releases the old render task.
    const cleanup = () => { try { page.cleanup(); } catch {} };
    if (task) view.releasePromise = Promise.resolve(task.promise).catch(() => {}).then(cleanup); else { cleanup(); view.releasePromise = Promise.resolve(); }
  } else view.releasePromise = task ? Promise.resolve(task.promise).catch(() => {}) : Promise.resolve();
  return view.releasePromise;
}
function prepareReaderCanvases(view) {
  if (view.pdfCanvas && view.inkCanvas) return;
  const paper = document.createElement('canvas'), ink = document.createElement('canvas');
  paper.className = 'pdf-page-canvas'; ink.className = 'ink-page-canvas';
  paper.setAttribute('aria-label', `${t('pdfContent')} · ${view.number}`);
  ink.setAttribute('aria-label', `${t('inkCanvas')} · ${view.number}`); ink.tabIndex = 0;
  paper.width = paper.height = ink.width = ink.height = 0;
  view.pdfCanvas = paper; view.inkCanvas = ink; view.sheet.prepend(paper, ink); readerMountedViews.add(view);
  readerCanvasViews.set(ink, view); bindReaderInk(ink); readerViewTools(view);
}
function bindReaderView(view) {
  if (!view) return;
  prepareReaderCanvases(view);
  const previous = readerBoundView;
  if (previous && previous !== view) { previous.sheet.removeAttribute('id'); previous.pdfCanvas?.removeAttribute('id'); previous.inkCanvas?.removeAttribute('id'); }
  readerBoundView = view;
  sheet = view.sheet; pdfCanvas = view.pdfCanvas; inkCanvas = view.inkCanvas;
  sheet.id = 'page-sheet'; pdfCanvas.id = 'pdf-canvas'; inkCanvas.id = 'ink-canvas';
  cssWidth = view.cssWidth; cssHeight = view.cssHeight; baseWidth = view.naturalWidth; pageAspect = view.aspect;
  pixelRatio = view.pixelRatio || 1; readerViewTools(view);
}
function initializeReaderViews() {
  if (readerViewsOwner === current && readerViewPDF === pdf) return;
  readerViewEpoch++; readerNeighbourGeneration++; readerNeighbourRunning = false; readerNeighbourRequested = false; readerNeighbourQueue = Promise.resolve();
  resetReaderTap(); readerTouchPointers.clear(); clearTimeout(readerPositionTimer);
  for (const view of [...readerMountedViews]) releaseReaderView(view);
  readerViews.clear(); readerMountedViews.clear(); readerBoundView = null; readerLayoutKey = null; readerViewsOwner = current; readerViewPDF = pdf;
  const area = $('page-area'), fragment = document.createDocumentFragment();
  for (let number = 1; number <= current.pageCount; number++) {
    const element = document.createElement('div'), label = document.createElement('span');
    element.className = 'page-sheet reader-page'; element.dataset.page = String(number); element.dataset.ready = 'false';
    element.setAttribute('role', 'group'); element.setAttribute('aria-label', `${t('pdfPage')} ${number}`); element.setAttribute('aria-busy', 'true');
    label.className = 'reader-page-number'; label.textContent = String(number); label.setAttribute('aria-hidden', 'true'); element.append(label);
    const view = { number, sheet: element, aspect: 1.414, naturalWidth: 595, cssWidth: 595, cssHeight: 842,
      pixelRatio: 1, ready: false, renderToken: 0, renderTask: null, pdfPage: null, pdfCanvas: null, inkCanvas: null, renderedKey: null };
    readerViews.set(number, view); readerViewTools(view); fragment.append(element);
  }
  area.replaceChildren(fragment); bindReaderView(readerViews.get(pageNumber));
}
function layoutReaderViews(width) {
  for (const view of readerViews.values()) {
    const height = width * view.aspect;
    if (view.cssWidth === width && view.cssHeight === height && view.sheet.style.width) continue;
    view.cssWidth = width; view.cssHeight = height;
    view.sheet.style.width = width + 'px'; view.sheet.style.height = view.cssHeight + 'px';
    for (const canvas of [view.pdfCanvas, view.inkCanvas]) if (canvas) { canvas.style.width = width + 'px'; canvas.style.height = view.cssHeight + 'px'; }
  }
}
function readerScrollToView(view) {
  if (!view) return;
  const viewport = readerVisibleViewport(), rect = view.sheet.getBoundingClientRect();
  if (!viewport) return;
  let dy = rect.top - viewport.top - 8;
  for (const element of [$('page-area'), $('reader-main')]) {
    if (!element) continue; const old = element.scrollTop;
    element.scrollTop = Math.max(0, Math.min(Math.max(0, element.scrollHeight - element.clientHeight), old + dy));
    dy -= element.scrollTop - old;
  }
  if (Math.abs(dy) > .5) window.scrollTo({ top: (window.scrollY || 0) + dy, left: window.scrollX || 0, behavior: 'instant' });
}
function scheduleReaderPosition() {
  clearTimeout(readerPositionTimer);
  const owner = current, number = pageNumber, generation = documentOpenGeneration;
  const remember = () => {
    readerPositionTimer = null;
    if (owner !== current || generation !== documentOpenGeneration || number !== pageNumber) return;
    if (active || busy) { readerPositionTimer = setTimeout(remember, 300); return; }
    markMeta();
  };
  readerPositionTimer = setTimeout(remember, 300);
}
function readerSelectView(view, remember = true) {
  if (!view || active || view.number === pageNumber) return false;
  pageNumber = view.number; bindReaderView(view); controls();
  if (remember) scheduleReaderPosition(); return true;
}
function nearestReaderView() {
  const viewport = readerVisibleViewport(); if (!viewport || !readerViews.size) return null;
  const middle = (viewport.top + viewport.bottom) / 2;
  let low = 1, high = current.pageCount;
  while (low < high) {
    const number = Math.floor((low + high) / 2), rect = readerViews.get(number).sheet.getBoundingClientRect();
    if (rect.bottom < middle) low = number + 1; else high = number;
  }
  const found = readerViews.get(low), before = readerViews.get(low - 1);
  if (!before) return found;
  const distance = view => { const r = view.sheet.getBoundingClientRect(); return middle < r.top ? r.top - middle : middle > r.bottom ? middle - r.bottom : 0; };
  return distance(before) < distance(found) ? before : found;
}
function readerVisibleChanged() {
  readerScrollFrame = 0;
  if (!current || !pdf || !readerViews.size) return;
  if (active || busy || (readerResizePending && readerAnchorCurrent(readerFocusAnchor))) { readerScrollPending = true; return; }
  readerScrollPending = false;
  const view = nearestReaderView();
  if (readerSelectView(view)) {
    void renderPage(false).catch(() => showError(t('loadError')));
  } else queueReaderNeighbours();
}
function scheduleReaderVisible() {
  if (!readerScrollFrame) readerScrollFrame = requestAnimationFrame(readerVisibleChanged);
}
function evictReaderDistant() {
  return Promise.all([...readerMountedViews].filter(view => Math.abs(view.number - pageNumber) > 1).map(releaseReaderView));
}
async function renderReaderNeighbour(view, epoch, owner, documentPDF) {
  if (!readerViewCurrent(view, epoch, owner, documentPDF) || active || busy || readerResizePending || Math.abs(view.number - pageNumber) !== 1) return;
  if (view.releasePromise) await view.releasePromise;
  if (!readerViewCurrent(view, epoch, owner, documentPDF) || active || busy || readerResizePending) return;
  const page = await documentPDF.getPage(view.number);
  if (!readerViewCurrent(view, epoch, owner, documentPDF) || active || busy || readerResizePending || Math.abs(view.number - pageNumber) !== 1) { try { page.cleanup(); } catch {} return; }
  if (!(await ensurePage(view.number))) { try { page.cleanup(); } catch {} return; }
  if (!readerViewCurrent(view, epoch, owner, documentPDF) || active || busy || readerResizePending || Math.abs(view.number - pageNumber) !== 1) { try { page.cleanup(); } catch {} return; }
  const natural = page.getViewport({ scale: 1 });
  view.naturalWidth = natural.width;
  if (view.aspect !== natural.height / natural.width) {
    const anchor = readerFocusAnchor || captureReaderFocusAnchor();
    if (anchor && !readerFocusAnchor) readerFocusAnchor = anchor;
    view.aspect = natural.height / natural.width; layoutReaderViews(cssWidth);
    if (anchor && readerAnchorCurrent(anchor)) { anchor.scroll = readerScrollOffsets(); restoreReaderFocusAnchor(anchor); }
  }
  prepareReaderCanvases(view); readerViewTools(view);
  const plan = readerRasterPlan(view.cssWidth, view.cssHeight, readerDesiredPixelRatio(), READER_NEIGHBOUR_PIXELS);
  const key = `${view.cssWidth}/${view.cssHeight}/${plan.width}/${plan.height}`;
  if (view.ready && view.renderedKey === key) { drawReaderViewInk(view); if (view.pdfPage !== page) { try { page.cleanup(); } catch {} } return; }
  const old = view.renderTask; if (old) { try { old.cancel(); } catch {} await Promise.resolve(old.promise).catch(() => {}); }
  if (!readerViewCurrent(view, epoch, owner, documentPDF) || active || busy || readerResizePending) { try { page.cleanup(); } catch {} return; }
  view.pdfPage = page; view.pixelRatio = plan.ratio; const token = ++view.renderToken;
  for (const canvas of [view.pdfCanvas, view.inkCanvas]) { canvas.width = plan.width; canvas.height = plan.height; canvas.style.width = view.cssWidth + 'px'; canvas.style.height = view.cssHeight + 'px'; }
  if (readerBitmapPixels() > READER_BITMAP_BUDGET) { releaseReaderView(view); return; }
  const viewport = page.getViewport({ scale: view.cssWidth / natural.width });
  const task = view.renderTask = page.render({ canvasContext: view.pdfCanvas.getContext('2d', { alpha: false }), viewport, transform: [plan.ratio, 0, 0, plan.ratio, 0, 0] });
  try { await task.promise; } catch (error) { if (error.name !== 'RenderingCancelledException') throw error; }
  if (!readerViewCurrent(view, epoch, owner, documentPDF) || token !== view.renderToken || Math.abs(view.number - pageNumber) > 1) { try { page.cleanup(); } catch {} return; }
  view.renderTask = null; view.ready = true; view.renderedKey = key; view.sheet.dataset.ready = 'true'; view.sheet.setAttribute('aria-busy', 'false'); drawReaderViewInk(view);
}
function queueReaderNeighbours() {
  if (!current || !pdf || !readerViews.size || active || busy || readerResizePending) return;
  readerNeighbourRequested = true;
  if (readerNeighbourRunning) return;
  readerNeighbourRunning = true;
  const queueGeneration = readerNeighbourGeneration;
  readerNeighbourQueue = Promise.resolve().then(async () => {
    while (queueGeneration === readerNeighbourGeneration && readerNeighbourRequested) {
      readerNeighbourRequested = false; await evictReaderDistant();
      if (queueGeneration !== readerNeighbourGeneration) break;
      const epoch = readerViewEpoch, owner = current, documentPDF = pdf, number = pageNumber;
      const entries = [readerViews.get(number + 1), readerViews.get(number - 1)].filter(Boolean);
      for (const view of entries) {
        if (!readerViewCurrent(view, epoch, owner, documentPDF) || active || busy || readerResizePending || pageNumber !== number) break;
        try { await renderReaderNeighbour(view, epoch, owner, documentPDF); } catch { /* A failed adjacent preview never replaces the active page. */ }
      }
    }
  }).finally(() => { if (queueGeneration === readerNeighbourGeneration) { readerNeighbourRunning = false; if (readerNeighbourRequested) queueReaderNeighbours(); } });
}
function selectReaderInput(event) {
  const view = readerCanvasViews.get(event.currentTarget);
  if (!view || !view.ready || !pages.has(view.number) || active || busy) return false;
  if (view.number !== pageNumber) { pageNumber = view.number; bindReaderView(view); controls(); scheduleReaderPosition(); readerResizePending = true; }
  return true;
}
function readerGestureView(event) {
  const element = event.target?.closest?.('.reader-page');
  return element ? readerViews.get(Number(element.dataset.page)) : null;
}
function readerTapEligible(event) {
  return event.pointerType === 'touch' && !$('finger-draw').checked && tool !== 'eraser';
}
function captureReaderTap(event) {
  if (event.pointerType !== 'touch') { if (event.pointerType === 'pen') resetReaderTap(); return; }
  readerTouchPointers.add(event.pointerId);
  if (readerTouchPointers.size !== 1 || !readerTapEligible(event)) { resetReaderTap(); return; }
  const view = readerGestureView(event);
  if (!view?.ready || active || busy) { resetReaderTap(); return; }
  if (readerLastGestureTap && !readerGestureScrollMatches(readerLastGestureTap)) resetReaderTap();
  readerGestureCandidate = { id: event.pointerId, x: event.clientX, y: event.clientY, at: Date.now(), number: view.number, owner: current, generation: documentOpenGeneration, scroll: readerGestureOffsets() };
}
function moveReaderTap(event) {
  const candidate = readerGestureCandidate;
  if (candidate?.id === event.pointerId && Math.hypot(event.clientX - candidate.x, event.clientY - candidate.y) > 10) resetReaderTap();
}
function finishReaderTap(event) {
  if (event.pointerType !== 'mouse') readerNonMouseAt = Date.now();
  readerTouchPointers.delete(event.pointerId);
  const candidate = readerGestureCandidate;
  if (event.type === 'lostpointercapture' && !candidate) return;
  readerGestureCandidate = null;
  if (event.type !== 'pointerup' || !candidate || candidate.id !== event.pointerId || readerTouchPointers.size || !readerTapEligible(event) ||
      candidate.owner !== current || candidate.generation !== documentOpenGeneration || !readerGestureScrollMatches(candidate) || Date.now() - candidate.at > 250 ||
      Math.hypot(event.clientX - candidate.x, event.clientY - candidate.y) > 10) { resetReaderTap(); return; }
  const last = readerLastGestureTap, now = Date.now();
  if (last && last.number === candidate.number && last.owner === current && now - last.at <= 320 && Math.hypot(event.clientX - last.x, event.clientY - last.y) <= 28) {
    resetReaderTap(); event.preventDefault(); toggleReaderZoom(event.clientX, event.clientY, candidate.number);
  } else readerLastGestureTap = { number: candidate.number, owner: current, at: now, x: event.clientX, y: event.clientY, scroll: candidate.scroll };
}
function readerPointAnchor(view, clientX, clientY) {
  const viewport = readerVisibleViewport(), rect = view?.sheet.getBoundingClientRect();
  if (!viewport || !rect?.width || !rect.height) return null;
  return { document: current, page: view.number, documentGeneration: documentOpenGeneration, focusGeneration: readerFocusGeneration,
    inputEpoch: readerFocusInputEpoch, x: clamp((clientX - rect.left) / rect.width, 0, 1), y: clamp((clientY - rect.top) / rect.height, 0, 1),
    viewportX: clamp((clientX - viewport.left) / (viewport.right - viewport.left), 0, 1), viewportY: clamp((clientY - viewport.top) / (viewport.bottom - viewport.top), 0, 1), scroll: readerScrollOffsets() };
}
function toggleReaderZoom(clientX, clientY, number = pageNumber) {
  if (!current || !pdf || active || busy) return;
  const view = readerViews.get(number); if (!view?.ready) return;
  readerSelectView(view, false); readerFocusAnchor = readerPointAnchor(view, clientX, clientY);
  $('zoom').value = Number($('zoom').value) > 1 ? '1' : '2';
  void renderPage(false).catch(() => showError(t('loadError')));
}
function initializeReaderScrolling() {
  const area = $('page-area');
  const scrolled = () => { readerGestureScrolled(); scheduleReaderVisible(); };
  area.addEventListener('scroll', scrolled, { passive: true }); window.addEventListener('scroll', scrolled, { passive: true });
  area.addEventListener('pointerdown', captureReaderTap, { capture: true, passive: true });
  area.addEventListener('pointermove', moveReaderTap, { capture: true, passive: true });
  for (const name of ['pointerup', 'pointercancel', 'lostpointercapture']) area.addEventListener(name, finishReaderTap, { capture: true, passive: false });
  area.addEventListener('dblclick', event => {
    if (tool !== 'read' || event.button !== 0 || Date.now() - readerNonMouseAt < 700) return;
    const view = readerGestureView(event); if (!view?.ready) return;
    event.preventDefault(); toggleReaderZoom(event.clientX, event.clientY, view.number);
  });
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', event => { resetReaderTap(); scheduleReaderResize(event); }, { passive: true });
    window.visualViewport.addEventListener('scroll', scrolled, { passive: true });
  }
}

function readerFocusMode() { return document.documentElement.dataset.readerFocus === 'true'; }
function readerScrollOffsets() {
  return [window.scrollX || 0, window.scrollY || 0, $('page-area')?.scrollLeft || 0, $('page-area')?.scrollTop || 0,
    $('reader-main')?.scrollLeft || 0, $('reader-main')?.scrollTop || 0];
}
function readerVisibleViewport() {
  const area = $('page-area'); if (!area?.getBoundingClientRect) return null;
  const rect = area.getBoundingClientRect(), header = document.querySelector('.reader-header')?.getBoundingClientRect?.();
  const footer = !$('page-controls')?.hidden && $('page-controls')?.getBoundingClientRect?.();
  const visual = window.visualViewport, visualLeft = visual?.offsetLeft || 0, visualTop = visual?.offsetTop || 0;
  const left = Math.max(visualLeft, rect.left), right = Math.min(visualLeft + (visual?.width || window.innerWidth), rect.right);
  const top = Math.max(visualTop, rect.top, header?.bottom || 0), bottom = Math.min(visualTop + (visual?.height || window.innerHeight), rect.bottom, footer?.top || Infinity);
  return right > left && bottom > top ? { left, right, top, bottom } : null;
}
function readerAnchorCurrent(anchor, checkScroll = false, nextMode = false) {
  return !!anchor && anchor === readerFocusAnchor && anchor.document === current && anchor.page === pageNumber
    && anchor.documentGeneration === documentOpenGeneration && (nextMode || anchor.focusGeneration === readerFocusGeneration)
    && anchor.inputEpoch === readerFocusInputEpoch
    && (!checkScroll || readerScrollOffsets().every((value, index) => value === anchor.scroll[index]));
}
function captureReaderFocusAnchor() {
  const viewport = readerVisibleViewport(), rect = sheet.getBoundingClientRect?.();
  if (!current || !pdf || !viewport || !rect?.width || !rect.height) return null;
  const left = Math.max(rect.left, viewport.left), right = Math.min(rect.right, viewport.right);
  const top = Math.max(rect.top, viewport.top), bottom = Math.min(rect.bottom, viewport.bottom);
  if (right <= left || bottom <= top) return null;
  const x = (left + right) / 2, y = (top + bottom) / 2;
  return { document: current, page: pageNumber, documentGeneration: documentOpenGeneration,
    focusGeneration: readerFocusGeneration, inputEpoch: readerFocusInputEpoch,
    x: (x - rect.left) / rect.width, y: (y - rect.top) / rect.height,
    viewportX: (x - viewport.left) / (viewport.right - viewport.left), viewportY: (y - viewport.top) / (viewport.bottom - viewport.top),
    scroll: readerScrollOffsets() };
}
function restoreReaderFocusAnchor(anchor) {
  if (!readerAnchorCurrent(anchor, true)) return;
  const viewport = readerVisibleViewport(), rect = sheet.getBoundingClientRect?.();
  if (!viewport || !rect?.width || !rect.height) return;
  let dx = rect.left + anchor.x * rect.width - viewport.left - anchor.viewportX * (viewport.right - viewport.left);
  let dy = rect.top + anchor.y * rect.height - viewport.top - anchor.viewportY * (viewport.bottom - viewport.top);
  // The normal layout scrolls the document; focus can scroll the PDF viewport.
  // Consume each delta from the inside out without assuming either container.
  for (const element of [$('page-area'), $('reader-main')]) {
    if (!element) continue;
    const x = element.scrollLeft || 0, y = element.scrollTop || 0;
    element.scrollLeft = Math.max(0, Math.min(Math.max(0, element.scrollWidth - element.clientWidth) || 0, x + dx));
    element.scrollTop = Math.max(0, Math.min(Math.max(0, element.scrollHeight - element.clientHeight) || 0, y + dy));
    dx -= element.scrollLeft - x; dy -= element.scrollTop - y;
  }
  if (Math.abs(dx) > .5 || Math.abs(dy) > .5) window.scrollTo({ left: (window.scrollX || 0) + dx, top: (window.scrollY || 0) + dy, behavior: 'instant' });
  if (readerFocusAnchor === anchor) readerFocusAnchor = null;
}
function cancelReaderFocusPosition(event) {
  const button = $('toggle-fullscreen');
  if (event.key === 'Escape' || (button && (event.target === button || button.contains?.(event.target)))) return;
  readerFocusInputEpoch++; readerFocusAnchor = null;
}
function scheduleReaderResize(event = null) {
  if (event?.type === 'resize') readerResizeAnchorPending = true;
  readerResizePending = true; clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    if (!readerResizePending || !pdf || !current || active || busy) return;
    readerResizePending = false;
    if (readerResizeAnchorPending && !readerAnchorCurrent(readerFocusAnchor)) readerFocusAnchor = captureReaderFocusAnchor();
    readerResizeAnchorPending = false;
    renderPage(false).catch(() => showError(t('loadError')));
  }, 180);
}
function setReaderFocus(enabled) {
  if (!readerAnchorCurrent(readerFocusAnchor, false, true)) readerFocusAnchor = captureReaderFocusAnchor();
  document.documentElement.dataset.readerFocus = String(enabled);
  // Force layout before taking the baseline, so CSS scroll clamping is not
  // mistaken for a later reader-selected scroll while rendering is pending.
  sheet.getBoundingClientRect?.();
  if (readerFocusAnchor) { readerFocusAnchor.focusGeneration = readerFocusGeneration; readerFocusAnchor.scroll = readerScrollOffsets(); }
  const button = $('toggle-fullscreen'), label = t(enabled ? 'exitFullscreen' : 'fullscreen');
  if (button) {
    button.setAttribute('aria-pressed', String(enabled)); button.setAttribute('title', label); button.setAttribute('aria-label', label);
    button.querySelector('use')?.setAttribute('href', enabled ? '#i-fullscreen-exit' : '#i-fullscreen');
  }
  scheduleReaderResize();
  if (!enabled && readerFocusReturn?.focus) { readerFocusReturn.focus({ preventScroll: true }); readerFocusReturn = null; }
}
function leaveReaderFullscreen() {
  readerFocusGeneration++; finishStroke(); setReaderFocus(false);
  if (document.fullscreenElement === document.documentElement && typeof document.exitFullscreen === 'function') {
    const generation = readerExpectedNativeExit = readerFocusGeneration;
    const failed = () => { if (readerExpectedNativeExit === generation) readerExpectedNativeExit = 0; };
    try { Promise.resolve(document.exitFullscreen()).catch(failed); } catch { failed(); }
  }
}
function toggleReaderFullscreen() {
  if (readerFocusMode()) { leaveReaderFullscreen(); return; }
  finishStroke(); readerFocusReturn = document.activeElement;
  const generation = ++readerFocusGeneration, root = document.documentElement; setReaderFocus(true);
  if (typeof root.requestFullscreen !== 'function' || document.fullscreenEnabled === false || document.fullscreenElement) return;
  readerExpectedNativeExit = 0;
  // Call synchronously inside the click, while transient activation is present.
  try {
    Promise.resolve(root.requestFullscreen({ navigationUI: 'hide' })).then(() => {
      if (!readerFocusMode()) {
        if (document.fullscreenElement === root) { try { Promise.resolve(document.exitFullscreen?.()).catch(() => {}); } catch {} }
      } else if (generation === readerFocusGeneration && document.fullscreenElement === root) { readerNativeFullscreen = true; scheduleReaderResize(); }
    }, () => { /* Unsupported or denied native fullscreen retains app focus. */ });
  } catch { /* An app viewport fallback is already active. */ }
}
function readerFullscreenChanged() {
  if (document.fullscreenElement === document.documentElement) {
    if (!readerFocusMode()) {
      try { Promise.resolve(document.exitFullscreen?.()).catch(() => {}); } catch {}
    } else { readerNativeFullscreen = true; scheduleReaderResize(); }
  } else if (readerExpectedNativeExit) {
    readerExpectedNativeExit = 0; readerNativeFullscreen = false;
    // A prior explicit exit may complete after a newer entry. That entry
    // retains its app viewport fallback rather than being closed by old work.
    if (readerFocusMode()) scheduleReaderResize();
  } else if (readerNativeFullscreen) {
    readerNativeFullscreen = false; readerFocusGeneration++; finishStroke(); setReaderFocus(false);
  }
}
function initializeReaderFullscreen() {
  $('toggle-fullscreen')?.addEventListener('click', toggleReaderFullscreen);
  document.addEventListener('fullscreenchange', readerFullscreenChanged);
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !readerFocusMode() || document.querySelector('dialog[open]')) return;
    event.preventDefault(); leaveReaderFullscreen();
  });
  window.addEventListener('resize', scheduleReaderResize);
  for (const name of ['wheel', 'touchstart', 'pointerdown', 'keydown']) document.addEventListener(name, cancelReaderFocusPosition, { capture: true, passive: true });
}
async function renderPage(scroll = true) {
  if (!pdf || !current) return;
  if (active) { readerResizePending = true; return; }
  const owner = current, documentPDF = pdf, generation = documentOpenGeneration;
  if (current.pageCount) initializeReaderViews();
  const view = readerViews.get(pageNumber);
  if (view) bindReaderView(view);
  const position = scroll ? null : readerFocusAnchor;
  const positionGeneration = readerFocusGeneration, positionMode = readerFocusMode();
  if (scroll) readerFocusAnchor = null;
  const sequence = ++renderSequence; busy = true; controls();
  try {
  if (renderTask) { try { renderTask.cancel(); } catch {} await Promise.resolve(renderTask.promise).catch(() => {}); }
  if (view) {
    view.renderToken++;
    const oldTask = view.renderTask;
    if (oldTask) { try { oldTask.cancel(); } catch {} await Promise.resolve(oldTask.promise).catch(() => {}); }
    view.renderTask = null;
    if (view.releasePromise) await view.releasePromise;
    const releases = [];
    for (const other of [...readerMountedViews]) if (other !== view && (Math.abs(other.number - pageNumber) > 1 ||
        (other.pdfCanvas && other.pdfCanvas.width * other.pdfCanvas.height > READER_NEIGHBOUR_PIXELS))) releases.push(releaseReaderView(other));
    await Promise.all(releases);
  }
  if (view && !(await ensurePage(pageNumber))) return;
  if (sequence !== renderSequence || owner !== current || documentPDF !== pdf || generation !== documentOpenGeneration) return;
  const page = await documentPDF.getPage(pageNumber);
  if (sequence !== renderSequence || owner !== current || documentPDF !== pdf || generation !== documentOpenGeneration) { try { page.cleanup(); } catch {} return; }
  const natural = page.getViewport({ scale: 1 }); baseWidth = natural.width; pageAspect = natural.height / natural.width;
  $('page-area').hidden = false;
  const area = $('page-area'), padding = getComputedStyle(area);
  const available = Math.max(240, Math.min(readerFocusMode() ? Infinity : 1100,
    area.clientWidth - (parseFloat(padding.paddingLeft) || 0) - (parseFloat(padding.paddingRight) || 0)));
  const scale = available / natural.width * Number($('zoom').value);
  const preservingPosition = positionGeneration === readerFocusGeneration && positionMode === readerFocusMode() && readerAnchorCurrent(position, true);
  const viewport = page.getViewport({ scale }); cssWidth = viewport.width; cssHeight = viewport.height;
  if (view) {
    const layoutKey = `${cssWidth}/${readerDesiredPixelRatio()}`;
    if (readerLayoutKey !== layoutKey) {
      readerLayoutKey = layoutKey; readerViewEpoch++;
      await Promise.all([...readerMountedViews].filter(other => other !== view).map(releaseReaderView));
    }
  }
  const raster = readerRasterPlan(cssWidth, cssHeight, readerDesiredPixelRatio(), view ? READER_ACTIVE_PIXELS : 10_000_000);
  pixelRatio = raster.ratio;
  if (view) {
    view.aspect = pageAspect; view.naturalWidth = baseWidth; view.pdfPage = page; view.pixelRatio = pixelRatio;
    layoutReaderViews(cssWidth); bindReaderView(view); view.ready = false; view.sheet.dataset.ready = 'false'; view.sheet.setAttribute('aria-busy', 'true');
  } else { sheet.style.width = cssWidth + 'px'; sheet.style.height = cssHeight + 'px'; }
  for (const canvas of [pdfCanvas, inkCanvas]) { canvas.width = raster.width; canvas.height = raster.height; canvas.style.width = cssWidth + 'px'; canvas.style.height = cssHeight + 'px'; }
  if (view && readerBitmapPixels() > READER_BITMAP_BUDGET) throw new Error('READER_BITMAP_BUDGET');
  if (preservingPosition && readerAnchorCurrent(position)) { sheet.getBoundingClientRect?.(); position.scroll = readerScrollOffsets(); }
  $('page-area').hidden = false; $('loading-state').hidden = true;
  const ctx = pdfCanvas.getContext('2d', { alpha: false });
  renderTask = page.render({ canvasContext: ctx, viewport, transform: [pixelRatio, 0, 0, pixelRatio, 0, 0] });
  if (view) view.renderTask = renderTask;
  try { await renderTask.promise; } catch (error) { if (error.name !== 'RenderingCancelledException') throw error; }
  if (sequence !== renderSequence || owner !== current || documentPDF !== pdf || generation !== documentOpenGeneration) return;
  if (view) { view.renderTask = null; view.ready = true; view.renderedKey = `${cssWidth}/${cssHeight}/${raster.width}/${raster.height}`; view.sheet.dataset.ready = 'true'; view.sheet.setAttribute('aria-busy', 'false'); }
  drawInk(); busy = false; controls();
  if (preservingPosition && positionGeneration === readerFocusGeneration && positionMode === readerFocusMode()) restoreReaderFocusAnchor(position);
  if (scroll) {
    if (view) readerScrollToView(view);
    else { window.scrollTo({ top: 0, behavior: 'instant' }); area.scrollLeft = 0; if (readerFocusMode()) area.scrollTop = 0; }
  }
  if (readerResizePending) scheduleReaderResize();
  if (view) { queueReaderNeighbours(); if (readerScrollPending) scheduleReaderVisible(); }
  } finally {
    if (owner === current && sequence === renderSequence) { busy = false; controls(); }
  }
}
async function ensurePage(number) {
  const owner = current, generation = documentOpenGeneration, inkEpoch = readerInkEpoch;
  if (!pages.has(number)) {
    let strokes = [];
    try { strokes = await storage.loadPage(owner.fingerprint, number); } catch (error) { if (inkEpoch === readerInkEpoch) storageFailure(owner, generation); throw error; }
    if (owner !== current || generation !== documentOpenGeneration || inkEpoch !== readerInkEpoch) return false;
    if (pages.has(number)) return true;
    let changed = false;
    strokes.forEach(s => { if (!s.id) { s.id = uid(); changed = true; } });
    strokes = strokes.flatMap(s => { if (s.points.length > 5000) { changed = true; return splitStroke(s, uid); } return [s]; });
    pages.set(number, strokes); if (changed) markDirty(number);
  }
  return true;
}
async function goPage(value) {
  if (!current || busy) return;
  finishStroke(); const target = clamp(Math.trunc(Number(value)) || 1, 1, current.pageCount);
  if (target === pageNumber) { controls(); return; }
  busy = true; controls();
  try { if (await ensurePage(target) === false) { busy = false; controls(); return; } pageNumber = target; markMeta(); await renderPage(); }
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
    for (const view of [...readerMountedViews]) releaseReaderView(view);
    if (pdfLoadingTask) await pdfLoadingTask.destroy();
    pdf = nextPDF; pdfLoadingTask = task; pdfBytes = new Uint8Array(bytes).slice();
    let previous;
    try { previous = await storage.getDocument(fingerprint); } catch { /* loading remains available without persistence */ }
    current = { ...previous, fingerprint, title: metadata.title, publicId: metadata.publicId || null,
      pageCount: pdf.numPages, pdf: new Blob([pdfBytes], { type: 'application/pdf' }), position: previous?.position || 1,
      bookmarks: previous?.bookmarks || [], annotatedPages: previous?.annotatedPages || [], updatedAt: Date.now() };
    status('ready');
    permissions = { role: 'local', accountId: null }; strokeAuthors.clear(); sheet.dataset.permission = 'local';
    pages.clear(); histories.clear(); dirty.clear(); versions.clear(); retiredIds.clear(); metaVersion = 0; metaSaved = 0;
    pageNumber = clamp(current.position, 1, current.pageCount); await ensurePage(pageNumber);
    let saved = true; try { await storage.putDocument(current); } catch { saved = false; storageFailure(); }
    $('document-title').textContent = current.title;
    // Local filenames stay out of the browser title and network-visible query.
    document.title = `${t('studyNotebook')} | Agentic Tech Review Letters`;
    const url = new URL(location.href), fragment = new URLSearchParams();
    const invitation = new URLSearchParams(url.hash.slice(1)).get('invite');
    // The cloud module consumes a private invitation after the PDF module loads.
    // Keep it until explicit acceptance, even when a cached PDF opens first.
    if (invitation && /^[A-Za-z0-9_-]{20,512}$/.test(invitation)) fragment.set('invite', invitation);
    if (metadata.publicId) {
      url.searchParams.set('id', metadata.publicId);
      const entry = catalog.find(doc => doc.id === metadata.publicId);
      if (entry && entry.sha256 !== fingerprint) fragment.set('edition', fingerprint);
    }
    else { url.searchParams.delete('id'); fragment.set('local', fingerprint); }
    url.hash = fragment.toString(); historyReplace(url);
    renderBookmarks(); renderEditions(); $('page-controls').hidden = false; busy = false; await renderPage();
    if (saved) status(dirty.size ? 'pending' : 'saved');
    signal('atr:document-open', currentInfo()); return true;
  } catch (error) {
    if (nextLoadingTask && nextLoadingTask !== pdfLoadingTask) { try { await nextLoadingTask.destroy(); } catch {} }
    busy = false; showError(t(error.message === 'PDF_TOO_LARGE' ? 'pdfLimit' : error.message === 'PAGE_LIMIT' ? 'pageLimit' : error.message === 'HASH_MISMATCH' ? 'hashMismatch' : 'loadError')); return false;
  }
}
function historyReplace(url) { try { window.history.replaceState(null, '', url); } catch {} }
function showError(message) { $('loading-state').hidden = true; $('error-state').hidden = false; $('error-message').textContent = message; busy = false; controls(); }
function renderEditions() {
  const selector = $('pdf-edition'), wrapper = $('pdf-edition-control');
  if (!selector || !wrapper) return;
  const rows = editionsFor(catalog.find(doc => doc.id === current?.publicId));
  selector.replaceChildren(); wrapper.hidden = rows.length < 2;
  for (const row of rows) {
    const option = document.createElement('option'); option.value = row.sha256;
    option.textContent = row.current ? (en ? 'Current edition' : '현재 판본') : `${en ? 'Previous edition' : '이전 판본'} · ${row.sha256.slice(0, 8)}`;
    option.selected = row.sha256 === current?.fingerprint; selector.append(option);
  }
}
$('pdf-edition')?.addEventListener('change', async event => {
  if (!current?.publicId || busy) { renderEditions(); return; }
  const id = current.publicId, fingerprint = event.target.value;
  const intent = beginDocumentOpen({ explicit: true, fingerprint });
  if (!(await openPublished(id, { intent, edition: fingerprint }))) renderEditions();
});
async function openPublished(id, { intent = null, edition = null } = {}) {
  if (busy) return false;
  intent ??= beginDocumentOpen();
  const doc = catalog.find(d => d.id === id);
  if (!doc) { showError(t('unknownPDF')); return false; }
  const selected = selectEdition(doc, edition);
  if (!selected) { showError(t('hashMismatch')); return false; }
  retry = () => openPublished(id, { edition }); $('original-link').href = new URL(selected.href, rootURL).href;
  try {
    const response = await fetch(new URL(selected.href, rootURL), { credentials: 'omit' });
    if (!isCurrentDocumentOpen(intent)) return false;
    if (!response.ok) throw new Error('NETWORK');
    const bytes = await response.arrayBuffer();
    if (!isCurrentDocumentOpen(intent)) return false;
    return await openBytes(bytes, { title: en && doc.title_en ? doc.title_en : doc.title, publicId: doc.id, sha256: selected.sha256 });
  } catch {
    if (!isCurrentDocumentOpen(intent)) return false;
    try {
      const cached = (await storage.listDocuments()).find(d => d.publicId === id && d.fingerprint === selected.sha256 && (d.hasPDF || d.pdf));
      if (!isCurrentDocumentOpen(intent)) return false;
      if (cached) return openStored(cached.fingerprint, { intent });
    } catch {}
    if (!isCurrentDocumentOpen(intent)) return false;
    showError(t('loadError')); return false;
  }
}
async function openStored(fingerprint, { quietMissing = false, intent = null } = {}) {
  if (busy) return false;
  intent ??= beginDocumentOpen();
  try {
    const doc = await storage.getDocument(fingerprint);
    if (!isCurrentDocumentOpen(intent)) return false;
    if (!doc?.pdf) throw new Error('MISSING');
    const bytes = await doc.pdf.arrayBuffer();
    if (!isCurrentDocumentOpen(intent)) return false;
    return openBytes(bytes, { title: doc.title, publicId: doc.publicId, sha256: doc.fingerprint });
  } catch { if (!isCurrentDocumentOpen(intent)) return false; if (!quietMissing) showError(t('loadError')); return false; }
}
function closeDialogs() { document.querySelectorAll('dialog[open]').forEach(d => d.close()); }
function openWorkspace() {
  finishStroke();const event=new CustomEvent('atr:workspace-request',{cancelable:true});
  if(window.dispatchEvent(event))return showLibrary();
}
async function libraryData() {
  const saved=await storage.listDocuments({includeTrash:true});
  return {local:saved.map(({pdf,...metadata})=>metadata),published:catalog.map(doc=>({...doc}))};
}
async function trashLocal(fingerprint) { if(!(await flush()))throw new Error('SAVE_FAILED');await storage.trashDocument(fingerprint); }
async function restoreLocal(fingerprint) { await storage.restoreDocument(fingerprint); }
function chooseLocalPDF() { finishStroke();$('pdf-input').click(); }
async function chooseStored(fingerprint) {
  if(busy)return false;const intent=beginDocumentOpen({explicit:true,fingerprint});
  clearLocalPDFRequest(requestedLocalPDF!==fingerprint);closeDialogs();return openStored(fingerprint,{intent});
}
async function choosePublished(id) {
  if(busy)return false;const doc=catalog.find(item=>item.id===id);if(!doc)return false;
  const intent=beginDocumentOpen({explicit:true,fingerprint:doc.sha256});
  clearLocalPDFRequest(requestedLocalPDF!==doc.sha256);closeDialogs();return openPublished(id,{intent});
}
async function openCloudPDF(blob,metadata) {
  if(busy)return false;
  const intent=beginDocumentOpen();const bytes=await blob.arrayBuffer();
  if(!isCurrentDocumentOpen(intent))return false;
  return openBytes(bytes,metadata);
}
function clearLocalPDFRequest(cancel = false) {
  const fingerprint = requestedLocalPDF; requestedLocalPDF = null;
  $('local-pdf-request')?.remove(); $('import-pdf').removeAttribute('aria-describedby');
  if (cancel && fingerprint) signal('atr:cloud-local-cancel', { fingerprint });
}
async function requestLocalPDF(detail) {
  if (!/^[a-f0-9]{64}$/.test(detail?.fingerprint || '')) return;
  requestedLocalPDF = detail.fingerprint; await showLibrary();
  if (requestedLocalPDF !== detail.fingerprint) return;
  let note = $('local-pdf-request');
  if (!note) { note = document.createElement('p'); note.id = 'local-pdf-request'; note.className = 'library-intro'; note.setAttribute('role', 'status'); $('import-pdf').before(note); }
  const title = typeof detail.title === 'string' ? detail.title.slice(0, 240) : '';
  note.textContent = en ? `Choose the original PDF for “${title}” with “Bring your own PDF” below. This opens the identical file on this device; cloud file storage is a separate choice.` : `“${title}”의 원본 PDF가 이 기기에 필요합니다. 아래 ‘내 PDF 가져오기’에서 같은 파일을 선택해 주세요. 이 선택은 기기에서 열기이며 클라우드 보관은 별도로 선택합니다.`;
  $('import-pdf').setAttribute('aria-describedby', note.id); $('import-pdf').focus();
}
async function importPDFFile(file) {
  if (!file) return;
  if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') return toast(t('notPDF'));
  if (file.size > 50 * 1024 * 1024) return toast(t('pdfLimit'));
  if (busy) return toast(t('busy'));
  const expected = requestedLocalPDF;
  const intent = beginDocumentOpen({ explicit: true, fingerprint: expected });
  let bytes;
  try {
    bytes = await file.arrayBuffer();
    if (!isCurrentDocumentOpen(intent)) return;
    if (expected) {
      const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(value => value.toString(16).padStart(2, '0')).join('');
      if (!isCurrentDocumentOpen(intent) || requestedLocalPDF !== expected) return;
      if (digest !== expected) {
        const note = $('local-pdf-request');
        if (note) { note.textContent = t('requestedPDFMismatch'); note.setAttribute('role', 'alert'); }
        toast(t('requestedPDFMismatch'), 9000); return;
      }
    }
  } catch { if (isCurrentDocumentOpen(intent)) toast(t('loadError'), 9000); return; }
  clearLocalPDFRequest(); closeDialogs();
  const open = () => openBytes(bytes.slice(0), { title: file.name.replace(/\.pdf$/i, ''), ...(expected ? { sha256: expected } : {}) });
  retry = () => {
    if (busy) return false;
    beginDocumentOpen({ explicit: true, fingerprint: expected }); return open();
  };
  $('original-link').hidden = true; await open();
}
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
      button.append(title, detail); button.addEventListener('click', () => {
        if (busy) return toast(t('busy'));
        const intent = beginDocumentOpen({ explicit: true, fingerprint: doc.fingerprint });
        clearLocalPDFRequest(requestedLocalPDF !== doc.fingerprint); closeDialogs(); openStored(doc.fingerprint, { intent });
      }); saved.append(button);
    });
  } catch { const p = document.createElement('p'); p.className = 'empty-list'; p.textContent = t('storageError'); saved.append(p); }
  const published = $('published-documents'); published.replaceChildren();
  if (!catalog.length) { const p = document.createElement('p'); p.className = 'empty-list'; p.textContent = t('noCatalog'); published.append(p); }
  for (const doc of catalog) {
    const button = document.createElement('button'); button.className = 'library-document'; button.type = 'button';
    const title = document.createElement('strong'); title.textContent = en && doc.title_en ? doc.title_en : doc.title;
    const detail = document.createElement('span'); detail.textContent = doc.date + ' · PDF'; button.append(title, detail);
    button.addEventListener('click', () => {
      if (busy) return toast(t('busy'));
      const intent = beginDocumentOpen({ explicit: true, fingerprint: doc.sha256 });
      clearLocalPDFRequest(requestedLocalPDF !== doc.sha256); closeDialogs(); openPublished(doc.id, { intent });
    }); published.append(button);
  }
}
function download(data, filename, type) {
  const blob = data instanceof Blob ? data : new Blob([data], { type });
  const url = URL.createObjectURL(blob), link = document.createElement('a'); link.href = url; link.download = filename; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 60000);
}
function exportOriginalPDF() {
  if (!current || busy || !pdfBytes) return;
  download(pdfBytes.slice(), safeName(current.title) + '.pdf', 'application/pdf'); toast(t('originalReady'));
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
  if (options.confirmReplace && !canEditAllInk()) throw new Error('NOTEBOOK_READ_ONLY');
  const backup = validateNotebook(value, current.fingerprint);
  if (backup.document.pageCount !== current.pageCount) throw new Error('FINGERPRINT_MISMATCH');
  if (options.confirmReplace && !confirm(t('replaceConfirm'))) return false;
  // Hold the edit lock across storage awaits so incoming Pencil events cannot
  // be overwritten by a remote snapshot after the initial drawing check.
  busy = true; readerInkEpoch++; controls();
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
    // The imported notebook is a complete snapshot; absent mounted pages are
    // known-empty now, so their ready overlays never await an obsolete read.
    for (const view of readerMountedViews) if (!pages.has(view.number)) pages.set(view.number, []);
    if (!options.preserveHistory || options.confirmReplace) histories.clear();
    dirty.clear(); current.bookmarks = backup.bookmarks; pageNumber = position; await ensurePage(pageNumber);
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
  if (!current || busy || !canAddInk()) return; finishStroke(); const h = history(); const source = redo ? h.redo : h.undo, destination = redo ? h.undo : h.redo;
  const item = source.pop(); if (!item) return;
  // Invert only this local action. A complete historical page snapshot would
  // erase unseen remote additions or resurrect somebody else's later erasure.
  const next = new Map(state().map(stroke => [stroke.id, stroke])), inverse = { added: [], removed: [] };
  for (const original of item.added) {
    const present = next.get(original.id);
    if (present && canEraseStroke(present)) { next.delete(original.id); retiredIds.add(original.id); inverse.removed.push(clone(present)); }
  }
  for (const original of item.removed) {
    if (next.has(original.id) || !canEraseStroke(original)) continue;
    const restored = { ...clone(original), id: uid() }; ownStroke(restored); next.set(restored.id, restored); inverse.added.push(clone(restored));
  }
  if (inverse.added.length || inverse.removed.length) {
    // Redo inverts what this undo actually changed, including its fresh IDs.
    destination.push(inverse); pages.set(pageNumber, [...next.values()]); markDirty(); drawInk();
  }
  controls();
}

document.querySelectorAll('button[data-tool]').forEach(button => button.addEventListener('click', () => chooseTool(button.dataset.tool)));
document.querySelectorAll('[data-color]').forEach(button => button.addEventListener('click', () => {
  color = button.dataset.color; document.querySelectorAll('[data-color]').forEach(b => { b.classList.toggle('active', b === button); b.setAttribute('aria-pressed', String(b === button)); }); chooseTool('pen');
}));
$('finger-draw').addEventListener('change', () => chooseTool(tool)); $('pen-width').addEventListener('input', () => { $('width-value').value = $('pen-width').value; });
$('undo').addEventListener('click', () => undo()); $('redo').addEventListener('click', () => undo(true));
$('previous-page').addEventListener('click', () => goPage(pageNumber - 1)); $('next-page').addEventListener('click', () => goPage(pageNumber + 1));
$('page-number').addEventListener('change', event => goPage(event.target.value)); $('page-number').addEventListener('keydown', event => { if (event.key === 'Enter') { event.target.blur(); goPage(event.target.value); } });
$('zoom').addEventListener('change', () => { finishStroke(); if (pdf && !busy) { readerFocusAnchor = captureReaderFocusAnchor(); renderPage(false).catch(() => showError(t('loadError'))); } });
$('bookmark').addEventListener('click', () => {
  if (!current) return; const marks = new Set(current.bookmarks || []); if (marks.has(pageNumber)) marks.delete(pageNumber); else marks.add(pageNumber);
  current.bookmarks = [...marks].sort((a, b) => a - b); renderBookmarks(); markMeta();
});
$('bookmarks').addEventListener('change', event => { if (event.target.value) goPage(Number(event.target.value)); event.target.value = ''; });
$('open-library').addEventListener('click', openWorkspace); $('choose-document').addEventListener('click', openWorkspace);
$('presentation-action').addEventListener('click',()=>window.dispatchEvent(new CustomEvent('atr:presentation-action')));
window.addEventListener('atr:cloud-open-local', event => { void requestLocalPDF(event.detail).catch(() => toast(t('storageError'))); });
window.addEventListener('atr:cloud-document-request', () => beginDocumentOpen());
$('library-dialog').addEventListener('close', () => clearLocalPDFRequest(true));
$('open-options').addEventListener('click', () => { finishStroke(); controls(); $('options-dialog').showModal(); });
document.querySelectorAll('.close-dialog').forEach(b => b.addEventListener('click', () => b.closest('dialog').close()));
document.querySelectorAll('dialog').forEach(dialog => dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } }));
$('import-pdf').addEventListener('click', () => $('pdf-input').click());
$('pdf-input').addEventListener('change', async event => {
  const file = event.target.files[0]; event.target.value = ''; await importPDFFile(file);
});
$('retry-open').addEventListener('click', () => retry ? retry() : showLibrary());
$('export-backup').addEventListener('click', async () => {
  if (!current) return toast(t('openFirst'));
  try { download(JSON.stringify(await notebook()), safeName(current.title) + '-notes.json', 'application/json'); toast(t('backupReady')); }
  catch { toast(t('exportFailed'), 10000); }
});
$('import-backup').addEventListener('click', () => { if (current && canEditAllInk()) $('backup-input').click(); else toast(t(current ? 'busy' : 'openFirst')); });
$('backup-input').addEventListener('change', async event => {
  const file = event.target.files[0]; event.target.value = ''; if (!file || !current || !canEditAllInk()) return;
  try { if (file.size > 30 * 1024 * 1024) throw new Error('INVALID'); const value = JSON.parse(await file.text()); if (await applyNotebook(value, { confirmReplace: true })) { closeDialogs(); toast(t('imported')); } }
  catch (error) { toast(t(error.message === 'FINGERPRINT_MISMATCH' ? 'fingerprintMismatch' : 'backupInvalid'), 9000); }
});
$('export-pdf').addEventListener('click', exportPDF);
$('export-original').addEventListener('click', exportOriginalPDF);
$('clear-page').addEventListener('click', () => {
  if (!current || !canEditAllInk() || !state().length || !confirm(t(permissions.notebookId ? 'clearSharedConfirm' : 'clearConfirm'))) return;
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
// Only a public PDF that finished rendering can acknowledge its local alert.
// Personal PDF metadata and notebook/account state never enter this message.
let renderedPublicRead = null;
function visiblePublicRead(snapshot) {
  if (!snapshot || snapshot !== renderedPublicRead || snapshot.document !== current ||
      snapshot.generation !== documentOpenGeneration || busy || !current?.publicId ||
      window.top !== window.self || document.visibilityState !== 'visible' ||
      typeof document.hasFocus !== 'function' || !document.hasFocus()) return false;
  const id = current.publicId, query = new URL(location.href).searchParams;
  return query.getAll('id').length === 1 && query.get('id') === id &&
    catalog.some(entry => entry.id === id && entry.href === 'archive/files/' + id + '.pdf');
}
async function acknowledgePublicRead() {
  try {
    const snapshot = renderedPublicRead;
    if (!visiblePublicRead(snapshot) || !navigator.serviceWorker) return;
    const workers = navigator.serviceWorker;
    const worker = workers.controller || (await workers.getRegistration(rootURL.href))?.active;
    // An awaited registration lookup must not acknowledge a superseded PDF.
    if (!visiblePublicRead(snapshot) || typeof worker?.postMessage !== 'function') return;
    const id = current.publicId;
    worker.postMessage({ type: 'atr-reader-article-read', articleId: 'lecture:' + id,
      url: new URL('archive/files/' + id + '.pdf', rootURL).href });
  } catch { /* Alert bookkeeping must never block reading or handwriting. */ }
}
window.addEventListener('atr:document-open', () => {
  renderedPublicRead = current ? { document: current, generation: documentOpenGeneration } : null;
  void acknowledgePublicRead();
});
window.addEventListener('focus', () => { void acknowledgePublicRead(); });
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') void acknowledgePublicRead(); });
initializeReaderFullscreen();
initializeReaderScrolling();
window.ATRNotebook = Object.freeze({ current: currentInfo, exportNotebook: notebook, applyNotebook, setPermissions, openPublic: openPublished, openStored,
  libraryData,chooseLocalPDF,chooseStored,choosePublished,openCloudPDF,goPage,trashLocal,restoreLocal,
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
    if (id) await openPublished(id, { edition: new URLSearchParams(location.hash.slice(1)).get('edition') });
    else if (/^[a-f0-9]{64}$/.test(initialLocal || '')) await openStored(initialLocal);
    else if (params.get('library') === '1') await openWorkspace();
  }
  signal('atr:reader-ready', currentInfo());
}
init().catch(() => showError(t('loadError')));
