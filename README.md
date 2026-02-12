# ADM - Armon Data Management

Offline Windows desktop viewer for BOM-driven article and part traceability.
Current app version: `1.0.0.1`

## Scope (current MVP)
- Scan `Datastruct` folder structure (`BOMS`, `PDF`, `STEP`, `SOP`, `OVERIG`)
- Import BOM Excel (`.xls`, `.xlsx`) into local SQLite
- Search articles and inspect BOM lines
- Link part documents (PDF/STEP/...) via filename heuristics with revision awareness
- Show assembly tree (parent-child subassemblies)
- Read-only UI (no source file edits)

## Expected data structure
Point the app to a `Datastruct` root containing:

- `BOMS`
- `PDF`
- `STEP`
- `SOP`
- `OVERIG`

## Runtime storage (persistent)
The app stores runtime data in:

- `%APPDATA%\ADM\settings.json` (saved settings, including Datastruct path)
- `%APPDATA%\ADM\adm.db` (SQLite database)
- `%APPDATA%\ADM\logs\adm.log` (app log)

This persists across app and system restarts.

## Local development setup
From `Script`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the app
```powershell
python -m adm_app
```

Optional:

```powershell
python -m adm_app --reindex
python -m adm_app --reindex --no-ui
```

## Tests
```powershell
python -m pytest -q
```

## Build Windows executable (.exe)
From `Script`:

```powershell
.\scripts\build.ps1 -Clean
```

Output:

- `dist\ADM\ADM.exe`

Portable output used for distribution:

- `dist\ADM_portable\ADM.exe`

Build dependencies are installed from:

- `requirements-build.txt`

## UI highlights
- Article list with search
- Animated toggle to show/hide subassemblies in article list/search
- Assembly tree linked to selected article (root-expanded)
- BOM table columns:
  - `Part NR`, `Rev`, `Description`, `Material`, `Finish`, `Qty`, `Type`, `Status`
- Status coloring:
  - `Approved` / `Released`: green
  - `Denied`: red
  - other/empty: orange
- Linked documents + PDF preview pane
- `Settings` dialog with folder picker for `Datastruct`
- `Settings` dialog includes `Theme` selector (`light` / `dark`)
- `?` help button opens `README_EXE_GEBRUIK.pdf`
- On first run, the user guide PDF opens automatically once

## GitHub preparation notes
- `.venv`, build artifacts, caches, and local DB files are ignored via `.gitignore`.
- Commit from `Script` as repo root, or copy `Script` content into your repo root.

## Release flow (v1.0.0.1 and later)
1. Prepare version files:
   - `.\release_prepare.bat 1.0.0.1`
   - If you omit the argument, default is `1.0.0.1`.
2. Commit + push with GitHub Desktop (or git CLI).
3. Build portable app:
   - `.\build_adm.bat`
4. Zip folder:
   - `dist\ADM_portable`
5. Create GitHub Release with tag:
   - `v1.0.0.1`
