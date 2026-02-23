# ADM - Armon Data Management

Offline Windows desktop app for BOM-driven article, part, and document traceability.

Current app version target in this repo: `1.0.1.1`

## What ADM does
- Scans a local `Datastruct` folder and builds a local SQLite index.
- Imports BOM Excel files (`.xls`, `.xlsx`, `.xlsm`) from `BOMS`.
- Shows article BOMs in a hierarchical tree (`Item No.` based).
- Links documents to parts/articles from filename heuristics.
- Shows linked PDFs in embedded preview.
- Shows top-level article image (if found).
- Supports order-list workflow with `XLSX + ZIP` export.

## Datastruct layout
Point ADM to a root folder containing:

- `BOMS`
- `PDF`
- `STEP-DXF`
- `SOP`
- `OVERIG`
- `IMAGES`

Notes:
- `IMAGES` is used for article images (top-level article context).
- App stores only links/metadata in DB; source files stay in Datastruct.

## Runtime storage (per user)
Stored in `%APPDATA%\ADM`:

- `settings.json`
- `adm.db`
- `logs\adm.log`

## UI behavior (current)
- Article list + search (`article / part / description`).
- BOM tree with `ROOT` node and child hierarchy from `Item No.`.
- Single-click parent row expands dropdown.
- Double-click BOM row opens `Used where`.
- Right side:
  - top-left: `Linked documents`
  - top-right: `Article image` (top-level article only)
  - bottom: `PDF preview`
- Status coloring in BOM:
  - `Approved` / `Released` = green
  - `Denied` = red
  - other/empty = orange

## Order workflow
- `Add to order` from selected BOM row.
- Include options:
  - `Parts only` (default)
  - `Selected only`
  - `Subs + parts`
- Quantity multiplication through parent chain.
- Recursive explode for subassemblies to leaf parts.
- Right-side order drawer with delete-per-line.
- Export creates:
  - `order_lines.xlsx`
  - docs bundle + zip

## Settings
- Datastruct path
- Theme (`light` / `dark`)
- Language (`English` / `Nederlands`)
- PDF preview engine (`WebEngine` / `QtPdf`)
- Auto re-index on startup
- BOM default expand behavior
- Search in children
- Order export path (default `%USERPROFILE%\Documents\ADM-Export`)
- Update check button

## In-app help
- `?` button opens in-app help dialog (no external PDF required).
- On true first run, help opens after valid Datastruct selection.

## Local development
From repo root (`ADM-Armon-Data-Management`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run:

```powershell
python -m adm_app
```

Optional:

```powershell
python -m adm_app --reindex
python -m adm_app --reindex --no-ui
```

Tests:

```powershell
python -m pytest -q
```

## Build (PyInstaller)
Use:

```powershell
.\build_adm.bat
```

Build outputs:
- `dist\ADM\ADM.exe`
- `dist\ADM_portable\...`

## Release flow
1. Prepare + build one-shot:
   - `.\release_one_click.bat X.Y.Z.B`
2. Commit + push.
3. Create GitHub release tag:
   - `vX.Y.Z.B`
4. Upload generated portable zip from `dist`.

## Version check
- App checks GitHub latest release on startup.
- If newer tag exists, user gets update prompt.
- If repo is private, anonymous release lookup will fail.
