const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const MiniSearch = require('../scripts/public_assets/minisearch.js');
const core = require('../scripts/public_assets/site-search-core.js');

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
