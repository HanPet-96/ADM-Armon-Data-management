# ADM - Armon Data Management

Offline Windows desktop viewer for BOM-driven article and part traceability.
Current app version: `1.0.0.1`

## Scope (current MVP)
- Scan `Datastruct` folder structure (`BOMS`, `PDF`, `STEP`, `SOP`, `OVERIG`)
- Import BOM Excel (`.xls`, `.xlsx`) into local SQLite
- Search articles and inspect BOM lines
- Link part documents (PDF/STEP/...) via filename heuristics with revision awareness
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

## App icon (Icon.ico)
- Place your icon file here:
  - `Icon.ico` in repo root (`ADM-Armon-Data-management\Icon.ico`)
- The app uses it for:
  - Main window icon
  - Popup/dialog icons (Settings, Part detail, Unlinked docs)
  - Built `ADM.exe` icon (via `build_adm.bat`)

## UI highlights
- Article list with search
- BOM table columns:
  - now shown as expandable BOM tree by `Item No.`
  - `Item`, `Part NR`, `Rev`, `Description`, `Material`, `Finish`, `Qty`, `Type`, `Status`
- Status coloring:
  - `Approved` / `Released`: green
  - `Denied`: red
  - other/empty: orange
- Linked documents + PDF preview pane
- Order workflow:
  - `Add to order` from selected BOM item
  - Optional include of selected subtree (children)
  - Assembly quantity multiplier
  - Sub-BOM references are exploded recursively to leaf parts in order list
  - Double-click on sub-BOM reference opens that referenced BOM
  - `Order list` right-side slide-in panel with `Part NR`, `Rev`, `Qty`
  - Export `XLSX + ZIP` with linked docs for supplier handoff
- `Settings` dialog with folder picker for `Datastruct`
- `Settings` dialog includes `Theme` selector (`light` / `dark`)
- `Settings` dialog includes UI language selector (`English` / `Nederlands`)
- `?` help button opens `README_EXE_GEBRUIK.pdf`
- On first run, the user guide PDF opens automatically once

## GitHub preparation notes
- `.venv`, build artifacts, caches, and local DB files are ignored via `.gitignore`.
- Commit from `Script` as repo root, or copy `Script` content into your repo root.

## Release flow (v1.0.0.1 and later)
1. Run one-click release script:
   - `.\release_one_click.bat 1.0.0.1`
2. Commit + push with GitHub Desktop (or git CLI).
3. Create GitHub Release with tag:
   - `v1.0.0.1`
4. Upload asset:
   - `dist\ADM_v1.0.0.1_portable.zip`

## Automatic update check
- On startup, ADM checks GitHub `latest release` for this repo:
  - `HanPet-96/ADM-Armon-Data-management`
- If the latest tag is higher than the installed app version, ADM shows an update prompt.
- To trigger this for users, publish a new GitHub release with a higher tag, for example:
  - current app: `1.0.0.1`
  - new release tag: `v1.0.0.2`
