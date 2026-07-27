from qgis.PyQt.QtWidgets import QComboBox
from qgis.PyQt.QtCore import Qt, QCoreApplication
from qgis.PyQt.QtGui import QFont, QColor

from ..qt_utils import qt_item_role, qt_scroll_policy

MAX_HISTORY_DEFAULT = 10
MAX_HISTORY_EXPANDED = 30
MAX_HISTORY_LIMIT = 100

TRANSLATION_CONTEXT = "HistoryManager"


class HistoryComboBox(QComboBox):

    def _visible_rows(self):
        count = self.count()

        if count <= MAX_HISTORY_DEFAULT:
            return count

        if count <= MAX_HISTORY_EXPANDED + 1:
            return count

        return MAX_HISTORY_EXPANDED + 1

    def _compute_height(self):
        view = self.view()
        rows = self._visible_rows()

        if rows <= 0:
            return 0

        row_h = view.sizeHintForRow(0)
        if row_h <= 0:
            row_h = self.fontMetrics().height() + 6

        frame = view.frameWidth() * 2
        return (row_h * rows) + frame + 2

    def showPopup(self):
        view = self.view()

        view.setMinimumHeight(0)
        view.setMaximumHeight(16777215)
        view.setFixedHeight(-1)

        height = self._compute_height()

        if self.count() > MAX_HISTORY_EXPANDED + 1:
            view.setVerticalScrollBarPolicy(qt_scroll_policy("ScrollBarAsNeeded"))
        else:
            view.setVerticalScrollBarPolicy(qt_scroll_policy("ScrollBarAlwaysOff"))

        if height > 0:
            view.setMinimumHeight(height)
            view.setMaximumHeight(height)

        super().showPopup()

        popup = view.window()
        if popup:
            popup.setFixedHeight(height)

    def hidePopup(self):
        view = self.view()
        view.setMinimumHeight(0)
        view.setMaximumHeight(16777215)
        view.setFixedHeight(-1)
        super().hidePopup()


class HistoryManager:
    """Manage expression history for combo box."""

    def __init__(self, combo, settings):
        self.combo = combo
        self.settings = settings
        self.history = self.settings.value(
            "MultiLayerFilterToolbar/history", [], type=list
        )

        # connexion des signaux
        self.combo.activated.connect(self._on_history_selected)

    def tr(self, message):
        """Translate a message.

        Args:
            message (str): Source message.

        Returns:
            str: Translated message.
        """
        return QCoreApplication.translate(TRANSLATION_CONTEXT, message)

    # ---------------- PUBLIC ----------------

    def refresh(self):
        self.combo.blockSignals(True)
        self.combo.clear()

        if len(self.history) <= MAX_HISTORY_DEFAULT:
            self.combo.addItems(self.history)
        else:
            self.combo.addItems(self.history[:MAX_HISTORY_DEFAULT])
            self._add_more_item()

        self.combo.blockSignals(False)

    def update(self, expr):
        if not expr:
            return

        if expr in self.history:
            self.history.remove(expr)

        self.history.insert(0, expr)
        self.history = self.history[:MAX_HISTORY_LIMIT]

        self.settings.setValue(
            "MultiLayerFilterToolbar/history",
            self.history
        )

    # ---------------- INTERNAL ----------------

    def _add_more_item(self):
        self.combo.addItem(self.tr("Show more…"))

        idx = self.combo.count() - 1
        self.combo.setItemData(idx, QColor("gray"), qt_item_role("ForegroundRole"))

        font = QFont()
        font.setItalic(True)
        self.combo.setItemData(idx, font, qt_item_role("FontRole"))

    def _on_history_selected(self, index):
        text = self.combo.itemText(index)

        if text == self.tr("Show more…"):
            self._expand_history()

    def _expand_history(self):
        self.combo.blockSignals(True)

        self.combo.clear()

        if len(self.history) <= MAX_HISTORY_DEFAULT + 1:
            self.combo.addItems(self.history[:MAX_HISTORY_EXPANDED])

            if len(self.history) > MAX_HISTORY_EXPANDED:
                self._add_more_item()
        else:
            self.combo.addItems(self.history[:MAX_HISTORY_LIMIT])

        self.combo.blockSignals(False)

        self.combo.showPopup()