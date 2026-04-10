import path from 'node:path';
import { chromium } from 'playwright';
import {
  chromeExecutablePath,
  cleanupTempPath,
  cloneNotebooklmChromeProfile,
  ensureNotebooklmExportDir,
  resolveTopicDir,
} from './workspace_paths.mjs';

const targetUrl = process.argv[2] || 'https://notebooklm.google.com/';
const topicDirArg = process.argv[3];

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
  await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForTimeout(12000);

  const title = await page.title();
  const bodyText = await page.locator('body').innerText().catch(() => '');
  const controls = await page.locator('button, a, [role="button"]').evaluateAll((els) =>
    els
      .map((el) => (el.textContent || '').trim().replace(/\s+/g, ' '))
      .filter(Boolean)
      .slice(0, 120)
  );

  const screenshotPath = path.join(outDir, 'notebooklm-profile-home.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });

  console.log(JSON.stringify({
    topicDir,
    url: page.url(),
    title,
    screenshotPath,
    controls,
    bodyPreview: bodyText.slice(0, 5000),
  }, null, 2));
} finally {
  if (context) {
    await context.close().catch(() => {});
  }
  cleanupTempPath(tempProfile);
}
