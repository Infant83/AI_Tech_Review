import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));

export const repoRoot = path.resolve(scriptDir, '..', '..');
export const chromeExecutablePath =
  process.env.CHROME_EXECUTABLE_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

const notebooklmDataDir =
  process.env.NOTEBOOKLM_DATA_DIR || path.join(os.homedir(), 'AppData', 'Local', 'notebooklm-mcp', 'Data');

export const notebooklmStatePath =
  process.env.NOTEBOOKLM_STATE_PATH || path.join(notebooklmDataDir, 'browser_state', 'state.json');

export const notebooklmChromeProfile =
  process.env.NOTEBOOKLM_CHROME_PROFILE || path.join(notebooklmDataDir, 'chrome_profile');

function isDirectory(targetPath) {
  return fs.existsSync(targetPath) && fs.statSync(targetPath).isDirectory();
}

export function isTopicDir(targetPath) {
  return isDirectory(targetPath) &&
    isDirectory(path.join(targetPath, 'notes')) &&
    isDirectory(path.join(targetPath, 'reports'));
}

function findContainingTopicDir(startPath) {
  let current = path.resolve(startPath);
  const normalizedRoot = path.resolve(repoRoot);

  while (true) {
    if (isTopicDir(current)) {
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

function findSingleTopicChild(startPath) {
  if (!isDirectory(startPath)) {
    return null;
  }

  const matches = fs
    .readdirSync(startPath, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(startPath, entry.name))
    .filter((candidate) => isTopicDir(candidate));

  return matches.length === 1 ? matches[0] : null;
}

export function resolveTopicDir(topicArg) {
  if (topicArg) {
    const candidates = path.isAbsolute(topicArg)
      ? [path.resolve(topicArg)]
      : [path.resolve(process.cwd(), topicArg), path.resolve(repoRoot, topicArg)];

    for (const candidate of new Set(candidates)) {
      if (isTopicDir(candidate)) {
        return candidate;
      }
    }

    throw new Error(
      `Topic directory not found or incomplete: ${topicArg}. Expected a folder with notes/ and reports/ subfolders.`,
    );
  }

  const inferred = findContainingTopicDir(process.cwd());
  if (inferred) {
    return inferred;
  }

  const singleChild = findSingleTopicChild(process.cwd());
  if (singleChild) {
    return singleChild;
  }

  throw new Error(
    `Could not infer a topic directory from ${process.cwd()}. Run the script from inside a topic folder or pass one as an argument.`,
  );
}

export function ensureNotebooklmExportDir(topicDir) {
  const outDir = path.join(topicDir, 'notebooklm_exports');
  fs.mkdirSync(outDir, { recursive: true });
  return outDir;
}

export function cloneNotebooklmChromeProfile() {
  if (!isDirectory(notebooklmChromeProfile)) {
    throw new Error(`NotebookLM Chrome profile not found: ${notebooklmChromeProfile}`);
  }

  const tempProfile = fs.mkdtempSync(path.join(os.tmpdir(), 'notebooklm-playwright-'));
  fs.cpSync(notebooklmChromeProfile, tempProfile, { recursive: true });

  for (const name of ['lockfile', 'SingletonLock', 'SingletonCookie', 'SingletonSocket']) {
    const targetPath = path.join(tempProfile, name);
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

function findSingleMatch(dirPath, pattern, label, required = true) {
  if (!isDirectory(dirPath)) {
    if (required) {
      throw new Error(`Expected directory for ${label}: ${dirPath}`);
    }
    return null;
  }

  const matches = fs
    .readdirSync(dirPath)
    .filter((entry) => pattern.test(entry))
    .sort((left, right) => left.localeCompare(right, 'en'));

  if (matches.length === 0) {
    if (required) {
      throw new Error(`Could not find ${label} in ${dirPath}`);
    }
    return null;
  }

  return path.join(dirPath, matches[0]);
}

export function resolveNotebookSourceFiles(topicDir) {
  const reportsDir = path.join(topicDir, 'reports');
  const notesDir = path.join(topicDir, 'notes');

  const files = [
    findSingleMatch(reportsDir, /_deepresearch\.md$/i, 'deep research markdown'),
    findSingleMatch(reportsDir, /_notebooklm_brief\.md$/i, 'NotebookLM brief markdown', false),
    findSingleMatch(notesDir, /_sources\.md$/i, 'source note markdown', false),
  ].filter(Boolean);

  if (files.length === 0) {
    throw new Error(`No NotebookLM source markdown files found in ${topicDir}`);
  }

  return files;
}

export function sanitizeFileStem(value, fallback = 'state') {
  const cleaned = value.replace(/[^\w-]+/g, '_').replace(/^_+|_+$/g, '');
  return cleaned || fallback;
}
