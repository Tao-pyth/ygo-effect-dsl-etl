<#
ygo-effect-dsl-etl : sync + export helper
Application logs are written by Python to data/logs/etl_YYYYMMDD.log
#>

$ErrorActionPreference = "Stop"

$VenvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $VenvPath) {
  . $VenvPath
}

Write-Host "Running sync..."
python -m ygo_effect_dsl_etl sync
if ($LASTEXITCODE -ne 0) {
  throw "sync failed (exit=$LASTEXITCODE)"
}

Write-Host "Running export..."
python -m ygo_effect_dsl_etl export
if ($LASTEXITCODE -ne 0) {
  throw "export failed (exit=$LASTEXITCODE)"
}

Write-Host "Done. Check logs in data/logs/etl_YYYYMMDD.log"
