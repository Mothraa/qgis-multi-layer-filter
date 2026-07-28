from qgis.core import (
    QgsProject, QgsVectorLayer,
    QgsExpression, QgsMessageLog
)
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QMessageBox

from .qt_utils import qgis_message_level

TRANSLATION_CONTEXT = "LayerFilterManager"


class LayerFilterManager:
    """Apply and clear filters on multiple QGIS layers."""

    def __init__(self, iface):
        self.iface = iface

    def tr(self, message):
        """Translate a message.

        Args:
            message (str): Source message.

        Returns:
            str: Translated message.
        """
        return QCoreApplication.translate(TRANSLATION_CONTEXT, message)

    def apply(self, layer_ids, expr):
        """Apply filter expression to layers.

        Args:
            layer_ids (set): IDs of selected layers.
            expr (str): Expression string.

        Returns:
            bool: True if at least one filter was applied.
        """

        qexp = QgsExpression(expr)
        if qexp.hasParserError():
            QMessageBox.critical(None, self.tr("Error"), qexp.parserErrorString())
            return False

        applied = False

        for lid in layer_ids:

            layer = QgsProject.instance().mapLayer(lid)

            if not isinstance(layer, QgsVectorLayer):
                continue

            ok = layer.setSubsetString(expr)

            if not ok:

                QgsMessageLog.logMessage(
                    self.tr(
                        'Layer "{layer_name}": invalid expression or missing field.'
                    ).format(layer_name=layer.name()),
                    "MultiLayerFilter",
                    qgis_message_level("Warning")
                )

                continue

            applied = True

        self._refresh_layer_tree()

        return applied

    def clear(self, layer_ids):
        """Clear filter on layers."""

        for lid in layer_ids:
            layer = QgsProject.instance().mapLayer(lid)

            if isinstance(layer, QgsVectorLayer):
                layer.setSubsetString("")

        self._refresh_layer_tree()

    def _refresh_layer_tree(self):
        """Force refresh of layer tree view."""

        view = self.iface.layerTreeView()
        model = view.layerTreeModel()

        if not model:
            return

        top = model.index(0, 0)
        bottom = model.index(model.rowCount() - 1, 0)

        model.dataChanged.emit(top, bottom)