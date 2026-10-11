$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$appUrl = 'http://127.0.0.1:8765'
try {
    $current = Invoke-RestMethod "$appUrl/api/bootstrap" -TimeoutSec 2
    if ($current.bank.sha -eq '75e22524b318039d960b72339afed37b56b492e94d60e5f1e03aada2ddfe7ec6') {
        Start-Process $appUrl
        exit 0
    }
    throw 'Port 8765 is used by another app.'
} catch {
    if ($_.Exception.Message -like '*another app*') { throw }
}
$pythonCandidates = @('python.exe', 'py.exe')
$pythonPath = $null
foreach ($candidate in $pythonCandidates) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) {
        & $cmd.Source -c "import sys; assert sys.version_info >= (3, 10)" 2>$null
        if ($LASTEXITCODE -eq 0) { $pythonPath = $cmd.Source; break }
    }
}
if (-not $pythonPath) {
    $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (Test-Path -LiteralPath $bundledPython) { $pythonPath = $bundledPython }
}
if (-not $pythonPath) { throw 'Python 3.10+ is required. Install Python, then open MO_UNG_DUNG.cmd again.' }
$dataFolder = Join-Path $env:LOCALAPPDATA 'ON_THI_TN1'
New-Item -ItemType Directory -Path $dataFolder -Force | Out-Null
$backend = Start-Process -FilePath $pythonPath -ArgumentList @('-m','study_app.server') -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $dataFolder 'server.log') -RedirectStandardError (Join-Path $dataFolder 'server-error.log')
$backend.Id | Set-Content -LiteralPath (Join-Path $dataFolder 'server.pid')
for ($attempt=0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Milliseconds 300
    try {
        $ready = Invoke-RestMethod "$appUrl/api/bootstrap" -TimeoutSec 1
        if ($ready.bank.sha -eq '75e22524b318039d960b72339afed37b56b492e94d60e5f1e03aada2ddfe7ec6') { Start-Process $appUrl; exit 0 }
    } catch { }
    if ($backend.HasExited) { throw "App could not start. See $dataFolder\server-error.log" }
}
throw "App did not start. See $dataFolder\server-error.log"
