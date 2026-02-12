@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"
set "LOG_FILE=%CD%\build_output.log"
echo ==== ADM Build Started %DATE% %TIME% ==== > "!LOG_FILE!"

set "PY_EXE="
if exist ".venv\Scripts\python.exe" set "PY_EXE=.venv\Scripts\python.exe"
if "!PY_EXE!"=="" if exist "..\.venv\Scripts\python.exe" set "PY_EXE=..\.venv\Scripts\python.exe"
if "!PY_EXE!"=="" set "PY_EXE=python"

call "!PY_EXE!" --version >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python executable not found.
  echo [ERROR] Checked: .venv, ..\.venv, and PATH>> "!LOG_FILE!"
  pause
  exit /b 1
)

set "PYI_TEMP_ROOT=%CD%\.pyi_temp"
set "PYI_WORK=%PYI_TEMP_ROOT%\work"
set "PYI_SPEC=%PYI_TEMP_ROOT%\spec"
set "PYI_DIST=%PYI_TEMP_ROOT%\dist"
set "FINAL_DIST=%CD%\dist\ADM_portable"
set "FINAL_EXE=%FINAL_DIST%\ADM.exe"

if exist "%PYI_TEMP_ROOT%" (
  rmdir /s /q "%PYI_TEMP_ROOT%" >nul 2>nul
)
mkdir "%PYI_WORK%" >nul 2>nul
mkdir "%PYI_SPEC%" >nul 2>nul

echo [1/3] Installing build dependencies...
call "!PY_EXE!" -m pip install -r requirements-build.txt >> "!LOG_FILE!" 2>&1
if errorlevel 1 (
  echo [ERROR] Failed to install build dependencies.
  echo [ERROR] Failed to install build dependencies. See: !LOG_FILE!
  type "!LOG_FILE!"
  pause
  exit /b 1
)

echo [2/3] Running PyInstaller build...
if exist "%CD%\Icon.ico" (
  call "!PY_EXE!" -m PyInstaller --noconfirm --noconsole --onedir --name ADM --paths . --collect-all PySide6 --icon "%CD%\Icon.ico" --distpath "%PYI_DIST%" --workpath "%PYI_WORK%" --specpath "%PYI_SPEC%" .\run_adm.py >> "!LOG_FILE!" 2>&1
) else (
  call "!PY_EXE!" -m PyInstaller --noconfirm --noconsole --onedir --name ADM --paths . --collect-all PySide6 --distpath "%PYI_DIST%" --workpath "%PYI_WORK%" --specpath "%PYI_SPEC%" .\run_adm.py >> "!LOG_FILE!" 2>&1
)
if errorlevel 1 (
  echo [ERROR] Build failed.
  echo [ERROR] Build failed. See: !LOG_FILE!
  echo.
  echo Tip: run this from a normal non-admin terminal/session.
  type "!LOG_FILE!"
  pause
  exit /b 1
)

echo [3/4] Preparing distribution folder...
if exist "%FINAL_DIST%" (
  rmdir /s /q "%FINAL_DIST%" >nul 2>nul
)
xcopy /E /I /Y "%PYI_DIST%\ADM" "%FINAL_DIST%" >> "!LOG_FILE!" 2>&1
if errorlevel 1 (
  set "FINAL_DIST=%CD%\dist\ADM_portable_%RANDOM%"
  xcopy /E /I /Y "%PYI_DIST%\ADM" "!FINAL_DIST!" >> "!LOG_FILE!" 2>&1
)
if exist "%CD%\README_EXE_GEBRUIK.pdf" (
  copy /Y "%CD%\README_EXE_GEBRUIK.pdf" "!FINAL_DIST!\README_EXE_GEBRUIK.pdf" >nul
)
if exist "%CD%\README_EXE_GEBRUIK.md" (
  copy /Y "%CD%\README_EXE_GEBRUIK.md" "!FINAL_DIST!\README_EXE_GEBRUIK.md" >nul
)
if exist "%CD%\README.md" (
  copy /Y "%CD%\README.md" "!FINAL_DIST!\README_DEV.md" >nul
)
if exist "%CD%\RELEASE_CHECKLIST_V1.md" (
  copy /Y "%CD%\RELEASE_CHECKLIST_V1.md" "!FINAL_DIST!\RELEASE_CHECKLIST_V1.md" >nul
)
if exist "%CD%\Icon.ico" (
  copy /Y "%CD%\Icon.ico" "!FINAL_DIST!\Icon.ico" >nul
)

echo [4/4] Final checks...
if not exist "!FINAL_EXE!" (
  echo [ERROR] Build finished but ADM.exe not found in output.
  echo [ERROR] Missing output executable>> "!LOG_FILE!"
  echo See log: !LOG_FILE!
  pause
  exit /b 1
)
if not exist "!FINAL_DIST!\README_EXE_GEBRUIK.pdf" (
  echo [WARN] README_EXE_GEBRUIK.pdf not found in Script folder, not copied.
  echo [WARN] README_EXE_GEBRUIK.pdf missing>> "!LOG_FILE!"
)

echo Output: !FINAL_EXE!
echo [OK] Build complete>> "!LOG_FILE!"
echo Log: !LOG_FILE!
echo Done.
pause
exit /b 0
