from __future__ import annotations

import os
from pathlib import Path
import sqlite3
import subprocess
import sys

from PySide6.QtCore import QEasingCurve, Property, QPropertyAnimation, QRectF, QSize, QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QAbstractItemView,
    QCheckBox,
)

from . import __version__
from .indexer import run_index
from .settings_store import AppSettings, save_settings
from .search import (
    get_article,
    get_article_by_number,
    get_article_bom_lines,
    get_documents_for_part_revision,
    get_documents_for_link,
    get_child_articles,
    get_parent_articles,
    get_part_detail,
    get_part_usages,
    get_unlinked_documents,
    list_articles,
)
from .update_check import fetch_latest_github_release, is_newer_version

RELEASES_URL = "https://github.com/HanPet-96/ADM-Armon-Data-management/releases"

try:
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtPdfWidgets import QPdfView

    PDF_PREVIEW_AVAILABLE = True
except Exception:
    QPdfDocument = None  # type: ignore[assignment]
    QPdfView = None  # type: ignore[assignment]
    PDF_PREVIEW_AVAILABLE = False


class PartDialog(QDialog):
    def __init__(self, conn: sqlite3.Connection, part_number: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.conn = conn
        self.part = get_part_detail(conn, part_number)
        self.setWindowTitle(f"Part: {part_number}")
        self.resize(760, 420)
        layout = QVBoxLayout(self)

        title = QLabel(
            f"<b>{self.part['part_number'] if self.part else part_number}</b> - {self.part['description'] if self.part and self.part['description'] else ''}"
        )
        layout.addWidget(title)
        layout.addWidget(QLabel(f"Part type: {self.part['part_type'] if self.part and self.part['part_type'] else '-'}"))

        self.usage_table = QTableWidget(0, 5)
        self.usage_table.setHorizontalHeaderLabels(["Article", "Title", "Qty", "Revision", "Material"])
        self.usage_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.usage_table.horizontalHeader().setStretchLastSection(True)
        self.usage_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.usage_table)

        self.docs_list = QListWidget()
        layout.addWidget(QLabel("Documents"))
        layout.addWidget(self.docs_list)

        if self.part:
            usages = get_part_usages(conn, int(self.part["id"]))
            self.usage_table.setRowCount(len(usages))
            for row_idx, row in enumerate(usages):
                values = [
                    row["article_number"],
                    row["title"] or "",
                    "" if row["qty"] is None else str(row["qty"]),
                    row["revision"] or "",
                    row["material"] or "",
                ]
                for col_idx, value in enumerate(values):
                    self.usage_table.setItem(row_idx, col_idx, QTableWidgetItem(value))

            docs = get_documents_for_link(conn, "part", int(self.part["id"]))
            for doc in docs:
                label = doc["filename"]
                if doc["part_revision"]:
                    label = f"{label} (rev {doc['part_revision']})"
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, doc["path"])
                self.docs_list.addItem(item)

        self.docs_list.itemDoubleClicked.connect(lambda item: open_file(item.data(Qt.ItemDataRole.UserRole)))


class UnlinkedDocsDialog(QDialog):
    def __init__(self, conn: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Unlinked documents")
        self.resize(980, 520)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Filename", "Reason", "Path"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        rows = get_unlinked_documents(conn)
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(row["filename"] or ""))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row["link_reason"] or ""))
            path_item = QTableWidgetItem(row["path"] or "")
            path_item.setData(Qt.ItemDataRole.UserRole, row["path"])
            self.table.setItem(row_idx, 2, path_item)
        self.table.itemDoubleClicked.connect(self.open_selected_path)

    def open_selected_path(self, item: QTableWidgetItem) -> None:
        path_item = self.table.item(item.row(), 2)
        if path_item:
            open_file(str(path_item.data(Qt.ItemDataRole.UserRole)))


class ToggleSwitch(QCheckBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._offset = 0.0
        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.stateChanged.connect(self._animate_to_state)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(52, 28)

    def sizeHint(self) -> QSize:
        return QSize(52, 28)

    def hitButton(self, pos) -> bool:  # type: ignore[override]
        return self.contentsRect().contains(pos)

    def _animate_to_state(self) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._offset)
        self._anim.setEndValue(1.0 if self.isChecked() else 0.0)
        self._anim.start()

    def get_offset(self) -> float:
        return self._offset

    def set_offset(self, value: float) -> None:
        self._offset = float(value)
        self.update()

    offset = Property(float, get_offset, set_offset)

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = QRectF(1, 1, self.width() - 2, self.height() - 2)
        track_on = QColor("#97C21E")
        track_off = QColor(130, 130, 130)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_on if self.isChecked() else track_off)
        painter.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)

        margin = 3.0
        knob_d = rect.height() - margin * 2
        x_min = rect.x() + margin
        x_max = rect.right() - margin - knob_d
        knob_x = x_min + (x_max - x_min) * self._offset
        knob_rect = QRectF(knob_x, rect.y() + margin, knob_d, knob_d)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(knob_rect)


class SettingsDialog(QDialog):
    def __init__(self, data_root: str, theme_mode: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(700, 220)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Datastruct folder"))
        row = QHBoxLayout()
        self.data_root_input = QLineEdit(data_root)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_data_root)
        row.addWidget(self.data_root_input)
        row.addWidget(browse_button)
        layout.addLayout(row)

        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Dark mode"))
        self.theme_toggle = ToggleSwitch()
        self.theme_toggle.setChecked(theme_mode.lower() == "dark")
        theme_row.addWidget(self.theme_toggle)
        theme_row.addStretch(1)
        layout.addLayout(theme_row)

        actions = QHBoxLayout()
        self.check_updates_button = QPushButton("Check for updates")
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        self.check_updates_button.clicked.connect(self.check_for_updates_clicked)
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        actions.addWidget(self.check_updates_button)
        actions.addStretch(1)
        actions.addWidget(save_button)
        actions.addWidget(cancel_button)
        layout.addLayout(actions)

    def browse_data_root(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select Datastruct folder", self.data_root_input.text())
        if selected:
            self.data_root_input.setText(selected)

    def selected_data_root(self) -> str:
        return self.data_root_input.text().strip()

    def selected_theme_mode(self) -> str:
        return "dark" if self.theme_toggle.isChecked() else "light"

    def check_for_updates_clicked(self) -> None:
        latest = fetch_latest_github_release()
        if not latest:
            QMessageBox.information(
                self,
                "Update check",
                "Latest version could not be retrieved from GitHub.",
            )
            return
        latest_tag = str(latest.get("tag_name") or "").strip()
        if not latest_tag:
            QMessageBox.information(
                self,
                "Update check",
                "Latest version could not be retrieved from GitHub.",
            )
            return
        if is_newer_version(__version__, latest_tag):
            answer = QMessageBox.question(
                self,
                "Update available",
                f"Installed version: {__version__}\nLatest version: {latest_tag}\n\nOpen releases page now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if answer == QMessageBox.StandardButton.Yes:
                open_file(RELEASES_URL)
            return
        QMessageBox.information(
            self,
            "Up to date",
            f"You are on the latest version ({__version__}).",
        )


class MainWindow(QMainWindow):
    def __init__(
        self,
        conn: sqlite3.Connection,
        data_root: str,
        theme_mode: str = "light",
        has_seen_help: bool = False,
    ) -> None:
        super().__init__()
        self.conn = conn
        self.data_root = data_root
        self.theme_mode = theme_mode if theme_mode in {"light", "dark"} else "light"
        self.has_seen_help = has_seen_help
        self.tree_root_article_id: int | None = None
        self._update_check_done = False
        self.setWindowTitle(f"ADM - Armon Data Management v{__version__}")
        self.resize(1250, 740)

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)

        top_actions = QHBoxLayout()
        self.reindex_button = QPushButton("Re-index")
        self.unlinked_button = QPushButton("Unlinked docs")
        self.settings_button = QPushButton("Settings")
        self.help_button = QPushButton("?")
        self.help_button.setToolTip("Open user guide")
        top_actions.addStretch(1)
        top_actions.addWidget(self.reindex_button)
        top_actions.addWidget(self.unlinked_button)
        top_actions.addWidget(self.settings_button)
        top_actions.addWidget(self.help_button)
        root_layout.addLayout(top_actions)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root_layout.addWidget(splitter)

        left_area = QWidget()
        left_area_layout = QVBoxLayout(left_area)
        left_area_layout.setContentsMargins(0, 0, 0, 0)
        left_controls = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search article / part / description")
        self.search_button = QPushButton("Search")
        self.show_subassemblies_toggle = ToggleSwitch()
        self.show_subassemblies_toggle.setChecked(False)
        self.subassemblies_label = QLabel("Show subassemblies")
        left_controls.addWidget(self.search_input, 1)
        left_controls.addWidget(self.search_button)
        left_controls.addWidget(self.subassemblies_label)
        left_controls.addWidget(self.show_subassemblies_toggle)
        left_area_layout.addLayout(left_controls)

        left_splitter = QSplitter(Qt.Orientation.Horizontal)
        left_area_layout.addWidget(left_splitter)
        splitter.addWidget(left_area)

        self.article_table = QTableWidget(0, 3)
        self.article_table.setHorizontalHeaderLabels(["Article", "Title", "BOM lines"])
        self.article_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.article_table.horizontalHeader().setStretchLastSection(True)
        self.article_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        left_splitter.addWidget(self.article_table)

        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        self.tree_root_label = QLabel("Assembly tree")
        tree_layout.addWidget(self.tree_root_label)
        self.article_tree = QTreeWidget()
        self.article_tree.setHeaderHidden(True)
        tree_layout.addWidget(self.article_tree)
        left_splitter.addWidget(tree_container)

        left_splitter.setStretchFactor(0, 3)
        left_splitter.setStretchFactor(1, 2)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        self.article_title_label = QLabel("Select an article")
        right_layout.addWidget(self.article_title_label)

        self.right_content_splitter = QSplitter(Qt.Orientation.Vertical)
        right_layout.addWidget(self.right_content_splitter)

        bom_container = QWidget()
        bom_layout = QVBoxLayout(bom_container)
        bom_layout.setContentsMargins(0, 0, 0, 0)
        self.bom_table = QTableWidget(0, 8)
        self.bom_table.setHorizontalHeaderLabels(
            ["Part NR", "Rev", "Description", "Material", "Finish", "Qty", "Type", "Status"]
        )
        self.bom_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.bom_table.horizontalHeader().setStretchLastSection(True)
        self.bom_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        bom_layout.addWidget(self.bom_table)
        self.right_content_splitter.addWidget(bom_container)

        docs_area = QWidget()
        docs_area_layout = QVBoxLayout(docs_area)
        docs_area_layout.setContentsMargins(0, 0, 0, 0)
        self.docs_context_label = QLabel("Linked documents (article)")
        self.docs_context_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        docs_area_layout.addWidget(self.docs_context_label)

        docs_preview_splitter = QSplitter(Qt.Orientation.Horizontal)
        docs_area_layout.addWidget(docs_preview_splitter)
        docs_area_layout.setStretch(1, 1)
        self.right_content_splitter.addWidget(docs_area)
        self.right_content_splitter.setStretchFactor(0, 1)
        self.right_content_splitter.setStretchFactor(1, 1)

        docs_list_container = QWidget()
        docs_list_layout = QVBoxLayout(docs_list_container)
        docs_list_layout.setContentsMargins(0, 0, 0, 0)
        self.docs_list = QListWidget()
        docs_list_layout.addWidget(self.docs_list)
        docs_preview_splitter.addWidget(docs_list_container)

        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_title = QLabel("PDF preview")
        preview_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        preview_layout.addWidget(preview_title)
        self.preview_stack = QStackedWidget()
        self.preview_message = QLabel("Select a BOM line with exactly one linked PDF.")
        self.preview_message.setWordWrap(True)
        self.preview_message.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.preview_message.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_stack.addWidget(self.preview_message)
        self.pdf_document = None
        self.pdf_view = None
        if PDF_PREVIEW_AVAILABLE:
            self.pdf_document = QPdfDocument(self)
            self.pdf_view = QPdfView()
            self.pdf_view.setDocument(self.pdf_document)
            self.pdf_view.setPageMode(QPdfView.PageMode.SinglePage)
            self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)
            self.pdf_view.verticalScrollBar().setValue(0)
            self.pdf_view.horizontalScrollBar().setValue(0)
            self.preview_stack.addWidget(self.pdf_view)
        preview_layout.addWidget(self.preview_stack)
        docs_preview_splitter.addWidget(preview_container)
        docs_preview_splitter.setStretchFactor(0, 2)
        docs_preview_splitter.setStretchFactor(1, 3)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        self.search_button.clicked.connect(self.refresh_articles)
        self.search_input.returnPressed.connect(self.refresh_articles)
        self.show_subassemblies_toggle.toggled.connect(lambda _checked: self.refresh_articles())
        self.reindex_button.clicked.connect(self.reindex)
        self.unlinked_button.clicked.connect(self.open_unlinked_docs)
        self.settings_button.clicked.connect(self.open_settings)
        self.help_button.clicked.connect(self.open_help_manual_clicked)
        self.article_table.itemSelectionChanged.connect(self.load_selected_article)
        self.article_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.docs_list.itemDoubleClicked.connect(lambda item: open_file(item.data(Qt.ItemDataRole.UserRole)))
        self.docs_list.itemSelectionChanged.connect(self.preview_selected_document)
        self.bom_table.itemDoubleClicked.connect(self.open_bom_line)
        self.bom_table.itemSelectionChanged.connect(self.load_docs_for_selected_bom_line)

        self.refresh_articles()
        QTimer.singleShot(0, self._set_initial_split_sizes)
        self.apply_theme(self.theme_mode)
        if not self.has_seen_help:
            QTimer.singleShot(250, self.open_help_manual_first_run)
        QTimer.singleShot(900, self.check_for_updates)

    def refresh_articles(self) -> None:
        rows = list_articles(
            self.conn,
            self.search_input.text(),
            top_level_only=not self.show_subassemblies_toggle.isChecked(),
        )
        self.article_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            article_item = QTableWidgetItem(row["article_number"])
            article_item.setData(Qt.ItemDataRole.UserRole, int(row["id"]))
            self.article_table.setItem(row_idx, 0, article_item)
            self.article_table.setItem(row_idx, 1, QTableWidgetItem(row["title"] or ""))
            self.article_table.setItem(row_idx, 2, QTableWidgetItem(str(row["bom_line_count"])))
        if rows:
            self.article_table.selectRow(0)

    def load_selected_article(self) -> None:
        row = self.article_table.currentRow()
        if row < 0:
            return
        article_id_item = self.article_table.item(row, 0)
        if article_id_item is None:
            return
        article_id = article_id_item.data(Qt.ItemDataRole.UserRole)
        if article_id is None:
            return
        self.display_article_by_id(int(article_id))

    def set_tree_root(self, root_article_id: int, selected_article_id: int | None = None) -> None:
        self.tree_root_article_id = root_article_id
        article = get_article(self.conn, root_article_id)
        self.article_tree.clear()
        if not article:
            self.tree_root_label.setText("Assembly tree")
            return
        self.tree_root_label.setText(f"Root: {article['article_number']}")
        root_label = f"{article['article_number']} - {article['title'] or ''}".strip()
        root_item = QTreeWidgetItem([root_label])
        root_item.setData(0, Qt.ItemDataRole.UserRole, int(article["id"]))
        self.article_tree.addTopLevelItem(root_item)
        self._add_tree_children(root_item, int(article["id"]), visited={int(article["id"])})
        self.article_tree.expandAll()
        if selected_article_id is not None:
            self._select_tree_item_by_article_id(root_item, selected_article_id)

    def _add_tree_children(self, parent_item: QTreeWidgetItem, article_id: int, visited: set[int]) -> None:
        children = get_child_articles(self.conn, article_id)
        for child in children:
            child_id = int(child["child_article_id"])
            qty_text = (
                ""
                if child["qty_total"] is None
                else f" x{int(child['qty_total']) if float(child['qty_total']).is_integer() else child['qty_total']}"
            )
            label = f"{child['article_number']} - {child['title'] or ''}{qty_text}".strip()
            item = QTreeWidgetItem([label])
            item.setData(0, Qt.ItemDataRole.UserRole, child_id)
            parent_item.addChild(item)
            if child_id in visited:
                continue
            self._add_tree_children(item, child_id, visited | {child_id})
            item.setExpanded(False)

    def on_tree_item_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        article_id = item.data(0, Qt.ItemDataRole.UserRole)
        if article_id is None:
            return
        if not self.select_article_in_table(int(article_id)):
            self.display_article_by_id(int(article_id))

    def select_article_in_table(self, article_id: int) -> bool:
        for row in range(self.article_table.rowCount()):
            row_item = self.article_table.item(row, 0)
            if row_item is None:
                continue
            if int(row_item.data(Qt.ItemDataRole.UserRole)) == article_id:
                self.article_table.selectRow(row)
                self.article_table.scrollToItem(row_item)
                return True
        return False

    def display_article_by_id(self, article_id: int) -> None:
        article = get_article(self.conn, article_id)
        if not article:
            return
        self.article_title_label.setText(
            f"<b>Article {article['article_number']}</b> - {article['title'] or ''}<br>{article['source_bom_filename'] or ''}"
        )
        lines = get_article_bom_lines(self.conn, article_id)
        self.bom_table.setRowCount(len(lines))
        for row_idx, line in enumerate(lines):
            values = [
                line["part_number"] or "",
                line["revision"] or "",
                line["description"] or "",
                line["material"] or "",
                line["finish"] or "",
                "" if line["qty"] is None else str(line["qty"]),
                line["line_type"] or "",
                line["status"] or "",
            ]
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col_idx == 7:
                    self.apply_status_style(item, value)
                self.bom_table.setItem(row_idx, col_idx, item)
        self.load_article_documents(article_id)
        if lines:
            self.bom_table.selectRow(0)
        tree_root_id = self.find_tree_root_article_id(article_id)
        self.set_tree_root(tree_root_id, selected_article_id=article_id)

    def find_tree_root_article_id(self, article_id: int) -> int:
        current = article_id
        visited: set[int] = set()
        while current not in visited:
            visited.add(current)
            parents = get_parent_articles(self.conn, current)
            if not parents:
                return current
            current = int(parents[0]["parent_article_id"])
        return article_id

    def _select_tree_item_by_article_id(self, item: QTreeWidgetItem, article_id: int) -> bool:
        if int(item.data(0, Qt.ItemDataRole.UserRole)) == article_id:
            self.article_tree.setCurrentItem(item)
            return True
        for idx in range(item.childCount()):
            if self._select_tree_item_by_article_id(item.child(idx), article_id):
                return True
        return False

    def _set_initial_split_sizes(self) -> None:
        total_height = self.right_content_splitter.height()
        if total_height <= 0:
            self.right_content_splitter.setSizes([1, 1])
            return
        half = max(1, total_height // 2)
        self.right_content_splitter.setSizes([half, half])

    def load_article_documents(self, article_id: int) -> None:
        self.docs_context_label.setText("Linked documents (article)")
        self.docs_list.clear()
        docs = get_documents_for_link(self.conn, "article", article_id)
        for doc in docs:
            item = QListWidgetItem(doc["filename"])
            item.setData(Qt.ItemDataRole.UserRole, doc["path"])
            self.docs_list.addItem(item)
        self.preview_first_pdf_in_list()

    def load_docs_for_selected_bom_line(self) -> None:
        selected = self.bom_table.selectedItems()
        if not selected:
            return
        row_idx = selected[0].row()
        part_item = self.bom_table.item(row_idx, 0)
        rev_item = self.bom_table.item(row_idx, 1)
        if not part_item:
            return
        part_number = part_item.text().strip()
        if not part_number:
            return
        part = get_part_detail(self.conn, part_number)
        if not part:
            return
        revision = rev_item.text().strip() if rev_item else None
        docs = get_documents_for_part_revision(self.conn, int(part["id"]), revision)
        self.docs_context_label.setText(
            f"Linked documents (part {part_number}{f', rev {revision}' if revision else ''})"
        )
        self.docs_list.clear()
        for doc in docs:
            label = doc["filename"]
            if doc["part_revision"]:
                label = f"{label} (rev {doc['part_revision']})"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, doc["path"])
            self.docs_list.addItem(item)
        self.preview_first_pdf_in_list()

    def reindex(self) -> None:
        stats = run_index(self.conn, data_root=self._path_to_root())
        self.refresh_articles()
        QMessageBox.information(
            self,
            "Re-index complete",
            f"BOMs: {stats.boms_parsed}\nLines: {stats.lines_imported}\nWarnings: {stats.warnings_count}\nErrors: {stats.errors_count}",
        )

    def _path_to_root(self):
        from pathlib import Path

        return Path(self.data_root).resolve()

    def open_bom_line(self, item: QTableWidgetItem) -> None:
        row = item.row()
        part_item = self.bom_table.item(row, 0)
        if part_item is None:
            return
        part_number = part_item.text().strip()
        if not part_number:
            return
        subassembly_article = get_article_by_number(self.conn, part_number)
        if subassembly_article:
            subassembly_id = int(subassembly_article["id"])
            if not self.select_article_in_table(subassembly_id):
                self.display_article_by_id(subassembly_id)
            return
        dlg = PartDialog(self.conn, part_number, self)
        dlg.exec()

    def open_unlinked_docs(self) -> None:
        dlg = UnlinkedDocsDialog(self.conn, self)
        dlg.exec()

    def open_settings(self) -> None:
        dlg = SettingsDialog(self.data_root, self.theme_mode, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        new_root = dlg.selected_data_root()
        if not new_root:
            QMessageBox.warning(self, "Invalid setting", "Datastruct folder cannot be empty.")
            return
        new_path = Path(new_root)
        if not new_path.exists() or not new_path.is_dir():
            QMessageBox.warning(self, "Invalid setting", "Selected Datastruct folder does not exist.")
            return
        self.data_root = str(new_path.resolve())
        self.theme_mode = dlg.selected_theme_mode()
        save_settings(
            AppSettings(
                data_root=self.data_root,
                theme_mode=self.theme_mode,
                has_seen_help=self.has_seen_help,
            )
        )
        self.apply_theme(self.theme_mode)
        should_reindex = QMessageBox.question(
            self,
            "Settings saved",
            "Datastruct path updated. Re-index now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if should_reindex == QMessageBox.StandardButton.Yes:
            self.reindex()

    def set_preview_message(self, message: str) -> None:
        self.preview_message.setText(message)
        self.preview_stack.setCurrentWidget(self.preview_message)

    def preview_first_pdf_in_list(self) -> None:
        for idx in range(self.docs_list.count()):
            item = self.docs_list.item(idx)
            path = str(item.data(Qt.ItemDataRole.UserRole) or "")
            if Path(path).suffix.lower() == ".pdf":
                self.docs_list.setCurrentRow(idx)
                self.preview_pdf(path)
                return
        self.set_preview_message("No PDF found in linked documents.")

    def preview_selected_document(self) -> None:
        selected = self.docs_list.selectedItems()
        if not selected:
            return
        path = str(selected[0].data(Qt.ItemDataRole.UserRole) or "")
        if Path(path).suffix.lower() != ".pdf":
            self.set_preview_message("Selected document is not a PDF.")
            return
        self.preview_pdf(path)

    def preview_pdf(self, path: str) -> None:
        if not path:
            self.set_preview_message("No PDF selected.")
            return
        if not PDF_PREVIEW_AVAILABLE or self.pdf_document is None or self.pdf_view is None:
            self.set_preview_message("PDF preview component is not available in this environment.")
            return
        load_result = self.pdf_document.load(path)
        no_error = getattr(QPdfDocument.Error, "None_", None)
        if no_error is None:
            no_error = getattr(QPdfDocument.Error, "NoError", None)
        if no_error is not None and load_result != no_error:
            self.set_preview_message(f"Failed to load PDF preview ({load_result}).")
            return
        if no_error is None and str(load_result).lower() not in ("error.none", "none", "noerror", "error.noerror"):
            self.set_preview_message("Failed to load PDF preview.")
            return
        self.pdf_view.verticalScrollBar().setValue(0)
        self.pdf_view.horizontalScrollBar().setValue(0)
        self.preview_stack.setCurrentWidget(self.pdf_view)

    def apply_status_style(self, item: QTableWidgetItem, status_text: str) -> None:
        normalized = (status_text or "").strip().lower()
        item.setForeground(QColor(255, 255, 255))
        if normalized in {"approved", "released"}:
            item.setBackground(QColor(30, 120, 55))
        elif normalized == "denied":
            item.setBackground(QColor(150, 35, 35))
        else:
            item.setBackground(QColor(170, 100, 20))

    def apply_theme(self, theme_mode: str) -> None:
        apply_app_theme(theme_mode)

    def resolve_help_pdf_path(self) -> Path | None:
        candidates = [
            Path(sys.executable).resolve().parent / "README_EXE_GEBRUIK.pdf",
            Path(__file__).resolve().parents[1] / "README_EXE_GEBRUIK.pdf",
            Path.cwd() / "README_EXE_GEBRUIK.pdf",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def open_help_manual_clicked(self) -> None:
        self.open_help_manual(mark_seen=True, show_warning=True)

    def open_help_manual_first_run(self) -> None:
        self.open_help_manual(mark_seen=True, show_warning=True)

    def open_help_manual(self, mark_seen: bool, show_warning: bool) -> None:
        help_pdf = self.resolve_help_pdf_path()
        if help_pdf is None:
            if show_warning:
                QMessageBox.warning(
                    self,
                    "User guide not found",
                    "README_EXE_GEBRUIK.pdf was not found next to the app.",
                )
        else:
            open_file(str(help_pdf))

        if mark_seen and not self.has_seen_help:
            self.has_seen_help = True
            save_settings(
                AppSettings(
                    data_root=self.data_root,
                    theme_mode=self.theme_mode,
                    has_seen_help=True,
                )
            )

    def check_for_updates(self) -> None:
        if self._update_check_done:
            return
        self._update_check_done = True
        latest = fetch_latest_github_release()
        if not latest:
            return
        latest_tag = str(latest.get("tag_name") or "").strip()
        if not latest_tag:
            return
        if not is_newer_version(__version__, latest_tag):
            return
        message = (
            f"Installed version: {__version__}\n"
            f"Latest version: {latest_tag}\n\n"
            "A newer ADM version is available."
        )
        answer = QMessageBox.question(
            self,
            "Update available",
            message + "\n\nOpen releases page now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.Yes:
            open_file(RELEASES_URL)


def apply_app_theme(theme_mode: str) -> None:
    app = QApplication.instance()
    if app is None:
        return
    app.setStyle("Fusion")
    mode = theme_mode if theme_mode in {"light", "dark"} else "light"
    if mode == "dark":
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1E1E1E"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#EDEDED"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#252525"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1E1E1E"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#252525"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#EDEDED"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#F2F2F2"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#2B2B2B"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#F2F2F2"))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#97C21E"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        app.setPalette(palette)
        app.setStyleSheet(
            """
            QLineEdit, QTableWidget, QTreeWidget, QListWidget, QComboBox {
                background: #252525;
                color: #F2F2F2;
                border: 1px solid #3A3A3A;
            }
            QPushButton {
                background: #2B2B2B;
                color: #F2F2F2;
                border: 1px solid #444444;
                padding: 4px 10px;
            }
            QPushButton:hover { background: #333333; }
            QHeaderView::section {
                background: #2F2F2F;
                color: #F2F2F2;
                border: 1px solid #3A3A3A;
                padding: 4px;
            }
            """
        )
        return

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#111111"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#F7F7F7"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#111111"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#111111"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#F3F4F6"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#111111"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#111111"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#97C21E"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#111111"))
    app.setPalette(palette)
    app.setStyleSheet(
        """
        QLineEdit, QTableWidget, QTreeWidget, QListWidget, QComboBox {
            background: #FFFFFF;
            color: #111111;
            border: 1px solid #D1D5DB;
        }
        QPushButton {
            background: #F3F4F6;
            color: #111111;
            border: 1px solid #D1D5DB;
            padding: 4px 10px;
        }
        QPushButton:hover { background: #E5E7EB; }
        QHeaderView::section {
            background: #F9FAFB;
            color: #111111;
            border: 1px solid #D1D5DB;
            padding: 4px;
        }
        """
    )


def open_file(path: str) -> None:
    if not path:
        return
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
        return
    subprocess.run(["xdg-open", path], check=False)


def run_ui(
    conn: sqlite3.Connection,
    data_root: str,
    theme_mode: str = "light",
    has_seen_help: bool = False,
) -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    apply_app_theme(theme_mode)
    win = MainWindow(conn, data_root=data_root, theme_mode=theme_mode, has_seen_help=has_seen_help)
    win.show()
    return app.exec()
