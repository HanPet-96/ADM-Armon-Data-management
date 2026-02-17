@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"
set "LOG_FILE=%CD%\release_one_click.log"
echo ==== ADM One-Click Release Started %DATE% %TIME% ==== > "!LOG_FILE!"

set "PY_EXE="
if exist ".venv\Scripts\python.exe" set "PY_EXE=.venv\Scripts\python.exe"
if "!PY_EXE!"=="" if exist "..\.venv\Scripts\python.exe" set "PY_EXE=..\.venv\Scripts\python.exe"
if "!PY_EXE!"=="" set "PY_EXE=python"

call "!PY_EXE!" --version >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python executable not found.
  echo [ERROR] Python executable not found.>> "!LOG_FILE!"
  pause
  exit /b 1
)

set "REL_VERSION=%~1"
if "%REL_VERSION%"=="" (
  echo Usage: release_one_click.bat MAJOR.MINOR.PATCH.BUILD
  echo Example: release_one_click.bat 1.0.0.4
  echo [ERROR] Missing version argument.>> "!LOG_FILE!"
  pause
  exit /b 1
)

set "ZIP_FILE=%CD%\dist\ADM_v%REL_VERSION%_portable.zip"

echo [1/5] Prepare version %REL_VERSION%...
call "!PY_EXE!" ".\scripts\release_prepare.py" --version "%REL_VERSION%" >> "!LOG_FILE!" 2>&1
if errorlevel 1 (
  echo [ERROR] Version prepare failed. See !LOG_FILE!
  type "!LOG_FILE!"
  pause
  exit /b 1
)

echo [2/5] Run tests...
call "!PY_EXE!" -m pytest -q >> "!LOG_FILE!" 2>&1
if errorlevel 1 (
  echo [ERROR] Tests failed. See !LOG_FILE!
  type "!LOG_FILE!"
  pause
  exit /b 1
)

echo [3/5] Build app...
set "ADM_NO_PAUSE=1"
call "%CD%\build_adm.bat" >> "!LOG_FILE!" 2>&1
set "ADM_NO_PAUSE="
if errorlevel 1 (
  echo [ERROR] Build failed. See !LOG_FILE!
  type "!LOG_FILE!"
  pause
  exit /b 1
)

if not exist "%CD%\dist\ADM_portable\ADM.exe" (
  echo [ERROR] Build output missing: dist\ADM_portable\ADM.exe
  echo [ERROR] Build output missing.>> "!LOG_FILE!"
  pause
  exit /b 1
)

echo [4/5] Create release zip...
if exist "%ZIP_FILE%" del /f /q "%ZIP_FILE%" >nul 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%CD%\dist\ADM_portable\*' -DestinationPath '%ZIP_FILE%' -Force" >> "!LOG_FILE!" 2>&1
if errorlevel 1 (
  echo [ERROR] Zip creation failed. See !LOG_FILE!
  type "!LOG_FILE!"
  pause
  exit /b 1
)

echo [5/5] Done.
echo.
echo [OK] One-click release finished for v%REL_VERSION%
echo Version updated in:
echo   - adm_app\__init__.py
echo   - version.json
echo Ready assets:
echo   - dist\ADM_portable\ADM.exe
echo   - dist\ADM_v%REL_VERSION%_portable.zip
echo.
echo Next in GitHub Desktop:
echo   1) Review changes
echo   2) Commit message: Release v%REL_VERSION%
echo   3) Push origin
echo   4) Create GitHub release tag: v%REL_VERSION%
echo   5) Upload dist\ADM_v%REL_VERSION%_portable.zip
echo.
echo Log: !LOG_FILE!
pause
exit /b 0
