# linkedin-playwright

LinkedIn daily recap automation for this workspace.

## Model
- Login happens in a normal Chrome window using a dedicated Chrome user-data directory.
- Capture happens by cloning that dedicated profile to a temp directory and running Playwright against the clone.
- This avoids using the user's main Chrome profile and avoids OS-level mouse/scroll conflicts during capture.

## Dedicated profile path
- Default persistent profile root:
  - `.automation/linkedin-playwright/Data`

Override with:
- `LINKEDIN_PLAYWRIGHT_DATA_DIR`

## PowerShell wrapper
- `scripts/linkedin_playwright.ps1 login`
- `scripts/linkedin_playwright.ps1 status`
- `scripts/linkedin_playwright.ps1 capture -ReviewDir <daily-review-dir>`

## Typical flow
1. Run `login` once and sign into LinkedIn in the dedicated Chrome window.
2. Close that dedicated Chrome window.
3. Run `capture` against a review package with `notes/` and `reports/`.
