<# 
ygo-effect-dsl-etl : sync + export (sample PowerShell)

Usage:
  powershell -ExecutionPolicy Bypass -File scripts\run_sync_export.ps1

Notes:
- If you use venv, set $VenvPath.
- Writes logs to data\logs\etl_YYYYMMDD.log
#>

$ErrorActionPreference = "Stop"

$VenvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $VenvPath) {
  . $VenvPath
}

$LogDir = "data\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$DateStamp = (Get-Date).ToString("yyyyMMdd")
$LogFile = Join-Path $LogDir ("etl_{0}.log" -f $DateStamp)

function Run-Step($Title, $Command) {
  Add-Content -Path $LogFile -Value ("[{0}] start {1}" -f (Get-Date), $Title)
  try {
    & $Command 2>&1 | Tee-Object -FilePath $LogFile -Append | Out-Null
    Add-Content -Path $LogFile -Value ("[{0}] {1} ok" -f (Get-Date), $Title)
  } catch {
    Add-Content -Path $LogFile -Value ("[{0}] {1} failed: {2}" -f (Get-Date), $Title, $_.Exception.Message)
    throw
  }
}

Run-Step "sync" { python -m ygo_effect_dsl_etl sync }
Run-Step "export" { python -m ygo_effect_dsl_etl export }

Write-Host ("Done. Log: {0}" -f $LogFile)
