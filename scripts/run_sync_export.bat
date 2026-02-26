@echo off
setlocal enabledelayedexpansion

REM ==========================================
REM ygo-effect-dsl-etl : sync + export (sample)
REM ==========================================
REM 使い方:
REM   scripts\run_sync_export.bat
REM
REM 前提:
REM   - Python が PATH にある
REM   - venv を使う場合は下の VENV パスを設定
REM ==========================================

REM --- (任意) 仮想環境 ---
set VENV=.venv
if exist "%VENV%\Scripts\activate.bat" (
  call "%VENV%\Scripts\activate.bat"
)

REM --- 実行ログ（追記） ---
set LOGDIR=data\logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

for /f "tokens=1-3 delims=/ " %%a in ("%date%") do (
  set yyyy=%%a
  set mm=%%b
  set dd=%%c
)
set LOGFILE=%LOGDIR%\etl_%yyyy%%mm%%dd%.log

echo [%date% %time%] start sync >> "%LOGFILE%"
python -m ygo_effect_dsl_etl sync >> "%LOGFILE%" 2>&1
if errorlevel 1 (
  echo [%date% %time%] sync failed (exit=%errorlevel%) >> "%LOGFILE%"
  exit /b %errorlevel%
)
echo [%date% %time%] sync ok >> "%LOGFILE%"

echo [%date% %time%] start export >> "%LOGFILE%"
python -m ygo_effect_dsl_etl export >> "%LOGFILE%" 2>&1
if errorlevel 1 (
  echo [%date% %time%] export failed (exit=%errorlevel%) >> "%LOGFILE%"
  exit /b %errorlevel%
)
echo [%date% %time%] export ok >> "%LOGFILE%"

echo Done. Log: %LOGFILE%
exit /b 0
