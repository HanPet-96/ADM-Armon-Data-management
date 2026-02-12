@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"
set "LOG_FILE=%CD%\build_output.log"
echo ==== ADM Build Started %DATE% %TIME% ==== > "!LOG_FILE!"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Virtual environment not found: .venv
  echo Create it first with: python -m venv .venv
  echo [ERROR] Virtual environment not found: .venv>> "!LOG_FILE!"
  pause
  exit /b 1
)

set "PYI_TEMP_ROOT=%CD%\.pyi_temp"
set "PYI_WORK=%PYI_TEMP_ROOT%\work"
set "PYI_SPEC=%PYI_TEMP_ROOT%\spec"
set "PYI_DIST=%PYI_TEMP_ROOT%\dist"
set "FINAL_DIST=%CD%\dist\ADM_portable"

if exist "%PYI_TEMP_ROOT%" (
  rmdir /s /q "%PYI_TEMP_ROOT%" >nul 2>nul
)
mkdir "%PYI_WORK%" >nul 2>nul
mkdir "%PYI_SPEC%" >nul 2>nul

echo [1/3] Installing build dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements-build.txt >> "!LOG_FILE!" 2>&1
if errorlevel 1 (
  echo [ERROR] Failed to install build dependencies.
  echo [ERROR] Failed to install build dependencies. See: !LOG_FILE!
  type "!LOG_FILE!"
  pause
  exit /b 1
)

echo [2/3] Running PyInstaller build...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --noconsole --onedir --name ADM --paths . --collect-all PySide6 --distpath "%PYI_DIST%" --workpath "%PYI_WORK%" --specpath "%PYI_SPEC%" .\run_adm.py >> "!LOG_FILE!" 2>&1
if errorlevel 1 (
  echo [ERROR] Build failed.
  echo [ERROR] Build failed. See: !LOG_FILE!
  echo.
  echo Tip: run this from a normal non-admin terminal/session.
  type "!LOG_FILE!"
  pause
  exit /b 1
)

echo [3/3] Build complete.
if exist "%FINAL_DIST%" (
  rmdir /s /q "%FINAL_DIST%" >nul 2>nul
)
xcopy /E /I /Y "%PYI_DIST%\ADM" "%FINAL_DIST%" >> "!LOG_FILE!" 2>&1
if errorlevel 1 (
  set "FINAL_DIST=%CD%\dist\ADM_portable_%RANDOM%"
  xcopy /E /I /Y "%PYI_DIST%\ADM" "!FINAL_DIST!" >> "!LOG_FILE!" 2>&1
)

echo Output: !FINAL_DIST!\ADM.exe
echo [OK] Build complete>> "!LOG_FILE!"
echo Log: !LOG_FILE!
type "!LOG_FILE!"
pause
exit /b 0
