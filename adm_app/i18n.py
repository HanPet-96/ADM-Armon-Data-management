from __future__ import annotations


LANGUAGES = ("en", "nl")

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "lang_name_en": "English",
        "lang_name_nl": "Dutch",
        "window_title": "ADM - Armon Data Management v{version}",
        "btn_reindex": "Re-index",
        "btn_unlinked": "Unlinked docs",
        "btn_order_list": "Order list",
        "btn_settings": "Settings",
        "btn_help": "?",
        "tooltip_help": "Open user guide",
        "search_placeholder": "Search article / part / description",
        "btn_search": "Search",
        "btn_expand_all": "Expand all",
        "btn_collapse_all": "Collapse all",
        "btn_used_where_article": "Used where",
        "btn_add_to_order": "Add to order",
        "btn_save_bom": "Save BOM",
        "btn_revision_check": "Revision check",
        "lbl_select_article": "Select an article",
        "lbl_docs_article": "Linked documents (article)",
        "lbl_article_image": "Article image",
        "lbl_pdf_preview": "PDF preview",
        "lbl_preview_default": "Select a BOM line with exactly one linked PDF.",
        "lbl_image_preview_default": "Shows the top-level article image (if found).",
        "btn_close": "Close",
        "btn_clear": "Clear",
        "btn_export_xlsx_zip": "Export XLSX + ZIP",
        "order_title": "Order list",
        "order_tbl_part": "Part NR",
        "order_tbl_rev": "Rev",
        "order_tbl_qty": "Qty",
        "bom_col_item": "Item",
        "bom_col_part": "Part NR",
        "bom_col_rev": "Rev",
        "bom_col_desc": "Description",
        "bom_col_material": "Material",
        "bom_col_finish": "Finish",
        "bom_col_qty": "Qty",
        "bom_col_type": "Type",
        "bom_col_status": "Status",
        "article_col_article": "Article",
        "article_col_title": "Title",
        "settings_title": "Settings",
        "settings_section_behavior": "Behavior",
        "settings_section_language": "Language",
        "settings_section_paths": "Paths",
        "settings_datastruct": "Datastruct folder",
        "settings_export_path": "Order export folder",
        "settings_browse": "Browse...",
        "settings_dark_mode": "Dark mode",
        "settings_auto_reindex_startup": "Auto re-index on startup",
        "settings_bom_expand_default": "BOM default: expand all",
        "settings_search_children": "Search in children",
        "settings_pdf_engine": "PDF preview engine",
        "settings_pdf_engine_web": "WebEngine (recommended)",
        "settings_pdf_engine_qtpdf": "QtPdf",
        "settings_language": "Language",
        "settings_developer_mode": "Developer mode",
        "settings_help_dark_mode": "Overrides system style with light or dark mode.",
        "settings_help_auto_reindex_startup": "When enabled, ADM refreshes the index automatically at startup.",
        "settings_help_bom_expand_default": "When enabled, BOM rows open expanded by default.",
        "settings_help_search_children": "When enabled, search also matches part numbers and descriptions in BOM children.",
        "settings_help_pdf_engine": "Choose which embedded PDF preview engine ADM should use.",
        "settings_help_language": "Changes UI language for the full app.",
        "settings_help_developer_mode": "Enables developer-only BOM edit/revision tools (restricted by computer name).",
        "settings_help_datastruct": "Root folder that contains BOMS, PDF, STEP-DXF, SOP, OVERIG and IMAGES.",
        "settings_help_export_path": "If set to an existing folder, order export uses this path directly without asking.",
        "settings_check_updates": "Check for updates",
        "settings_save": "Save",
        "settings_cancel": "Cancel",
        "update_check_title": "Update check",
        "update_check_failed": "Latest version could not be retrieved from GitHub.",
        "update_available_title": "Update available",
        "update_available_msg": "Installed version: {installed}\nLatest version: {latest}\n\nOpen releases page now?",
        "up_to_date_title": "Up to date",
        "up_to_date_msg": "You are on the latest version ({version}).",
        "unlinked_title": "Unlinked documents",
        "unlinked_col_filename": "Filename",
        "unlinked_col_reason": "Reason",
        "unlinked_col_path": "Path",
        "part_title": "Part: {part_number}",
        "part_type": "Part type: {part_type}",
        "part_docs": "Documents",
        "used_where_title": "Article used-where",
        "used_where_target": "Target article: {article}",
        "used_where_open_hint": "Double-click a row to open article.",
        "used_where_no_article_ref": "Selected BOM line is not linked to an article.",
        "used_where_no_parents": "No parent articles found.",
        "used_where_col_level": "Level",
        "used_where_col_article": "Article",
        "used_where_col_title": "Title",
        "used_where_col_via_child": "Via child",
        "used_where_col_via_part": "Via part",
        "used_where_col_via_item": "Via item",
        "used_where_col_qty": "Qty",
        "used_where_col_rev": "Rev",
        "used_where_col_node": "Node",
        "used_where_col_item": "Item",
        "used_where_col_via": "Via",
        "used_where_no_usage": "No usage found for selected item.",
        "used_where_tag_direct": "Direct usage",
        "used_where_tag_parent": "Parent",
        "used_where_via_subassembly": "in subassembly {item}",
        "used_where_via_article": "from article {article}",
        "used_where_related_files": "Related files",
        "order_select_first": "Select a BOM item first.",
        "order_include_title": "What would you like to include?",
        "order_include_label": "Select option:",
        "order_include_selected": "Selected only",
        "order_include_children": "Parts only",
        "order_include_both": "Subs + parts",
        "order_qty_title": "Order quantity",
        "order_qty_label": "How many assemblies to add?",
        "order_added_title": "Order",
        "order_added_msg": "Added {count} leaf part line(s) to order list.{warnings}",
        "order_export_empty": "Order list is empty.",
        "order_export_select_folder": "Select export folder",
        "order_export_done_title": "Order export complete",
        "order_export_done_msg": "XLSX: {xlsx}\nDocs copied: {docs}\nZIP: {zip_path}",
        "order_clear_title": "Clear order list",
        "order_clear_msg": "Clear all items in the order list?",
        "order_remove_parent_title": "Remove parent line",
        "order_remove_parent_msg": "This parent has {count} child line(s). Remove all children too?",
        "settings_invalid_title": "Invalid setting",
        "settings_invalid_empty": "Datastruct folder cannot be empty.",
        "settings_invalid_not_exists": "Selected Datastruct folder does not exist.",
        "settings_saved_title": "Settings saved",
        "settings_saved_reindex": "Datastruct path updated. Re-index now?",
        "reindex_done_title": "Re-index complete",
        "reindex_done_msg": "BOMs: {boms}\nLines: {lines}\nWarnings: {warnings}\nErrors: {errors}",
        "reindex_progress_title": "Re-index",
        "reindex_progress_msg": "ADM is updating the local index. Please wait...",
        "reindex_progress_running": "Re-index in progress...",
        "reindex_progress_done": "Re-index complete.",
        "reindex_progress_failed": "Re-index failed.",
        "help_not_found_title": "User guide not found",
        "help_not_found_msg": "README_EXE_GEBRUIK.pdf was not found next to the app.",
        "help_dialog_title": "ADM Help",
        "help_dialog_markdown": """# ADM - Quick Help

## 1) Select datastruct folder
- On first start, ADM requires a Datastruct folder selection.
- If canceled on first start, ADM closes.
- You can change the folder later in `Settings`.
- Expected subfolders are `BOMS`, `PDF`, `STEP-DXF`, `SOP`, `OVERIG`, and `IMAGES`.

## 2) Re-index
- Use `Re-index` to refresh all BOM and document links.
- Auto re-index on startup can be enabled/disabled in `Settings`.

## 3) Find articles and parts
- Use the search box on the left.
- Search supports article number, part number, and description text.
- `Search in children` can be toggled in `Settings`.

## 4) Read the BOM tree
- Select an article to load its BOM.
- `Expand all` and `Collapse all` control tree visibility.
- Single-click on a parent row expands that dropdown.
- Double-click any BOM row opens `Used where` for that selection.

## 5) Used where
- Shows direct usage and parent-chain usage in a tree view.
- Includes a `Related files` section for the selected usage node.
- Double-click a usage node opens the linked article and selects the linked BOM item.

## 6) Linked documents, article image and PDF preview
- Selecting a BOM line loads linked documents.
- `Article image` shows the top-level article image (if found).
- The image preview stays tied to the selected top-level article.
- The PDF preview automatically shows the first PDF in the list.
- Multi-page PDFs can be navigated directly in the embedded viewer.

## 7) Order list
- Select a BOM item and click `Add to order`.
- Choose what to include: selected item, children, or both.
- Export creates `order_lines.xlsx` and a ZIP with linked docs.
- If `Order export folder` is configured, export uses it directly.

## 8) Settings
- Theme, language, PDF preview engine, and startup behavior are in `Settings`.
- Default order export path is `%USERPROFILE%\\Documents\\ADM-Export`.
- The app remembers settings between restarts.

## 9) Help
- Use `?` in the top-right corner to open this in-app help.
""",
        "preview_no_pdf": "No PDF found in linked documents.",
        "preview_no_image": "No image found in linked documents.",
        "preview_not_pdf": "Selected document is not a PDF.",
        "preview_image_no_selected": "No image selected.",
        "preview_image_failed_load": "Failed to load image preview.",
        "preview_no_selected": "No PDF selected.",
        "preview_component_missing": "PDF preview component is not available in this environment.",
        "preview_failed_load": "Failed to load PDF preview ({result}).",
        "preview_failed_load_generic": "Failed to load PDF preview.",
        "preview_page_label": "Page {page}/{count}",
        "preview_multi_page": "Multiple pages available",
        "save_bom_done_title": "BOM saved",
        "save_bom_done_msg": "Saved and re-indexed.\nBOMs: {boms}\nLines: {lines}\nWarnings: {warnings}\nErrors: {errors}",
        "save_bom_failed_title": "Save failed",
        "save_bom_missing_file": "Source BOM file was not found.",
        "save_bom_xls_unsupported": "Editing .xls files is not supported. Save as .xlsx first.",
        "startup_reindex_title": "Starting ADM",
        "startup_datastruct_title": "Select Datastruct folder",
        "startup_reindex_msg": "ADM is updating the local index. Please wait...",
        "startup_reindex_running": "Re-index in progress...",
        "startup_reindex_done": "Re-index complete.",
        "startup_reindex_failed": "Re-index failed.",
        "startup_reindex_error_title": "Startup re-index failed",
        "startup_reindex_error_msg": "Re-index failed at startup.\n\n{error}",
        "revision_suggest_title": "Revision suggestions",
        "revision_suggest_none": "No revision suggestions found.",
        "revision_col_apply": "Apply",
        "revision_col_item": "Item",
        "revision_col_part": "Part NR",
        "revision_col_current": "Current rev",
        "revision_col_found": "Found rev",
        "root_label": "ROOT",
        "root_type": "article",
        "warn_max_depth": "Maximum subassembly depth reached (20).",
        "warn_missing_subassembly": "Missing subassembly target for {part}.",
        "warn_subassembly_no_lines": "Subassembly article {article_id} has no BOM lines.",
        "warn_cycle_detected": "Cycle detected on article ref {part}.",
        "warn_section": "\n\nWarnings:\n- {items}",
    },
    "nl": {
        "lang_name_en": "Engels",
        "lang_name_nl": "Nederlands",
        "window_title": "ADM - Armon Data Management v{version}",
        "btn_reindex": "Herindexeren",
        "btn_unlinked": "Ongekoppelde docs",
        "btn_order_list": "Bestellijst",
        "btn_settings": "Instellingen",
        "btn_help": "?",
        "tooltip_help": "Gebruikershandleiding openen",
        "search_placeholder": "Zoek op artikel / part / omschrijving",
        "btn_search": "Zoeken",
        "btn_expand_all": "Alles uitklappen",
        "btn_collapse_all": "Alles inklappen",
        "btn_used_where_article": "Waar gebruikt",
        "btn_add_to_order": "Aan bestelling toevoegen",
        "btn_save_bom": "BOM opslaan",
        "btn_revision_check": "Revisiecheck",
        "lbl_select_article": "Selecteer een artikel",
        "lbl_docs_article": "Gekoppelde documenten (artikel)",
        "lbl_article_image": "Artikelafbeelding",
        "lbl_pdf_preview": "PDF voorbeeld",
        "lbl_image_preview_default": "Toont de afbeelding van het top-level artikel (indien gevonden).",
        "lbl_preview_default": "Selecteer een BOM-regel met precies één gekoppelde PDF.",
        "btn_close": "Sluiten",
        "btn_clear": "Wissen",
        "btn_export_xlsx_zip": "Exporteer XLSX + ZIP",
        "order_title": "Bestellijst",
        "order_tbl_part": "Part NR",
        "order_tbl_rev": "Rev",
        "order_tbl_qty": "Aantal",
        "bom_col_item": "Item",
        "bom_col_part": "Part NR",
        "bom_col_rev": "Rev",
        "bom_col_desc": "Omschrijving",
        "bom_col_material": "Materiaal",
        "bom_col_finish": "Afwerking",
        "bom_col_qty": "Aantal",
        "bom_col_type": "Type",
        "bom_col_status": "Status",
        "article_col_article": "Artikel",
        "article_col_title": "Titel",
        "settings_title": "Instellingen",
        "settings_section_behavior": "Gedrag",
        "settings_section_language": "Taal",
        "settings_section_paths": "Paden",
        "settings_datastruct": "Datastruct map",
        "settings_export_path": "Bestel-exportmap",
        "settings_browse": "Bladeren...",
        "settings_dark_mode": "Donkere modus",
        "settings_auto_reindex_startup": "Automatisch herindexeren bij opstarten",
        "settings_bom_expand_default": "BOM standaard: alles uitklappen",
        "settings_search_children": "Zoeken in children",
        "settings_pdf_engine": "PDF preview-engine",
        "settings_pdf_engine_web": "WebEngine (aanbevolen)",
        "settings_pdf_engine_qtpdf": "QtPdf",
        "settings_language": "Taal",
        "settings_developer_mode": "Developer modus",
        "settings_help_dark_mode": "Overschrijft systeemstijl met lichte of donkere modus.",
        "settings_help_auto_reindex_startup": "Als dit aan staat, ververst ADM automatisch de index bij opstarten.",
        "settings_help_bom_expand_default": "Als dit aan staat, wordt de BOM standaard volledig uitgeklapt.",
        "settings_help_search_children": "Als dit aan staat, zoekt de zoekbalk ook op partnummers en omschrijvingen in BOM-children.",
        "settings_help_pdf_engine": "Kies welke ingebouwde PDF-previewengine ADM gebruikt.",
        "settings_help_language": "Wijzigt de UI-taal voor de hele app.",
        "settings_help_developer_mode": "Zet developer-tools aan voor BOM bewerken/revisiecheck (alleen op toegestane pc-namen).",
        "settings_help_datastruct": "Rootmap met BOMS, PDF, STEP-DXF, SOP, OVERIG en IMAGES.",
        "settings_help_export_path": "Als dit een bestaande map is, exporteert de bestellijst direct hierheen zonder extra dialoog.",
        "settings_check_updates": "Controleer updates",
        "settings_save": "Opslaan",
        "settings_cancel": "Annuleren",
        "update_check_title": "Updatecontrole",
        "update_check_failed": "Nieuwste versie kon niet van GitHub worden opgehaald.",
        "update_available_title": "Update beschikbaar",
        "update_available_msg": "Geïnstalleerde versie: {installed}\nNieuwste versie: {latest}\n\nReleasespagina nu openen?",
        "up_to_date_title": "Up-to-date",
        "up_to_date_msg": "Je gebruikt de nieuwste versie ({version}).",
        "unlinked_title": "Ongekoppelde documenten",
        "unlinked_col_filename": "Bestandsnaam",
        "unlinked_col_reason": "Reden",
        "unlinked_col_path": "Pad",
        "part_title": "Part: {part_number}",
        "part_type": "Part type: {part_type}",
        "part_docs": "Documenten",
        "used_where_title": "Artikel waar-gebruikt",
        "used_where_target": "Doelartikel: {article}",
        "used_where_open_hint": "Dubbelklik op een regel om artikel te openen.",
        "used_where_no_article_ref": "Geselecteerde BOM-regel is niet gekoppeld aan een artikel.",
        "used_where_no_parents": "Geen parent-artikelen gevonden.",
        "used_where_col_level": "Niveau",
        "used_where_col_article": "Artikel",
        "used_where_col_title": "Titel",
        "used_where_col_via_child": "Via child",
        "used_where_col_via_part": "Via part",
        "used_where_col_via_item": "Via item",
        "used_where_col_qty": "Aantal",
        "used_where_col_rev": "Rev",
        "used_where_col_node": "Node",
        "used_where_col_item": "Item",
        "used_where_col_via": "Via",
        "used_where_no_usage": "Geen gebruik gevonden voor geselecteerd item.",
        "used_where_tag_direct": "Direct gebruik",
        "used_where_tag_parent": "Parent",
        "used_where_via_subassembly": "in subassembly {item}",
        "used_where_via_article": "uit artikel {article}",
        "used_where_related_files": "Gerelateerde bestanden",
        "order_select_first": "Selecteer eerst een BOM-item.",
        "order_include_title": "Wat wil je toevoegen?",
        "order_include_label": "Kies optie:",
        "order_include_selected": "Alleen selectie",
        "order_include_children": "Alleen parts",
        "order_include_both": "Subs + parts",
        "order_qty_title": "Bestelhoeveelheid",
        "order_qty_label": "Hoeveel assemblies toevoegen?",
        "order_added_title": "Bestelling",
        "order_added_msg": "{count} leaf part regel(s) toegevoegd aan de bestellijst.{warnings}",
        "order_export_empty": "Bestellijst is leeg.",
        "order_export_select_folder": "Kies exportmap",
        "order_export_done_title": "Bestelling geëxporteerd",
        "order_export_done_msg": "XLSX: {xlsx}\nGekopieerde docs: {docs}\nZIP: {zip_path}",
        "order_clear_title": "Bestellijst wissen",
        "order_clear_msg": "Alle items in de bestellijst wissen?",
        "order_remove_parent_title": "Parentregel verwijderen",
        "order_remove_parent_msg": "Deze parent heeft {count} child regel(s). Ook alle children verwijderen?",
        "settings_invalid_title": "Ongeldige instelling",
        "settings_invalid_empty": "Datastruct map mag niet leeg zijn.",
        "settings_invalid_not_exists": "Geselecteerde Datastruct map bestaat niet.",
        "settings_saved_title": "Instellingen opgeslagen",
        "settings_saved_reindex": "Datastruct pad aangepast. Nu herindexeren?",
        "reindex_done_title": "Herindexeren voltooid",
        "reindex_done_msg": "BOMs: {boms}\nRegels: {lines}\nWaarschuwingen: {warnings}\nFouten: {errors}",
        "reindex_progress_title": "Herindexeren",
        "reindex_progress_msg": "ADM werkt de lokale index bij. Even geduld...",
        "reindex_progress_running": "Herindexeren bezig...",
        "reindex_progress_done": "Herindexeren voltooid.",
        "reindex_progress_failed": "Herindexeren mislukt.",
        "help_not_found_title": "Handleiding niet gevonden",
        "help_not_found_msg": "README_EXE_GEBRUIK.pdf is niet gevonden naast de app.",
        "help_dialog_title": "ADM Help",
        "help_dialog_markdown": """# ADM - Korte Handleiding

## 1) Datastruct map kiezen
- Bij eerste start vraagt ADM verplicht om een Datastruct map.
- Als je annuleert bij eerste start, sluit ADM af.
- Je kunt de map later wijzigen via `Instellingen`.
- Verwachte submappen zijn `BOMS`, `PDF`, `STEP-DXF`, `SOP`, `OVERIG` en `IMAGES`.

## 2) Herindexeren
- Gebruik `Herindexeren` om BOM- en documentkoppelingen te vernieuwen.
- Automatisch herindexeren bij opstarten is instelbaar in `Instellingen`.

## 3) Artikelen en parts zoeken
- Gebruik het zoekveld links.
- Zoeken werkt op artikelnummer, partnummer en omschrijving.
- `Zoeken in children` is instelbaar in `Instellingen`.

## 4) BOM-boom lezen
- Selecteer een artikel om de BOM te laden.
- `Alles uitklappen` en `Alles inklappen` sturen de boomweergave.
- Enkelklik op een parentregel klapt die dropdown open.
- Dubbelklik op een BOM-regel opent `Waar gebruikt` voor die selectie.

## 5) Waar gebruikt
- Toont direct gebruik en parent-ketens in een boomweergave.
- Bevat onderin `Gerelateerde bestanden` voor de geselecteerde node.
- Dubbelklik op een usage-node opent het gekoppelde artikel en selecteert de gekoppelde BOM-regel.

## 6) Gekoppelde documenten, artikelafbeelding en PDF-preview
- Bij selectie van een BOM-regel worden gekoppelde documenten geladen.
- `Artikelafbeelding` toont de afbeelding van het top-level artikel (indien gevonden).
- De afbeelding blijft gekoppeld aan het geselecteerde top-level artikel.
- De PDF-preview toont automatisch de eerste PDF uit de lijst.
- Bij meerpagina-PDF's kun je direct navigeren in de ingebouwde viewer.

## 7) Bestellijst
- Selecteer een BOM-item en klik `Aan bestelling toevoegen`.
- Kies wat je wilt opnemen: selectie, children, of beide.
- Export maakt `order_lines.xlsx` en een ZIP met gekoppelde documenten.
- Als `Bestel-exportmap` is ingesteld, exporteert ADM direct daarheen.

## 8) Instellingen
- Thema, taal, PDF-preview-engine en opstartgedrag staan in `Instellingen`.
- Standaard bestelpads is `%USERPROFILE%\\Documents\\ADM-Export`.
- De app onthoudt deze instellingen tussen herstarts.

## 9) Help
- Gebruik `?` rechtsboven om deze in-app help te openen.
""",
        "preview_no_pdf": "Geen PDF gevonden in gekoppelde documenten.",
        "preview_no_image": "Geen afbeelding gevonden in gekoppelde documenten.",
        "preview_not_pdf": "Geselecteerd document is geen PDF.",
        "preview_image_no_selected": "Geen afbeelding geselecteerd.",
        "preview_image_failed_load": "Afbeelding kon niet worden geladen.",
        "preview_no_selected": "Geen PDF geselecteerd.",
        "preview_component_missing": "PDF-previewcomponent is niet beschikbaar in deze omgeving.",
        "preview_failed_load": "PDF preview laden mislukt ({result}).",
        "preview_failed_load_generic": "PDF preview laden mislukt.",
        "preview_page_label": "Pagina {page}/{count}",
        "preview_multi_page": "Meerdere pagina's beschikbaar",
        "save_bom_done_title": "BOM opgeslagen",
        "save_bom_done_msg": "Opgeslagen en hergeindexeerd.\nBOMs: {boms}\nRegels: {lines}\nWaarschuwingen: {warnings}\nFouten: {errors}",
        "save_bom_failed_title": "Opslaan mislukt",
        "save_bom_missing_file": "Bron-BOM-bestand is niet gevonden.",
        "save_bom_xls_unsupported": "Bewerken van .xls-bestanden wordt niet ondersteund. Sla eerst op als .xlsx.",
        "startup_reindex_title": "ADM starten",
        "startup_datastruct_title": "Selecteer Datastruct map",
        "startup_reindex_msg": "ADM werkt de lokale index bij. Even geduld...",
        "startup_reindex_running": "Herindexeren bezig...",
        "startup_reindex_done": "Herindexeren voltooid.",
        "startup_reindex_failed": "Herindexeren mislukt.",
        "startup_reindex_error_title": "Herindexeren bij opstarten mislukt",
        "startup_reindex_error_msg": "Herindexeren bij opstarten is mislukt.\n\n{error}",
        "revision_suggest_title": "Revisiesuggesties",
        "revision_suggest_none": "Geen revisiesuggesties gevonden.",
        "revision_col_apply": "Toepassen",
        "revision_col_item": "Item",
        "revision_col_part": "Part NR",
        "revision_col_current": "Huidige rev",
        "revision_col_found": "Gevonden rev",
        "root_label": "ROOT",
        "root_type": "artikel",
        "warn_max_depth": "Maximale subassembly diepte bereikt (20).",
        "warn_missing_subassembly": "Subassembly-doel ontbreekt voor {part}.",
        "warn_subassembly_no_lines": "Subassembly artikel {article_id} heeft geen BOM-regels.",
        "warn_cycle_detected": "Cycle gedetecteerd op artikelref {part}.",
        "warn_section": "\n\nWaarschuwingen:\n- {items}",
    },
}


def normalize_language(language: str) -> str:
    lang = str(language or "en").lower().strip()
    return lang if lang in LANGUAGES else "en"


def tr(language: str, key: str, **kwargs) -> str:
    lang = normalize_language(language)
    value = TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS["en"].get(key) or key
    try:
        return value.format(**kwargs)
    except Exception:
        return value
