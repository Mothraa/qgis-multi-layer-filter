from qgis.core import QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QInputDialog
from qgis.gui import QgsExpressionBuilderDialog


TRANSLATION_CONTEXT = "QueryBuilder"


class QueryBuilder:
    """Handle QGIS expression builder dialog."""

    def __init__(self, iface):
        self.iface = iface

    def tr(self, message):
        return QCoreApplication.translate(TRANSLATION_CONTEXT, message)

    def open(self, layer_ids, current_expr):
        """Open expression builder and return expression.

        Args:
            layer_ids (set): Selected layer IDs.
            current_expr (str): Current expression.

        Returns:
            str or None: Expression if confirmed, else None.
        """

        layers = [
            QgsProject.instance().mapLayer(lid)
            for lid in layer_ids
            if isinstance(QgsProject.instance().mapLayer(lid), QgsVectorLayer)
        ]

        if not layers:
            return None

        names = [layer.name() for layer in layers]

        name, ok = QInputDialog.getItem(
            None,
            self.tr("Expression builder"),
            self.tr("Reference layer:"),
            names,
            0,
            False
        )

        if not ok:
            return None

        layer = layers[names.index(name)]

        dlg = QgsExpressionBuilderDialog(layer, current_expr, None)

        if dlg.exec():
            expr = dlg.expressionText().strip()

            if expr:
                return expr

        return None