import path from 'node:path';
import { chromium } from 'playwright';
import {
  chromeExecutablePath,
  cleanupTempPath,
  cloneNotebooklmChromeProfile,
  ensureNotebooklmExportDir,
  resolveNotebookSourceFiles,
  resolveTopicDir,
} from './workspace_paths.mjs';

const topicDir = resolveTopicDir(process.argv[2]);
const outDir = ensureNotebooklmExportDir(topicDir);
const files = resolveNotebookSourceFiles(topicDir);
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
  await page.goto('https://notebooklm.google.com/', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForTimeout(8000);
  await page.getByText('새 노트 만들기', { exact: false }).first().click({ timeout: 15000 });
  await page.waitForTimeout(8000);

  const fileInputCount = await page.locator('input[type="file"]').count();
  if (fileInputCount === 0) {
    await page.getByText('파일 업로드', { exact: false }).first().click({ timeout: 15000 });
    await page.waitForTimeout(3000);
  }

  const afterClickCount = await page.locator('input[type="file"]').count();
  if (afterClickCount === 0) {
    throw new Error('No file input found');
  }

  await page.locator('input[type="file"]').first().setInputFiles(files);
  await page.waitForTimeout(20000);

  const title = await page.title();
  const bodyText = await page.locator('body').innerText().catch(() => '');
  const screenshotPath = path.join(outDir, 'notebooklm-after-upload.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });

  console.log(JSON.stringify({
    topicDir,
    files,
    url: page.url(),
    title,
    fileInputCount,
    afterClickCount,
    screenshotPath,
    bodyPreview: bodyText.slice(0, 6000),
  }, null, 2));
} finally {
  if (context) {
    await context.close().catch(() => {});
  }
  cleanupTempPath(tempProfile);
}
