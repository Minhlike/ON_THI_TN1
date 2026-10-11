$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$appUrl = 'http://127.0.0.1:8765'
$buildFiles = @('server.py','math_engine.py','content/bank.json','static/app.js','static/index.html','static/style.css')
$buildBytes = New-Object System.IO.MemoryStream
foreach ($name in $buildFiles) {
    $bytes = [System.IO.File]::ReadAllBytes((Join-Path $PSScriptRoot $name))
    $buildBytes.Write($bytes, 0, $bytes.Length)
}
$buildHasher = [System.Security.Cryptography.SHA256]::Create()
$expectedBuild = ([BitConverter]::ToString($buildHasher.ComputeHash($buildBytes.ToArray()))).Replace('-','').ToLowerInvariant()
$buildHasher.Dispose()
$buildBytes.Dispose()
$current = $null
try {
    $current = Invoke-RestMethod "$appUrl/api/bootstrap" -TimeoutSec 2
} catch { }
if ($current) {
    if ($current.bank.sha -ne '75e22524b318039d960b72339afed37b56b492e94d60e5f1e03aada2ddfe7ec6') { throw 'Port 8765 is used by another app.' }
    if ($current.app_build -eq $expectedBuild) {
        Start-Process $appUrl
        exit 0
    }
    # Reuse only the exact loaded build. Stop only a verified launcher-owned PID.
    & (Join-Path $PSScriptRoot 'stop.ps1')
    if (Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue) { throw 'An old TN1 server is still running. Close its terminal before opening again.' }
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
        if ($ready.app_build -eq $expectedBuild) { Start-Process $appUrl; exit 0 }
    } catch { }
    if ($backend.HasExited) { throw "App could not start. See $dataFolder\server-error.log" }
}
throw "App did not start. See $dataFolder\server-error.log"
