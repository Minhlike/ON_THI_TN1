$ErrorActionPreference = 'Stop'
$pidFile = Join-Path $env:LOCALAPPDATA 'ON_THI_TN1\server.pid'
if (-not (Test-Path -LiteralPath $pidFile)) { Write-Output 'App is not running from this launcher.'; exit 0 }
$appPid = [int](Get-Content -LiteralPath $pidFile)
$processInfo = Get-CimInstance Win32_Process -Filter "ProcessId=$appPid"
if (-not $processInfo) { Write-Output 'App is already stopped.'; exit 0 }
$ownsPort = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -eq $appPid }
if ($processInfo.CommandLine -notmatch ' -m study_app\.server(?:\s|$)' -or -not $ownsPort) { throw 'PID does not match the TN1 app. No process was stopped.' }
Stop-Process -Id $appPid
Write-Output 'App stopped. Study progress remains saved.'
