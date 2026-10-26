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
    unlikedSaved: "Your like was removed.", likeSaving: "Saving…", likeFailed: "Could not confirm your like. The previous display has been restored.", likeLoadFailed: "Likes are temporarily unavailable.",
    share: "Share", copy: "Copy link", copied: "Article link copied.", shareFailed: "Sharing failed. You can copy the article link instead.",
    copyFailed: "The link could not be copied. Select and copy this address:", install: "Add to Home Screen", installLater: "You can enable alerts whenever you are ready.",
    iosVersion: "Web alerts require iOS or iPadOS 16.4 or later.", busy: "Connecting…", actions: "Reader actions",
    test: "Send a test alert to this device", testQueued: "The test alert was accepted for sending. Check this device’s notifications; acceptance does not confirm delivery.",
    testLimited: "The test limit was reached. Wait at least a minute; up to five tests are available per device each day.",
    cookieFailed: "The browser could not keep this device connected. Allow cookies for this site in your privacy settings, then try again.",
    permissionTimeout: "The notification permission window has not responded. Check any open permission window, then try again. If no window appears, open this page in your regular browser.",
    pushTimeout: "The browser’s alert connection has not responded. Check your connection, then try again."
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
    unlikedSaved: "좋아요를 취소했어요.", likeSaving: "저장 중…", likeFailed: "좋아요 저장 여부를 확인하지 못해 화면을 이전 상태로 되돌렸어요.", likeLoadFailed: "지금은 좋아요 정보를 불러올 수 없어요.",
    share: "공유", copy: "주소 복사", copied: "글 주소를 복사했어요.", shareFailed: "공유하지 못했어요. 글 주소를 복사할 수 있어요.",
    copyFailed: "주소를 복사하지 못했어요. 아래 주소를 선택해 복사해 주세요.", install: "홈 화면에 추가", installLater: "원할 때 새 글 알림을 켤 수 있어요.",
    iosVersion: "웹 알림은 iOS·iPadOS 16.4 이상에서 사용할 수 있어요.", busy: "연결 중…", actions: "독자 참여",
    test: "이 기기로 테스트 알림 보내기", testQueued: "테스트 알림 발송을 접수했어요. 이 기기의 알림을 확인해 주세요. 접수는 도착 확인과 다릅니다.",
    testLimited: "테스트 횟수 제한에 도달했어요. 1분 이상 간격을 두고, 기기당 하루 5회까지 보낼 수 있어요.",
    cookieFailed: "브라우저에서 이 기기의 연결을 유지하지 못했어요. 개인정보 설정에서 이 사이트의 쿠키를 허용한 뒤 다시 시도해 주세요.",
    permissionTimeout: "알림 권한 창이 응답하지 않았어요. 열려 있는 권한 창을 확인한 뒤 다시 시도해 주세요. 창이 보이지 않으면 기본 브라우저에서 이 페이지를 열어 주세요.",
    pushTimeout: "브라우저의 알림 연결이 응답하지 않았어요. 네트워크 연결을 확인한 뒤 다시 시도해 주세요."
  };
  var guideText = english ? {
    title: "Installation and alert help", device: "Show instructions for", iphone: "iPhone · iPad", chrome: "Mac · Chrome", safari: "Mac · Safari", other: "Other devices",
    iphoneReady: "You are using the Home Screen app. Manage alerts below without installing it again.",
    macOptional: "Installing an app is optional on Mac. You can also receive alerts from a regular browser tab.",
    macReady: "You are using the installed web app. Manage alerts below without installing it again.",
    alreadySubscribed: "Alerts are already on for this device. Use Send a test alert to this device to check delivery.",
    iphoneSteps: ["Open your browser’s Share menu.", "Choose Add to Home Screen, then Add. Keep Open as Web App enabled if shown.", "Open the AI Tech Review icon on your Home Screen. If you already have a web app icon for this same address, use it instead of adding another."],
    iphoneNext: "In the app, tap Enable new article alerts → Allow, then Send a test alert to this device.",
    iphoneAppSteps: ["Tap Enable new article alerts below and choose Allow in the iOS prompt.", "After subscribing, use Send a test alert to this device to check delivery."],
    iphoneSettings: "If an alert does not arrive: iPhone Settings → Notifications → the AI Tech Review app → Allow Notifications. Also check Focus. Enable Badges there for an icon number. Your chosen Home Screen app name may differ.",
    chromeSteps: ["Optional: use the install icon in Chrome’s address bar, or ⋮ → Cast, save, and share → Install page as app. Menu names vary by version.", "If you install it, open its Dock/app icon and subscribe in that window. Otherwise, subscribe in this tab. Tap Enable new article alerts and allow the Chrome or macOS prompt that appears.", "Send a test alert to this device and allow any additional macOS notification prompt."],
    safariSteps: ["Optional: in a supported Safari/macOS version, choose File → Add to Dock.", "If you add it to the Dock, open that app and subscribe in its own window. Otherwise, subscribe in this tab. Tap Enable new article alerts and allow the prompt that appears.", "Send a test alert to this device and allow any macOS notification prompt."],
    macAppSteps: ["Tap Enable new article alerts and allow the browser or macOS permission prompt that appears.", "Send a test alert to this device and allow any additional macOS notification prompt."],
    existingMac: "Already installed for this address? Open its existing Dock or app icon. This browser tab cannot reliably tell whether you installed it earlier.",
    chromeSettings: "If an alert does not arrive: Chrome Settings → Privacy and security → Site settings → Notifications. In macOS System Settings → Notifications, check the actual app entry, such as AI Tech Review Letters or Google Chrome.",
    safariSettings: "For a Safari tab, check Safari Settings → Websites → Notifications and the Safari entry in macOS System Settings → Notifications. A Dock app has its own notification settings.",
    appSettings: "For an installed app, check macOS System Settings → Notifications → its actual app name, such as AI Tech Review Letters. App notification settings may differ from the browser tab’s site settings. Enable Badge app icon for the icon number.",
    macCenter: "Click the date and time at the top right of your Mac to open Notification Center. Check Focus if banners are hidden. Test from a regular browser window, not private browsing.",
    otherSteps: ["Use a browser that supports web notifications, then tap Enable new article alerts.", "Choose Allow and send a test alert. App installation is optional when your browser supports alerts in a tab."],
    installButton: "Install app (optional)", installBusy: "Opening install window…", installAccepted: "Continue in the browser’s install window, then open the app icon. Alert permission is a separate step.",
    installOptional: "Installation is optional. You can keep reading and receiving alerts in this browser tab.",
    installFailed: "The install window did not open or respond. You can use the browser menu above, or keep receiving alerts in this tab.",
    recentTitle: "Recent new article alerts", recentEmpty: "No new article alerts are saved on this device/browser yet. New article alerts received from now on will appear here.",
    recentNote: "These alerts belong to this device/browser. Supported installed apps can show a number when OS badge display is allowed; opening the app/site clears that number while keeping this list. Test alerts do not add to the number or list.",
    received: "Received", more: "Show more"
  } : {
    title: "설치·알림 받는 방법", device: "안내할 기기", iphone: "iPhone · iPad", chrome: "Mac · Chrome", safari: "Mac · Safari", other: "그 밖의 기기",
    iphoneReady: "홈 화면 앱으로 열었어요. 추가 설치 없이 아래에서 알림을 설정할 수 있어요.",
    macOptional: "Mac에서는 앱 설치가 선택 사항이에요. 일반 브라우저 탭에서도 알림을 받을 수 있어요.",
    macReady: "설치한 웹앱으로 열었어요. 추가 설치 없이 아래에서 알림을 설정할 수 있어요.",
    alreadySubscribed: "이미 이 기기에서 새 글 알림을 받고 있어요. ‘이 기기로 테스트 알림 보내기’로 도착을 확인하세요.",
    iphoneSteps: ["브라우저의 공유 메뉴를 여세요.", "‘홈 화면에 추가’ → ‘추가’를 누르세요. ‘웹앱으로 열기’가 보이면 켜두세요.", "홈 화면의 AI Tech Review 아이콘을 여세요. 이미 같은 주소의 웹앱 아이콘이 있으면 새로 추가하지 말고 그 아이콘을 사용하세요."],
    iphoneNext: "앱에서 ‘새 글 알림 받기’ → iOS ‘허용’을 누르고, ‘이 기기로 테스트 알림 보내기’로 확인하세요.",
    iphoneAppSteps: ["아래 ‘새 글 알림 받기’를 누르고 iOS 권한 창에서 ‘허용’을 선택하세요.", "구독한 뒤 ‘이 기기로 테스트 알림 보내기’로 도착을 확인하세요."],
    iphoneSettings: "알림이 안 오면 iPhone 설정 → 알림 → 테크리뷰 앱 → 알림 허용과 집중 모드를 확인하세요. 아이콘 숫자는 같은 화면의 ‘배지’도 켜야 보여요. 홈 화면에 지정한 앱 이름에 따라 항목 이름이 다를 수 있어요.",
    chromeSteps: ["설치는 선택입니다. Chrome 주소창의 설치 아이콘 또는 ⋮ → 전송, 저장 및 공유 → 페이지를 앱으로 설치를 이용하세요. 메뉴 이름은 버전에 따라 달라질 수 있어요.", "설치했다면 Dock·앱 아이콘을 열고 그 창에서 구독하세요. 설치하지 않았다면 이 탭에서 구독하면 됩니다. ‘새 글 알림 받기’를 누르고 표시되는 Chrome 또는 macOS 권한 창에서 허용하세요.", "‘이 기기로 테스트 알림 보내기’를 누르고 추가 macOS 권한 창이 나오면 허용하세요."],
    safariSteps: ["설치는 선택입니다. 지원하는 Safari·macOS 버전에서는 파일 → Dock에 추가를 이용하세요.", "Dock에 추가했다면 그 앱을 열고 앱 창에서 구독하세요. 추가하지 않았다면 이 탭에서 구독하면 됩니다. ‘새 글 알림 받기’를 누르고 표시되는 권한 창에서 허용하세요.", "‘이 기기로 테스트 알림 보내기’를 누르고 macOS의 알림 허용 창이 나오면 허용하세요."],
    macAppSteps: ["‘새 글 알림 받기’를 누르고 표시되는 브라우저 또는 macOS 권한 창에서 허용하세요.", "‘이 기기로 테스트 알림 보내기’를 누르고 추가 macOS 권한 창이 나오면 허용하세요."],
    existingMac: "이미 이 주소의 앱을 설치했다면 기존 Dock·앱 아이콘을 여세요. 일반 브라우저 탭에서는 이전 설치 여부를 정확히 확인할 수 없어요.",
    chromeSettings: "알림이 안 오면 Chrome 설정 → 개인정보 및 보안 → 사이트 설정 → 알림을 확인하세요. macOS 시스템 설정 → 알림에서도 AI Tech Review Letters 또는 Google Chrome 등 실제 표시된 앱 항목을 확인하세요.",
    safariSettings: "Safari 탭은 Safari 설정 → 웹사이트 → 알림의 사이트 허용과 macOS 시스템 설정 → 알림의 Safari 항목을 확인하세요. Dock 앱의 알림 설정은 별도입니다.",
    appSettings: "설치 앱은 macOS 시스템 설정 → 알림에서 AI Tech Review Letters 등 실제 앱 이름의 항목을 확인하세요. 앱의 알림 설정은 브라우저 탭의 사이트 설정과 다를 수 있어요. 아이콘 숫자는 ‘앱 아이콘에 배지 표시’도 켜야 보여요.",
    macCenter: "Mac 화면 오른쪽 위 날짜·시간을 누르면 알림센터가 열려요. 배너가 안 보이면 집중 모드를 확인하세요. 비공개 탐색 대신 일반 창에서 테스트하세요.",
    otherSteps: ["웹 알림을 지원하는 브라우저에서 ‘새 글 알림 받기’를 누르세요.", "‘허용’을 선택한 뒤 테스트 알림을 보내보세요. 브라우저 탭의 알림을 지원하는 환경에서는 앱 설치가 선택 사항입니다."],
    installButton: "앱 설치하기 (선택)", installBusy: "설치 창 여는 중…", installAccepted: "브라우저의 설치 창에서 진행한 뒤 앱 아이콘을 열어 주세요. 알림 허용은 별도 단계입니다.",
    installOptional: "앱 설치는 선택이에요. 이 브라우저 탭에서도 계속 읽고 알림을 받을 수 있어요.",
    installFailed: "설치 창이 열리지 않거나 응답하지 않아요. 위의 브라우저 메뉴를 이용하거나 이 탭에서 알림을 받을 수 있어요.",
    recentTitle: "최근 받은 새 글 알림", recentEmpty: "이 기기·브라우저에 저장된 새 글 알림이 아직 없어요. 앞으로 도착하는 새 글 알림을 여기에 모아 보여드려요.",
    recentNote: "기기·브라우저별 알림입니다. 숫자는 지원하는 설치 앱에서 운영체제의 배지 표시를 허용해야 보여요. 앱·사이트를 열면 숫자는 0이 되고 목록은 남아요. 테스트 알림은 숫자·목록에 포함하지 않아요.",
    received: "받은 시각", more: "더 보기"
  };
  var state = { preparing: true, busy: false, configError: false, registrationError: false, key: "", registration: null,
    localSubscription: null, serverSubscription: null, topics: ["review", "lecture"], feedback: "", feedbackError: false,
    liked: false, count: null, likeBusy: false, likeRetryDesired: null, pendingServerDelete: false, guideDevice: null, guideOpen: null, installBusy: false,
    notificationHistory: [], historyReady: false, historyLimit: 5, historyCount: null };
  var subscriptionButtons = [];
  var dialog = null, dialogBody = null, dialogHeading = null, dialogFeedback = null, opener = null;
  var likeButton = null, likeButtons = [], articleStatus = null, articleStatuses = [], likeRevision = 0, scrollState = null;
  var pendingPermission = null, pendingPushLookup = null, pendingPushSubscription = null;
  var deviceSessionKnown = false, pendingDeviceRegistration = null, pendingLikeWrite = null;
  var installPrompt = null, installedInSession = false, currentGuide = null, recentHeading = null;
  var historyRequest = null, historyLastAttempt = 0, historyGeneration = 0, historyQueued = false, historyDirty = false;
  var metricsRoot = null, metricsFields = {}, metricsStatus = null, metricsRequest = null, metricsRefreshQueued = false, metricsWrites = 0, metricsGeneration = 0, metricsOpenStarted = false;
  var metricsVisitor = null, metricsStorageChecked = false;
  var reviewHub = !article && (location.pathname === scope || location.pathname === scope + "index.html" || location.pathname === scope.slice(0, -1) || location.pathname === scope + "en/" || location.pathname === scope + "en/index.html");
  var metricsText = english ? {
    title: "Reader activity", visitors: "Visitors", opens: "Article opens", shares: "Shares · copies",
    subscribers: "Alert subscriptions", articleOpens: "This article opened", articleShares: "Shared · copied",
    unavailable: "Counts temporarily unavailable", deviceUnit: " devices"
  } : {
    title: "독자 활동", visitors: "방문자수", opens: "글 열람", shares: "공유·복사",
    subscribers: "알림 구독", articleOpens: "이 글 열람", articleShares: "공유·복사",
    unavailable: "통계를 잠시 불러올 수 없어요", deviceUnit: "기기"
  };

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
  function deviceGuide() {
    if (isIOS()) return "iphone";
    var agent = navigator.userAgent || "";
    if (/Macintosh|Mac OS X/.test(agent)) return /Safari/.test(agent) && !/Chrome|Chromium|Edg|OPR/.test(agent) ? "mac-safari" : "mac-chrome";
    return "other";
  }
  function guideInstalled(device) { return device === deviceGuide() && (standalone() || installedInSession); }
  function appendGuide(defaultOpen) {
    var device = state.guideDevice || deviceGuide();
    var installed = guideInstalled(device);
    var activeSubscription = device === deviceGuide() && subscribed();
    var details = node("details", "atr-reader-guide");
    currentGuide = details;
    details.open = state.guideOpen === null ? defaultOpen : state.guideOpen;
    var summary = node("summary", "", guideText.title);
    summary.dataset.readerGuide = "summary";
    details.appendChild(summary);
    var label = node("label", "atr-reader-guide-device");
    label.appendChild(node("span", "", guideText.device));
    var select = node("select", "atr-reader-guide-select");
    select.setAttribute("aria-label", guideText.device);
    select.dataset.readerGuide = "device";
    [["iphone", guideText.iphone], ["mac-chrome", guideText.chrome], ["mac-safari", guideText.safari], ["other", guideText.other]].forEach(function (item) {
      var option = node("option", "", item[1]); option.value = item[0]; select.appendChild(option);
    });
    select.value = device;
    label.appendChild(select);
    details.appendChild(label);
    var steps;
    if (device === "iphone") steps = installed ? guideText.iphoneAppSteps : guideText.iphoneSteps;
    else if (device === "mac-chrome") steps = installed ? guideText.macAppSteps : guideText.chromeSteps;
    else if (device === "mac-safari") steps = installed ? guideText.macAppSteps : guideText.safariSteps;
    else steps = guideText.otherSteps;
    if (activeSubscription) {
      steps = !installed && device === "mac-chrome" ? [guideText.chromeSteps[0], guideText.alreadySubscribed]
        : !installed && device === "mac-safari" ? [guideText.safariSteps[0], guideText.alreadySubscribed] : [guideText.alreadySubscribed];
    }
    var list = node("ol");
    steps.forEach(function (step) { list.appendChild(node("li", "", step)); });
    details.appendChild(list);
    if (device === "iphone") {
      if (!installed && !activeSubscription) details.appendChild(node("p", "", guideText.iphoneNext));
      details.appendChild(node("p", "atr-reader-note", guideText.iphoneSettings));
      details.appendChild(node("p", "atr-reader-note", text.iosVersion));
    } else if (device === "mac-chrome" || device === "mac-safari") {
      if (!installed) details.appendChild(node("p", "atr-reader-note", guideText.existingMac));
      details.appendChild(node("p", "atr-reader-note", installed ? guideText.appSettings : device === "mac-chrome" ? guideText.chromeSettings : guideText.safariSettings));
      details.appendChild(node("p", "atr-reader-note", guideText.macCenter));
    }
    if (device === deviceGuide() && device !== "iphone" && !installed && (installPrompt || state.installBusy)) {
      var install = button(state.installBusy ? guideText.installBusy : guideText.installButton, "install-app");
      install.disabled = state.installBusy;
      details.appendChild(install);
    }
    details.addEventListener("toggle", function () { if (currentGuide === details) state.guideOpen = details.open; });
    dialogBody.appendChild(details);
  }
  function notificationURL(value) {
    if (typeof value !== "string") return null;
    try {
      var url = new URL(value, location.origin + scope);
      return url.origin === location.origin && url.pathname.startsWith(scope) && !url.username && !url.password ? url.href : null;
    } catch (_) { return null; }
  }
  function notificationList(reply) {
    if (!reply || typeof reply !== "object" || Array.isArray(reply) || reply.ok !== true || !Number.isSafeInteger(reply.count) || reply.count < 0 || !Array.isArray(reply.notifications)) return null;
    var seen = new Set();
    var result = [];
    reply.notifications.slice(0, 20).forEach(function (item) {
      if (!item || typeof item !== "object" || typeof item.id !== "string" || !item.id.trim() || item.id.length > 180 || seen.has(item.id)
        || typeof item.title !== "string" || !item.title.trim() || !Number.isSafeInteger(item.receivedAt) || item.receivedAt <= 0 || !Number.isFinite(new Date(item.receivedAt).getTime())) return;
      var url = notificationURL(item.url);
      if (!url) return;
      seen.add(item.id);
      result.push({ id: item.id, title: item.title.slice(0, 240), url: url, receivedAt: item.receivedAt });
    });
    return result;
  }
  function appendRecentNotifications() {
    if (!state.historyReady) return;
    var recent = node("section", "atr-reader-recent");
    recent.setAttribute("aria-labelledby", "atr-reader-recent-title");
    var title = node("h3", "", guideText.recentTitle); title.id = "atr-reader-recent-title"; title.tabIndex = -1;
    recentHeading = title;
    recent.appendChild(title);
    if (!state.notificationHistory.length) recent.appendChild(node("p", "atr-reader-note", guideText.recentEmpty));
    else {
      var list = node("ul", "atr-reader-recent-list");
      state.notificationHistory.slice(0, state.historyLimit).forEach(function (item) {
        var row = node("li");
        var link = node("a", "", item.title); link.href = item.url;
        row.appendChild(link);
        var received = node("time", "", guideText.received + " · " + new Intl.DateTimeFormat(english ? "en-US" : "ko-KR", { year: "numeric", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(item.receivedAt));
        received.dateTime = new Date(item.receivedAt).toISOString();
        row.appendChild(received);
        list.appendChild(row);
      });
      recent.appendChild(list);
      if (state.historyLimit < state.notificationHistory.length) recent.appendChild(button(guideText.more + " (" + state.notificationHistory.length + ")", "recent-more"));
    }
    recent.appendChild(node("p", "atr-reader-note", guideText.recentNote));
    dialogBody.appendChild(recent);
  }
  function notificationWorker() {
    if (!("serviceWorker" in navigator)) return null;
    var worker = navigator.serviceWorker.controller || (state.registration && state.registration.active);
    return worker && typeof worker.postMessage === "function" ? worker : null;
  }
  function requestNotificationState(worker) {
    return new Promise(function (resolve, reject) {
      var channel = new window.MessageChannel();
      var finished = false;
      var timer = window.setTimeout(function () { finish(apiError("notification_state_timeout")); }, 4000);
      function finish(error, reply) {
        if (finished) return;
        finished = true;
        window.clearTimeout(timer);
        channel.port1.onmessage = null;
        channel.port1.onmessageerror = null;
        try { if (typeof channel.port1.close === "function") channel.port1.close(); } catch (_) { /* Already detached. */ }
        try { if (typeof channel.port2.close === "function") channel.port2.close(); } catch (_) { /* Already transferred. */ }
        if (error) reject(error); else resolve(reply);
      }
      channel.port1.onmessage = function (event) { finish(null, event.data); };
      channel.port1.onmessageerror = function () { finish(apiError("notification_state_unavailable")); };
      if (typeof channel.port1.start === "function") channel.port1.start();
      try { worker.postMessage({ type: "atr-reader-notification-state" }, [channel.port2]); }
      catch (error) { finish(error); }
    });
  }
  function refreshNotificationState(force) {
    if (document.visibilityState !== "visible" || (typeof document.hasFocus === "function" && !document.hasFocus())) return Promise.resolve();
    if (window.top && window.top !== window.self) return Promise.resolve();
    if (historyRequest) { if (force || historyDirty) historyQueued = true; return historyRequest; }
    if (!force && !historyDirty && Date.now() - historyLastAttempt < 750) return Promise.resolve();
    var worker = notificationWorker();
    if (!worker || typeof window.MessageChannel !== "function") return Promise.resolve();
    historyLastAttempt = Date.now();
    historyDirty = false;
    var generation = ++historyGeneration;
    historyRequest = requestNotificationState(worker).then(function (reply) {
      if (generation !== historyGeneration || worker !== notificationWorker()) { historyQueued = true; return; }
      var records = notificationList(reply);
      if (records === null) return;
      state.notificationHistory = records;
      state.historyCount = reply.count;
      state.historyReady = true;
      if (dialog && dialog.open) renderDialog();
    }).catch(function () { /* Old workers and unsupported browsers must not affect subscription controls. */ }).then(function () {
      historyRequest = null;
      if (historyQueued) { historyQueued = false; void refreshNotificationState(true); }
    });
    return historyRequest;
  }
  function notificationHint(event) {
    if (!event || !event.data || event.data.type !== "atr-reader-notifications-changed" || !event.source || typeof event.source.scriptURL !== "string") return;
    try { if (new URL(event.source.scriptURL).href !== new URL(scope + "sw.js", location.origin).href) return; }
    catch (_) { return; }
    historyDirty = true;
    void refreshNotificationState(false);
  }
  function supported() {
    return window.isSecureContext !== false && "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
  }
  function permission() { return "Notification" in window ? Notification.permission : "default"; }
  function subscribed() {
    return Boolean(state.localSubscription && state.serverSubscription && state.localSubscription.endpoint === state.serverSubscription.endpoint && permission() === "granted");
  }
  function apiError(code) { var error = new Error(code); error.code = code; return error; }
  function withDeadline(promise, milliseconds, code) {
    return new Promise(function (resolve, reject) {
      var settled = false;
      var timer = window.setTimeout(function () {
        if (settled) return;
        settled = true;
        reject(apiError(code));
      }, milliseconds);
      Promise.resolve(promise).then(function (value) {
        if (settled) return;
        settled = true;
        window.clearTimeout(timer);
        resolve(value);
      }, function (error) {
        if (settled) return;
        settled = true;
        window.clearTimeout(timer);
        reject(error);
      });
    });
  }
  function permissionFromGesture() {
    if (permission() === "granted") return Promise.resolve("granted");
    if (!pendingPermission) {
      var requested = Promise.resolve(Notification.requestPermission());
      pendingPermission = requested;
      function clear() { if (pendingPermission === requested) pendingPermission = null; }
      requested.then(clear, clear);
    }
    return pendingPermission;
  }
  function browserSubscription(registration) {
    if (!pendingPushLookup) {
      var requested = Promise.resolve(registration.pushManager.getSubscription());
      pendingPushLookup = requested;
      function clear() { if (pendingPushLookup === requested) pendingPushLookup = null; }
      requested.then(clear, clear);
    }
    return withDeadline(pendingPushLookup, 25000, "push_timeout");
  }
  function createBrowserSubscription(registration) {
    if (!pendingPushSubscription) {
      var requested = Promise.resolve(registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: publicKey(state.key) }));
      pendingPushSubscription = requested;
      function clear() { if (pendingPushSubscription === requested) pendingPushSubscription = null; }
      requested.then(clear, clear);
    }
    return withDeadline(pendingPushSubscription, 25000, "push_timeout");
  }
  async function request(path, method, body, credentials) {
    var controller = typeof AbortController === "function" ? new AbortController() : null;
    var timer = controller ? window.setTimeout(function () { controller.abort(); }, 12000) : null;
    try {
      var response = await fetch(apiBase + path, {
        method: method || "GET", mode: "cors", credentials: credentials || "include", cache: "no-store",
        headers: body === undefined ? { Accept: "application/json" } : { Accept: "application/json", "Content-Type": "application/json" },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: controller ? controller.signal : undefined
      });
      if (!response.ok) {
        if (response.status === 401 && credentials !== "omit") deviceSessionKnown = false;
        throw apiError("http_" + response.status);
      }
      var result = await response.json();
      if (!result || typeof result !== "object" || Array.isArray(result) || result.ok === false) throw apiError("api_failed");
      if (credentials !== "omit" && result.ok === true &&
        ((path === "/v1/devices" && typeof result.deviceId === "string" && result.deviceId.length > 0)
          || (path === "/v1/subscription" && (method === "PUT" || method === "DELETE" || ((!method || method === "GET") && typeof result.subscribed === "boolean")))
          || (method === "PUT" && /^\/v1\/articles\/[^/]+\/like$/.test(path)))) deviceSessionKnown = true;
      return result;
    } finally { if (timer !== null) window.clearTimeout(timer); }
  }
  function metricsTracked() {
    return navigator.globalPrivacyControl !== true && !/^(1|yes)$/i.test(String(navigator.doNotTrack || window.doNotTrack || ""));
  }

  function metricsUUID() {
    if (!window.crypto) return null;
    if (typeof window.crypto.randomUUID === "function") return window.crypto.randomUUID();
    if (typeof window.crypto.getRandomValues !== "function") return null;
    var bytes = new Uint8Array(16); window.crypto.getRandomValues(bytes);
    bytes[6] = (bytes[6] & 15) | 64; bytes[8] = (bytes[8] & 63) | 128;
    var hex = Array.from(bytes, function (value) { return value.toString(16).padStart(2, "0"); }).join("");
    return hex.slice(0, 8) + "-" + hex.slice(8, 12) + "-" + hex.slice(12, 16) + "-" + hex.slice(16, 20) + "-" + hex.slice(20);
  }
  function metricsVisitorId() {
    if (!metricsTracked()) return null;
    if (metricsStorageChecked) return metricsVisitor;
    metricsStorageChecked = true;
    try {
      var key = "atr-reader-metrics-visitor:" + scope;
      var previous = window.localStorage.getItem(key);
      var valid = /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
      var value = valid.test(previous || "") ? previous : metricsUUID();
      if (value && valid.test(value)) {
        window.localStorage.setItem(key, value);
        if (window.localStorage.getItem(key) === value) metricsVisitor = value;
      }
    } catch (_) { /* Do not inflate counts with a new identifier on every storage-blocked page. */ }
    return metricsVisitor;
  }
  function metricsForeground() {
    try { return window.self === window.top && document.visibilityState === "visible" && document.prerendering !== true; } catch (_) { return false; }
  }
  function metricsField(parent, key, label, suffix) {
    var item = node("span", "atr-reader-metric");
    item.appendChild(node("span", "atr-reader-metric-label", label));
    var value = node("strong", "", "—"); value.dataset.readerMetric = key;
    if (!metricsFields[key]) metricsFields[key] = [];
    metricsFields[key].push(value); item.appendChild(value);
    if (suffix) item.appendChild(node("span", "", suffix));
    parent.appendChild(item);
  }
  function mountMetrics(articleActions) {
    if (!articleActions && !reviewHub) return;
    metricsRoot = node("section", "atr-reader-metrics" + (article ? " atr-reader-metrics-article" : ""));
    metricsRoot.setAttribute("aria-label", metricsText.title);
    metricsRoot.dataset.state = "loading";
    var primary = node("div", "atr-reader-metrics-row");
    if (article) {
      metricsField(primary, "articleOpens", metricsText.articleOpens);
      metricsField(primary, "articleShares", metricsText.articleShares);
    } else {
      metricsField(primary, "visitors", metricsText.visitors);
      metricsField(primary, "opens", metricsText.opens);
      metricsField(primary, "shares", metricsText.shares);
      metricsField(primary, "activeSubscribers", metricsText.subscribers, metricsText.deviceUnit);
    }
    metricsRoot.appendChild(primary);
    metricsStatus = node("p", "atr-reader-metrics-status");
    metricsStatus.setAttribute("role", "status");
    metricsStatus.setAttribute("aria-live", "polite");
    metricsRoot.appendChild(metricsStatus);
    if (!article) {
      var info = node("a", "atr-reader-metrics-info", english ? "About reader statistics" : "통계 안내");
      info.href = scope + "methods/#reader-metrics";
      metricsRoot.appendChild(info);
    }
    if (articleActions) articleActions.appendChild(metricsRoot);
    else {
      var slot = document.querySelector("[data-reader-site-metrics]");
      if (slot) slot.appendChild(metricsRoot);
      else {
        var anchor = document.querySelector(".hero .stats");
        if (anchor) anchor.insertAdjacentElement("afterend", metricsRoot);
      }
    }
  }
  function metricsValue(value) { return typeof value === "number" && Number.isSafeInteger(value) && value >= 0 ? value : null; }
  function applyMetrics(result) {
    if (!result || result.ok !== true || !result.site || typeof result.site !== "object" || Array.isArray(result.site)
      || typeof result.since !== "string" || !/^\d{4}-\d{2}-\d{2}T/.test(result.since) || !Number.isFinite(Date.parse(result.since))) throw apiError("invalid_metrics");
    var values = {}, fields = ["visitors", "todayVisitors", "opens", "shares", "copies", "activeSubscribers", "subscriptionRegistrations", "articleNotificationsSent"];
    fields.forEach(function (key) { var value = metricsValue(result.site[key]); if (value === null) throw apiError("invalid_metrics"); values[key] = value; });
    values.shares += values.copies;
    if (!Number.isSafeInteger(values.shares)) throw apiError("invalid_metrics");
    if (article) {
      var row = result.article;
      if (!row || row.id !== article.id) throw apiError("invalid_metrics");
      values.articleOpens = metricsValue(row.opens);
      var shares = metricsValue(row.shares), copies = metricsValue(row.copies);
      if (values.articleOpens === null || shares === null || copies === null || !Number.isSafeInteger(shares + copies)) throw apiError("invalid_metrics");
      values.articleShares = shares + copies;
    }
    Object.keys(metricsFields).forEach(function (key) { metricsFields[key].forEach(function (field) { field.textContent = new Intl.NumberFormat(english ? "en-US" : "ko-KR").format(values[key]); }); });

    if (metricsRoot) { metricsRoot.dataset.state = "ready"; metricsRoot.removeAttribute("title"); }
    if (metricsStatus) metricsStatus.textContent = "";
  }
  async function metricsCall(type) {
    var generation, writing = false;
    try {
      var path = "/v1/metrics" + (article ? "?articleId=" + encodeURIComponent(article.id) : "");
      var body;
      if (type) {
        var visitorId = metricsVisitorId(), eventId = metricsUUID();
        if (!visitorId || !eventId) return;
        path = "/v1/metrics/events";
        body = { type: type, visitorId: visitorId, eventId: eventId, articleId: article ? article.id : null };
      }
      generation = ++metricsGeneration;
      if (body) { writing = true; metricsWrites += 1; }
      var result = await withDeadline(request(path, body ? "POST" : "GET", body, "omit"), 5000, "metrics_timeout");
      if (generation === metricsGeneration) applyMetrics(result);
    } catch (_) {
      if (generation === metricsGeneration && metricsRoot && metricsRoot.dataset.state !== "ready") {
        metricsRoot.dataset.state = "error"; metricsRoot.setAttribute("title", metricsText.unavailable);
        if (metricsStatus) metricsStatus.textContent = metricsText.unavailable;
      }
    } finally { if (writing) { metricsWrites -= 1; flushMetricsRefresh(); } }
  }
  function flushMetricsRefresh() {
    if (metricsRefreshQueued && !metricsRequest && metricsWrites === 0) { metricsRefreshQueued = false; void refreshMetrics(); }
  }
  function refreshMetrics(force) {
    if (!metricsRoot) return Promise.resolve();
    if (metricsRequest || metricsWrites > 0) { if (force) metricsRefreshQueued = true; return metricsRequest || Promise.resolve(); }
    metricsRequest = metricsCall().finally(function () {
      metricsRequest = null;
      flushMetricsRefresh();
    });
    return metricsRequest;
  }
  function recordMetrics(type) {
    if (!metricsRoot || !metricsTracked() || (!article && type !== "open")) return Promise.resolve();
    try { if (window.self !== window.top || (type === "open" && !metricsForeground())) return Promise.resolve(); } catch (_) { return Promise.resolve(); }
    return metricsCall(type);
  }
  function startMetrics() {
    if (!metricsRoot || !metricsForeground() || metricsOpenStarted) return;
    metricsOpenStarted = true;
    if (metricsVisitorId()) void recordMetrics("open");
    else void refreshMetrics();
  }
  function metricsPageShow(event) {
    if (event && event.persisted && metricsRoot && metricsForeground()) { void refreshMetrics(true); return; }
    startMetrics();
  }
  function ensureDevice() {
    if (deviceSessionKnown) return Promise.resolve();
    if (!pendingDeviceRegistration) {
      var pending = request("/v1/devices", "POST", {});
      pendingDeviceRegistration = pending;
      function clear() { if (pendingDeviceRegistration === pending) pendingDeviceRegistration = null; }
      pending.then(clear, clear);
    }
    return pendingDeviceRegistration;
  }
  function selectedTopics() {
    if (!dialogBody) return state.topics.slice();
    return Array.from(dialogBody.querySelectorAll("input[data-reader-topic]:checked")).map(function (input) { return input.value; });
  }
  function validTopics(value) {
    return Array.isArray(value) ? value.filter(function (topic) { return topic === "review" || topic === "lecture"; }) : ["review", "lecture"];
  }
  function subscriptionButtonLabel(element) {
    if (element.dataset.readerHubHeader === "true") {
      var fullLabel = english ? "Alerts" : "알림 설정";
      var symbol = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      symbol.setAttribute("viewBox", "0 0 24 24");
      symbol.setAttribute("width", "21");
      symbol.setAttribute("height", "21");
      symbol.setAttribute("fill", "none");
      symbol.setAttribute("stroke", "currentColor");
      symbol.setAttribute("stroke-width", "1.6");
      symbol.setAttribute("stroke-linecap", "round");
      symbol.setAttribute("stroke-linejoin", "round");
      symbol.setAttribute("aria-hidden", "true");
      symbol.setAttribute("focusable", "false");
      var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", "M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4");
      symbol.appendChild(path);
      element.replaceChildren(symbol);
      element.setAttribute("aria-label", fullLabel);
      element.setAttribute("title", fullLabel);
    } else element.textContent = subscribed() ? text.settings : text.open;
    element.dataset.subscribed = subscribed() ? "true" : "false";
  }
  function updateButtons() {
    subscriptionButtons.forEach(subscriptionButtonLabel);
    likeButtons.forEach(function (element) {
      element.disabled = state.likeBusy;
      element.setAttribute("aria-busy", state.likeBusy ? "true" : "false");
      element.setAttribute("aria-pressed", state.liked ? "true" : "false");
      element.setAttribute("aria-label", state.liked ? text.unlike : text.like);
      element.textContent = (state.liked ? "♥ " : "♡ ") + text.like + " " + (state.count === null ? "—" : new Intl.NumberFormat(english ? "en-US" : "ko-KR").format(state.count));
    });
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
    articleStatuses.forEach(function (element) {
      element.dataset.readerStatusAction = retryAction || "";
      element.replaceChildren(document.createTextNode(message));
      if (retryAction) element.appendChild(button(retryAction === "copy" ? text.copy : text.retry, retryAction));
      if (url) {
        var input = node("input", "atr-reader-copy-url");
        input.type = "text"; input.value = url; input.readOnly = true;
        input.setAttribute("aria-label", text.copy);
        input.addEventListener("focus", function () { input.select(); });
        element.appendChild(input);
      }
    });
  }
  function addSubscribeButton(target) {
    var element = button(text.open, "open");
    element.classList.add("atr-reader-header-button");
    element.setAttribute("aria-haspopup", "dialog");
    element.setAttribute("aria-controls", "atr-reader-dialog");
    element.setAttribute("aria-expanded", "false");
    if (!article && /(?:^|\s)hub-page(?:\s|$)/.test(String(document.body && document.body.className || ""))) element.dataset.readerHubHeader = "true";
    subscriptionButtonLabel(element);
    subscriptionButtons.push(element);
    target.appendChild(element);
    return element;
  }
  function layoutChildren(element) {
    try { return element && typeof window.getComputedStyle === "function" && /^(?:inline-)?(?:grid|flex)$/.test(window.getComputedStyle(element).display); }
    catch (_) { return false; }
  }
  function mount() {
    if (article) {
      var articleElement = document.querySelector("main article") || document.querySelector("article:not(.review-card)") || document.querySelector("main");
      if (articleElement) {
        var actions = node("section", "atr-reader-actions");
        actions.setAttribute("aria-label", text.actions);
        likeButton = button(text.like + " —", "like");
        likeButtons.push(likeButton);
        likeButton.setAttribute("aria-pressed", "false");
        actions.appendChild(likeButton);
        actions.appendChild(button(text.share, "share"));
        actions.appendChild(button(text.copy, "copy"));
        addSubscribeButton(actions);
        mountMetrics(actions);
        articleStatus = node("p", "atr-reader-status");
        articleStatus.setAttribute("role", "status");
        articleStatus.setAttribute("aria-live", "polite");
        articleStatuses.push(articleStatus);
        actions.appendChild(articleStatus);
        if (articleElement.tagName === "MAIN" || layoutChildren(articleElement.parentElement)) articleElement.appendChild(actions);
        else articleElement.insertAdjacentElement("afterend", actions);
        actions.addEventListener("click", handleAction);
        var topActions = node("div", "atr-reader-actions atr-reader-actions-top");
        topActions.setAttribute("aria-label", text.actions);
        metricsField(topActions, "articleOpens", english ? "Views" : "조회");
        var topLike = button(text.like + " —", "like"); likeButtons.push(topLike); topActions.appendChild(topLike);
        topActions.appendChild(button(text.share, "share"));
        var topStatus = node("p", "atr-reader-status"); topStatus.setAttribute("aria-live", "off");
        articleStatuses.push(topStatus); topActions.appendChild(topStatus);
        var headline = (typeof articleElement.querySelector === "function" ? articleElement.querySelector("h1") : null) || document.querySelector("h1");
        if (headline) {
          var anchor = headline;
          while (anchor.parentElement && anchor.parentElement.tagName !== "BODY" && layoutChildren(anchor.parentElement)) anchor = anchor.parentElement;
          anchor.insertAdjacentElement("afterend", topActions);
        } else articleElement.insertAdjacentElement("afterbegin", topActions);
        topActions.addEventListener("click", handleAction);
      }
      var articleHeader = document.querySelector(".topbar-links") || document.querySelector(".topline-actions") || document.querySelector("body > header .topbar") || document.querySelector("body > header");
      if (articleHeader) {
        articleHeader.classList.add("atr-reader-topbar");
        addSubscribeButton(articleHeader).addEventListener("click", handleAction);
      }
    } else {
      var topbar = document.querySelector(".topbar-links") || document.querySelector(".topline-actions") || document.querySelector(".topbar nav") || document.querySelector("header nav") || document.querySelector(".topbar") || document.querySelector("header");
      if (topbar) { topbar.classList.add("atr-reader-topbar"); addSubscribeButton(topbar).addEventListener("click", handleAction); }
      mountMetrics(null);
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
      if (event.target.dataset && event.target.dataset.readerGuide === "device" && ["iphone", "mac-chrome", "mac-safari", "other"].indexOf(event.target.value) !== -1) {
        state.guideDevice = event.target.value;
        state.guideOpen = true;
        renderDialog();
      }
    });
    dialog.addEventListener("close", function () { restorePage(); });
    dialog.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && typeof dialog.close !== "function") { event.preventDefault(); closeDialog(); }
      if (event.key !== "Tab") return;
      var focusable = Array.from(dialog.querySelectorAll("button:not(:disabled),input:not(:disabled),select:not(:disabled),summary,a[href]")).filter(function (element) {
        return typeof element.getClientRects !== "function" || element.getClientRects().length > 0;
      });
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
    void refreshNotificationState(true);
  }
  function renderDialog() {
    if (!dialog) return;
    var focused = document.activeElement && document.activeElement.dataset && document.activeElement.dataset.readerAction;
    var focusedTopic = document.activeElement && document.activeElement.dataset && document.activeElement.dataset.readerTopic;
    var focusedGuide = document.activeElement && document.activeElement.dataset && document.activeElement.dataset.readerGuide;
    // Native toggle events are queued; preserve the actual disclosure state now.
    if (currentGuide) state.guideOpen = currentGuide.open;
    currentGuide = null;
    recentHeading = null;
    dialogBody.replaceChildren();
    dialogBody.setAttribute("aria-busy", state.busy || state.preparing ? "true" : "false");
    dialogHeading.textContent = text.title;
    setFeedback(state.feedback, state.feedbackError);
    if (isIOS() && !standalone()) {
      dialogHeading.textContent = text.installTitle;
      dialogBody.appendChild(node("p", "", text.installIntro));
      appendRecentNotifications();
      appendGuide(true);
      dialogBody.appendChild(button(text.close, "close"));
    } else if (!supported()) {
      dialogBody.appendChild(node("p", "", text.unsupported));
    } else if (permission() === "denied") {
      dialogBody.appendChild(node("p", "", isIOS() ? text.denied : text.deniedOther));
      dialogBody.appendChild(button(text.recheck, "recheck"));
      if (state.serverSubscription || state.localSubscription || state.pendingServerDelete) dialogBody.appendChild(button(text.unsubscribe, "unsubscribe"));
    } else {
      if (isIOS() && standalone()) dialogBody.appendChild(node("p", "atr-reader-note", guideText.iphoneReady));
      else if (deviceGuide() === "mac-chrome" || deviceGuide() === "mac-safari") dialogBody.appendChild(node("p", "atr-reader-note", standalone() ? guideText.macReady : guideText.macOptional));
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
    if (!(isIOS() && !standalone())) { appendRecentNotifications(); appendGuide(false); }
    if ((focused || focusedTopic || focusedGuide) && dialog.open) {
      var restore = focused ? Array.from(dialog.querySelectorAll("[data-reader-action]")).find(function (element) { return element.dataset.readerAction === focused; })
        : focusedTopic ? Array.from(dialog.querySelectorAll("[data-reader-topic]")).find(function (element) { return element.dataset.readerTopic === focusedTopic; })
        : Array.from(dialog.querySelectorAll("[data-reader-guide]")).find(function (element) { return element.dataset.readerGuide === focusedGuide; });
      if (restore && !restore.disabled) restore.focus({ preventScroll: true });
      else if (focused === "recent-more" && recentHeading) recentHeading.focus({ preventScroll: true });
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
      registration = withDeadline(Promise.resolve().then(function () { return navigator.serviceWorker.register(scope + "sw.js", { scope: scope, updateViaCache: "none" }); }), 25000, "push_timeout").then(function (registered) {
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
      }).then(function (registered) { void refreshNotificationState(true); return browserSubscription(registered); })
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
    try { granted = permissionFromGesture(); }
    catch (_) { setFeedback(text.failed, true); return; }
    state.busy = true;
    renderDialog();
    try {
      if (await withDeadline(granted, 30000, "permission_timeout") !== "granted") { setFeedback(text.installLater, false); return; }
      await ensureDevice();
      var subscription = await browserSubscription(state.registration);
      if (!subscription) subscription = await createBrowserSubscription(state.registration);
      state.localSubscription = subscription;
      var result = await request("/v1/subscription", "PUT", { subscription: subscription.toJSON(), topics: topics });
      state.serverSubscription = result.subscription || subscription.toJSON();
      state.pendingServerDelete = false;
      setFeedback(text.enabled, false);
      void refreshNotificationState(true);
      void refreshMetrics(true);
    } catch (error) { setFeedback(error.code === "permission_timeout" ? text.permissionTimeout : error.code === "push_timeout" ? text.pushTimeout : error.code === "http_401" ? text.cookieFailed : text.failed, true); }
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
      void refreshMetrics(true);
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
      void refreshMetrics(true);
    } catch (_) { /* No HTTP failure, including a missing session cookie, confirms server removal. */ }
    try {
      if (state.localSubscription) browserRemoved = await withDeadline(state.localSubscription.unsubscribe(), 25000, "push_timeout");
      if (browserRemoved) state.localSubscription = null;
    } catch (_) { /* Keep a retry control when browser removal fails. */ }
    state.pendingServerDelete = !serverRemoved;
    state.busy = false;
    setFeedback(serverRemoved && browserRemoved ? text.disabled : browserRemoved ? text.partialOff : text.failed, !(serverRemoved && browserRemoved));
    updateButtons();
    renderDialog();
  }
  async function loadLikes() {
    if (!article || !likeButton || state.likeBusy) return;
    var revision = likeRevision;
    try {
      var result = await request("/v1/articles/" + encodeURIComponent(article.id) + "/like");
      if (revision !== likeRevision || state.likeBusy) return;
      validateLike(result);
      state.count = result.count;
      state.liked = result.liked;
      updateButtons();
      if (articleStatus && articleStatus.dataset.readerStatusAction === "load-likes") articleMessage("");
    } catch (_) { if (revision === likeRevision) articleMessage(text.likeLoadFailed, "load-likes"); }
  }
  function validateLike(result, desired) {
    if (!result || result.ok !== true || typeof result.liked !== "boolean" || typeof result.count !== "number"
      || !Number.isSafeInteger(result.count) || result.count < 0 || (desired !== undefined && result.liked !== desired)) throw apiError("invalid_like_response");
  }
  async function persistLike(desired, active) {
    await ensureDevice();
    if (!active()) throw apiError("like_expired");
    if (pendingLikeWrite) {
      var previous = pendingLikeWrite;
      if (previous.desired === desired) return previous.promise;
      try { await previous.promise; } catch (_) { /* Serialize a changed intent after an ambiguous earlier write. */ }
      if (!active()) throw apiError("like_expired");
    }
    var pending = { desired: desired, promise: request("/v1/articles/" + encodeURIComponent(article.id) + "/like", "PUT", { liked: desired }) };
    pendingLikeWrite = pending;
    function clear() { if (pendingLikeWrite === pending) pendingLikeWrite = null; }
    pending.promise.then(clear, clear);
    return pending.promise;
  }
  async function like(retry) {
    if (!article || state.likeBusy) return;
    var previous = { liked: state.liked, count: state.count };
    var desired = retry === true && typeof state.likeRetryDesired === "boolean" ? state.likeRetryDesired : !previous.liked;
    var active = true;
    likeRevision += 1;
    state.likeBusy = true;
    state.likeRetryDesired = null;
    state.liked = desired;
    var optimisticCount = typeof previous.count === "number" ? Math.max(0, previous.count + Number(desired) - Number(previous.liked)) : null;
    state.count = Number.isSafeInteger(optimisticCount) ? optimisticCount : null;
    updateButtons();
    articleMessage(text.likeSaving);
    try {
      var result = await withDeadline(persistLike(desired, function () { return active; }), 12000, "like_timeout");
      validateLike(result, desired);
      state.count = result.count;
      state.liked = result.liked;
      articleMessage(state.liked ? text.likedSaved : text.unlikedSaved);
    } catch (error) {
      state.liked = previous.liked;
      state.count = previous.count;
      state.likeRetryDesired = desired;
      articleMessage(error.code === "http_401" ? text.cookieFailed : text.likeFailed, "retry-like");
    } finally { active = false; state.likeBusy = false; updateButtons(); }
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
      void recordMetrics("copy");
    } catch (_) { articleMessage(text.copyFailed, "copy", url); }
  }
  async function share() {
    if (typeof navigator.share !== "function") { await copyLink(); return; }
    try { await navigator.share({ title: String(article.title || document.title), url: shareURL() }); void recordMetrics("share"); }
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
  function offerInstall(event) {
    if (!event || typeof event.prompt !== "function" || standalone() || installedInSession) return;
    if (typeof event.preventDefault === "function") event.preventDefault();
    installPrompt = event;
    if (dialog && dialog.open) renderDialog();
  }
  function installedApp() {
    installedInSession = true;
    installPrompt = null;
    if (dialog && dialog.open) renderDialog();
  }
  async function installFromGesture() {
    if (!installPrompt || standalone() || installedInSession || state.installBusy) return;
    var offered = installPrompt;
    installPrompt = null;
    state.installBusy = true;
    try {
      // Only the explicit install button may open the browser's real prompt.
      var opening = offered.prompt();
      renderDialog();
      var choice = await withDeadline(Promise.resolve(opening).then(function () { return offered.userChoice || null; }), 30000, "install_timeout");
      setFeedback(choice && choice.outcome === "accepted" ? guideText.installAccepted : guideText.installOptional, false);
    } catch (_) { setFeedback(guideText.installFailed, true); }
    finally { state.installBusy = false; renderDialog(); }
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
    else if (action === "retry-like") void like(true);
    else if (action === "load-likes") void loadLikes();
    else if (action === "share") void share();
    else if (action === "copy") void copyLink();
    else if (action === "test") void testAlert();
    else if (action === "install-app") void installFromGesture();
    else if (action === "recent-more") { state.historyLimit = Math.min(20, state.historyLimit + 5); renderDialog(); }
  }
  mount();
  if (typeof window.addEventListener === "function") {
    window.addEventListener("beforeinstallprompt", offerInstall);
    window.addEventListener("appinstalled", installedApp);
    window.addEventListener("pageshow", function (event) { void refreshNotificationState(false); metricsPageShow(event); });
    window.addEventListener("focus", function () { void refreshNotificationState(false); });
    document.addEventListener("visibilitychange", function () { if (document.visibilityState === "visible") { void refreshNotificationState(false); startMetrics(); } });
    document.addEventListener("prerenderingchange", startMetrics);
    if ("serviceWorker" in navigator && typeof navigator.serviceWorker.addEventListener === "function") {
      navigator.serviceWorker.addEventListener("controllerchange", function () { void refreshNotificationState(true); });
      navigator.serviceWorker.addEventListener("message", notificationHint);
    }
  }
  void prepare();
  void loadLikes();
  startMetrics();
})();
