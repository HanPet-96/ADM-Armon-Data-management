@echo off
setlocal

cd /d "%~dp0"

set "PY_EXE="
if exist ".venv\Scripts\python.exe" set "PY_EXE=.venv\Scripts\python.exe"
if "%PY_EXE%"=="" if exist "..\.venv\Scripts\python.exe" set "PY_EXE=..\.venv\Scripts\python.exe"
if "%PY_EXE%"=="" set "PY_EXE=python"

set "REL_VERSION=%~1"
if "%REL_VERSION%"=="" set "REL_VERSION=1.0.0.2"

echo Preparing release version %REL_VERSION%...
call "%PY_EXE%" ".\scripts\release_prepare.py" --version "%REL_VERSION%"
if errorlevel 1 (
  echo [ERROR] Release prepare failed. Ensure Python is installed and dependencies are available.
  pause
  exit /b 1
)

echo.
echo [OK] Ready to commit release version %REL_VERSION%.
echo Next steps:
echo   1) Commit changes
echo   2) Build via build_adm.bat
echo   3) Push to GitHub + create release tag v%REL_VERSION%
pause
exit /b 0
