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
const topicDirArg = process.argv[3];

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
  await page.waitForTimeout(5000);

  const title = await page.title();
  const bodyText = await page.locator('body').innerText().catch(() => '');
  const controls = await page.locator('button, a, [role="menuitem"], [role="button"]').evaluateAll((els) =>
    els
      .map((el) => {
        const text = (el.textContent || '').trim().replace(/\s+/g, ' ');
        const aria = el.getAttribute('aria-label') || '';
        return [aria, text].filter(Boolean).join(' | ');
      })
      .filter(Boolean)
      .slice(0, 200)
  );

  const screenshotPath = path.join(outDir, 'notebooklm-artifact-menu.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });

  console.log(JSON.stringify({
    topicDir,
    url: page.url(),
    title,
    moreButtonCount: count,
    screenshotPath,
    controls,
    bodyPreview: bodyText.slice(0, 7000),
  }, null, 2));
} finally {
  if (context) {
    await context.close().catch(() => {});
  }
  cleanupTempPath(tempProfile);
}
