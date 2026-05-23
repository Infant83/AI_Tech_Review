param(
  [ValidateSet('login', 'capture', 'status')]
  [string]$Command = 'status',
  [string]$ReviewDir,
  [int]$Screens = 6,
  [int]$WaitMs = 2500,
  [int]$ScrollPx = 1000,
  [int]$InspectPosts = 4,
  [int]$PostWaitMs = 2200,
  [switch]$Headed
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$automationDir = Join-Path $repoRoot '.automation\linkedin-playwright'
$dataDir = Join-Path $automationDir 'Data'
$captureScript = Join-Path $automationDir 'capture_feed.mjs'
$playwrightModule = Join-Path $repoRoot '.automation\notebooklm-playwright\node_modules\playwright\index.mjs'

function Resolve-ChromePath {
  if ($env:CHROME_EXECUTABLE_PATH -and (Test-Path $env:CHROME_EXECUTABLE_PATH)) {
    return $env:CHROME_EXECUTABLE_PATH
  }

  $candidates = @(
    'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
  )

  foreach ($candidate in $candidates) {
    if (Test-Path $candidate) {
      return $candidate
    }
  }

  throw 'Chrome executable not found. Set CHROME_EXECUTABLE_PATH if Chrome is installed in a custom path.'
}

function Show-Status {
  $chrome = @(Get-Process chrome -ErrorAction SilentlyContinue | Select-Object Id, MainWindowTitle)
  $lockNames = @('lockfile', 'SingletonLock', 'SingletonCookie', 'SingletonSocket')
  $locks = @($lockNames | Where-Object { Test-Path (Join-Path $dataDir $_) })

  [pscustomobject]@{
    DedicatedProfileDir = $dataDir
    DedicatedProfileExists = (Test-Path $dataDir)
    DedicatedProfileLocked = ($locks.Count -gt 0)
    LockFiles = if ($locks.Count -gt 0) { $locks -join ', ' } else { '' }
    CaptureScript = $captureScript
    PlaywrightInstalled = (Test-Path $playwrightModule)
    ChromeProcessCount = $chrome.Count
  } | Format-List
}

switch ($Command) {
  'login' {
    $chromePath = Resolve-ChromePath
    New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

    Start-Process -FilePath $chromePath -ArgumentList @(
      "--user-data-dir=$dataDir",
      '--profile-directory=Default',
      '--new-window',
      'https://www.linkedin.com/login'
    ) | Out-Null

    Write-Output "Opened dedicated LinkedIn Chrome profile: $dataDir"
    Write-Output 'Sign into LinkedIn in that window once, then close only that dedicated window before running capture.'
  }

  'capture' {
    if (-not (Test-Path $captureScript)) {
      throw "Capture script not found: $captureScript"
    }
    if (-not (Test-Path $playwrightModule)) {
      throw "Playwright dependency not found at $playwrightModule"
    }

    $nodeArgs = @($captureScript)
    if ($ReviewDir) {
      $nodeArgs += @('--review-dir', $ReviewDir)
    }
    $nodeArgs += @(
      '--screens', $Screens.ToString(),
      '--wait-ms', $WaitMs.ToString(),
      '--scroll-px', $ScrollPx.ToString(),
      '--inspect-posts', $InspectPosts.ToString(),
      '--post-wait-ms', $PostWaitMs.ToString()
    )
    if ($Headed) {
      $nodeArgs += '--headed'
    }

    & node @nodeArgs
    if ($LASTEXITCODE -ne 0) {
      exit $LASTEXITCODE
    }
  }

  'status' {
    Show-Status
  }
}
