export const LIMITS = Object.freeze({ maxRows: 2000, maxBytes: 2_000_000, maxQuery: 200, pageSizes: [50, 100] });
const KINDS = ['review', 'archive', 'external', 'catalog_only'];
const MEMBERSHIP = ['present', 'absent', 'unknown'];
const CONTENT = ['matches', 'differs', 'unknown', 'not_applicable'];
const INPUT = ['matched', 'changed', 'not_recorded', 'unknown'];
const LINK_EVIDENCE = ['sealed_artifact_metadata', 'registered_source_only', 'external_link_only'];
const KIND_LABEL = { review: '리뷰', archive: '자료', external: '외부 자료', catalog_only: '알림 조정' };
const MEMBERSHIP_LABEL = { present: '공개 묶음에 있음', absent: '확인한 묶음에 없음', unknown: '미확인' };
const CONTENT_LABEL = { matches: '확인 범위 일치', differs: '차이 있음', unknown: '미확인', not_applicable: '해당 없음' };
const INPUT_LABEL = { matched: '일치', changed: '변경', not_recorded: '기록 없음', unknown: '미확인' };
const LANG_LABEL = { ko: '한국어', en: '영어' };
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = value => typeof value === 'string';
const strings = value => Array.isArray(value) && value.every(text);
const failure = code => { throw new Error(code); };

export function validateInventory(data) {
  if (!object(data) || data.schemaVersion !== 1 || !object(data.baseline) || !object(data.totals) || !Array.isArray(data.items)) failure('INVALID_INVENTORY');
  if (data.items.length > LIMITS.maxRows) failure('ROW_LIMIT');
  if (!['verified_deployed_artifact', 'not_provided'].includes(data.baseline.status)) failure('INVALID_BASELINE');
  for (const key of ['registered', 'reconciled', 'displayed']) if (!Number.isSafeInteger(data.totals[key]) || data.totals[key] < 0) failure('INVALID_TOTALS');
  if (data.totals.displayed !== data.items.length || data.totals.registered + data.totals.reconciled !== data.items.length) failure('TOTALS_MISMATCH');
  const baselineProvided = data.baseline.status === 'verified_deployed_artifact';
  const ids = new Set();
  for (const item of data.items) {
    if (!object(item) || !text(item.id) || !item.id || !text(item.sourceId) || !item.sourceId || !KINDS.includes(item.kind) || !text(item.title) || !item.title.trim()) failure('INVALID_ITEM');
    if (item.id !== `${item.kind}:${item.sourceId}` || ids.has(item.id)) failure('DUPLICATE_OR_INVALID_ID');
    ids.add(item.id);
    if (!strings(item.languages) || !strings(item.tags) || !strings(item.warnings) || !strings(item.relatedDocumentIds)) failure('INVALID_ITEM_LIST');
    if (!(item.category === null || text(item.category)) || !(item.series === null || (object(item.series) && text(item.series.id) && text(item.series.title)))) failure('INVALID_GROUP');
    if (!MEMBERSHIP.includes(item.releaseMembership) || !object(item.contentComparison) || !CONTENT.includes(item.contentComparison.state) || !object(item.checkedInputState) || !INPUT.includes(item.checkedInputState.article) || !INPUT.includes(item.checkedInputState.registration)) failure('INVALID_EVIDENCE');
    if (!['registered', 'baseline_only_source_missing'].includes(item.registrationState) || (baselineProvided ? typeof item.notificationCatalogMember !== 'boolean' : item.notificationCatalogMember !== null) || item.candidateState !== 'not_provided' || item.previewUrl !== null || !object(item.versionEvidence) || !Array.isArray(item.publicLinks)) failure('INVALID_ITEM_STATE');
    if (!baselineProvided && (item.releaseMembership !== 'unknown' || !['unknown', 'not_applicable'].includes(item.contentComparison.state))) failure('INVALID_BASELINE_EVIDENCE');
    if (!strings(item.contentComparison.coveredPaths)) failure('INVALID_CONTENT_SCOPE');
    for (const link of item.publicLinks) {
      if (!object(link) || !text(link.url) || !text(link.role) || !LINK_EVIDENCE.includes(link.evidenceState) || link.httpsVerifiedAt !== null) failure('INVALID_LINK');
      if (!(link.sha256 === null || (text(link.sha256) && /^[a-f0-9]{64}$/u.test(link.sha256))) || !(link.sizeBytes === null || (Number.isSafeInteger(link.sizeBytes) && link.sizeBytes >= 0))) failure('INVALID_LINK');
    }
  }
  if (data.totals.registered !== data.items.filter(item => item.registrationState === 'registered').length || data.totals.reconciled !== data.items.filter(item => item.registrationState === 'baseline_only_source_missing').length) failure('TOTALS_MISMATCH');
  return data;
}

export function safePublicURL(link, kind) {
  if (!object(link) || !text(link.url) || !LINK_EVIDENCE.includes(link.evidenceState) || /[\u0000-\u0020\u007f\\?]/u.test(link.url)) return null;
  let url;
  try { url = new URL(link.url); } catch { return null; }
  if (url.protocol !== 'https:' || url.username || url.password || url.search || url.port || url.href !== link.url) return null;
  if (/%|(?:^|\/)\.{1,2}(?:\/|$)/u.test(url.pathname) || (url.hash && !/^#[A-Za-z0-9_.:-]+$/u.test(url.hash))) return null;
  if (link.evidenceState === 'external_link_only') {
    if (kind !== 'external' || !url.hostname.includes('.') || /^[\d.]+$/u.test(url.hostname) || url.hostname.startsWith('[') || /(?:^|\.)(?:localhost|local|internal|test|invalid)$/iu.test(url.hostname)) return null;
    return url.href;
  }
  return url.origin === 'https://infant83.io' && url.pathname.startsWith('/AI_Tech_Review/') ? url.href : null;
}

export function linkDisplayPath(link, kind, siblings = []) {
  const url = safePublicURL(link, kind);
  if (!url || (link.role !== 'study_view' && siblings.filter(candidate => candidate.role === link.role).length < 2)) return null;
  const target = new URL(url);
  return target.pathname + target.hash;
}

export function filterItems(items, filters = {}) {
  const query = filters.query ?? '';
  if (!text(query) || Array.from(query).length > LIMITS.maxQuery) failure('SEARCH_TOO_LONG');
  const needle = query.normalize('NFKC').toLowerCase().trim();
  return items.filter(item =>
    (!filters.kind || item.kind === filters.kind) &&
    (filters.category === undefined || item.category === filters.category) &&
    (filters.series === undefined || (item.series?.id ?? null) === filters.series) &&
    (!filters.language || (filters.language === 'unknown' ? item.languages.length === 0 : item.languages.includes(filters.language))) &&
    (!filters.evidence || item.releaseMembership === filters.evidence) &&
    (!needle || [item.title, item.id, item.sourceId, ...item.tags].some(value => value.normalize('NFKC').toLowerCase().includes(needle)))
  );
}

export function pageItems(items, page = 1, pageSize = 50) {
  if (!Number.isSafeInteger(page) || page < 1 || !LIMITS.pageSizes.includes(pageSize)) failure('INVALID_PAGE');
  const pages = Math.max(1, Math.ceil(items.length / pageSize));
  const selected = Math.min(page, pages);
  const start = (selected - 1) * pageSize;
  return { items: items.slice(start, start + pageSize), page: selected, pages, pageSize, total: items.length, from: items.length ? start + 1 : 0, to: Math.min(start + pageSize, items.length) };
}

export async function readInventoryResponse(response) {
  if (!response.ok) failure('INVENTORY_UNAVAILABLE');
  const contentLength = response.headers.get('content-length');
  if (contentLength && (!/^\d+$/u.test(contentLength) || Number(contentLength) > LIMITS.maxBytes)) failure('BYTE_LIMIT');
  if (!/^application\/json(?:\s*;|$)/iu.test(response.headers.get('content-type') || '')) failure('INVALID_CONTENT_TYPE');
  const reader = response.body?.getReader();
  if (!reader) failure('INVENTORY_UNAVAILABLE');
  const chunks = []; let size = 0;
  try {
    while (true) {
      const part = await reader.read();
      if (part.done) break;
      size += part.value.byteLength;
      if (size > LIMITS.maxBytes) { await reader.cancel(); failure('BYTE_LIMIT'); }
      chunks.push(part.value);
    }
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  let data;
  try { data = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)); } catch { failure('INVALID_JSON'); }
  return validateInventory(data);
}

function node(tag, value, className) {
  const result = document.createElement(tag);
  if (value !== undefined) result.textContent = value;
  if (className) result.className = className;
  return result;
}
function fact(list, label, value) { list.append(node('dt', label), node('dd', value)); }
function reason(value) { return text(value) && value ? value : '근거 미확인'; }
function revision(value) { return text(value) && /^[a-f0-9]{40,64}$/u.test(value) ? value : '미확인'; }
function bytesLabel(value) { return Number.isSafeInteger(value) && value >= 0 ? `${value.toLocaleString('ko-KR')} B` : '크기 미확인'; }
function labelLink(link) {
  const role = ({ pdf: 'PDF', html: '본문', page: '본문', translation: '번역', course: '코스', lecture: '렉처', external: '외부 자료', original: '원본', supplement: '보충 자료', article_html: '본문', article_pdf: '글 PDF', registered_pdf: '등록 PDF', pdf_edition: '보존 판본 PDF', editorial_html: '설명 페이지', study_view: '읽기 화면', course_unit_pdf: '회차 PDF', latest_unit_pdf: '최신 회차 PDF', study_pdf: '학습 PDF', supplement_pdf: '보충 PDF', external_landing_page: '외부 자료', deployed_view: '공개 화면', catalog_view: '알림 연결 화면' })[link.role] || link.role;
  return [role, LANG_LABEL[link.language] || link.language].filter(text).filter(Boolean).join(' · ');
}
function renderItem(item, baselineProvided) {
  const li = node('li'); const article = node('article', undefined, 'item');
  const header = node('div', undefined, 'item-header');
  header.append(node('span', KIND_LABEL[item.kind], 'badge'), node('span', MEMBERSHIP_LABEL[item.releaseMembership], 'badge state'));
  article.append(header, node('h3', item.title), node('p', item.id, 'source-id'));
  const facts = node('dl', undefined, 'item-facts');
  fact(facts, '등록', item.registrationState === 'registered' ? '원장 등록' : '공개 묶음만 확인 · 대응 원장 없음');
  fact(facts, '알림 목록', baselineProvided ? (item.notificationCatalogMember ? '연결됨' : '연결 없음') : '미확인 · 공개 묶음 제공 안 됨');
  fact(facts, '분류 · 언어', `${item.category || '미분류'} · ${item.languages.map(value => LANG_LABEL[value] || value).join(' / ') || '미확인'}`);
  if (item.series) fact(facts, '시리즈', item.series.title);
  fact(facts, '원 발행일', item.originalPublishedDate || '미확인');
  fact(facts, '내용 비교', CONTENT_LABEL[item.contentComparison.state]);
  fact(facts, '입력 검토', `글 입력 ${INPUT_LABEL[item.checkedInputState.article]} · 전체 등록 ${INPUT_LABEL[item.checkedInputState.registration]}`);
  fact(facts, '후보 미리보기', '제공하지 않음');
  article.append(facts);
  if (item.tags.length) article.append(node('p', `태그 · ${item.tags.join(' · ')}`, 'tags'));
  const links = node('ul', undefined, 'links');
  for (const link of item.publicLinks) {
    const entry = node('li'); const url = safePublicURL(link, item.kind);
    if (url) {
      const anchor = node('a', labelLink(link));
      const path = linkDisplayPath(link, item.kind, item.publicLinks);
      if (path) anchor.append(document.createTextNode(' '), node('span', path, 'link-path'));
      anchor.href = url; anchor.target = '_blank'; anchor.rel = 'noopener noreferrer'; anchor.referrerPolicy = 'no-referrer';
      entry.append(anchor);
    } else entry.append(node('span', `${labelLink(link)} · 열기 불가`));
    const evidence = ({ external_link_only: '선언된 외부 링크 · 외부 bytes 미확인', sealed_artifact_metadata: '봉인 metadata · 개별 HTTPS 재확인 없음', registered_source_only: '원장 경로만 확인 · 공개 bytes 미확인' })[link.evidenceState];
    entry.append(node('span', `${evidence} · ${bytesLabel(link.sizeBytes)}`, 'link-evidence'));
    links.append(entry);
  }
  if (item.publicLinks.length) article.append(links);
  else article.append(node('p', '열 수 있는 공개 링크가 없습니다.', 'metadata'));
  const details = node('details'); details.append(node('summary', '근거와 확인 범위'));
  const detailList = node('ul', undefined, 'details-list');
  detailList.append(node('li', `내용 비교 근거 · ${reason(item.contentComparison.basis)}`), node('li', `입력 검토 근거 · ${reason(item.checkedInputState.basis)}`));
  for (const path of item.contentComparison.coveredPaths) detailList.append(node('li', `비교 경로 · ${path}`));
  if (text(item.versionEvidence.basis)) detailList.append(node('li', `판본 근거 · ${item.versionEvidence.basis}`));
  if (text(item.versionEvidence.documentVersion)) detailList.append(node('li', `자료 버전 · ${item.versionEvidence.documentVersion}`));
  for (const warning of item.warnings) detailList.append(node('li', `확인 사항 · ${warning}`));
  if (item.relatedDocumentIds.length) detailList.append(node('li', `연결 ID · ${item.relatedDocumentIds.join(' · ')}`));
  details.append(detailList); article.append(details); li.append(article); return li;
}

async function start() {
  const element = id => document.getElementById(id);
  const status = element('status'); let inventory;
  const controller = new AbortController();
  const deadline = setTimeout(() => controller.abort(), 8000);
  try {
    const url = new URL('./inventory.json', window.location.href);
    if (url.origin !== window.location.origin) failure('INVALID_INVENTORY_LOCATION');
    const response = await fetch(url, { method: 'GET', credentials: 'omit', redirect: 'error', mode: 'same-origin', cache: 'no-store', signal: controller.signal });
    inventory = await readInventoryResponse(response);
  } catch (error) {
    const codes = ['ROW_LIMIT', 'BYTE_LIMIT', 'INVALID_JSON', 'INVALID_TOTALS', 'TOTALS_MISMATCH', 'INVALID_BASELINE', 'INVALID_BASELINE_EVIDENCE', 'INVALID_INVENTORY', 'INVALID_ITEM', 'DUPLICATE_OR_INVALID_ID', 'INVALID_ITEM_LIST', 'INVALID_GROUP', 'INVALID_EVIDENCE', 'INVALID_ITEM_STATE', 'INVALID_CONTENT_SCOPE', 'INVALID_LINK', 'INVALID_CONTENT_TYPE'];
    const code = codes.includes(error?.message) ? error.message : 'INVENTORY_UNAVAILABLE';
    status.className = 'error'; status.textContent = `목록을 읽지 못했습니다. (${code}) 기존 산출물과 입력을 확인한 뒤 새로 여세요.`;
    return;
  } finally {
    clearTimeout(deadline);
  }
  const baselineProvided = inventory.baseline.status === 'verified_deployed_artifact';
  const members = baselineProvided ? inventory.items.filter(item => item.notificationCatalogMember).length : '미확인';
  for (const [label, value] of [['등록 원장', inventory.totals.registered], ['조정 행', inventory.totals.reconciled], ['목록 전체', inventory.totals.displayed], ['알림 목록 연결', members]]) {
    const box = node('div', undefined, 'total'); box.append(node('strong', typeof value === 'number' ? value.toLocaleString('ko-KR') : value), node('span', label)); element('totals').append(box);
  }
  const snapshot = element('snapshot');
  fact(snapshot, '공개 근거', inventory.baseline.status === 'verified_deployed_artifact' ? '검증된 공개 아티팩트 묶음' : '공개 묶음 제공 안 됨 · 공개 상태 미확인');
  fact(snapshot, '소스 커밋', revision(inventory.sourceRevision));
  fact(snapshot, '공개 소스', revision(inventory.baseline.releaseRevision));
  fact(snapshot, '목록 확인 시각', reason(inventory.checkedAt));
  const sourceState = typeof inventory.sourceInputState === 'string' ? inventory.sourceInputState : inventory.sourceInputState?.state;
  fact(snapshot, '소스 입력 상태', ({ match: '선택 입력이 소스 커밋과 일치', different: '선택 입력이 소스 커밋과 다름', unknown: '미확인' })[sourceState] || reason(sourceState));
  const choices = {};
  function options(id, values) {
    choices[id] = values;
    element(id).replaceChildren(...values.map((entry, index) => { const option = node('option', entry.label); option.value = String(index); return option; }));
  }
  options('kind', [{ label: '전체', value: null }, ...KINDS.filter(kind => inventory.items.some(item => item.kind === kind)).map(value => ({ label: KIND_LABEL[value], value }))]);
  options('category', [{ label: '전체', value: undefined }, ...[...new Set(inventory.items.map(item => item.category))].map(value => ({ label: value || '미분류', value }))]);
  const series = new Map(inventory.items.filter(item => item.series).map(item => [item.series.id, item.series.title]));
  options('series', [{ label: '전체', value: undefined }, { label: '시리즈 없음', value: null }, ...[...series].map(([value, label]) => ({ label, value }))]);
  const languages = [...new Set(inventory.items.flatMap(item => item.languages))];
  options('language', [{ label: '전체', value: null }, ...languages.map(value => ({ label: LANG_LABEL[value] || value, value })), { label: '미확인', value: 'unknown' }]);
  options('evidence', [{ label: '전체', value: null }, ...MEMBERSHIP.map(value => ({ label: MEMBERSHIP_LABEL[value], value }))]);
  let page = 1;
  function render(moveFocus = false) {
    const filters = { query: element('search').value };
    for (const id of Object.keys(choices)) filters[id] = choices[id][Number(element(id).value)]?.value;
    let filtered;
    try { filtered = filterItems(inventory.items, filters); }
    catch {
      element('search').setAttribute('aria-invalid', 'true'); status.className = 'error'; status.textContent = '검색어는 200자까지 입력하세요.';
      element('items').replaceChildren(); element('pagination').hidden = true; element('result-count').textContent = ''; return;
    }
    element('search').removeAttribute('aria-invalid');
    const selected = pageItems(filtered, page, Number(element('page-size').value)); page = selected.page;
    element('items').replaceChildren(...selected.items.map(item => renderItem(item, baselineProvided)));
    element('result-count').textContent = `${selected.total.toLocaleString('ko-KR')}개 중 ${selected.from}–${selected.to}개`;
    status.className = ''; status.textContent = selected.total ? '원 발행일 내림차순·ID 오름차순의 원본 목록 순서를 유지합니다.' : '조건에 맞는 자료가 없습니다. 필터나 검색어를 바꿔 보세요.';
    element('page-status').textContent = `${selected.page} / ${selected.pages} 페이지`;
    element('previous').disabled = selected.page === 1; element('next').disabled = selected.page === selected.pages;
    element('pagination').hidden = selected.total === 0;
    if (moveFocus) {
      const results = element('results');
      results.focus({ preventScroll: true });
      results.scrollIntoView({ block: 'start', behavior: 'instant' });
    }
  }
  for (const id of [...Object.keys(choices), 'page-size']) element(id).addEventListener('change', () => { page = 1; render(); });
  element('search').addEventListener('input', () => { page = 1; render(); });
  element('reset').addEventListener('click', () => { for (const id of Object.keys(choices)) element(id).value = '0'; element('page-size').value = '50'; element('search').value = ''; page = 1; render(); element('search').focus(); });
  element('previous').addEventListener('click', () => { page -= 1; render(true); });
  element('next').addEventListener('click', () => { page += 1; render(true); });
  element('filters').disabled = false; render();
}

if (typeof document !== 'undefined') start();
