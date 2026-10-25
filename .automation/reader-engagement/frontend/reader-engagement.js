(function () {
  "use strict";
  if (document.querySelector("[data-atr-reader-dialog]")) return;
  var script = document.currentScript;
  var supplied = {};
  try {
    var configNode = document.getElementById("reader-engagement-config");
    if (configNode && configNode.tagName === "SCRIPT" && configNode.type === "application/json") {
      var parsed = JSON.parse(configNode.textContent);
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) supplied = parsed;
    }
  } catch (_) { /* Invalid embedded configuration uses the public defaults. */ }
  var scope = String(supplied.scope || (script && script.dataset.scope) || "/AI_Tech_Review/");
  if (!/^\/[A-Za-z0-9_/-]+\/$/.test(scope) || scope.indexOf("//") !== -1) scope = "/AI_Tech_Review/";
  if (location.protocol !== "https:" && location.protocol !== "http:") return;
  if (location.pathname !== scope.slice(0, -1) && !location.pathname.startsWith(scope)) return;
  var localHost = /^(localhost|127\.0\.0\.1|\[::1\])$/;
  var apiBase = "https://api.infant83.io";
  try {
    var requestedAPI = new URL(String(supplied.apiBase || (script && script.dataset.apiBase) || apiBase));
    if (requestedAPI.origin === apiBase || (supplied.allowLocalApi === true && localHost.test(location.hostname) && localHost.test(requestedAPI.hostname))) {
      apiBase = requestedAPI.origin;
    }
  } catch (_) { /* Never send credentials to arbitrary configured hosts. */ }
  var article = supplied.article && typeof supplied.article === "object" ? supplied.article : null;
  if (!article && script && script.dataset.articleId) article = { id: script.dataset.articleId };
  if (article && (typeof article.id !== "string" || !article.id || article.id.length > 180)) article = null;
  var english = String(document.documentElement.lang || "ko").toLowerCase().startsWith("en");
  var text = english ? {
    open: "New article alerts", settings: "Alert settings", close: "Close", subscribe: "Enable new article alerts",
    subscribed: "Alerts on", title: "New article alerts", intro: "Receive an alert on this device when a new review or lecture note is published.",
    device: "This subscription and your likes belong to this browser. No account is required.",
    installTitle: "Add AI Tech Review to your Home Screen", installIntro: "On iPhone and iPad, open the installed web app to enable alerts.",
    steps: ["Open your browser’s Share menu.", "Choose Add to Home Screen, then Add. Keep Open as Web App enabled if shown.", "Open the added AI Tech Review icon, then tap New article alerts."],
    denied: "Notifications are turned off. In iPhone Settings → Notifications → AI Tech Review, allow notifications, then return here.",
    deniedOther: "Notifications are blocked. Allow notifications for this site in your browser settings, then return here.",
    recheck: "Check again", unsupported: "This browser does not support web alerts. You can keep reading the site normally.",
    preparing: "Preparing the notification connection…", unavailable: "The alert service is unavailable. Please try again shortly.",
    retry: "Try again", choose: "Notify me about", review: "In-depth reviews", lecture: "Lecture notes",
    selectOne: "Choose at least one type of article.", save: "Save preferences", saved: "Alert preferences saved.",
    enabled: "New article alerts are on for this device.", unsubscribe: "Unsubscribe on this device", disabled: "Alerts are off on this device.",
    partialOff: "This browser’s alerts are off, but the server connection could not be removed. Try again to finish removing it.",
    reconnect: "Reconnect alerts", reconnectNote: "The browser and server connection needs to be refreshed.",
    failed: "The connection failed. Please try again.", like: "Like", unlike: "Unlike", liked: "Liked", likedSaved: "Your like was saved.",
    unlikedSaved: "Your like was removed.", likeFailed: "Your like could not be saved.", likeLoadFailed: "Likes are temporarily unavailable.",
    share: "Share", copy: "Copy link", copied: "Article link copied.", shareFailed: "Sharing failed. You can copy the article link instead.",
    copyFailed: "The link could not be copied. Select and copy this address:", install: "Add to Home Screen", installLater: "You can enable alerts whenever you are ready.",
    iosVersion: "Web alerts require iOS or iPadOS 16.4 or later.", busy: "Connecting…", actions: "Reader actions",
    test: "Send a test alert to this device", testQueued: "The test alert was accepted for sending. Check this device’s notifications; acceptance does not confirm delivery.",
    testLimited: "The test limit was reached. Wait at least a minute; up to five tests are available per device each day.",
    cookieFailed: "The browser could not keep this device connected. Allow cookies for this site in your privacy settings, then try again."
  } : {
    open: "새 글 알림", settings: "알림 설정", close: "닫기", subscribe: "새 글 알림 받기",
    subscribed: "알림 받는 중", title: "새 글 알림", intro: "새 리뷰와 렉처 노트가 발행되면 이 기기로 알려드려요.",
    device: "구독 설정과 좋아요는 이 브라우저에 연결됩니다. 회원가입은 필요하지 않습니다.",
    installTitle: "테크리뷰를 홈 화면에 추가해 주세요", installIntro: "아이폰·아이패드에서는 홈 화면에 추가한 웹앱에서 알림을 켤 수 있어요.",
    steps: ["브라우저의 공유 메뉴를 여세요.", "‘홈 화면에 추가’를 선택하고 추가하세요. ‘웹앱으로 열기’가 보이면 켜두세요.", "추가한 AI Tech Review 아이콘을 열고 ‘새 글 알림’을 누르세요."],
    denied: "알림이 꺼져 있어요. iPhone 설정 → 알림 → AI Tech Review에서 알림을 허용한 뒤 돌아와 주세요.",
    deniedOther: "알림이 차단되어 있어요. 브라우저의 사이트 설정에서 알림을 허용한 뒤 돌아와 주세요.",
    recheck: "다시 확인", unsupported: "이 브라우저는 웹 알림을 지원하지 않아요. 글은 계속 읽을 수 있습니다.",
    preparing: "알림 연결을 준비하고 있어요…", unavailable: "알림 서비스에 연결할 수 없어요. 잠시 후 다시 시도해 주세요.",
    retry: "다시 시도", choose: "받고 싶은 글", review: "심층 리뷰", lecture: "렉처 노트",
    selectOne: "받고 싶은 글을 하나 이상 선택해 주세요.", save: "설정 저장", saved: "알림 설정을 저장했어요.",
    enabled: "이 기기에서 새 글 알림을 받습니다.", unsubscribe: "이 기기에서 구독 해제", disabled: "이 기기의 새 글 알림을 해제했어요.",
    partialOff: "이 브라우저의 알림은 해제했지만 서버 연결을 지우지 못했어요. 다시 시도하면 정리를 마칠 수 있어요.",
    reconnect: "알림 다시 연결", reconnectNote: "브라우저와 서버의 알림 연결을 다시 확인해 주세요.",
    failed: "연결하지 못했어요. 다시 시도해 주세요.", like: "좋아요", unlike: "좋아요 취소", liked: "좋아요", likedSaved: "좋아요를 반영했어요.",
    unlikedSaved: "좋아요를 취소했어요.", likeFailed: "좋아요를 반영하지 못했어요.", likeLoadFailed: "지금은 좋아요 정보를 불러올 수 없어요.",
    share: "공유", copy: "주소 복사", copied: "글 주소를 복사했어요.", shareFailed: "공유하지 못했어요. 글 주소를 복사할 수 있어요.",
    copyFailed: "주소를 복사하지 못했어요. 아래 주소를 선택해 복사해 주세요.", install: "홈 화면에 추가", installLater: "원할 때 새 글 알림을 켤 수 있어요.",
    iosVersion: "웹 알림은 iOS·iPadOS 16.4 이상에서 사용할 수 있어요.", busy: "연결 중…", actions: "독자 참여",
    test: "이 기기로 테스트 알림 보내기", testQueued: "테스트 알림 발송을 접수했어요. 이 기기의 알림을 확인해 주세요. 접수는 도착 확인과 다릅니다.",
    testLimited: "테스트 횟수 제한에 도달했어요. 1분 이상 간격을 두고, 기기당 하루 5회까지 보낼 수 있어요.",
    cookieFailed: "브라우저에서 이 기기의 연결을 유지하지 못했어요. 개인정보 설정에서 이 사이트의 쿠키를 허용한 뒤 다시 시도해 주세요."
  };
  var state = { preparing: true, busy: false, configError: false, registrationError: false, key: "", registration: null,
    localSubscription: null, serverSubscription: null, topics: ["review", "lecture"], feedback: "", feedbackError: false,
    liked: false, count: null, likeBusy: false, pendingServerDelete: false };
  var subscriptionButtons = [];
  var dialog = null, dialogBody = null, dialogHeading = null, dialogFeedback = null, opener = null;
  var likeButton = null, articleStatus = null, likeRevision = 0, scrollState = null;

  function node(tag, className, content) {
    var element = document.createElement(tag);
    if (className) element.className = className;
    if (content !== undefined) element.textContent = content;
    return element;
  }
  function button(label, action, primary) {
    var element = node("button", "atr-reader-button" + (primary ? " atr-reader-primary" : ""), label);
    element.type = "button";
    element.dataset.readerAction = action;
    return element;
  }
  function isIOS() {
    return /iPhone|iPad|iPod/.test(navigator.userAgent || "") || (/Macintosh/.test(navigator.userAgent || "") && navigator.maxTouchPoints > 1);
  }
  function standalone() {
    return navigator.standalone === true || (typeof window.matchMedia === "function" && (window.matchMedia("(display-mode: standalone)").matches || window.matchMedia("(display-mode: fullscreen)").matches));
  }
  function supported() {
    return window.isSecureContext !== false && "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
  }
  function permission() { return "Notification" in window ? Notification.permission : "default"; }
  function subscribed() {
    return Boolean(state.localSubscription && state.serverSubscription && state.localSubscription.endpoint === state.serverSubscription.endpoint && permission() === "granted");
  }
  function apiError(code) { var error = new Error(code); error.code = code; return error; }
  async function request(path, method, body) {
    var controller = typeof AbortController === "function" ? new AbortController() : null;
    var timer = controller ? window.setTimeout(function () { controller.abort(); }, 12000) : null;
    try {
      var response = await fetch(apiBase + path, {
        method: method || "GET", mode: "cors", credentials: "include", cache: "no-store",
        headers: body === undefined ? { Accept: "application/json" } : { Accept: "application/json", "Content-Type": "application/json" },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: controller ? controller.signal : undefined
      });
      if (!response.ok) throw apiError("http_" + response.status);
      var result = await response.json();
      if (!result || typeof result !== "object" || Array.isArray(result) || result.ok === false) throw apiError("api_failed");
      return result;
    } finally { if (timer !== null) window.clearTimeout(timer); }
  }
  async function ensureDevice() { await request("/v1/devices", "POST", {}); }
  function selectedTopics() {
    if (!dialogBody) return state.topics.slice();
    return Array.from(dialogBody.querySelectorAll("input[data-reader-topic]:checked")).map(function (input) { return input.value; });
  }
  function validTopics(value) {
    return Array.isArray(value) ? value.filter(function (topic) { return topic === "review" || topic === "lecture"; }) : ["review", "lecture"];
  }
  function validCount(value) {
    var count = Number(value);
    return Number.isSafeInteger(count) && count >= 0 ? count : 0;
  }
  function updateButtons() {
    subscriptionButtons.forEach(function (element) {
      element.textContent = subscribed() ? text.settings : text.open;
      element.dataset.subscribed = subscribed() ? "true" : "false";
    });
    if (likeButton) {
      likeButton.disabled = state.likeBusy;
      likeButton.setAttribute("aria-pressed", state.liked ? "true" : "false");
      likeButton.setAttribute("aria-label", state.liked ? text.unlike : text.like);
      likeButton.textContent = (state.liked ? "♥ " : "♡ ") + text.like + " " + (state.count === null ? "—" : new Intl.NumberFormat(english ? "en-US" : "ko-KR").format(state.count));
    }
  }
  function setFeedback(message, error) {
    state.feedback = message;
    state.feedbackError = Boolean(error);
    if (dialogFeedback) {
      dialogFeedback.textContent = message;
      dialogFeedback.dataset.error = error ? "true" : "false";
    }
  }
  function articleMessage(message, retryAction, url) {
    if (!articleStatus) return;
    articleStatus.dataset.readerStatusAction = retryAction || "";
    articleStatus.replaceChildren(document.createTextNode(message));
    if (retryAction) articleStatus.appendChild(button(retryAction === "copy" ? text.copy : text.retry, retryAction));
    if (url) {
      var input = node("input", "atr-reader-copy-url");
      input.type = "text";
      input.value = url;
      input.readOnly = true;
      input.setAttribute("aria-label", text.copy);
      input.addEventListener("focus", function () { input.select(); });
      articleStatus.appendChild(input);
    }
  }
  function addSubscribeButton(target) {
    var element = button(text.open, "open");
    element.classList.add("atr-reader-header-button");
    element.setAttribute("aria-haspopup", "dialog");
    element.setAttribute("aria-controls", "atr-reader-dialog");
    element.setAttribute("aria-expanded", "false");
    subscriptionButtons.push(element);
    target.appendChild(element);
    return element;
  }
  function mount() {
    if (article) {
      var articleElement = document.querySelector("main article") || document.querySelector("article:not(.review-card)") || document.querySelector("main");
      if (articleElement) {
        var actions = node("section", "atr-reader-actions");
        actions.setAttribute("aria-label", text.actions);
        likeButton = button(text.like + " —", "like");
        likeButton.setAttribute("aria-pressed", "false");
        actions.appendChild(likeButton);
        actions.appendChild(button(text.share, "share"));
        addSubscribeButton(actions);
        articleStatus = node("p", "atr-reader-status");
        articleStatus.setAttribute("role", "status");
        articleStatus.setAttribute("aria-live", "polite");
        actions.appendChild(articleStatus);
        if (articleElement.tagName === "MAIN") articleElement.appendChild(actions);
        else articleElement.insertAdjacentElement("afterend", actions);
        actions.addEventListener("click", handleAction);
      }
      var articleHeader = document.querySelector(".topbar-links") || document.querySelector(".topline-actions") || document.querySelector("body > header .topbar") || document.querySelector("body > header");
      if (articleHeader) {
        articleHeader.classList.add("atr-reader-topbar");
        addSubscribeButton(articleHeader).addEventListener("click", handleAction);
      }
    } else {
      var topbar = document.querySelector(".topbar-links") || document.querySelector(".topline-actions") || document.querySelector(".topbar") || document.querySelector("header nav") || document.querySelector("header");
      if (topbar) { topbar.classList.add("atr-reader-topbar"); addSubscribeButton(topbar).addEventListener("click", handleAction); }
    }
    dialog = node("dialog", "atr-reader-dialog");
    dialog.id = "atr-reader-dialog";
    dialog.dataset.atrReaderDialog = "true";
    dialog.setAttribute("aria-labelledby", "atr-reader-dialog-title");
    var header = node("div", "atr-reader-dialog-header");
    dialogHeading = node("h2", "", text.title);
    dialogHeading.id = "atr-reader-dialog-title";
    dialogHeading.tabIndex = -1;
    header.appendChild(dialogHeading);
    var close = button(text.close, "close");
    close.classList.add("atr-reader-quiet");
    header.appendChild(close);
    dialog.appendChild(header);
    dialogFeedback = node("div", "atr-reader-feedback");
    dialogFeedback.setAttribute("role", "status");
    dialogFeedback.setAttribute("aria-live", "polite");
    dialog.appendChild(dialogFeedback);
    dialogBody = node("div", "atr-reader-dialog-body");
    dialog.appendChild(dialogBody);
    document.body.appendChild(dialog);
    dialog.addEventListener("click", handleAction);
    dialog.addEventListener("change", function (event) {
      if (event.target.dataset && event.target.dataset.readerTopic) state.topics = selectedTopics();
    });
    dialog.addEventListener("close", function () { restorePage(); });
    dialog.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && typeof dialog.close !== "function") { event.preventDefault(); closeDialog(); }
      if (event.key !== "Tab") return;
      var focusable = Array.from(dialog.querySelectorAll("button:not(:disabled),input:not(:disabled),a[href]"));
      if (!focusable.length) { event.preventDefault(); dialogHeading.focus(); return; }
      var first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && (document.activeElement === first || document.activeElement === dialogHeading)) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
    updateButtons();
  }
  function lockPage() {
    if (scrollState) return;
    scrollState = { x: window.scrollX || 0, y: window.scrollY || 0,
      rootOverflow: document.documentElement.style.overflow, bodyOverflow: document.body.style.overflow };
    document.documentElement.style.overflow = "hidden";
    document.body.style.overflow = "hidden";
  }
  function restorePage() {
    if (scrollState) {
      var previous = scrollState;
      scrollState = null;
      document.documentElement.style.overflow = previous.rootOverflow;
      document.body.style.overflow = previous.bodyOverflow;
      window.scrollTo(previous.x, previous.y);
    }
    if (opener && document.contains(opener)) {
      opener.setAttribute("aria-expanded", "false");
      opener.focus({ preventScroll: true });
    }
  }
  function closeDialog() {
    if (typeof dialog.close === "function") dialog.close();
    else { dialog.removeAttribute("open"); restorePage(); }
  }
  function openDialog(element) {
    if (dialog.open) { dialogHeading.focus({ preventScroll: true }); return; }
    opener = element;
    opener.setAttribute("aria-expanded", "true");
    lockPage();
    setFeedback("", false);
    renderDialog();
    if (typeof dialog.showModal === "function") dialog.showModal();
    else { dialog.setAttribute("open", ""); dialog.setAttribute("role", "dialog"); dialog.setAttribute("aria-modal", "true"); dialog.classList.add("atr-reader-fallback"); }
    dialogHeading.focus({ preventScroll: true });
  }
  function renderDialog() {
    if (!dialog) return;
    var focused = document.activeElement && document.activeElement.dataset && document.activeElement.dataset.readerAction;
    var focusedTopic = document.activeElement && document.activeElement.dataset && document.activeElement.dataset.readerTopic;
    dialogBody.replaceChildren();
    dialogBody.setAttribute("aria-busy", state.busy || state.preparing ? "true" : "false");
    dialogHeading.textContent = text.title;
    setFeedback(state.feedback, state.feedbackError);
    if (isIOS() && !standalone()) {
      dialogHeading.textContent = text.installTitle;
      dialogBody.appendChild(node("p", "", text.installIntro));
      var steps = node("ol");
      text.steps.forEach(function (step) { steps.appendChild(node("li", "", step)); });
      dialogBody.appendChild(steps);
      dialogBody.appendChild(node("p", "atr-reader-note", text.iosVersion));
      dialogBody.appendChild(button(text.close, "close"));
    } else if (!supported()) {
      dialogBody.appendChild(node("p", "", text.unsupported));
    } else if (permission() === "denied") {
      dialogBody.appendChild(node("p", "", isIOS() ? text.denied : text.deniedOther));
      dialogBody.appendChild(button(text.recheck, "recheck"));
      if (state.serverSubscription || state.localSubscription || state.pendingServerDelete) dialogBody.appendChild(button(text.unsubscribe, "unsubscribe"));
    } else {
      dialogBody.appendChild(node("p", "", subscribed() ? text.enabled : text.intro));
      if (!subscribed() && (state.serverSubscription || state.localSubscription)) dialogBody.appendChild(node("p", "atr-reader-note", text.reconnectNote));
      var fieldset = node("fieldset");
      fieldset.disabled = state.busy;
      fieldset.appendChild(node("legend", "", text.choose));
      ["review", "lecture"].forEach(function (topic) {
        var label = node("label");
        var input = node("input");
        input.type = "checkbox";
        input.value = topic;
        input.dataset.readerTopic = topic;
        input.checked = state.topics.indexOf(topic) !== -1;
        label.appendChild(input);
        label.appendChild(document.createTextNode(text[topic]));
        fieldset.appendChild(label);
      });
      dialogBody.appendChild(fieldset);
      if (state.preparing) dialogBody.appendChild(node("p", "atr-reader-note", text.preparing));
      else if (state.configError || state.registrationError) dialogBody.appendChild(node("p", "atr-reader-note", text.unavailable));
      var actions = node("div", "atr-reader-dialog-actions");
      var primary = button(state.busy ? text.busy : subscribed() ? text.save : (state.localSubscription ? text.reconnect : text.subscribe), subscribed() ? "save" : "subscribe", true);
      primary.disabled = state.busy || state.preparing || state.configError || state.registrationError;
      actions.appendChild(primary);
      if (state.configError || state.registrationError) actions.appendChild(button(text.retry, "retry"));
      if (state.localSubscription || state.serverSubscription || state.pendingServerDelete) {
        var off = button(text.unsubscribe, "unsubscribe"); off.disabled = state.busy; actions.appendChild(off);
      }
      if (subscribed()) {
        var test = button(text.test, "test"); test.disabled = state.busy; actions.appendChild(test);
      }
      dialogBody.appendChild(actions);
      dialogBody.appendChild(node("p", "atr-reader-note", text.device));
    }
    if ((focused || focusedTopic) && dialog.open) {
      var restore = focused ? Array.from(dialog.querySelectorAll("[data-reader-action]")).find(function (element) { return element.dataset.readerAction === focused; })
        : Array.from(dialog.querySelectorAll("[data-reader-topic]")).find(function (element) { return element.dataset.readerTopic === focusedTopic; });
      if (restore && !restore.disabled) restore.focus({ preventScroll: true });
      else dialogHeading.focus({ preventScroll: true });
    }
  }
  async function prepare() {
    if (state.busy) return;
    state.preparing = true;
    state.configError = false;
    state.registrationError = false;
    renderDialog();
    var configuration = request("/v1/config").then(function (result) {
      if (typeof result.vapidPublicKey !== "string" || !/^[A-Za-z0-9_-]{80,100}$/.test(result.vapidPublicKey)) throw apiError("invalid_public_key");
      state.key = result.vapidPublicKey;
    }).catch(function () { state.configError = true; });
    var registration = Promise.resolve();
    if (supported()) {
      registration = navigator.serviceWorker.register(scope + "sw.js", { scope: scope }).then(function (registered) {
        // Activation is normally already complete; wait for this registration only.
        state.registration = registered;
        if (registered.active) return registered;
        return new Promise(function (resolve, reject) {
          var worker = registered.installing || registered.waiting;
          if (!worker) { reject(apiError("worker_unavailable")); return; }
          var timeout = window.setTimeout(function () { reject(apiError("worker_activation_timeout")); }, 12000);
          function changed() {
            if (worker.state === "activated") { window.clearTimeout(timeout); worker.removeEventListener("statechange", changed); resolve(registered); }
            else if (worker.state === "redundant") { window.clearTimeout(timeout); worker.removeEventListener("statechange", changed); reject(apiError("worker_redundant")); }
          }
          worker.addEventListener("statechange", changed);
          changed();
        });
      }).then(function (registered) { return registered.pushManager.getSubscription(); })
        .then(function (subscription) { state.localSubscription = subscription; })
        .catch(function () { state.registrationError = true; });
    }
    var server = request("/v1/subscription").then(function (result) {
      state.serverSubscription = result.subscription || null;
      if (result.subscription) state.topics = validTopics(result.topics);
    }).catch(function (error) {
      if (error.code === "http_401") state.serverSubscription = null;
    });
    await Promise.all([configuration, registration, server]);
    state.preparing = false;
    updateButtons();
    renderDialog();
  }
  function publicKey(value) {
    var binary = atob(value.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - value.length % 4) % 4));
    return Uint8Array.from(binary, function (character) { return character.charCodeAt(0); });
  }
  async function subscribeFromGesture() {
    var topics = selectedTopics();
    if (!topics.length) { setFeedback(text.selectOne, true); return; }
    state.topics = topics;
    if (!supported() || (isIOS() && !standalone()) || state.preparing || !state.registration || !state.key || state.busy) return;
    if (permission() === "denied") { renderDialog(); return; }
    // Call the real OS permission API immediately inside the reader's click.
    // Do not put device creation, a network request, or SW readiness before it.
    var granted;
    try { granted = permission() === "granted" ? Promise.resolve("granted") : Notification.requestPermission(); }
    catch (_) { setFeedback(text.failed, true); return; }
    state.busy = true;
    renderDialog();
    try {
      if (await granted !== "granted") { setFeedback(text.installLater, false); return; }
      await ensureDevice();
      var subscription = await state.registration.pushManager.getSubscription();
      if (!subscription) subscription = await state.registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: publicKey(state.key) });
      state.localSubscription = subscription;
      var result = await request("/v1/subscription", "PUT", { subscription: subscription.toJSON(), topics: topics });
      state.serverSubscription = result.subscription || subscription.toJSON();
      state.pendingServerDelete = false;
      setFeedback(text.enabled, false);
    } catch (error) { setFeedback(error.code === "http_401" ? text.cookieFailed : text.failed, true); }
    finally { state.busy = false; updateButtons(); renderDialog(); }
  }
  async function savePreferences() {
    if (state.busy) return;
    var topics = selectedTopics();
    if (!topics.length) { setFeedback(text.selectOne, true); return; }
    if (!state.localSubscription) { setFeedback(text.reconnectNote, true); return; }
    state.topics = topics;
    state.busy = true;
    renderDialog();
    try {
      await ensureDevice();
      var result = await request("/v1/subscription", "PUT", { subscription: state.localSubscription.toJSON(), topics: topics });
      state.serverSubscription = result.subscription || state.localSubscription.toJSON();
      setFeedback(text.saved, false);
    } catch (error) { setFeedback(error.code === "http_401" ? text.cookieFailed : text.failed, true); }
    finally { state.busy = false; updateButtons(); renderDialog(); }
  }
  async function unsubscribe() {
    if (state.busy) return;
    state.busy = true;
    renderDialog();
    var serverRemoved = false, browserRemoved = !state.localSubscription;
    try {
      await request("/v1/subscription", "DELETE");
      serverRemoved = true;
      state.serverSubscription = null;
    } catch (_) { /* No HTTP failure, including a missing session cookie, confirms server removal. */ }
    try {
      if (state.localSubscription) browserRemoved = await state.localSubscription.unsubscribe();
      if (browserRemoved) state.localSubscription = null;
    } catch (_) { /* Keep a retry control when browser removal fails. */ }
    state.pendingServerDelete = !serverRemoved;
    state.busy = false;
    setFeedback(serverRemoved && browserRemoved ? text.disabled : browserRemoved ? text.partialOff : text.failed, !(serverRemoved && browserRemoved));
    updateButtons();
    renderDialog();
  }
  async function loadLikes() {
    if (!article || !likeButton) return;
    var revision = likeRevision;
    try {
      var result = await request("/v1/articles/" + encodeURIComponent(article.id) + "/like");
      if (revision !== likeRevision) return;
      state.count = validCount(result.count);
      state.liked = result.liked === true;
      updateButtons();
      if (articleStatus && articleStatus.dataset.readerStatusAction === "load-likes") articleMessage("");
    } catch (_) { if (revision === likeRevision) articleMessage(text.likeLoadFailed, "load-likes"); }
  }
  async function like() {
    if (!article || state.likeBusy) return;
    likeRevision += 1;
    state.likeBusy = true;
    updateButtons();
    try {
      await ensureDevice();
      var result = await request("/v1/articles/" + encodeURIComponent(article.id) + "/like", "PUT", { liked: !state.liked });
      state.count = validCount(result.count);
      state.liked = result.liked === true;
      articleMessage(state.liked ? text.likedSaved : text.unlikedSaved);
    } catch (error) { articleMessage(error.code === "http_401" ? text.cookieFailed : text.likeFailed, "like"); }
    finally { state.likeBusy = false; updateButtons(); }
  }
  function shareURL() {
    var path = location.pathname.startsWith(scope) ? location.pathname : scope;
    path = path.replace(/\/index\.html$/i, "/");
    return new URL(path, "https://infant83.io").href;
  }
  async function copyLink() {
    var url = shareURL();
    try {
      if (!navigator.clipboard || typeof navigator.clipboard.writeText !== "function") throw apiError("clipboard_unavailable");
      await navigator.clipboard.writeText(url);
      articleMessage(text.copied);
    } catch (_) { articleMessage(text.copyFailed, "copy", url); }
  }
  async function share() {
    if (typeof navigator.share !== "function") { await copyLink(); return; }
    try { await navigator.share({ title: String(article.title || document.title), url: shareURL() }); }
    catch (error) { if (!error || error.name !== "AbortError") articleMessage(text.shareFailed, "copy"); }
  }
  async function testAlert() {
    if (state.busy || !subscribed()) return;
    state.busy = true;
    renderDialog();
    try {
      await request("/v1/subscription/test", "POST", {});
      setFeedback(text.testQueued, false);
    } catch (error) { setFeedback(error.code === "http_429" ? text.testLimited : text.failed, true); }
    finally { state.busy = false; renderDialog(); }
  }
  function handleAction(event) {
    var element = event.target.closest("button[data-reader-action]");
    if (!element || element.disabled) return;
    var action = element.dataset.readerAction;
    if (action === "open") openDialog(element);
    else if (action === "close") closeDialog();
    else if (action === "subscribe") void subscribeFromGesture();
    else if (action === "save") void savePreferences();
    else if (action === "unsubscribe") void unsubscribe();
    else if (action === "retry" || action === "recheck") { setFeedback("", false); void prepare(); }
    else if (action === "like") void like();
    else if (action === "load-likes") void loadLikes();
    else if (action === "share") void share();
    else if (action === "copy") void copyLink();
    else if (action === "test") void testAlert();
  }
  mount();
  void prepare();
  void loadLikes();
})();
