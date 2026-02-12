param(
    [string]$OutputFolder = ".\github_upload"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (Test-Path $OutputFolder) {
    Remove-Item $OutputFolder -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputFolder | Out-Null

$excludeDirs = @(
    ".venv",
    "dist",
    "build",
    ".pyi_temp",
    ".pytest_cache",
    "__pycache__"
)
$excludeFiles = @(
    "adm.db",
    "*.log",
    "build_output.log",
    "ADM.spec"
)

$items = Get-ChildItem -Force
foreach ($item in $items) {
    $name = $item.Name
    if ($excludeDirs -contains $name) { continue }
    $skipFile = $false
    foreach ($pattern in $excludeFiles) {
        if ($name -like $pattern) { $skipFile = $true; break }
    }
    if ($skipFile) { continue }

    if ($item.PSIsContainer) {
        robocopy $item.FullName (Join-Path $OutputFolder $name) /E /XD .venv dist build .pyi_temp .pytest_cache __pycache__ /XF adm.db *.log build_output.log ADM.spec > $null
    } else {
        Copy-Item $item.FullName -Destination (Join-Path $OutputFolder $name) -Force
    }
}

Write-Host "Prepared clean upload folder: $OutputFolder"
