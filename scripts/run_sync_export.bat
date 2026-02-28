@echo off
setlocal

REM ygo-effect-dsl-etl : sync + export helper
REM Application logs are written by Python to data\logs\etl_YYYYMMDD.log

set VENV=.venv
if exist "%VENV%\Scripts\activate.bat" (
  call "%VENV%\Scripts\activate.bat"
)

set LOGDIR=data\logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

echo Running sync...
python -m ygo_effect_dsl_etl sync
if errorlevel 1 (
  echo sync failed (exit=%errorlevel%)
  exit /b %errorlevel%
)

echo Running export...
python -m ygo_effect_dsl_etl export
if errorlevel 1 (
  echo export failed (exit=%errorlevel%)
  exit /b %errorlevel%
)

echo Done. Check logs in data\logs\etl_YYYYMMDD.log
exit /b 0
