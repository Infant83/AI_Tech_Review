(function () {
  "use strict";
  if (!document.body.hasAttribute("data-qml-course-index")) return;
  const source = document.body.dataset.qmlSource;
  const manifestUrl = new URL("chapter-manifest.json", location.href);
  if (source && /^[a-f0-9]{64}$/.test(source)) manifestUrl.searchParams.set("v", source);
  let loading;
  function routeFragment() {
    if (!location.hash) return;
    let anchor;
    try { anchor = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    if (!loading) loading = fetch(manifestUrl, {credentials: "omit"})
      .then(response => { if (!response.ok) throw Error("chapter routes unavailable"); return response.json(); });
    loading.then(manifest => {
      // Ignore a stale response when a reader selected another fragment.
      if (decodeURIComponent(location.hash.slice(1)) !== anchor) return;
      const target = manifest.version === 1 && manifest.source_sha256 === source && manifest.anchors && manifest.anchors[anchor];
      if (!target || target === "index.html" || !/^[a-z0-9]+(?:-[a-z0-9]+)*\.html$/.test(target)) return;
      const url = new URL(target, location.href);
      url.search = location.search;
      url.hash = anchor;
      location.replace(url.href);
    }).catch(() => { loading = null; /* Existing fragment exposes its explicit chapter link. */ });
  }
  window.addEventListener("hashchange", routeFragment);
  routeFragment();
})();
