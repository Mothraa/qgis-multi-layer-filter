import os

from qgis.PyQt.QtWidgets import (
    QAction, QToolBar, QMessageBox,
    QWidget, QHBoxLayout, QSplitter,
)
from qgis.PyQt.QtCore import QSettings, QCoreApplication

from .translation import install_translation, uninstall_translation
from .ui.history import HistoryComboBox, HistoryManager
from .ui.layer_selection_dialog import LayerSelectionDialog
from .ui.query_builder import QueryBuilder
from .layer_filter_manager import LayerFilterManager
from .editing_control import EditingControl
from .qt_utils import theme_icon, qt_horizontal, combo_no_insert, qt_size_policy


TRANSLATION_CONTEXT = "MultiLayerFilterToolbar"
SETTINGS_KEY_WIDTH = "MultiLayerFilterToolbar/width"


class MultiLayerFilterToolbar:
    def __init__(self, iface):
        self.iface = iface
        self.toolbar = None
        self.layer_selection = set()
        self.settings = QSettings()
        self._has_active_filter = False
        self.history_manager = None
        self.query_builder = QueryBuilder(self.iface)
        self.layer_filter_manager = LayerFilterManager(self.iface)
        self.editing_control = EditingControl(self.iface)
        self.plugin_dir = os.path.dirname(__file__)

        self.translator = install_translation(
            self.settings,
            self.plugin_dir,
            "multi_layer_filter",
        )

    def tr(self, message):
        return QCoreApplication.translate(
            TRANSLATION_CONTEXT,
            message
        )

    def initGui(self):
        self.toolbar = QToolBar(self.tr("Multi Layer Filter"))
        self.iface.mainWindow().addToolBar(self.toolbar)

        self.config_action = QAction(
            theme_icon("mIconTreeView.svg"),
            "",
            self.iface.mainWindow()
        )
        self.config_action.setToolTip(self.tr("Choose layers to filter"))
        self.config_action.triggered.connect(self.configure_layers)
        self.toolbar.addAction(self.config_action)

        self.builder_action = QAction(
            theme_icon("mIconExpression.svg"),
            "",
            self.iface.mainWindow()
        )
        self.builder_action.setToolTip(self.tr("Expression builder"))
        self.builder_action.triggered.connect(self.open_expression_builder)
        self.builder_action.setEnabled(False)
        self.toolbar.addAction(self.builder_action)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 5, 0)
        layout.setSpacing(2)

        self.splitter = QSplitter(qt_horizontal())

        self.expr_combo = HistoryComboBox()
        self.expr_combo.setEditable(True)
        self.expr_combo.setInsertPolicy(combo_no_insert())
        self.expr_combo.setMinimumWidth(120)
        self.expr_combo.setSizePolicy(
            qt_size_policy("Preferred"),
            qt_size_policy("Preferred")
        )

        expr_input = self.expr_combo.lineEdit()
        expr_input.setPlaceholderText('"field" = \'value\'')
        expr_input.textChanged.connect(self._update_buttons)
        expr_input.returnPressed.connect(self._on_enter_pressed)

        self.splitter.addWidget(self.expr_combo)
        self.splitter.setCollapsible(0, False)

        width = int(self.settings.value(SETTINGS_KEY_WIDTH, 250))
        self.splitter.setSizes([width, 5])
        self.splitter.splitterMoved.connect(self._save_width)

        layout.addWidget(self.splitter)
        self.toolbar.addWidget(container)

        self.apply_action = QAction(
            theme_icon("mActionFilter2.svg"),
            "",
            self.iface.mainWindow()
        )
        self.apply_action.setToolTip(self.tr("Apply filter"))
        self.apply_action.setEnabled(False)
        self.apply_action.triggered.connect(self.apply_filter)
        self.toolbar.addAction(self.apply_action)

        self.clear_action = QAction(
            theme_icon("mActionRemove.svg"),
            "",
            self.iface.mainWindow()
        )
        self.clear_action.setToolTip(self.tr("Clear filter"))
        self.clear_action.setEnabled(False)
        self.clear_action.triggered.connect(self.clear_filter)
        self.toolbar.addAction(self.clear_action)

        self.history_manager = HistoryManager(self.expr_combo, self.settings)
        self.history_manager.refresh()

    def unload(self):
        if self.toolbar:
            self.iface.mainWindow().removeToolBar(self.toolbar)
            self.toolbar.deleteLater()
            self.toolbar = None

        uninstall_translation(self.translator)
        self.translator = None

    # ---------------- UI ----------------

    def _on_enter_pressed(self):
        if not self._ensure_layers_selected():
            return

        self.apply_filter()

    def _save_width(self):
        self.settings.setValue(SETTINGS_KEY_WIDTH, self.splitter.sizes()[0])

    def _current_expr(self):
        return self.expr_combo.currentText().strip()

    def _ensure_layers_selected(self):
        if not self.layer_selection:
            QMessageBox.warning(
                self.iface.mainWindow(),
                self.tr("No layer selected"),
                self.tr("Please select at least one layer before applying a filter.")
            )
            return False
        return True

    def _update_buttons(self):
        expr = self._current_expr()

        has_layers = len(self.layer_selection) > 0

        self.apply_action.setEnabled(bool(expr) and has_layers)
        self.clear_action.setEnabled(self._has_active_filter)
        self.builder_action.setEnabled(has_layers)

    def apply_filter(self):

        if not self._ensure_layers_selected():
            return

        if not self.editing_control.handle(self.layer_selection):
            return

        expr = self._current_expr()
        if not expr:
            return

        applied = self.layer_filter_manager.apply(
            self.layer_selection,
            expr
        )

        self._has_active_filter = applied

        self._update_buttons()

        self.history_manager.update(expr)
        self.history_manager.refresh()

    def clear_filter(self):

        if not self.editing_control.handle(self.layer_selection):
            return

        self.layer_filter_manager.clear(self.layer_selection)

        self._has_active_filter = False

        self._update_buttons()

    def open_expression_builder(self):

        expr = self.query_builder.open(
            self.layer_selection,
            self._current_expr()
        )

        if not expr:
            return

        self.expr_combo.setCurrentText(expr)

        self.apply_filter()

        expr_input = self.expr_combo.lineEdit()
        expr_input.setFocus()
        expr_input.setCursorPosition(len(expr_input.text()))

    def configure_layers(self):

        dlg = LayerSelectionDialog(self.iface, self.layer_selection)

        if dlg.exec():
            self.layer_selection = dlg.get_selection()
            self._update_buttons()