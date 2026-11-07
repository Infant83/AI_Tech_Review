const test = require('node:test');
const assert = require('node:assert/strict');
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
