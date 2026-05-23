import fs from 'node:fs';
import path from 'node:path';
import {
  chromeExecutablePath,
  cleanupTempPath,
  cloneLinkedinChromeProfile,
  ensureArtifactDir,
  ensureNotesDir,
  playwrightImportUrl,
  resolveReviewDir,
  sanitizeFileStem,
} from './workspace_paths.mjs';

function parseArgs(argv) {
  const options = {
    screens: 6,
    waitMs: 2500,
    scrollPx: 1000,
    inspectPosts: 4,
    postWaitMs: 2200,
    headed: false,
    reviewDir: null,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    switch (arg) {
      case '--review-dir':
        options.reviewDir = argv[++i];
        break;
      case '--screens':
        options.screens = Number.parseInt(argv[++i], 10);
        break;
      case '--wait-ms':
        options.waitMs = Number.parseInt(argv[++i], 10);
        break;
      case '--scroll-px':
        options.scrollPx = Number.parseInt(argv[++i], 10);
        break;
      case '--inspect-posts':
        options.inspectPosts = Number.parseInt(argv[++i], 10);
        break;
      case '--post-wait-ms':
        options.postWaitMs = Number.parseInt(argv[++i], 10);
        break;
      case '--headed':
        options.headed = true;
        break;
      default:
        throw new Error(`Unknown argument: ${arg}`);
    }
  }

  if (!Number.isFinite(options.screens) || options.screens < 1) {
    throw new Error(`Invalid --screens value: ${options.screens}`);
  }
  if (!Number.isFinite(options.waitMs) || options.waitMs < 0) {
    throw new Error(`Invalid --wait-ms value: ${options.waitMs}`);
  }
  if (!Number.isFinite(options.scrollPx) || options.scrollPx < 100) {
    throw new Error(`Invalid --scroll-px value: ${options.scrollPx}`);
  }
  if (!Number.isFinite(options.inspectPosts) || options.inspectPosts < 0) {
    throw new Error(`Invalid --inspect-posts value: ${options.inspectPosts}`);
  }
  if (!Number.isFinite(options.postWaitMs) || options.postWaitMs < 0) {
    throw new Error(`Invalid --post-wait-ms value: ${options.postWaitMs}`);
  }

  return options;
}

function formatTimestamp(date) {
  return date.toISOString().replace('T', ' ').replace(/\.\d+Z$/, 'Z');
}

function relativeToReview(reviewDir, targetPath) {
  return path.relative(reviewDir, targetPath).replace(/\\/g, '/');
}

function safeMarkdownLinkLabel(value, fallback = 'link') {
  const label = (value || '').replace(/\s+/g, ' ').trim().replace(/[[\]]/g, '');
  return label || fallback;
}

function renderLinkBullets(links, indent = '  - ') {
  if (!links || !links.length) {
    return `${indent}No direct links extracted.`;
  }

  return links
    .map((link) => `${indent}[${safeMarkdownLinkLabel(link.label, link.href)}](${link.href})`)
    .join('\n');
}

function renderBlockquote(text, fallback) {
  const normalized = (text || '').trim();
  if (!normalized) {
    return `> ${fallback}`;
  }
  return normalized
    .split(/\r?\n/)
    .map((line) => `> ${line}`)
    .join('\n');
}

function renderCaptureNote({ reviewDir, noteName, pageTitle, pageUrl, capturedAt, shots, rightRailSamples, detailedPosts }) {
  const relativeShots = shots
    .map((shot) => `  - \`${relativeToReview(reviewDir, shot.screenshotPath)}\``)
    .join('\n');

  const stepSections = shots
    .map((shot, index) => {
      const cards = shot.cards.length
        ? shot.cards
          .map((card, cardIndex) => {
            const actorLine = card.actorName ? ` | Author: ${card.actorName}` : '';
            const linkLine = card.permalink ? ` | Post: ${card.permalink}` : '';
            return `- Card ${cardIndex + 1}${actorLine}${linkLine}\n  - Preview: ${card.text}`;
          })
          .join('\n')
        : '- No visible cards extracted from this viewport.';
      return `### Viewport ${index + 1}\n- Screenshot: \`${relativeToReview(reviewDir, shot.screenshotPath)}\`\n${cards}`;
    })
    .join('\n\n');

  const rightRailSection = rightRailSamples.length
    ? rightRailSamples.map((sample, index) => `- Sample ${index + 1}: ${sample}`).join('\n')
    : '- No right-rail text was extracted.';

  const detailedSection = detailedPosts.length
    ? detailedPosts
      .map((post, index) => {
        const profileLine = post.actorLink ? `- Author profile: [open](${post.actorLink})` : '- Author profile: not detected';
        const postLine = post.detailUrl || post.permalink
          ? `- Post link: [open](${post.detailUrl || post.permalink})`
          : '- Post link: not detected';
        const screenshotLine = post.detailScreenshotPath
          ? `- Detail screenshot: \`${relativeToReview(reviewDir, post.detailScreenshotPath)}\``
          : '- Detail screenshot: not captured';
        const previewBlock = renderBlockquote(post.previewText, 'No feed preview text extracted.');
        const detailBlock = renderBlockquote(post.detailText, 'Direct post text could not be extracted.');
        const externalLinks = renderLinkBullets(post.detailLinks?.filter((link) => link.href.startsWith('http')), '  - ');
        return `### Post ${index + 1}\n- Status: \`${post.detailStatus}\`\n- Feed viewport: \`${post.viewportIndex}\`\n- Author: ${post.actorName || 'not detected'}\n- Role line: ${post.actorMeta || 'not detected'}\n${profileLine}\n${postLine}\n${screenshotLine}\n- Feed preview excerpt:\n${previewBlock}\n- Direct post excerpt:\n${detailBlock}\n- Links found at post level:\n${externalLinks}`;
      })
      .join('\n\n')
    : '- No direct post inspections were completed.';

  return `# ${noteName}

## Capture Context
- Captured at: \`${capturedAt}\`
- URL: \`${pageUrl}\`
- Page title: \`${pageTitle}\`
- Mode: Playwright capture using a cloned dedicated LinkedIn Chrome profile

## Screenshot Artifacts
${relativeShots}

## Visible Feed Samples

${stepSections}

## Direct Post Inspections
${detailedSection}

## Right-Rail Samples
${rightRailSection}
`;
}

async function collectVisibleCards(page) {
  return page.evaluate(() => {
    const normalize = (value) => (value || '').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
    const isVisible = (element) => {
      const style = window.getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        rect.width >= 480 &&
        rect.width <= 700 &&
        rect.height >= 220 &&
        rect.height <= 1800 &&
        rect.bottom > 120 &&
        rect.top < window.innerHeight;
    };
    const summarizeActor = (text, links) => {
      const lines = text.split('\n').map((line) => normalize(line)).filter(Boolean);
      const actorLine = lines.find((line) =>
        !['피드 게시물', '광고'].includes(line) &&
        !/^글 올리기|이벤트|글쓰기|정렬/.test(line) &&
        line.length < 120,
      ) || '';
      const actorLink = links.find((link) => /linkedin\.com\/(in|company|school)\//i.test(link.href));
      return actorLink?.label || actorLine.replace(/\s*•.*$/, '').trim() || '';
    };

    const seen = new Set();
    const cards = [];
    const candidates = Array.from(document.querySelectorAll('main div'))
      .filter(isVisible)
      .map((candidate) => {
        const text = normalize(candidate.innerText || '');
        return {
          candidate,
          rect: candidate.getBoundingClientRect(),
          text,
        };
      })
      .filter((item) =>
        item.text.length >= 160 &&
        item.text.length <= 4500 &&
        !/^글 올리기 이벤트 글쓰기 정렬/i.test(item.text) &&
        !item.text.startsWith('Hyun-Jung Kim Researcher') &&
        !item.text.startsWith('LinkedIn 뉴스 탑 스토리'),
      )
      .sort((left, right) => left.rect.top - right.rect.top);

    for (const item of candidates) {
      const snippetKey = item.text.slice(0, 220);
      if (seen.has(snippetKey)) {
        continue;
      }
      seen.add(snippetKey);
      const links = Array.from(item.candidate.querySelectorAll('a[href]')).map((anchor) => ({
        href: anchor.href || '',
        label: normalize(anchor.textContent || ''),
      }));
      cards.push({
        top: Math.round(item.rect.top),
        actorName: summarizeActor(item.text, links),
        permalink: links.find((link) => /linkedin\.com\/(feed\/update|posts\/|pulse\/)/i.test(link.href))?.href || '',
        text: item.text.slice(0, 900),
      });
      if (cards.length === 6) {
        break;
      }
    }

    const rightRailCandidates = Array.from(
      document.querySelectorAll('aside, .scaffold-layout__aside, [data-view-name="feed-news-module"]'),
    );
    let rightRailText = '';
    for (const element of rightRailCandidates) {
      const text = normalize(element.innerText || '');
      if (text.length > 50) {
        rightRailText = text.slice(0, 1200);
        break;
      }
    }

    return {
      cards: cards.sort((left, right) => left.top - right.top).slice(0, 6),
      rightRailText,
    };
  });
}

async function collectVisiblePosts(page) {
  return page.evaluate(() => {
    const normalize = (value) => (value || '').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
    const toAbsolute = (href) => {
      try {
        return new URL(href, window.location.href).href;
      } catch {
        return href || '';
      }
    };
    const isVisible = (element) => {
      const style = window.getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        rect.width >= 480 &&
        rect.width <= 700 &&
        rect.height >= 220 &&
        rect.height <= 1800 &&
        rect.bottom > 120 &&
        rect.top < window.innerHeight;
    };
    const looksLikePostUrl = (href) =>
      /linkedin\.com\/(feed\/update|posts\/|pulse\/)/i.test(href);
    const looksLikeActorUrl = (href) =>
      /linkedin\.com\/(in|company|school)\//i.test(href);
    const seen = new Set();
    const posts = [];
    const candidates = Array.from(document.querySelectorAll('main div'))
      .filter(isVisible)
      .map((candidate) => {
        const rect = candidate.getBoundingClientRect();
        const previewText = normalize(candidate.innerText || '');
        return { candidate, rect, previewText };
      })
      .filter((item) =>
        item.previewText.length >= 160 &&
        item.previewText.length <= 4500 &&
        !/^글 올리기 이벤트 글쓰기 정렬/i.test(item.previewText) &&
        !item.previewText.startsWith('Hyun-Jung Kim Researcher') &&
        !item.previewText.startsWith('LinkedIn 뉴스 탑 스토리'),
      )
      .sort((left, right) => left.rect.top - right.rect.top);

    for (const item of candidates) {
      const snippetKey = item.previewText.slice(0, 220);
      if (seen.has(snippetKey)) {
        continue;
      }
      seen.add(snippetKey);

      const rawAnchors = Array.from(item.candidate.querySelectorAll('a[href]'))
        .map((anchor) => ({
          href: toAbsolute(anchor.getAttribute('href') || anchor.href || ''),
          label: normalize(anchor.textContent || ''),
        }))
        .filter((anchor) => anchor.href && !anchor.href.startsWith('javascript:'));

      const dedupedAnchors = [];
      const linkSeen = new Set();
      for (const anchor of rawAnchors) {
        if (linkSeen.has(anchor.href)) {
          continue;
        }
        linkSeen.add(anchor.href);
        dedupedAnchors.push(anchor);
      }

      const lines = item.previewText.split('\n').map((line) => normalize(line)).filter(Boolean);
      const actorLine = lines.find((line) =>
        !['피드 게시물', '광고'].includes(line) &&
        !/^글 올리기|이벤트|글쓰기|정렬/.test(line) &&
        line.length < 120,
      ) || '';
      const actorName =
        dedupedAnchors.find((anchor) => looksLikeActorUrl(anchor.href) && anchor.label.length > 1)?.label ||
        actorLine.replace(/\s*•.*$/, '').trim() ||
        '';
      const actorMeta =
        lines.find((line, index) => index > 0 && line !== actorLine && line.length < 160) ||
        '';
      const permalink = dedupedAnchors.find((anchor) => looksLikePostUrl(anchor.href))?.href || '';
      const actorLink = dedupedAnchors.find((anchor) => looksLikeActorUrl(anchor.href))?.href || '';
      const externalLinks = dedupedAnchors
        .filter((anchor) => /^https?:/i.test(anchor.href) && !/linkedin\.com/i.test(anchor.href))
        .slice(0, 8);

      posts.push({
        top: Math.round(item.rect.top),
        actorName,
        actorMeta,
        permalink,
        actorLink,
        previewText: item.previewText.slice(0, 1800),
        externalLinks,
      });
      if (posts.length === 8) {
        break;
      }
    }

    return posts.sort((left, right) => left.top - right.top).slice(0, 8);
  });
}

async function inspectPostDetail(browserContext, reviewDir, reviewStem, post, postIndex, waitMs) {
  if (!post.permalink) {
    return {
      ...post,
      detailStatus: 'feed-card-inspected-no-permalink',
      detailTitle: '',
      detailUrl: '',
      detailText: post.previewText,
      detailLinks: (post.externalLinks || []).map((link) => ({
        href: link.href,
        label: link.label,
      })),
      detailScreenshotPath: null,
    };
  }

  const detailPage = await browserContext.newPage();
  try {
    await detailPage.goto(post.permalink, {
      waitUntil: 'domcontentloaded',
      timeout: 120000,
    });
    await detailPage.waitForTimeout(waitMs);
    await ensureLoggedInFeed(detailPage);

    const detailScreenshotPath = path.join(
      ensureArtifactDir(reviewDir),
      `${reviewStem}_post_detail_${String(postIndex).padStart(2, '0')}.png`,
    );
    await detailPage.screenshot({ path: detailScreenshotPath, fullPage: false });

    const detailData = await detailPage.evaluate(() => {
      const normalize = (value) => (value || '').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
      const toAbsolute = (href) => {
        try {
          return new URL(href, window.location.href).href;
        } catch {
          return href || '';
        }
      };
      const collectLinks = (root) => {
        const seen = new Set();
        const links = [];
        for (const anchor of Array.from(root.querySelectorAll('a[href]'))) {
          const href = toAbsolute(anchor.getAttribute('href') || anchor.href || '');
          if (!href || href.startsWith('javascript:') || seen.has(href)) {
            continue;
          }
          seen.add(href);
          links.push({
            href,
            label: normalize(anchor.textContent || '') || href,
          });
        }
        return links;
      };

      const main = document.querySelector('main') || document.body;
      const articleCandidates = Array.from(
        document.querySelectorAll('main article, article, main [data-id^="urn:li:activity:"], main .feed-shared-update-v2'),
      )
        .map((element) => {
          const rect = element.getBoundingClientRect();
          const text = normalize(element.innerText || '');
          return {
            element,
            text,
            score: text.length + Math.round(rect.width) + Math.round(rect.height),
          };
        })
        .filter((candidate) => candidate.text.length > 140)
        .sort((left, right) => right.score - left.score);

      const bestRoot = articleCandidates[0]?.element || main;
      const bodyText = normalize(bestRoot.innerText || main.innerText || document.body.innerText).slice(0, 9000);
      const detailLinks = collectLinks(bestRoot)
        .filter((link) => /^https?:/i.test(link.href))
        .slice(0, 14);

      return {
        pageTitle: document.title,
        canonicalUrl: window.location.href,
        bodyText,
        detailLinks,
      };
    });

    return {
      ...post,
      detailStatus: 'full-post-inspected',
      detailTitle: detailData.pageTitle,
      detailUrl: detailData.canonicalUrl,
      detailText: detailData.bodyText,
      detailLinks: detailData.detailLinks,
      detailScreenshotPath,
    };
  } catch (error) {
    return {
      ...post,
      detailStatus: `inspection-failed: ${error.message}`,
      detailTitle: '',
      detailUrl: post.permalink,
      detailText: '',
      detailLinks: post.externalLinks || [],
      detailScreenshotPath: null,
    };
  } finally {
    await detailPage.close().catch(() => {});
  }
}

async function ensureLoggedInFeed(page) {
  const url = page.url();
  if (url.includes('/login') || url.includes('/uas/login')) {
    throw new Error(
      `Dedicated LinkedIn profile is not logged in. Open the dedicated profile once and sign into LinkedIn. Current URL: ${url}`,
    );
  }

  const pageText = await page.locator('body').innerText().catch(() => '');
  if (pageText.includes('로그인') && pageText.includes('회원 가입')) {
    throw new Error('Dedicated LinkedIn profile is showing the login page instead of the feed.');
  }
}

const options = parseArgs(process.argv.slice(2));
const reviewDir = resolveReviewDir(options.reviewDir);
const artifactDir = ensureArtifactDir(reviewDir);
const notesDir = ensureNotesDir(reviewDir);
const reviewStem = sanitizeFileStem(path.basename(reviewDir), 'linkedin_feed_daily_review');
const captureNoteName = `${reviewStem}_browser_capture.md`;
const captureNotePath = path.join(notesDir, captureNoteName);

const { chromium } = await import(playwrightImportUrl);
const tempProfile = cloneLinkedinChromeProfile();

let browserContext;

try {
  browserContext = await chromium.launchPersistentContext(tempProfile, {
    headless: !options.headed,
    executablePath: chromeExecutablePath,
    viewport: { width: 1440, height: 1200 },
    acceptDownloads: false,
  });

  const page = browserContext.pages()[0] || await browserContext.newPage();
  await page.goto('https://www.linkedin.com/feed/', {
    waitUntil: 'domcontentloaded',
    timeout: 120000,
  });
  await page.waitForTimeout(options.waitMs);
  await ensureLoggedInFeed(page);

  const shots = [];
  const rightRailSamples = [];
  const visiblePosts = [];
  const postSeen = new Set();

  for (let index = 1; index <= options.screens; index += 1) {
    const screenshotPath = path.join(
      artifactDir,
      `${reviewStem}_playwright_capture_${String(index).padStart(2, '0')}.png`,
    );

    await page.screenshot({ path: screenshotPath, fullPage: false });
    const sample = await collectVisibleCards(page);
    const posts = await collectVisiblePosts(page);
    shots.push({
      index,
      screenshotPath,
      cards: sample.cards,
    });
    for (const post of posts) {
      const stableKey = post.permalink || `${post.actorName}::${post.previewText.slice(0, 160)}`;
      if (postSeen.has(stableKey)) {
        continue;
      }
      postSeen.add(stableKey);
      visiblePosts.push({
        ...post,
        viewportIndex: index,
      });
    }
    if (sample.rightRailText) {
      rightRailSamples.push(sample.rightRailText);
    }

    if (index < options.screens) {
      await page.mouse.move(720, 980);
      await page.mouse.wheel(0, options.scrollPx);
      await page.waitForTimeout(350);
      await page.keyboard.press('PageDown').catch(() => {});
      await page.waitForTimeout(350);
      await page.evaluate((scrollPx) => {
        const candidates = [
          document.scrollingElement,
          document.documentElement,
          document.body,
          document.querySelector('main'),
          document.querySelector('[role="main"]'),
          document.querySelector('.scaffold-layout__main'),
          document.querySelector('.scaffold-finite-scroll'),
          document.querySelector('.scaffold-finite-scroll__content'),
        ].filter(Boolean);

        for (const candidate of candidates) {
          if ((candidate.scrollHeight || 0) - (candidate.clientHeight || 0) > 200) {
            candidate.scrollTop = (candidate.scrollTop || 0) + scrollPx;
          }
        }
      }, options.scrollPx);
      await page.waitForTimeout(options.waitMs);
    }
  }

  const detailedPosts = [];
  for (const [postIndex, post] of visiblePosts.slice(0, options.inspectPosts).entries()) {
    const inspected = await inspectPostDetail(
      browserContext,
      reviewDir,
      reviewStem,
      post,
      postIndex + 1,
      options.postWaitMs,
    );
    detailedPosts.push(inspected);
  }

  const capturedAt = formatTimestamp(new Date());
  const noteBody = renderCaptureNote({
    reviewDir,
    noteName: captureNoteName.replace(/\.md$/i, ''),
    pageTitle: await page.title(),
    pageUrl: page.url(),
    capturedAt,
    shots,
    rightRailSamples: [...new Set(rightRailSamples)].slice(0, 4),
    detailedPosts,
  });

  fs.writeFileSync(captureNotePath, noteBody, 'utf8');

  console.log(JSON.stringify({
    reviewDir,
    captureNotePath,
    screenshots: shots.map((shot) => shot.screenshotPath),
    inspectedPosts: detailedPosts.map((post) => ({
      actorName: post.actorName,
      permalink: post.permalink,
      detailStatus: post.detailStatus,
      detailScreenshotPath: post.detailScreenshotPath,
    })),
    url: page.url(),
    title: await page.title(),
  }, null, 2));
} finally {
  if (browserContext) {
    await browserContext.close().catch(() => {});
  }
  cleanupTempPath(tempProfile);
}
