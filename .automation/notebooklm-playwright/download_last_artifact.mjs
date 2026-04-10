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
const outputName = process.argv[3] || 'artifact';
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
  await page.waitForTimeout(8000);

  const buttons = page.getByLabel('더보기');
  const count = await buttons.count();
  if (count === 0) throw new Error('No 더보기 buttons');
  await buttons.nth(count - 1).click({ timeout: 15000 });
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
