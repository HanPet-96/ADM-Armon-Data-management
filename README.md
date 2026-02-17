# ADM - Armon Data Management

Offline Windows desktop viewer for BOM-driven article and part traceability.
Current app version: `1.0.0.4`

## Scope (current MVP)
- Scan `Datastruct` folder structure (`BOMS`, `PDF`, `STEP-DXF`, `SOP`, `OVERIG`)
- Import BOM Excel (`.xls`, `.xlsx`) into local SQLite
- Search articles and inspect BOM lines
- Link part documents (PDF/STEP/DXF/...) via filename heuristics with revision awareness
- Read-only UI (no source file edits)

## Expected data structure
Point the app to a `Datastruct` root containing:

- `BOMS`
- `PDF`
- `STEP-DXF`
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
.\build_adm.bat
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
- BOM view:
  - expandable BOM tree by `Item No.` hierarchy
  - ROOT node for selected article
  - ROOT selected shows article-linked documents
  - double-click sub-BOM reference opens referenced BOM
  - `Item`, `Part NR`, `Rev`, `Description`, `Material`, `Finish`, `Qty`, `Type`, `Status`
- Status coloring:
  - `Approved` / `Released`: green
  - `Denied`: red
  - other/empty: orange
- Linked documents + PDF preview pane
- Order workflow:
  - `Add to order` from selected BOM item
  - Include choice:
    - `Selected only`
    - `Children only`
    - `Selected + children`
  - Assembly quantity multiplier
  - Sub-BOM references are exploded recursively to leaf parts in order list
  - `Order list` right-side animated slide-in panel with backdrop
  - Order list shows `Part NR`, `Rev`, `Qty`
  - Per-line delete button with optional child-delete confirmation
  - Export `XLSX + ZIP` with linked docs for supplier handoff
- `Settings` dialog with folder picker for `Datastruct`
- `Settings` dialog includes `Theme` selector (`light` / `dark`)
- `Settings` dialog includes UI language selector (`English` / `Nederlands`)
- `?` help button opens `README_EXE_GEBRUIK.pdf`
- On first run, the user guide PDF opens automatically once

## GitHub preparation notes
- `.venv`, build artifacts, caches, and local DB files are ignored via `.gitignore`.
- Commit from `Script` as repo root, or copy `Script` content into your repo root.

## Release flow
1. Run one-click release script:
   - `.\release_one_click.bat X.Y.Z.B`
2. Commit + push with GitHub Desktop (or git CLI).
3. Create GitHub Release with tag:
   - `vX.Y.Z.B`
4. Upload asset:
   - `dist\ADM_vX.Y.Z.B_portable.zip`

## Automatic update check
- On startup, ADM checks GitHub `latest release` for this repo:
  - `HanPet-96/ADM-Armon-Data-management`
- If the latest tag is higher than the installed app version, ADM shows an update prompt.
- To trigger this for users, publish a new GitHub release with a higher tag, for example:
  - current app: `1.0.0.4`
  - new release tag: `v1.0.0.5`
