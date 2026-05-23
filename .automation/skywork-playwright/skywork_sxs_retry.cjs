const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const repoRoot = path.resolve(__dirname, "..", "..");
const playwrightRoot = path.join(repoRoot, ".automation", "notebooklm-playwright", "node_modules", "playwright");
const { chromium } = require(playwrightRoot);

if (!process.env.TOPIC_DIR) {
  throw new Error("TOPIC_DIR is required. Pass the topic package directory relative to the repo root or as an absolute path.");
}
const topicDir = path.isAbsolute(process.env.TOPIC_DIR)
  ? path.resolve(process.env.TOPIC_DIR)
  : path.resolve(repoRoot, process.env.TOPIC_DIR);
const topicSlug = path.basename(topicDir);
const profileDir = process.env.SKYWORK_PROFILE_DIR;
const chromePath = process.env.CHROME_EXECUTABLE_PATH || path.join(process.env.LOCALAPPDATA || "", "Google", "Chrome SxS", "Application", "chrome.exe");
const mode = process.env.SKYWORK_MODE || "probe";

if (!profileDir) {
  throw new Error("SKYWORK_PROFILE_DIR is required");
}
if (!fs.existsSync(chromePath)) {
  throw new Error(`Chrome executable not found: ${chromePath}`);
}
if (!fs.existsSync(profileDir)) {
  throw new Error(`Profile directory not found: ${profileDir}`);
}

const artifactsDir = path.join(topicDir, "artifacts");
const exportsDir = path.join(topicDir, "skywork_exports");
const inputsDir = path.join(topicDir, "skywork_inputs");
const notesDir = path.join(topicDir, "notes");
const reportsDir = path.join(topicDir, "reports");
const sourcesDir = path.join(topicDir, "sources");
fs.mkdirSync(artifactsDir, { recursive: true });
fs.mkdirSync(exportsDir, { recursive: true });
fs.mkdirSync(inputsDir, { recursive: true });

function existingFilesFromDir(dir, pattern) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir)
    .filter((name) => pattern.test(name))
    .map((name) => path.join(dir, name))
    .filter((file) => fs.existsSync(file));
}

function resolveFirstMatchingFile(dir, pattern, description) {
  const matches = existingFilesFromDir(dir, pattern);
  if (!matches.length) {
    throw new Error(`${description} not found in ${dir}`);
  }
  return matches[0];
}

function parseSourcePaths() {
  if (process.env.SKYWORK_SOURCE_PATHS) {
    return process.env.SKYWORK_SOURCE_PATHS
      .split(path.delimiter)
      .map((item) => item.trim())
      .filter(Boolean)
      .map((item) => path.isAbsolute(item) ? item : path.resolve(repoRoot, item))
      .filter((file) => fs.existsSync(file));
  }
  return [
    ...existingFilesFromDir(reportsDir, /\.md$/i),
    ...existingFilesFromDir(notesDir, /(sources|claim_audit|deepresearch_prompt).*\.md$/i),
    ...existingFilesFromDir(sourcesDir, /\.pdf$/i),
  ];
}

function allocTempScreenshot(name) {
  const proc = spawnSync("python", ["scripts/skywork_temp.py", "alloc", "--name", name], {
    cwd: repoRoot,
    encoding: "utf8",
  });
  if (proc.status === 0 && proc.stdout.trim()) {
    return proc.stdout.trim().split(/\r?\n/).pop();
  }
  return path.join(artifactsDir, name);
}

async function extractStatus(page, label) {
  await page.waitForTimeout(3500);
  const title = await page.title().catch(() => "");
  const url = page.url();
  const body = await page.locator("body").innerText({ timeout: 8000 }).catch(() => "");
  const screenshot = allocTempScreenshot(`${label}.png`);
  await page.screenshot({ path: screenshot, fullPage: true }).catch(() => {});
  const loginHints = /sign\s*in|log\s*in|로그인|continue with google|email|password/i.test(body + " " + title + " " + url);
  const creationHints = /ppt|presentation|slide|project|generate|create|시작|생성|새 프로젝트|프레젠테이션|슬라이드|파워포인트/i.test(body);
  const output = {
    label,
    title,
    url,
    loginHints,
    creationHints,
    screenshot,
    bodySnippet: body.replace(/\s+/g, " ").slice(0, 3000),
  };
  console.log(JSON.stringify(output, null, 2));
  return output;
}

async function clickByText(page, patterns, timeout = 2500) {
  for (const pattern of patterns) {
    const locator = page.getByText(pattern, { exact: false }).first();
    if (await locator.isVisible({ timeout }).catch(() => false)) {
      await locator.click();
      await page.waitForTimeout(2500);
      return String(pattern);
    }
  }
  return null;
}

async function openLoginDialog(page) {
  if (await page.locator('[role="dialog"], .el-overlay-dialog').first().isVisible({ timeout: 1500 }).catch(() => false)) {
    return true;
  }
  const loginButton = page.getByText(/^로그인$/).last();
  if (await loginButton.isVisible({ timeout: 3000 }).catch(() => false)) {
    await loginButton.click();
    await page.waitForTimeout(2500);
    return true;
  }
  return false;
}

async function handleGoogleOAuth(context, page) {
  const deadline = Date.now() + 90000;
  let activePage = page;

  while (Date.now() < deadline) {
    let pages = [];
    try {
      pages = context.pages().filter((candidate) => !candidate.isClosed());
    } catch (err) {
      console.log(`OAUTH_CONTEXT_PAGES_FAILED=${err.message}`);
      return { loggedIn: false, activePage };
    }
    activePage = pages[pages.length - 1] || page;
    for (const candidate of pages) {
      if (candidate.isClosed()) continue;
      const url = candidate.url();
      if (/accounts\.google\.com|google\.com\/signin|login\.live\.com|login\.microsoftonline\.com|login\.microsoft\.com/i.test(url)) {
        activePage = candidate;
        const account = candidate.locator("[data-identifier]").first();
        if (await account.isVisible({ timeout: 1500 }).catch(() => false)) {
          await account.click();
          await candidate.waitForTimeout(3000).catch(() => {});
        }
        if (candidate.isClosed()) continue;
        const signedInTileText = candidate.getByText(/로그인되어 있음|signed in/i).first();
        if (await signedInTileText.isVisible({ timeout: 1000 }).catch(() => false)) {
          await signedInTileText.click();
          await candidate.waitForTimeout(4000).catch(() => {});
        }
        if (candidate.isClosed()) continue;
        const microsoftTile = candidate.locator('[role="button"]').filter({ hasText: /@|outlook|hotmail|live|angpa|jung/i }).first();
        if (await microsoftTile.isVisible({ timeout: 1000 }).catch(() => false)) {
          await microsoftTile.click();
          await candidate.waitForTimeout(3000).catch(() => {});
        }
        if (candidate.isClosed()) continue;
        const continueClicked = await clickByText(candidate, [/Continue/i, /계속/i, /허용/i, /Allow/i, /다음/i, /예/i, /Yes/i, /동의/i], 1200).catch(() => null);
        if (continueClicked) {
          await candidate.waitForTimeout(4000).catch(() => {});
        }
        if (candidate.isClosed()) continue;
        const password = candidate.locator('input[type="password"]').first();
        const bodyText = await candidate.locator("body").innerText({ timeout: 2000 }).catch(() => "");
        if (!/로그인되어 있음|signed in/i.test(bodyText) && await password.isVisible({ timeout: 800 }).catch(() => false)) {
          console.log("LOGIN_NEEDS_MANUAL=password_prompt");
          return { loggedIn: false, activePage: candidate };
        }
      }
    }

    const skyworkPages = context.pages().filter((candidate) => !candidate.isClosed() && /skywork\.ai/i.test(candidate.url()));
    if (skyworkPages.length) {
      activePage = skyworkPages[skyworkPages.length - 1];
      const dialogVisible = await activePage.locator('[role="dialog"], .el-overlay-dialog').first().isVisible({ timeout: 1000 }).catch(() => false);
      const text = await activePage.locator("body").innerText({ timeout: 4000 }).catch(() => "");
      const stillLoggedOut = /로그인\/회원가입|Microsoft 계정으로 로그인|이메일로 계속/i.test(text) || dialogVisible;
      if (!stillLoggedOut) {
        return { loggedIn: true, activePage };
      }
    }
    await activePage.waitForTimeout(3000).catch(() => {});
  }

  return { loggedIn: false, activePage };
}

async function clickExistingSkyworkAccountTile(page) {
  const started = Date.now();
  while (Date.now() - started < 12000) {
    const box = await page.evaluate(() => {
      const matcher = /Hyun-Jung|angpangmokjang@gmail\.com/i;
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let node = walker.nextNode();
      while (node) {
        if (matcher.test(node.nodeValue || "")) {
          let el = node.parentElement;
          for (let i = 0; i < 8 && el; i += 1, el = el.parentElement) {
            const rect = el.getBoundingClientRect();
            if (rect.width > 250 && rect.width < 520 && rect.height > 32 && rect.height < 90) {
              return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
            }
          }
        }
        node = walker.nextNode();
      }
      return null;
    }).catch(() => null);
    if (box) {
      await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
      await page.waitForTimeout(5000).catch(() => {});
      console.log(`LOGIN_ACCOUNT_TILE_CLICKED=${Math.round(box.x + box.width / 2)},${Math.round(box.y + box.height / 2)}`);
      return true;
    }
    await page.waitForTimeout(1000).catch(() => {});
  }
  return false;
}

async function isSkyworkLoggedIn(page) {
  const text = await page.locator("body").innerText({ timeout: 5000 }).catch(() => "");
  if (/Microsoft 계정으로 로그인|Facebook으로 로그인|GitHub로 로그인|이메일로 계속|로그인\/회원가입|회원가입 시 당사의 서비스 약관/i.test(text)) {
    return false;
  }
  return /Signed in|멤버십 보상|\bBasic\b|내 템플릿|모두 보기|프로젝트\s+팔란티어|11,620/i.test(text);
}

async function waitForManualSkyworkLogin(context, page, maxMs) {
  console.log(`MANUAL_LOGIN_WAIT_STARTED_MS=${maxMs}`);
  await openLoginDialog(page).catch(() => {});
  const started = Date.now();
  let lastCapture = 0;
  while (Date.now() - started < maxMs) {
    const skyworkPages = context.pages().filter((candidate) => /skywork\.ai/i.test(candidate.url()));
    for (const candidate of skyworkPages.length ? skyworkPages : [page]) {
      if (await isSkyworkLoggedIn(candidate).catch(() => false)) {
        console.log(`MANUAL_LOGIN_DETECTED=${candidate.url()}`);
        return candidate;
      }
    }
    const elapsed = Date.now() - started;
    if (elapsed - lastCapture > 60000 || lastCapture === 0) {
      lastCapture = elapsed;
      const active = skyworkPages[skyworkPages.length - 1] || page;
      await extractStatus(active, `skywork_manual_login_wait_${Math.round(elapsed / 1000)}s`).catch(() => {});
      console.log(`MANUAL_LOGIN_WAIT_ELAPSED_SECONDS=${Math.round(elapsed / 1000)}`);
    }
    await page.waitForTimeout(5000).catch(() => {});
  }
  return null;
}

async function ensureGoogleLogin(context, page) {
  if (await isSkyworkLoggedIn(page)) {
    return { loggedIn: true, page };
  }
  await openLoginDialog(page);
  await extractStatus(page, "skywork_sxs_login_dialog");
  if (await isSkyworkLoggedIn(page)) {
    return { loggedIn: true, page };
  }
  const accountTileClicked = await clickExistingSkyworkAccountTile(page).catch((err) => {
    console.log(`LOGIN_ACCOUNT_TILE_FAILED=${err.message}`);
    return false;
  });
  if (accountTileClicked) {
    const accountResult = await handleGoogleOAuth(context, page).catch((err) => {
      console.log(`LOGIN_ACCOUNT_TILE_OAUTH_FAILED=${err.message}`);
      return { loggedIn: false, activePage: page };
    });
    await extractStatus(accountResult.activePage || page, "skywork_sxs_after_account_tile_login").catch(() => {});
    if (accountResult.loggedIn || await isSkyworkLoggedIn(accountResult.activePage || page).catch(() => false)) {
      return { loggedIn: true, page: accountResult.activePage || page };
    }
  }
  const provider = process.env.SKYWORK_LOGIN_PROVIDER || "google";
  const accountLogin = provider === "microsoft"
    ? page.getByText(/Microsoft 계정으로 로그인/i).first()
    : page.getByText(/로 로그인/i).first();
  let popupPromise = null;
  if (await accountLogin.isVisible({ timeout: 5000 }).catch(() => false)) {
    popupPromise = context.waitForEvent("page", { timeout: 10000 }).catch(() => null);
    await accountLogin.click();
  } else {
    let box = null;
    for (const selector of [".el-dialog", '[role="dialog"]', ".el-overlay-dialog"]) {
      const candidate = page.locator(selector).first();
      if (await candidate.isVisible({ timeout: 1000 }).catch(() => false)) {
        const candidateBox = await candidate.boundingBox().catch(() => null);
        if (candidateBox && candidateBox.width > 300 && candidateBox.height > 300 && candidateBox.height < 800) {
          box = candidateBox;
          break;
        }
      }
    }
    if (!box) {
      const viewport = page.viewportSize() || { width: 1440, height: 1000 };
      box = { x: viewport.width / 2 - 260, y: 260, width: 520, height: 580 };
    }
    popupPromise = context.waitForEvent("page", { timeout: 10000 }).catch(() => null);
    const yOffset = provider === "microsoft" ? 192 : 140;
    await page.mouse.click(box.x + box.width / 2, box.y + yOffset);
    console.log(`LOGIN_COORDINATE_FALLBACK=${provider}:${Math.round(box.x + box.width / 2)},${Math.round(box.y + yOffset)}`);
  }
  const popup = await popupPromise;
  if (popup) {
    await popup.waitForLoadState("domcontentloaded", { timeout: 30000 }).catch(() => {});
  }
  await page.waitForTimeout(5000);
  const result = await handleGoogleOAuth(context, popup || page);
  await extractStatus(result.activePage, "skywork_sxs_after_google_login");
  return { loggedIn: result.loggedIn, page: result.activePage };
}

async function uploadTemplate(page) {
  const templatePath = process.env.SKYWORK_TEMPLATE_PATH || path.join(inputsDir, "LGD_Template.pptx");
  if (!fs.existsSync(templatePath)) {
    throw new Error(`Template file not found: ${templatePath}`);
  }

  const uploadText = page.getByText(/PPTX 파일 업로드/i).first();
  if (await uploadText.isVisible({ timeout: 3000 }).catch(() => false)) {
    const cardBox = await uploadText.evaluate((el) => {
      let node = el;
      for (let i = 0; i < 8 && node; i += 1, node = node.parentElement) {
        const rect = node.getBoundingClientRect();
        if (rect.width > 120 && rect.height > 80) {
          return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
        }
      }
      const rect = el.getBoundingClientRect();
      return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
    });
    try {
      const [chooser] = await Promise.all([
        page.waitForEvent("filechooser", { timeout: 7000 }),
        page.mouse.click(cardBox.x + cardBox.width / 2, cardBox.y + cardBox.height / 2),
      ]);
      await chooser.setFiles(templatePath);
      await page.waitForTimeout(6000);
      await handleUploadDialogs(page);
      await closePptxUploadDialog(page);
      console.log(`TEMPLATE_UPLOADED=filechooser:${templatePath}`);
      return true;
    } catch (err) {
      console.log(`TEMPLATE_FILECHOOSER_FAILED=${err.message}`);
    }
  }

  const fileInput = page.locator('input[type="file"]').first();
  if (await fileInput.count()) {
    await fileInput.setInputFiles(templatePath);
    await page.waitForTimeout(6000);
    await handleUploadDialogs(page);
    await closePptxUploadDialog(page);
    console.log(`TEMPLATE_UPLOADED=input:${templatePath}`);
    return true;
  }
  return false;
}

async function closePptxUploadDialog(page) {
  const body = await page.locator("body").innerText({ timeout: 3000 }).catch(() => "");
  if (!/PPTX 파일 업로드|클릭하여 파일 업로드|\.pptx 최대/i.test(body)) {
    return false;
  }
  const closeCandidates = [
    page.locator(".el-dialog__headerbtn").last(),
    page.locator("[aria-label='Close'], [aria-label='닫기']").last(),
    page.locator(".el-overlay-dialog button").filter({ hasText: /^$/ }).last(),
  ];
  for (const closeButton of closeCandidates) {
    if (await closeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await closeButton.click({ force: true }).catch(() => {});
      await page.waitForTimeout(2000);
      console.log("UPLOAD_DIALOG_ACTION=close_pptx_upload_dialog");
      return true;
    }
  }
  const dialog = page.locator(".el-dialog, [role='dialog']").last();
  const box = await dialog.boundingBox().catch(() => null);
  if (box && box.width > 300 && box.height > 200) {
    await page.mouse.click(box.x + box.width - 34, box.y + 36);
    await page.waitForTimeout(2000);
    console.log(`UPLOAD_DIALOG_ACTION=close_pptx_upload_dialog_coordinate:${Math.round(box.x + box.width - 34)},${Math.round(box.y + 36)}`);
    return true;
  }
  await page.keyboard.press("Escape").catch(() => {});
  await page.waitForTimeout(1200);
  console.log("UPLOAD_DIALOG_ACTION=close_pptx_upload_dialog_escape");
  return true;
}

async function closeBlockingOverlays(page) {
  for (let i = 0; i < 5; i += 1) {
    const body = await page.locator("body").innerText({ timeout: 3000 }).catch(() => "");
    if (!/풀옵션|업그레이드 보기|SkyClaw 설정\s*1\.|알림\s+다운로드|더 이상 메시지가 없습니다|Claw🦞|로그인 후 더 즐거움/i.test(body)) {
      return false;
    }
    let clicked = false;
    for (const locator of [
      page.locator(".el-dialog__headerbtn").last(),
      page.locator("[aria-label='Close'], [aria-label='닫기']").last(),
      page.locator(".el-drawer__close-btn, .el-notification__closeBtn").last(),
    ]) {
      if (await locator.isVisible({ timeout: 800 }).catch(() => false)) {
        await locator.click({ force: true }).catch(() => {});
        await page.waitForTimeout(1200);
        clicked = true;
        console.log("BLOCKING_OVERLAY_ACTION=close_selector");
        break;
      }
    }
    const dialogs = await page.locator(".el-dialog, [role='dialog']").elementHandles().catch(() => []);
    for (const dialog of dialogs.slice(-2)) {
      const box = await dialog.boundingBox().catch(() => null);
      if (box && box.width > 360 && box.height > 240) {
        await page.mouse.click(box.x + box.width - 45, box.y + 48).catch(() => {});
        await page.waitForTimeout(1200);
        clicked = true;
        console.log(`BLOCKING_OVERLAY_ACTION=close_dialog_coordinate:${Math.round(box.x + box.width - 45)},${Math.round(box.y + 48)}`);
      }
    }
    for (const [x, y] of [[1224, 227], [1372, 82], [1354, 116], [1396, 805]]) {
      await page.mouse.click(x, y).catch(() => {});
      await page.waitForTimeout(600);
    }
    await page.keyboard.press("Escape").catch(() => {});
    await page.waitForTimeout(1000);
    if (!clicked) {
      return false;
    }
  }
  return true;
}

async function handleUploadDialogs(page) {
  await closeBlockingOverlays(page).catch(() => {});
  for (let i = 0; i < 6; i += 1) {
    const body = await page.locator("body").innerText({ timeout: 3000 }).catch(() => "");
    if (/동일한 파일이 감지되었습니다|직접 사용/i.test(body)) {
      const useDirect = page.getByRole("button", { name: /직접 사용|Use directly/i }).first();
      if (await useDirect.isVisible({ timeout: 2000 }).catch(() => false)) {
        await useDirect.click({ force: true });
        await page.waitForTimeout(3000);
        console.log("UPLOAD_DIALOG_ACTION=direct_use");
        continue;
      }
    }
    if (/풀옵션|업그레이드 보기/i.test(body)) {
      const closeButton = page.locator(".el-dialog__headerbtn, [aria-label='Close'], [aria-label='닫기']").last();
      if (await closeButton.isVisible({ timeout: 1500 }).catch(() => false)) {
        await closeButton.click({ force: true }).catch(() => {});
        await page.waitForTimeout(2000);
        console.log("UPLOAD_DIALOG_ACTION=close_overlay");
        continue;
      }
      const dialog = page.locator(".el-dialog, [role='dialog']").last();
      const box = await dialog.boundingBox().catch(() => null);
      if (box && box.width > 400 && box.height > 300) {
        await page.mouse.click(box.x + box.width - 45, box.y + 48);
        await page.waitForTimeout(2000);
        console.log(`UPLOAD_DIALOG_ACTION=close_overlay_coordinate:${Math.round(box.x + box.width - 45)},${Math.round(box.y + 48)}`);
        continue;
      }
      for (const [x, y] of [[1226, 226], [1220, 226], [1226, 232]]) {
        await page.mouse.click(x, y).catch(() => {});
        await page.waitForTimeout(1200);
        const nextBody = await page.locator("body").innerText({ timeout: 2000 }).catch(() => "");
        if (!/풀옵션|업그레이드 보기/i.test(nextBody)) {
          console.log(`UPLOAD_DIALOG_ACTION=close_overlay_fixed:${x},${y}`);
          break;
        }
      }
      const afterFixed = await page.locator("body").innerText({ timeout: 2000 }).catch(() => "");
      if (!/풀옵션|업그레이드 보기/i.test(afterFixed)) {
        continue;
      }
      await page.keyboard.press("Escape").catch(() => {});
      await page.waitForTimeout(1500);
      continue;
    }
    break;
  }
}

async function ensurePptSkill(page) {
  const currentBody = await page.locator("body").innerText({ timeout: 5000 }).catch(() => "");
  if (/스토리를 전문\s*슬라이드로 변환|PPTX 파일 업로드/i.test(currentBody)) {
    await closeBlockingOverlays(page).catch(() => {});
    return true;
  }
  for (let attempt = 0; attempt < 3; attempt += 1) {
    await closeBlockingOverlays(page).catch(() => {});
    await page.goto("https://skywork.ai/?skill_id=102", { waitUntil: "domcontentloaded", timeout: 60000 }).catch((err) => {
      console.log(`PPT_SKILL_GOTO_FAILED=${err.message}`);
    });
    await page.waitForTimeout(5500);
    await closeBlockingOverlays(page).catch(() => {});
    let body = await page.locator("body").innerText({ timeout: 5000 }).catch(() => "");
    if (/스토리를 전문\s*슬라이드로 변환|PPTX 파일 업로드/i.test(body)) {
      return true;
    }
    const pptClicked = await clickPptTool(page).catch(() => null);
    if (pptClicked) {
      await page.waitForTimeout(5500);
      await closeBlockingOverlays(page).catch(() => {});
    }
    body = await page.locator("body").innerText({ timeout: 5000 }).catch(() => "");
    if (/스토리를 전문\s*슬라이드로 변환|PPTX 파일 업로드/i.test(body)) {
      return true;
    }
  }
  return false;
}

async function clickPptTool(page) {
  const matches = await page.locator("text=파워포인트").elementHandles();
  for (const handle of matches) {
    const box = await handle.boundingBox().catch(() => null);
    if (!box) continue;
    if (box.x > 300 && box.x < 1200 && box.y > 180 && box.y < 850) {
      await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
      console.log(`PPT_TOOL_CLICKED=${Math.round(box.x + box.width / 2)},${Math.round(box.y + box.height / 2)}`);
      return "파워포인트";
    }
  }
  const fallback = page.getByText(/파워포인트|PowerPoint|PPT/i).first();
  if (await fallback.isVisible({ timeout: 2000 }).catch(() => false)) {
    await fallback.click({ force: true });
    console.log("PPT_TOOL_CLICKED=fallback");
    return "fallback";
  }
  return null;
}

async function uploadSourceFiles(page) {
  const sourceFiles = parseSourcePaths();

  if (!sourceFiles.length) {
    console.log("SOURCE_UPLOAD_SKIPPED=no_files");
    return 0;
  }

  const fileInput = page.locator('input[type="file"]').first();
  if (await fileInput.count()) {
    await fileInput.setInputFiles(sourceFiles);
    await page.waitForTimeout(7000);
    await handleUploadDialogs(page);
    console.log(`SOURCE_FILES_UPLOADED=${sourceFiles.length}`);
    return sourceFiles.length;
  }

  const plusButton = page.locator("text=+").first();
  if (await plusButton.isVisible({ timeout: 2000 }).catch(() => false)) {
    try {
      const [chooser] = await Promise.all([
        page.waitForEvent("filechooser", { timeout: 7000 }),
        plusButton.click({ force: true }),
      ]);
      await chooser.setFiles(sourceFiles);
      await page.waitForTimeout(7000);
      await handleUploadDialogs(page);
      console.log(`SOURCE_FILES_UPLOADED=filechooser:${sourceFiles.length}`);
      return sourceFiles.length;
    } catch (err) {
      console.log(`SOURCE_UPLOAD_FILECHOOSER_FAILED=${err.message}`);
    }
  }
  console.log("SOURCE_UPLOAD_FAILED=no_input");
  return 0;
}

async function fillPrompt(page) {
  const promptPath = process.env.SKYWORK_PROMPT_PATH
    ? (path.isAbsolute(process.env.SKYWORK_PROMPT_PATH) ? process.env.SKYWORK_PROMPT_PATH : path.resolve(repoRoot, process.env.SKYWORK_PROMPT_PATH))
    : resolveFirstMatchingFile(inputsDir, /skywork_prompt.*\.md$/i, "Skywork prompt packet");
  if (!fs.existsSync(promptPath)) {
    throw new Error(`Prompt file not found: ${promptPath}`);
  }
  const prompt = fs.readFileSync(promptPath, "utf8");
  await handleUploadDialogs(page).catch(() => {});
  const editor = page.locator('[contenteditable="true"]').first();
  await editor.click({ force: true }).catch(() => {});
  await page.keyboard.press("Control+A").catch(() => {});
  await page.keyboard.press("Backspace").catch(() => {});
  await editor.evaluate((el, value) => {
    el.focus();
    el.innerText = value;
    el.dispatchEvent(new InputEvent("input", { bubbles: true, data: value, inputType: "insertText" }));
  }, prompt);
  await page.waitForTimeout(1500);
  const length = await editor.innerText().then((text) => text.length).catch(() => 0);
  console.log(`PROMPT_FILLED_LENGTH=${length}`);
  return length;
}

async function clickSubmit(page) {
  await handleUploadDialogs(page).catch(() => {});
  for (const selector of [
    "footer .footer-right svg.cursor-pointer",
    ".footer-right svg.cursor-pointer",
    "svg.cursor-pointer",
    "button:has(svg)",
  ]) {
    const locator = page.locator(selector).last();
    if (await locator.isVisible({ timeout: 1500 }).catch(() => false)) {
      await locator.click({ force: true }).catch(async () => {
        const box = await locator.boundingBox().catch(() => null);
        if (box) await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
      });
      await page.waitForTimeout(5000);
      console.log(`SUBMIT_CLICKED_SELECTOR=${selector}`);
      return;
    }
  }
  const editor = page.locator('[contenteditable="true"]').first();
  const box = await editor.evaluate((el) => {
    let node = el;
    for (let i = 0; i < 8 && node; i += 1, node = node.parentElement) {
      const rect = node.getBoundingClientRect();
      if (rect.width > 500 && rect.height > 70) {
        return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
      }
    }
    const rect = el.getBoundingClientRect();
    return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
  });
  await page.mouse.click(box.x + box.width - 36, box.y + box.height - 31);
  await page.waitForTimeout(5000);
  console.log(`SUBMIT_CLICKED_AT=${Math.round(box.x + box.width - 36)},${Math.round(box.y + box.height - 31)}`);
}

async function writeAutomationStatus(label, status) {
  const statusPath = path.join(inputsDir, `${topicSlug}_skywork_automation_status.json`);
  const payload = {
    label,
    recordedAt: new Date().toISOString(),
    ...status,
  };
  fs.writeFileSync(statusPath, JSON.stringify(payload, null, 2), "utf8");
  console.log(`STATUS_WRITTEN=${statusPath}`);
}

async function waitForProjectReady(page, maxMs) {
  const started = Date.now();
  let lastCapture = 0;
  let status = null;
  while (Date.now() - started < maxMs) {
    await closeBlockingOverlays(page).catch(() => {});
    const body = await page.locator("body").innerText({ timeout: 10000 }).catch(() => "");
    const url = page.url();
    if (!/\/project\//.test(url) && process.env.SKYWORK_PROJECT_URL) {
      await page.goto(process.env.SKYWORK_PROJECT_URL, { waitUntil: "domcontentloaded", timeout: 60000 }).catch((err) => {
        console.log(`PROJECT_REOPEN_FAILED=${err.message}`);
      });
      await page.waitForTimeout(5000);
      continue;
    }
    const readyHints = /다운로드|Download|export|Export|내보내기|선택 다운로드 형식|성공적으로 생성|완성된 프레젠테이션/i.test(body);
    const progressHints = /생각 중|생성 중|분석 중|작성 중|processing|generating|progress|outline|슬라이드 생성/i.test(body);
    const completedHints = /성공적으로 생성|완성된 프레젠테이션/i.test(body);
    if (/\/project\//.test(url) && readyHints && (!progressHints || completedHints)) {
      status = await extractStatus(page, "skywork_project_ready");
      return status;
    }
    const elapsed = Date.now() - started;
    if (elapsed - lastCapture > 90000 || lastCapture === 0) {
      lastCapture = elapsed;
      status = await extractStatus(page, `skywork_generation_wait_${Math.round(elapsed / 1000)}s`).catch(() => null);
      console.log(`GENERATION_WAIT_ELAPSED_SECONDS=${Math.round(elapsed / 1000)} URL=${url}`);
    }
    await page.waitForTimeout(10000);
  }
  return status || await extractStatus(page, "skywork_project_wait_timeout").catch(() => null);
}

async function openDownloadDialog(page) {
  if (await page.getByRole("heading", { name: /선택 다운로드 형식|download format/i }).isVisible({ timeout: 1500 }).catch(() => false)) {
    return true;
  }
  const candidates = [
    page.locator(".download-container .cursor-pointer").first(),
    page.getByText(/다운로드|Download/i).first(),
    page.locator("[class*=download]").first(),
  ];
  for (const candidate of candidates) {
    if (await candidate.isVisible({ timeout: 2500 }).catch(() => false)) {
      await candidate.click({ force: true }).catch(async () => {
        const box = await candidate.boundingBox().catch(() => null);
        if (box) await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
      });
      await page.waitForTimeout(3000);
      if (await page.getByRole("heading", { name: /선택 다운로드 형식|download format/i }).isVisible({ timeout: 5000 }).catch(() => false)) {
        return true;
      }
    }
  }
  return false;
}

async function downloadFormat(page, format, targetName) {
  const dialogOpened = await openDownloadDialog(page);
  if (!dialogOpened) {
    throw new Error(`Download dialog did not open for ${format}`);
  }

  const downloadPromise = page.waitForEvent("download", { timeout: 240000 }).catch((err) => {
    console.log(`DOWNLOAD_EVENT_TIMEOUT_${format}=${err.message}`);
    return null;
  });
  const clicked = await page.evaluate((format) => {
    const normalize = (value) => (value || "").replace(/\s+/g, " ").trim();
    const isVisible = (el) => {
      if (!el || !(el instanceof HTMLElement)) return false;
      const style = window.getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return style.visibility !== "hidden" && style.display !== "none" && rect.width > 8 && rect.height > 8;
    };
    const center = (el) => {
      const rect = el.getBoundingClientRect();
      return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2, rect };
    };
    const formatPattern = new RegExp(`\\b${format}\\b`, "i");
    const labels = Array.from(document.querySelectorAll("body *"))
      .filter((el) => isVisible(el))
      .map((el) => ({ el, text: normalize(el.innerText || el.textContent) }))
      .filter((item) => item.text.length > 0 && item.text.length < 180 && formatPattern.test(item.text));
    const buttons = Array.from(document.querySelectorAll("button, [role='button'], .cursor-pointer"))
      .filter((el) => isVisible(el))
      .map((el) => ({
        el,
        text: normalize(el.innerText || el.textContent || el.getAttribute("aria-label") || ""),
        pos: center(el),
      }))
      .filter((item) => /다운로드|Download|내보내기|Export/i.test(item.text) || item.el.tagName.toLowerCase() === "button");

    let best = null;
    for (const label of labels) {
      const labelPos = center(label.el);
      for (const button of buttons) {
        const dy = Math.abs(button.pos.y - labelPos.y);
        const leftPenalty = button.pos.x < labelPos.x ? 800 : 0;
        const distance = dy + Math.abs(button.pos.x - labelPos.x) * 0.03 + leftPenalty;
        if (!best || distance < best.distance) {
          best = {
            distance,
            x: button.pos.x,
            y: button.pos.y,
            label: label.text.slice(0, 80),
            button: button.text.slice(0, 80),
          };
        }
      }
    }
    if (!best) return null;
    return best;
  }, format);
  if (clicked) {
    await page.mouse.click(clicked.x, clicked.y);
    console.log(`DOWNLOAD_BUTTON_SELECTED_${format}=${Math.round(clicked.x)},${Math.round(clicked.y)} label=${clicked.label} button=${clicked.button}`);
  } else {
    const fallbackButton = page.getByRole("button", { name: /다운로드|Download/i }).first();
    await fallbackButton.click({ force: true });
    console.log(`DOWNLOAD_BUTTON_SELECTED_${format}=fallback_first_button`);
  }
  await page.waitForTimeout(2000);
  const confirm = page.locator(".download-dialog-overlay button, .el-dialog button").filter({ hasText: /다운로드|확인|Download|OK/i }).first();
  if (await confirm.isVisible({ timeout: 3000 }).catch(() => false)) {
    await confirm.click({ force: true }).catch(() => {});
  }

  const download = await downloadPromise;
  if (!download) {
    throw new Error(`No download event captured for ${format}`);
  }
  const targetPath = path.join(exportsDir, targetName);
  await download.saveAs(targetPath);
  console.log(`DOWNLOADED_${format.toUpperCase()}=${targetPath}`);
  return targetPath;
}

async function downloadExports(page) {
  const pptxName = `${topicSlug}_skywork_v1.pptx`;
  const pdfName = `${topicSlug}_skywork_v1.pdf`;
  const pptxPath = await downloadFormat(page, "PPTX", pptxName);
  await page.waitForTimeout(3000);
  const pdfPath = await downloadFormat(page, "PDF", pdfName);
  return { pptxPath, pdfPath };
}

async function main() {
  const context = await chromium.launchPersistentContext(profileDir, {
    executablePath: chromePath,
    headless: false,
    acceptDownloads: true,
    downloadsPath: exportsDir,
    viewport: { width: 1440, height: 1000 },
    args: [
      "--disable-blink-features=AutomationControlled",
      "--disable-features=Translate",
      "--no-first-run",
      "--no-default-browser-check",
    ],
  });
  context.setDefaultTimeout(15000);

  let page = context.pages()[0] || await context.newPage();
  await page.goto("https://skywork.ai/", { waitUntil: "domcontentloaded", timeout: 60000 }).catch((err) => {
    console.log(`HOME_GOTO_TIMEOUT_OR_FAILED=${err.message}`);
  });
  await page.waitForTimeout(5000);
  const home = await extractStatus(page, "skywork_sxs_home_probe");

  if (mode === "probe") {
    await context.close();
    return;
  }

  if (mode === "wait_download_existing") {
    const projectUrl = process.env.SKYWORK_PROJECT_URL;
    if (!projectUrl) {
      throw new Error("SKYWORK_PROJECT_URL is required for wait_download_existing mode");
    }
    await page.goto(projectUrl, { waitUntil: "domcontentloaded", timeout: 60000 }).catch(() => {});
    await page.waitForTimeout(5000);
    let body = await page.locator("body").innerText({ timeout: 5000 }).catch(() => "");
    if (/로그인\/회원가입|Microsoft 계정으로 로그인|이메일로 계속/i.test(body)) {
      const loginResult = await ensureGoogleLogin(context, page);
      page = loginResult.page || page;
      await page.goto(projectUrl, { waitUntil: "domcontentloaded", timeout: 60000 }).catch(() => {});
      await page.waitForTimeout(5000);
    }
    const waitMinutes = Number(process.env.SKYWORK_GENERATION_WAIT_MINUTES || "60");
    const finalStatus = await waitForProjectReady(page, waitMinutes * 60 * 1000);
    let exports = {};
    try {
      exports = await downloadExports(page);
    } catch (err) {
      console.log(`EXPORT_DOWNLOAD_FAILED=${err.message}`);
      exports = { error: err.message };
    }
    await writeAutomationStatus("wait_download_existing", {
      mode,
      title: await page.title().catch(() => ""),
      url: page.url(),
      bodySnippet: finalStatus?.bodySnippet || "",
      screenshot: finalStatus?.screenshot || "",
      exports,
    });
    await context.close();
    return;
  }

  if (home.loginHints && !home.creationHints) {
    console.log("LOGIN_REQUIRED: Please complete Skywork login in the visible Chrome SxS window. Waiting up to 10 minutes.");
    const started = Date.now();
    while (Date.now() - started < 10 * 60 * 1000) {
      await page.waitForTimeout(5000);
      const status = await extractStatus(page, "skywork_sxs_login_wait");
      if (!status.loginHints && status.creationHints) {
        break;
      }
    }
  }

  const afterLogin = await extractStatus(page, "skywork_sxs_after_login");
  if (afterLogin.loginHints && !afterLogin.creationHints) {
    console.log("STOPPED: login still appears required.");
    await context.close();
    process.exitCode = 2;
    return;
  }

  const clicked = await clickByText(page, [/presentation/i, /ppt/i, /slide/i, /프레젠테이션/i, /슬라이드/i, /파워포인트/i, /PPT/]).catch(() => null);
  console.log(`PPT_CLICKED=${clicked || "none"}`);
  await extractStatus(page, "skywork_sxs_after_ppt_click");

  if (mode === "inspect") {
    const dom = await page.evaluate(() => {
      const summarize = (el) => ({
        tag: el.tagName,
        type: el.getAttribute("type"),
        accept: el.getAttribute("accept"),
        role: el.getAttribute("role"),
        aria: el.getAttribute("aria-label"),
        placeholder: el.getAttribute("placeholder"),
        text: (el.innerText || el.textContent || "").replace(/\s+/g, " ").slice(0, 180),
        cls: el.className,
      });
      return {
        inputs: Array.from(document.querySelectorAll("input")).map(summarize),
        textareas: Array.from(document.querySelectorAll("textarea")).map(summarize),
        editables: Array.from(document.querySelectorAll('[contenteditable="true"]')).map(summarize),
        buttons: Array.from(document.querySelectorAll("button")).slice(0, 40).map(summarize),
      };
    });
    console.log(JSON.stringify(dom, null, 2));
  }

  if (mode === "submit" || mode === "submit_wait_download") {
    let workPage = page;
    let loggedIn = false;
    if (mode === "submit_wait_download") {
      if (process.env.SKYWORK_AUTO_LOGIN === "1") {
        const loginResult = await ensureGoogleLogin(context, page);
        workPage = loginResult.page || page;
        loggedIn = loginResult.loggedIn;
      }
      if (!loggedIn) {
        const waitMinutes = Number(process.env.SKYWORK_LOGIN_WAIT_MINUTES || "30");
        workPage = await waitForManualSkyworkLogin(context, page, waitMinutes * 60 * 1000);
        loggedIn = Boolean(workPage);
      }
    } else {
      const loginResult = await ensureGoogleLogin(context, page);
      workPage = loginResult.page || page;
      loggedIn = loginResult.loggedIn;
    }
    if (!loggedIn) {
      await writeAutomationStatus("login_blocked", {
        mode,
        title: await workPage?.title().catch(() => "") || "",
        url: workPage?.url() || page.url(),
        bodySnippet: await (workPage || page).locator("body").innerText({ timeout: 4000 }).then((text) => text.replace(/\s+/g, " ").slice(0, 3000)).catch(() => ""),
      });
      await context.close();
      process.exitCode = 3;
      return;
    }
    let pptReady = await ensurePptSkill(workPage);
    if (!pptReady) {
      await workPage.waitForTimeout(3000);
      pptReady = await ensurePptSkill(workPage);
      console.log(`PPT_SKILL_READY_RETRY=${pptReady}`);
    }
    console.log(`PPT_SKILL_READY=${pptReady}`);
    if (!pptReady) {
      await writeAutomationStatus("ppt_not_ready", {
        mode,
        title: await workPage.title().catch(() => ""),
        url: workPage.url(),
        bodySnippet: await workPage.locator("body").innerText({ timeout: 4000 }).then((text) => text.replace(/\s+/g, " ").slice(0, 3000)).catch(() => ""),
      });
      await context.close();
      process.exitCode = 4;
      return;
    }
    await extractStatus(workPage, "skywork_sxs_after_login_ppt_page");
    const uploaded = await uploadTemplate(workPage);
    await extractStatus(workPage, "skywork_sxs_after_template_upload");
    const sourceUploaded = await uploadSourceFiles(workPage);
    await extractStatus(workPage, "skywork_sxs_after_source_upload");
    const promptLength = await fillPrompt(workPage);
    await extractStatus(workPage, "skywork_sxs_after_prompt_fill");
    await clickSubmit(workPage);
    let finalStatus = await extractStatus(workPage, "skywork_sxs_after_submit");
    const started = Date.now();
    while (!/\/project\//.test(workPage.url()) && Date.now() - started < 120000) {
      await workPage.waitForTimeout(5000);
      finalStatus = await extractStatus(workPage, "skywork_sxs_submit_wait");
      if (/login|로그인|회원가입/i.test(finalStatus.bodySnippet) && !/project/i.test(finalStatus.url)) {
        break;
      }
    }
    let exports = {};
    if (mode === "submit_wait_download" && /\/project\//.test(workPage.url())) {
      const waitMinutes = Number(process.env.SKYWORK_GENERATION_WAIT_MINUTES || "60");
      finalStatus = await waitForProjectReady(workPage, waitMinutes * 60 * 1000) || finalStatus;
      try {
        exports = await downloadExports(workPage);
      } catch (err) {
        console.log(`EXPORT_DOWNLOAD_FAILED=${err.message}`);
        exports = { error: err.message };
      }
    }
    await writeAutomationStatus("submit", {
      mode,
      uploaded,
      sourceUploaded,
      promptLength,
      title: await workPage.title().catch(() => ""),
      url: workPage.url(),
      bodySnippet: finalStatus.bodySnippet,
      screenshot: finalStatus.screenshot,
      exports,
    });
  }

  await context.close();
}

main().catch((err) => {
  console.error(err && err.stack ? err.stack : err);
  process.exit(1);
});
