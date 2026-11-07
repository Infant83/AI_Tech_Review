const test = require('node:test'), assert = require('node:assert/strict'), fs = require('node:fs'), vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../scripts/public_assets/course-navigation.js'), 'utf8');
const revision = 'a'.repeat(64);
const tick = () => new Promise(resolve => setImmediate(resolve));
function harness(hash = '', get = async () => ({version:1, source_sha256:revision, anchors:{first:'first.html', second:'second.html'}})) {
  const routed = [], events = {}, requests = [];
  const location = {href:'https://example.test/course/' + hash, hash, search:'?lang=en', replace:href=>routed.push(href)};
  const context = {document:{body:{hasAttribute:()=>true,dataset:{qmlSource:revision}}}, location, URL, decodeURIComponent,
    window:{addEventListener:(event, handler)=>events[event]=handler},
    fetch:async url=>{requests.push(url.href);return {ok:true,json:get};}};
  vm.runInNewContext(source, context);
  return {routed,requests,change:hash=>{location.hash=hash;events.hashchange();}};
}
test('old links route on initial visit and later fragment navigation using a pinned manifest', async () => {
  const qa = harness('#first'); await tick();
  assert.match(qa.routed[0], /first\.html\?lang=en#first$/);
  assert.match(qa.requests[0], /chapter-manifest\.json\?v=a{64}$/);
  qa.change('#second'); await tick(); assert.match(qa.routed[1], /second\.html\?lang=en#second$/);
  assert.equal(qa.requests.length,1);
  const empty = harness(); assert.equal(empty.requests.length,0); empty.change('#first'); await tick(); assert.equal(empty.routed.length,1);
});
test('an old delayed route never supersedes the newly selected fragment', async () => {
  let release; const held = new Promise(resolve=>release=resolve);
  const qa = harness('#first',()=>held); qa.change('#second');
  release({version:1,source_sha256:revision,anchors:{first:'first.html',second:'second.html'}}); await tick();
  assert.equal(qa.routed.length,1); assert.match(qa.routed[0], /second\.html/);
});
test('stale manifests and foreign page targets retain the explicit fallback link', async () => {
  for(const value of [{version:1,source_sha256:'b'.repeat(64),anchors:{first:'first.html'}},{version:1,source_sha256:revision,anchors:{first:'https://foreign.test/private'}}]) {
    const qa=harness('#first',async()=>value);await tick();assert.equal(qa.routed.length,0);
  }
});
