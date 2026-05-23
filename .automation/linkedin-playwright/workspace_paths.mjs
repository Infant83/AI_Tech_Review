import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));

export const repoRoot = path.resolve(scriptDir, '..', '..');

export const chromeExecutablePath =
  process.env.CHROME_EXECUTABLE_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

export const linkedinDataDir =
  process.env.LINKEDIN_PLAYWRIGHT_DATA_DIR || path.join(repoRoot, '.automation', 'linkedin-playwright', 'Data');

export const playwrightImportUrl = pathToFileURL(
  path.join(repoRoot, '.automation', 'notebooklm-playwright', 'node_modules', 'playwright', 'index.mjs'),
).href;

function isDirectory(targetPath) {
  return fs.existsSync(targetPath) && fs.statSync(targetPath).isDirectory();
}

export function isReviewDir(targetPath) {
  return isDirectory(targetPath) &&
    isDirectory(path.join(targetPath, 'notes')) &&
    isDirectory(path.join(targetPath, 'reports'));
}

function findContainingReviewDir(startPath) {
  let current = path.resolve(startPath);
  const normalizedRoot = path.resolve(repoRoot);

  while (true) {
    if (isReviewDir(current)) {
      return current;
    }

    if (current === normalizedRoot) {
      return null;
    }

    const parent = path.dirname(current);
    if (parent === current) {
      return null;
    }
    current = parent;
  }
}

function findSingleReviewChild(startPath) {
  if (!isDirectory(startPath)) {
    return null;
  }

  const matches = fs
    .readdirSync(startPath, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(startPath, entry.name))
    .filter((candidate) => isReviewDir(candidate));

  return matches.length === 1 ? matches[0] : null;
}

export function resolveReviewDir(reviewDirArg) {
  if (reviewDirArg) {
    const candidates = path.isAbsolute(reviewDirArg)
      ? [path.resolve(reviewDirArg)]
      : [path.resolve(process.cwd(), reviewDirArg), path.resolve(repoRoot, reviewDirArg)];

    for (const candidate of new Set(candidates)) {
      if (isReviewDir(candidate)) {
        return candidate;
      }
    }

    throw new Error(
      `Review directory not found or incomplete: ${reviewDirArg}. Expected a folder with notes/ and reports/ subfolders.`,
    );
  }

  const inferred = findContainingReviewDir(process.cwd());
  if (inferred) {
    return inferred;
  }

  const singleChild = findSingleReviewChild(process.cwd());
  if (singleChild) {
    return singleChild;
  }

  throw new Error(
    `Could not infer a review directory from ${process.cwd()}. Run inside a review package or pass -ReviewDir.`,
  );
}

export function ensureArtifactDir(reviewDir) {
  const outDir = path.join(reviewDir, 'artifacts');
  fs.mkdirSync(outDir, { recursive: true });
  return outDir;
}

export function ensureNotesDir(reviewDir) {
  const notesDir = path.join(reviewDir, 'notes');
  fs.mkdirSync(notesDir, { recursive: true });
  return notesDir;
}

export function ensureLinkedinDataDir() {
  fs.mkdirSync(linkedinDataDir, { recursive: true });
  return linkedinDataDir;
}

export function cloneLinkedinChromeProfile() {
  if (!isDirectory(linkedinDataDir)) {
    throw new Error(`LinkedIn Chrome profile not found: ${linkedinDataDir}`);
  }

  for (const lockName of ['lockfile', 'SingletonLock', 'SingletonCookie', 'SingletonSocket']) {
    if (fs.existsSync(path.join(linkedinDataDir, lockName))) {
      throw new Error(
        `LinkedIn dedicated Chrome profile appears to be open. Close the dedicated Chrome window first: ${linkedinDataDir}`,
      );
    }
  }

  const tempProfile = fs.mkdtempSync(path.join(os.tmpdir(), 'linkedin-playwright-'));
  fs.cpSync(linkedinDataDir, tempProfile, {
    recursive: true,
    filter: (sourcePath) => {
      const base = path.basename(sourcePath);
      return ![
        'Cache',
        'Code Cache',
        'GPUCache',
        'DawnGraphiteCache',
        'GrShaderCache',
        'ShaderCache',
      ].includes(base);
    },
  });

  for (const lockName of ['lockfile', 'SingletonLock', 'SingletonCookie', 'SingletonSocket']) {
    const targetPath = path.join(tempProfile, lockName);
    if (fs.existsSync(targetPath)) {
      fs.rmSync(targetPath, { force: true });
    }
  }

  return tempProfile;
}

export function cleanupTempPath(targetPath) {
  if (targetPath && fs.existsSync(targetPath)) {
    fs.rmSync(targetPath, { recursive: true, force: true });
  }
}

export function sanitizeFileStem(value, fallback = 'linkedin_capture') {
  const cleaned = value.replace(/[^\w-]+/g, '_').replace(/^_+|_+$/g, '');
  return cleaned || fallback;
}
