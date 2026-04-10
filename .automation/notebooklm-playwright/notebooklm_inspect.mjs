import path from 'node:path';
import { chromium } from 'playwright';
import {
  chromeExecutablePath,
  ensureNotebooklmExportDir,
  notebooklmStatePath,
  resolveTopicDir,
} from './workspace_paths.mjs';

const targetUrl = process.argv[2] || 'https://notebooklm.google.com/';
const topicDir = resolveTopicDir(process.argv[3]);
const outDir = ensureNotebooklmExportDir(topicDir);

const browser = await chromium.launch({
  headless: true,
  executablePath: chromeExecutablePath,
});

const context = await browser.newContext({
  storageState: notebooklmStatePath,
  acceptDownloads: true,
  viewport: { width: 1440, height: 1100 },
});

const page = await context.newPage();
await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 120000 });
await page.waitForTimeout(8000);

const title = await page.title();
const bodyText = await page.locator('body').innerText().catch(() => '');
const controls = await page.locator('button, a, [role="button"]').evaluateAll((els) =>
  els
    .map((el) => (el.textContent || '').trim().replace(/\s+/g, ' '))
    .filter(Boolean)
    .slice(0, 80)
);

const screenshotPath = path.join(outDir, 'notebooklm-home.png');
await page.screenshot({ path: screenshotPath, fullPage: true });

console.log(JSON.stringify({
  topicDir,
  url: page.url(),
  title,
  screenshotPath,
  controls,
  bodyPreview: bodyText.slice(0, 4000),
}, null, 2));

await browser.close();
