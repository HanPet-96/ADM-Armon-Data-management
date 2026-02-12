# ADM v1 Release Checklist

## 1) Build And Smoke Test
- [ ] Run `build_adm.bat` from `Script`
- [ ] Confirm output exists: `dist\\ADM_portable\\ADM.exe`
- [ ] Start `ADM.exe` on your own machine
- [ ] Open `Settings` and confirm Datastruct path is correct
- [ ] Run `Re-index` once and confirm no crash
- [ ] Open 3-5 random articles and verify:
  - [ ] BOM table loads
  - [ ] Status colors visible
  - [ ] Linked docs list works
  - [ ] PDF preview works on selected PDF
  - [ ] Assembly tree navigation works

## 2) Stress Dataset Validation
- [ ] Confirm BOM count is as expected (100 total in `Datastruct\\BOMS`)
- [ ] Confirm search responds acceptably with full dataset
- [ ] Toggle test:
  - [ ] `Show subassemblies` OFF -> only top-level shown
  - [ ] `Show subassemblies` ON -> children/subchildren shown

## 3) Runtime Persistence Validation
- [ ] Close and reopen app -> settings still present
- [ ] Reboot Windows and reopen app -> settings still present
- [ ] Confirm files exist in `%APPDATA%\\ADM`:
  - [ ] `settings.json`
  - [ ] `adm.db`
  - [ ] `logs\\adm.log`

## 4) Portable Distribution Test
- [ ] Zip `dist\\ADM_portable` (entire folder)
- [ ] Unzip to a different folder name/location
- [ ] Launch `ADM.exe` from unzipped folder
- [ ] Confirm app still starts and can re-index

## 5) Repo Hygiene Before GitHub Upload
- [ ] Ensure no local runtime data is committed:
  - [ ] `.venv`
  - [ ] `dist`
  - [ ] `build`
  - [ ] local db/log files
- [ ] Confirm `.gitignore` is present
- [ ] Confirm `README.md` is up to date
- [ ] Optional: add 2 screenshots to README after final UI polish

## 6) Release Hand-off Bundle (Internal)
- [ ] Build zip ready: `ADM_portable.zip`
- [ ] Short user instructions included:
  - [ ] Start `ADM.exe`
  - [ ] Set Datastruct path in `Settings`
  - [ ] Click `Re-index`
  - [ ] Use search/article tree/BOM/doc preview
