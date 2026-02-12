param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if ($Clean) {
    if (Test-Path ".\build") { Remove-Item ".\build" -Recurse -Force }
    if (Test-Path ".\dist") { Remove-Item ".\dist" -Recurse -Force }
}

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Virtual environment not found at .\.venv. Create it first."
}

& .\.venv\Scripts\python.exe -m pip install -r .\requirements-build.txt

& .\.venv\Scripts\python.exe -m PyInstaller `
    --name ADM `
    --windowed `
    --onedir `
    --paths . `
    .\run_adm.py

Write-Host ""
Write-Host "Build complete:"
Write-Host "  dist\ADM\ADM.exe"
