const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const MiniSearch = require('../scripts/public_assets/minisearch.js');
const core = require('../scripts/public_assets/site-search-core.js');
const wireCodec = require('../scripts/public_assets/site-search-wire.js');

const wireFields = ['id', 'scope', 'title', 'title_en', 'url', 'url_en', 'date', 'titles', 'topics', 'summary', 'summary_en', 'text', 'headings'];
const wireCoverage = 'Public titles, topics, summaries and study HTML headings/glossary terms; not full PDF text.';
const wireFixture = () => ({version: 2, coverage: wireCoverage, fields: [...wireFields], records: [
  ['note', 'reviews', '한글 🧪', 'Ａ English', 'reviews/note/', 'reviews/note/en/', '2026-11-28',
    [2, ' · ', 3], 'QML', '공백  두 개\n', 'Mixed CASE', ['(', 9, ') ', 10, '!'], 'e\u0301\ud800']
]});

test('wire restores exact original fields before the unchanged search core runs', async () => {
  const source = wireFixture(), before = JSON.stringify(source);
  const decoded = await wireCodec.decodeAsync(source);
  assert.deepEqual(Object.keys(decoded.records[0]), wireFields);
  assert.equal(decoded.version, 1);
  assert.equal(decoded.records[0].titles, '한글 🧪 · Ａ English');
  assert.equal(decoded.records[0].text, '(공백  두 개\n) Mixed CASE!');
  assert.equal(decoded.records[0].headings, 'e\u0301\ud800');
  assert.equal(JSON.stringify(source), before);
  const direct = {...decoded.records[0], titles: '한글 🧪 · Ａ English', text: '(공백  두 개\n) Mixed CASE!'};
  const expected = core.create(MiniSearch, [direct]);
  const actual = await core.createAsync(MiniSearch, decoded.records);
  for (const query of ['', '?!', '2026-11', 'QML', '한글', 'English', 'mixed', 'unknown']) {
    for (const scope of ['all', 'reviews', 'lectures']) assert.deepEqual(actual.search(query, scope), expected.search(query, scope));
  }
});

test('wire yields before inspecting records and between bounded row batches', async () => {
  const wire = wireFixture(); let readRows = 0;
  wire.records = Array.from({length: 5}, (_, i) => {
    const cells = [...wire.records[0]];
    Object.defineProperty(cells, 0, {get() { readRows++; return 'note-' + i; }});
    return cells;
  });
  const observed = [];
  const decoded = await wireCodec.decodeAsync(wire, {batchSize: 2, now: () => 0, yieldTask: async () => { observed.push(readRows); }});
  assert.deepEqual(observed, [0, 2, 4]);
  assert.equal(decoded.records.length, 5);
});

test('wire rejects unsupported shapes, field changes and invalid references', async () => {
  const changes = [
    x => { x.version = 1; }, x => { x.extra = true; }, x => { x.coverage = true; },
    x => { [x.fields[0], x.fields[1]] = [x.fields[1], x.fields[0]]; },
    x => { x.records[0].pop(); }, x => { x.records[0][0] = [2, 3]; },
    x => { x.records[0][7] = [true, ' ', 3]; }, x => { x.records[0][7] = [-1, ' ', 3]; },
    x => { x.records[0][7] = [7, ' ', 3]; }, x => { x.records[0][7] = [3, ' ', 2]; },
    x => { x.records[0][7] = [[2], ' ', 3]; }, x => { x.records[0][7] = [2, '', 3]; },
    x => { x.records[0][7] = [2, 'a', 'b', 3]; }, x => { x.records[0][7] = [2]; },
    x => { x.records[0][2] = ''; }, x => { x.records = Array(10001).fill(x.records[0]); }
  ];
  for (const change of changes) { const value = wireFixture(); change(value); await assert.rejects(wireCodec.decodeAsync(value), /Invalid search wire/); }
  const twoRefs = wireFixture(); twoRefs.records[0][7] = [2, 3];
  assert.equal((await wireCodec.decodeAsync(twoRefs)).records[0].titles, '한글 🧪Ａ English');
});

test('wire refuses expansion before joining a large referenced result and caps UTF-8 bytes', async () => {
  const expansion = wireFixture(); expansion.records[0][2] = 'a'.repeat(700000); expansion.records[0][3] = 'b'.repeat(700000);
  await assert.rejects(wireCodec.decodeAsync(expansion), /Invalid search wire/);
  const bytes = wireFixture(); bytes.records[0][2] = '가'.repeat(700000);
  await assert.rejects(wireCodec.decodeAsync(bytes), /Invalid search wire/);
});

test('loader selects one format before fetching, rejects oversized streams and retries without legacy fallback', async () => {
  const source = fs.readFileSync(require.resolve('../scripts/public_assets/site-search.js'), 'utf8');
  async function mounted(format, oversized = false) {
    const urls = [], scripts = [], received = [], handlers = {}; let cancelled = 0, released = 0, resolve;
    let completed = new Promise(done => { resolve = done; });
    const node = () => ({addEventListener() {}}), input = {...node(), value: '', focus() {}};
    const scope = {...node(), value: 'all', options: [{value: 'all'}]};
    const status = {set textContent(value) { if (/^(No results|Search could not load)/.test(value)) resolve(value); }};
    const list = {replaceChildren() {}}, button = node();
    const panel = {querySelector: selector => selector === '[data-search-status]' ? status : selector === '[data-search-list]' ? list : button};
    const form = {dataset: {root: '/', defaultScope: 'all', searchVersion: 'legacy', searchWireVersion: 'active', searchCodecVersion: 'codec'},
      querySelector: selector => selector.startsWith('input') ? input : scope, addEventListener: (name, callback) => { handlers[name] = callback; }};
    if (format !== null) form.dataset.searchFormat = format;
    const location = {href: 'http://localhost/?q=QML'};
    const window = {MiniSearch: {}, SiteSearchCore: {createAsync: async (_mini, rows) => { received.push(rows); return {search: () => []}; }}, addEventListener() {}};
    const document = {documentElement: {lang: 'en'}, body: {classList: {toggle() {}}},
      querySelector: selector => selector === '[data-site-search]' ? form : selector === '[data-site-search-results]' ? panel : null,
      querySelectorAll: () => [], createElement: () => ({remove() {}}),
      head: {append(script) { scripts.push(script.src); window.SiteSearchWire = wireCodec; script.onload(); }}};
    vm.runInNewContext(source, {window, document, location, URL, TextDecoder, Uint8Array,
      history: {replaceState: (_a, _b, target) => { location.href = new URL(target, location.href).href; }},
      setTimeout: () => 0, clearTimeout() {},
      fetch: async url => {
        urls.push(String(url)); let done = false;
        return {ok: true, json: async () => ({version: 1, records: [{id: 'legacy'}]}),
          arrayBuffer() { assert.fail('Whole oversized response must not be buffered'); },
          body: {getReader: () => ({
            async read() {
              if (done) return {done: true}; done = true;
              return {done: false, value: oversized ? {byteLength: 8 * 1024 * 1024 + 1} : new TextEncoder().encode(JSON.stringify(wireFixture()))};
            }, async cancel() { cancelled++; }, releaseLock() { released++; }
          })}};
      }});
    const first = await completed;
    return {urls, scripts, received, first, counts: () => ({cancelled, released}),
      async retry() { oversized = false; completed = new Promise(done => { resolve = done; }); handlers.submit({preventDefault() {}}); return completed; }};
  }
  const legacy = await mounted(null);
  assert.match(legacy.first, /^No results/); assert.deepEqual(legacy.received, [[{id: 'legacy'}]]);
  assert.equal(legacy.scripts.length, 0); assert.deepEqual(legacy.urls, ['http://localhost/assets/search-records.json?v=legacy']);
  const active = await mounted('2');
  assert.match(active.first, /^No results/); assert.equal(active.received[0][0].id, 'note');
  assert.deepEqual(active.urls, ['http://localhost/assets/search-records-v2.json?v=active']);
  assert.deepEqual(active.scripts, ['http://localhost/assets/site-search-wire.js?v=codec']);
  const tooBig = await mounted('2', true);
  assert.match(tooBig.first, /^Search could not load/); assert.equal(tooBig.received.length, 0);
  assert.deepEqual(tooBig.counts(), {cancelled: 1, released: 1});
  assert.match(await tooBig.retry(), /^No results/);
  assert.equal(tooBig.urls.length, 2); assert.ok(tooBig.urls.every(url => url.includes('search-records-v2.json')));
  const unknown = await mounted('3'); assert.match(unknown.first, /^Search could not load/); assert.equal(unknown.urls.length, 0);
});

const record = (id, scope, titles, text = '', topics = '', headings = '') => ({
  id, scope, titles, title: titles, text, topics, headings, date: '2026-11-01'
});
const records = [
  record('oled', 'reviews', 'TabPFN and OLED manufacturing', 'Tabular learning and materials.'),
  record('qml', 'lectures', 'Quantum machine learning', '양자 머신러닝 학습 노트', '양자컴퓨팅', 'Barren plateau and gradients'),
  record('mention', 'briefings', 'Other research', 'Quantum machine learning and OLED.'),
  record('body-only', 'reviews', 'A short note', 'TabPFN OLED manufacturing'),
  record('other', 'books', 'An unrelated book', 'Ordinary reading.')
];
const engine = core.create(MiniSearch, records);

test('all concepts are required and word order and extra spaces are immaterial', () => {
  const ids = query => engine.search(query).map(row => row.id);
  assert.deepEqual(ids('TabPFN OLED'), ids('OLED    TabPFN'));
  assert.equal(ids('TabPFN OLED')[0], 'oled');
  assert.equal(ids('TabPFN OLED unmatched').length, 0);
});

test('known multilingual aliases are equivalent, without broad unrelated expansion', () => {
  const ids = query => engine.search(query).map(row => row.id);
  for (const query of ['QML', 'quantum machine learning', '양자 머신러닝', '양자머신러닝']) {
    assert.deepEqual(ids(query), ['qml', 'mention']);
  }
  assert.deepEqual(ids('QML TabPFN'), []);
});

test('title matches outrank incidental summary matches and scope is enforced', () => {
  assert.equal(engine.search('TabPFN OLED')[0].id, 'oled');
  assert.deepEqual(engine.search('QML', 'lectures').map(row => row.id), ['qml']);
  assert.deepEqual(engine.search('QML', 'reviews'), []);
});

test('lecture headings are searchable and Korean compound prefixes work at two characters', () => {
  assert.deepEqual(engine.search('barren plateau').map(row => row.id), ['qml']);
  assert.deepEqual(engine.search('양자', 'lectures').map(row => row.id), ['qml']);
});

test('NFKC input and empty scoped browsing are deterministic', () => {
  assert.equal(engine.search('ＴａｂＰＦＮ OLED')[0].id, 'oled');
  assert.deepEqual(engine.search('', 'books').map(row => row.id), ['other']);
  assert.equal(engine.search('reallynotpresent').length, 0);
});

test('duplicate publication identities are rejected', () => {
  assert.throws(() => core.create(MiniSearch, [records[0], records[0]]), /Duplicate/);
});

test('publication month and full date search retain exact date filtering', () => {
  assert.equal(engine.search('2026-11-01').length, records.length);
  assert.equal(engine.search('2026-11', 'lectures').length, 1);
  assert.equal(engine.search('2026-10-01').length, 0);
});

test('record grouping preserves ranked IDs, displayed metadata and date/ID ties', () => {
  const item = (id, scope, date, titles, text, topics = '', headings = '') => ({
    ...record(id, scope, titles, text, topics, headings), date,
    title: `Display ${id}`, title_en: `English ${id}`,
    summary: `Summary ${id}`, summary_en: `English summary ${id}`,
    url: `${id}/`, url_en: `${id}/en/`
  });
  const fixture = [
    item('tie-b', 'briefings', '2026-11-18', 'Fock photon sensing', 'Quantum probe.'),
    item('long', 'lectures', '2026-11-20', 'Quantum machine learning',
      'A longer discussion of quantum sensing, photon statistics and noise. '.repeat(9),
      '양자 머신러닝', 'Fisher information and gradients'),
    item('tie-a', 'reviews', '2026-11-18', 'Fock photon sensing', 'Quantum probe.'),
    item('older', 'books', '2026-10-01', 'Fock states', 'A short photon reference.'),
    item('newer', 'reviews', '2026-11-21', 'Quantum sensing', 'Photon probes and repeated readout.', 'QEC'),
    item('korean', 'lectures', '2026-11-18', '양자 센싱', '광자 분포와 측정.', 'Quantum sensing')
  ];
  const grouped = [...fixture].sort((a, b) =>
    b.scope.localeCompare(a.scope) || b.date.localeCompare(a.date) || b.id.localeCompare(a.id));
  const reference = core.create(MiniSearch, fixture);
  const queries = ['', '   ', '?!', '2026-11', '2026-11-18', '2026-10-01',
    'Fock photon', 'quantum', 'photon', '양자', '양자 센싱', 'QML', 'QEC', 'unmatched'];
  for (const order of [[...fixture].reverse(), grouped]) {
    const candidate = core.create(MiniSearch, order);
    for (const scope of ['all', 'reviews', 'lectures', 'briefings', 'books']) {
      for (const query of queries) {
        const expected = reference.search(query, scope), actual = candidate.search(query, scope);
        const metadata = rows => rows.map(({score, ...row}) => row);
        assert.deepEqual(metadata(actual), metadata(expected), `${scope}: ${query}`);
        for (let i = 0; i < expected.length; i++) {
          if (expected[i].score === undefined) continue;
          assert.ok(Math.abs(actual[i].score - expected[i].score) <=
            1e-12 * Math.max(1, Math.abs(expected[i].score)), `score ${actual[i].id}: ${query}`);
        }
      }
    }
  }
  assert.deepEqual(reference.search('Fock photon').filter(row => row.id.startsWith('tie-'))
    .map(row => row.id), ['tie-a', 'tie-b']);
  assert.deepEqual(reference.search('2026-11-18').map(row => row.id), ['korean', 'tie-a', 'tie-b']);
  assert.deepEqual(reference.search('').map(row => row.id),
    ['newer', 'long', 'korean', 'tie-a', 'tie-b', 'older']);
});

test('async construction yields before preprocessing and between bounded batches', async () => {
  let yields = 0, added = 0;
  class ObservedMiniSearch extends MiniSearch { add(record) { added++; return super.add(record); } }
  const observations = [];
  const asyncEngine = await core.createAsync(ObservedMiniSearch, records, {batchSize: 2, now: () => 0, yieldTask: async () => { yields++; observations.push(added); }});
  assert.deepEqual(observations, [0, 2, 4]);
  assert.equal(yields, 3);
  for (const query of ['QML', 'OLED TabPFN', 'barren plateau', '2026-11', '']) assert.deepEqual(asyncEngine.search(query), engine.search(query));
});

test('async construction rejects duplicate IDs across separate batches', async () => {
  await assert.rejects(core.createAsync(MiniSearch, [...records, records[0]], {batchSize: 2, yieldTask: async () => {}}), /Duplicate/);
});

test('initial and history URLs share the raw 180 UTF-16 unit query boundary', () => {
  const source = fs.readFileSync(require.resolve('../scripts/public_assets/site-search.js'), 'utf8');
  function mounted(query, selectedScope, defaultScope = 'all') {
    const listeners = new Map(), replacements = [], fetches = [];
    const node = () => ({addEventListener() {}});
    const input = {...node(), value: '', focus() {}};
    const scope = {...node(), value: defaultScope,
      options: ['all', 'reviews', 'lectures', 'briefings', 'books'].map(value => ({value}))};
    const status = {}, list = {replaceChildren() {}}, more = node(), clear = node();
    const form = {...node(), dataset: {root: '/AI_Tech_Review/', defaultScope},
      querySelector(selector) {
        assert.ok(['input[name=q]', 'select[name=scope]'].includes(selector));
        return selector === 'input[name=q]' ? input : scope;
      }};
    const panel = {querySelector(selector) {
      const elements = {'[data-search-status]': status, '[data-search-list]': list,
        '[data-search-more]': more, '[data-search-clear]': clear};
      assert.ok(Object.hasOwn(elements, selector));
      return elements[selector];
    }};
    const url = (q, filter) => {
      const value = new URL('https://example.invalid/AI_Tech_Review/?keep=1#reading');
      if (q !== null) value.searchParams.set('q', q);
      if (filter !== null) value.searchParams.set('scope', filter);
      return value.href;
    };
    const location = {href: url(query, selectedScope)};
    const document = {documentElement: {lang: 'ko'}, body: {classList: {toggle() {}}},
      querySelector(selector) {
        if (selector === '[data-site-search]') return form;
        if (selector === '[data-site-search-results]') return panel;
        if (selector === '.site-header') return null;
        assert.fail(`Unexpected document selector: ${selector}`);
      },
      querySelectorAll() { return []; },
      createElement() { assert.fail('Pending fetch must prevent index/render construction'); }};
    const window = {MiniSearch: {}, SiteSearchCore: {
      createAsync() { assert.fail('This URL test must not build an index'); }
    }, addEventListener(name, callback) { listeners.set(name, callback); }};
    const history = {replaceState(state, title, target) {
      location.href = new URL(target, location.href).href;
      replacements.push(location.href);
    }};
    vm.runInNewContext(source, {document, window, location, history, URL,
      fetch(target, options) {
        fetches.push({target: String(target), credentials: options.credentials});
        return new Promise(() => {}); // No network, resolved catalog, or live timer.
      }, setTimeout() { return 1; }, clearTimeout() {}}, {filename: 'site-search.js'});
    return {input, scope, location, replacements, fetches,
      pop(q, filter) {
        location.href = url(q, filter); // The browser has moved before popstate.
        assert.equal(typeof listeners.get('popstate'), 'function');
        listeners.get('popstate')();
      }};
  }
  function shown(app, query, scope, defaultScope = 'all') {
    const expected = query.slice(0, 180), current = new URL(app.location.href);
    assert.equal(app.input.value, expected);
    assert.ok(app.input.value.length <= 180);
    assert.equal(app.scope.value, scope);
    assert.equal(current.searchParams.get('q'), expected || null);
    assert.equal(current.searchParams.get('scope'), scope === defaultScope ? null : scope);
    assert.equal(current.searchParams.get('keep'), '1');
    assert.equal(current.hash, '#reading');
    assert.ok(app.replacements.length > 0);
  }
  const within = '양자 계산과 광자';
  const boundary = '가'.repeat(178) + '🧪';
  const over = '한'.repeat(250);
  const expandedByNFKC = '㍿'.repeat(180);
  for (const [query, filter, expectedScope] of [
    ['', null, 'all'], [within, 'lectures', 'lectures'],
    [boundary, 'reviews', 'reviews'], [over, 'books', 'books'],
    [expandedByNFKC, 'invalid', 'all']
  ]) {
    const initial = mounted(query, filter);
    shown(initial, query, expectedScope);
    assert.ok(initial.fetches.length <= 1);
    for (const [nextQuery, nextFilter, nextScope] of [
      [over, 'lectures', 'lectures'], [within, 'reviews', 'reviews'],
      [boundary, 'all', 'all'], [expandedByNFKC, 'books', 'books'],
      [within, 'invalid', 'all'], ['', null, 'all']
    ]) {
      initial.pop(nextQuery, nextFilter);
      shown(initial, nextQuery, nextScope);
    }
    assert.ok(initial.fetches.length <= 1, 'The pending catalog is reused across history');
    assert.ok(initial.fetches.every(call => call.credentials === 'omit'));
  }
  const scopedDefault = mounted(over, null, 'reviews');
  shown(scopedDefault, over, 'reviews', 'reviews');
  scopedDefault.pop(within, 'invalid');
  shown(scopedDefault, within, 'reviews', 'reviews');
});
