from qgis.core import QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QMessageBox

from .qt_utils import message_box_button_role, message_box_icon


TRANSLATION_CONTEXT = "EditingControl"


class EditingControl:
    """Handle layers in editing mode before applying filters."""

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

    def handle(self, layer_ids):
        """Ensure editing layers are properly handled.

        Args:
            layer_ids (set): IDs of selected layers.

        Returns:
            bool: True if operation can continue, False otherwise.
        """

        modified_layers = []

        for lid in layer_ids:
            layer = QgsProject.instance().mapLayer(lid)

            if not isinstance(layer, QgsVectorLayer):
                continue

            if not layer.isEditable():
                continue

            if not layer.isModified():
                layer.rollBack()
                continue

            modified_layers.append(layer)

        if not modified_layers:
            return True

        names = "\n".join(
            f"→ {layer.name()}"
            for layer in modified_layers
        )

        msg = QMessageBox(self.iface.mainWindow())
        msg.setIcon(message_box_icon("Warning"))
        msg.setWindowTitle(self.tr("Layers in editing mode"))
        msg.setText(
            self.tr(
                "Some layers are currently being edited.\n\n"
                "Close editing mode before continuing:\n\n"
                "{layer_names}"
            ).format(layer_names=names)
        )

        save_btn = msg.addButton(
            self.tr("Exit editing mode and save"),
            message_box_button_role("AcceptRole")
        )

        discard_btn = msg.addButton(
            self.tr("Exit editing mode without saving"),
            message_box_button_role("DestructiveRole")
        )

        cancel_btn = msg.addButton(
            self.tr("Cancel"),
            message_box_button_role("RejectRole")
        )

        msg.exec()

        clicked = msg.clickedButton()

        if clicked == cancel_btn:
            return False

        if clicked == save_btn:

            for layer in modified_layers:

                if not layer.commitChanges():
                    QMessageBox.critical(
                        self.iface.mainWindow(),
                        self.tr("Error"),
                        self.tr("Unable to save layer: {layer_name}").format(
                            layer_name=layer.name()
                        )
                    )
                    return False

        elif clicked == discard_btn:

            for layer in modified_layers:
                layer.rollBack()

        return True