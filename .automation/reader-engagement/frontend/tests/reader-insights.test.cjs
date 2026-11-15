"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const subject = require("../reader-insights.js");
const clone = value => JSON.parse(JSON.stringify(value));
const articles = [
  { id: "review-one", title: "Review", path: "/AI_Tech_Review/reviews/review-one/", topic: "review", publishedAt: "2026-11-01", category: "AI Research", categoryLabel: "AI 연구", contentLanguage: "ko" },
  { id: "lecture:lecture-one", title: "Lecture", path: "/AI_Tech_Review/archive/files/lecture-one.pdf", topic: "lecture", publishedAt: "2026-11-02", category: null, categoryLabel: "미분류", contentLanguage: "ko" }
];
const catalog = { version: 1, language: "ko", scope: "/AI_Tech_Review/", apiBase: "https://api.infant83.io", articles };
const raw = {
  ok: true, since: "2026-11-10T09:00:00.000Z", activitySince: "2026-11-12", generatedAt: "2026-11-15T02:00:00.000Z",
  range: { period: "7d", from: "2026-11-09", to: "2026-11-15" },
  coverage: { timezone: "Asia/Seoul", collectionStartedOn: "2026-11-10", activityRecordedFrom: "2026-11-12", firstDayMayBePartial: true, todayPartial: true, outageHistoryAvailable: false },
  articles: [{ id: "review-one", periodOpens: 3 }, { id: "lecture:lecture-one", periodOpens: 2 }],
  daily: [{ day: "2026-11-11", articleId: "review-one", opens: 1 }, { day: "2026-11-14", articleId: "review-one", opens: 2 }, { day: "2026-11-15", articleId: "lecture:lecture-one", opens: 2 }],
  limits: { maxArticles: 500, maxDays: 90, maxRows: 10000, maxBytes: 750000 }
};
const discoveryRaw = { ok: true, since: raw.since, range: raw.range, articles: articles.map((row, index) => ({ id: row.id, opens: 30, likes: index ? 7 : 2, shares: 0, copies: 0, periodOpens: index ? 2 : 4, periodLikes: 1 })) };
const parsed = () => subject.validateInsights(clone(raw), "7d", catalog);
const joined = () => subject.validateDiscovery(clone(discoveryRaw), parsed(), catalog);
test("only public scoped paths and the fixed origin enter the catalog", () => {
  assert.equal(subject.validateCatalog(clone(catalog)).articles.length, 2);
  for (const path of ["javascript:alert(1)", "https://evil.example/", "/AI_Tech_Review/reviews/../x/", "/AI_Tech_Review//reviews/a", "/AI_Tech_Review/reviews/%2e%2e/x", "/AI_Tech_Review/reviews/a/?x=1"]) {
    const bad = clone(catalog); bad.articles[0].path = path; assert.throws(() => subject.validateCatalog(bad));
  }
  const lecture = clone(catalog); lecture.articles[1].category = "inferred"; assert.throws(() => subject.validateCatalog(lecture));
  const api = clone(catalog); api.apiBase = "https://other.example"; assert.throws(() => subject.validateCatalog(api));
});
test("daily, article and category sums agree for every type filter", () => {
  for (const [kind, expected, groups] of [["all", 5, 2], ["review", 3, 1], ["lecture", 2, 1]]) {
    const result = subject.summarize(catalog, parsed(), joined(), kind);
    assert.equal(result.total, expected); assert.equal(result.categories.length, groups);
    assert.equal(result.categories.reduce((sum, row) => sum + row.opens, 0), expected);
    assert.equal(result.daily.reduce((sum, row) => sum + (row.opens || 0), 0), expected);
    if (kind === "lecture") assert.equal(result.categories[0].key, "unclassified");
  }
});
test("uncollected, pre-retention, retained zero and partial days stay distinct", () => {
  const days = subject.summarize(catalog, parsed(), joined(), "all").daily;
  assert.deepEqual(days.map(day => [day.day, day.opens, day.state]), [
    ["2026-11-09", null, "uncollected"], ["2026-11-10", null, "incomplete"], ["2026-11-11", 1, "incomplete"],
    ["2026-11-12", 0, "first"], ["2026-11-13", 0, "recorded"], ["2026-11-14", 2, "recorded"], ["2026-11-15", 2, "today"]
  ]);
});
test("unknown, duplicate, absent IDs and inconsistent totals are visible failures", () => {
  for (const change of [value => value.articles.pop(), value => value.articles.push(value.articles[0]), value => value.articles[0].id = "unknown", value => value.articles[0].periodOpens++, value => value.daily.push(value.daily[0]), value => value.daily[0].opens = -1, value => value.daily[0].articleId = "unknown", value => value.daily[0].day = "2026-11-08"]) {
    const value = clone(raw); change(value); assert.throws(() => subject.validateInsights(value, "7d", catalog));
  }
});
test("range, KST date, coverage and hard response bounds are checked", () => {
  for (const change of [value => value.range.period = "30d", value => value.range.from = "2026-11-10", value => value.generatedAt = "2026-11-14T14:00:00Z", value => value.coverage.timezone = "UTC", value => value.coverage.activityRecordedFrom = "2026-11-11", value => value.coverage.todayPartial = false, value => value.limits.maxRows = 10001]) {
    const value = clone(raw); change(value); assert.throws(() => subject.validateInsights(value, "7d", catalog));
  }
  assert.equal(subject.kstDay("2026-11-14T16:00:00Z"), "2026-11-15"); assert.equal(subject.validDay("2026-02-30"), false);
});
test("likes rank current retained likes while opens keep the shared snapshot", () => {
  const values = subject.summarize(catalog, parsed(), joined(), "all");
  assert.equal(subject.ranked(values.articles, "likes")[0].id, "lecture:lecture-one");
  assert.equal(subject.ranked(values.articles, "opens")[0].id, "review-one");
  assert.equal(values.articles[0].opens, 3);
  const wrongRange = clone(discoveryRaw); wrongRange.range = { ...wrongRange.range, from: "2026-11-10" };
  assert.throws(() => subject.validateDiscovery(wrongRange, parsed(), catalog));
  const missing = clone(discoveryRaw); missing.articles.pop(); assert.throws(() => subject.validateDiscovery(missing, parsed(), catalog));
});
test("bounded streamed responses reject oversized and failed requests", async () => {
  await assert.rejects(subject.jsonResponse(new Response("{}", { status: 503 }), 100));
  await assert.rejects(subject.jsonResponse(new Response("123456"), 5));
  await assert.rejects(subject.jsonResponse(new Response("{}", { headers: { "content-length": "1000" } }), 100));
  assert.deepEqual(await subject.jsonResponse(new Response('{"ok":true}'), 100), { ok: true });
});
test("zero counts remain in the complete table model without an invented popular ranking", () => {
  const allZero = articles.map(row => ({ ...row, opens: 0, likes: 0 }));
  for (const metric of ["opens", "likes"]) {
    assert.deepEqual(subject.popularArticles(allZero, metric), []);
    assert.equal(subject.ranked(allZero, metric).length, 2);
    const one = allZero.map((row, index) => ({ ...row, [metric]: index }));
    assert.equal(subject.popularArticles(one, metric).length, 1);
    assert.equal(subject.popularArticles(one, metric)[0].id, "lecture:lecture-one");
  }
});
test("a retained daily zero from non-open activity is valid and remains zero in every summary", () => {
  const zero = clone(raw);
  zero.articles = articles.map(row => ({ id: row.id, periodOpens: 0 }));
  zero.daily = [{ day: "2026-11-14", articleId: "review-one", opens: 0 }];
  const insights = subject.validateInsights(zero, "7d", catalog);
  for (const kind of ["all", "review", "lecture"]) {
    const summary = subject.summarize(catalog, insights, joined(), kind);
    assert.equal(summary.total, 0);
    assert.equal(summary.daily.find(row => row.day === "2026-11-14").opens, 0);
    assert.equal(summary.daily.find(row => row.day === "2026-11-14").state, "recorded");
    assert.equal(subject.popularArticles(summary.articles, "opens").length, 0);
    assert.ok(summary.articles.every(row => row.opens === 0));
  }
});
