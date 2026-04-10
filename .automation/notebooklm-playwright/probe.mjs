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
const clickText = process.env.NOTEBOOKLM_CLICK_TEXT || '';

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
await page.waitForTimeout(10000);

if (clickText) {
  const locator = page.getByText(clickText, { exact: false }).first();
  if (await locator.count()) {
    await locator.click({ timeout: 10000 });
    await page.waitForTimeout(12000);
  }
}

const title = await page.title();
const bodyText = await page.locator('body').innerText().catch(() => '');
const controls = await page.locator('button, a, [role="button"]').evaluateAll((els) =>
  els
    .map((el) => (el.textContent || '').trim().replace(/\s+/g, ' '))
    .filter(Boolean)
    .slice(0, 120)
);

const screenshotPath = path.join(outDir, clickText ? 'notebooklm-after-click.png' : 'notebooklm-home.png');
await page.screenshot({ path: screenshotPath, fullPage: true });

console.log(JSON.stringify({
  topicDir,
  url: page.url(),
  title,
  screenshotPath,
  controls,
  bodyPreview: bodyText.slice(0, 5000),
}, null, 2));

await browser.close();
