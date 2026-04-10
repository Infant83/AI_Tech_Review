import path from 'node:path';
import { chromium } from 'playwright';
import {
  chromeExecutablePath,
  cleanupTempPath,
  cloneNotebooklmChromeProfile,
  ensureNotebooklmExportDir,
  resolveTopicDir,
} from './workspace_paths.mjs';

const notebookUrl = process.argv[2];
const outputName = process.argv[3] || 'slides';
const topicDirArg = process.argv[4];

if (!notebookUrl) throw new Error('Notebook URL required');

const topicDir = resolveTopicDir(topicDirArg);
const outDir = ensureNotebooklmExportDir(topicDir);
const tempProfile = cloneNotebooklmChromeProfile();

let context;

try {
  context = await chromium.launchPersistentContext(tempProfile, {
    headless: true,
    executablePath: chromeExecutablePath,
    acceptDownloads: true,
    viewport: { width: 1440, height: 1100 },
  });

  const page = context.pages()[0] || await context.newPage();
  await page.goto(notebookUrl, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForTimeout(10000);

  const startText = await page.locator('body').innerText();
  if (!startText.includes('슬라이드 자료 생성 중')) {
    await page.getByText('슬라이드 자료', { exact: false }).first().click({ timeout: 15000 });
    await page.waitForTimeout(10000);
  }

  let ready = false;
  let moreCount = 0;
  for (let i = 0; i < 30; i += 1) {
    const body = await page.locator('body').innerText();
    moreCount = await page.getByLabel('더보기').count();
    if (!body.includes('슬라이드 자료 생성 중') && moreCount >= 5) {
      ready = true;
      break;
    }
    await page.waitForTimeout(30000);
    await page.reload({ waitUntil: 'domcontentloaded', timeout: 120000 });
    await page.waitForTimeout(8000);
  }

  if (!ready) {
    const screenshotPath = path.join(outDir, 'notebooklm-slide-wait-timeout.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });
    throw new Error(`Slide artifact did not become ready. moreCount=${moreCount}`);
  }

  const buttons = page.getByLabel('더보기');
  const count = await buttons.count();
  if (count < 5) throw new Error(`Unexpected more button count: ${count}`);

  const slideMenuButton = buttons.nth(count - 2);
  await slideMenuButton.click({ timeout: 15000 });
  await page.waitForTimeout(2000);

  const downloadButton = page.getByText('다운로드', { exact: false }).first();
  const downloadPromise = page.waitForEvent('download', { timeout: 120000 });
  await downloadButton.click({ timeout: 15000 });
  const download = await downloadPromise;

  const suggested = download.suggestedFilename();
  const ext = path.extname(suggested) || '.bin';
  const savePath = path.join(outDir, `${outputName}${ext}`);
  await download.saveAs(savePath);

  console.log(JSON.stringify({
    topicDir,
    notebookUrl,
    suggested,
    savePath,
  }, null, 2));
} finally {
  if (context) {
    await context.close().catch(() => {});
  }
  cleanupTempPath(tempProfile);
}
