from qgis.core import Qgis, QgsApplication
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QComboBox, QSizePolicy, QMessageBox


def theme_icon(name):
    """Return QGIS theme icon."""
    return QgsApplication.getThemeIcon(f"/{name}")

##### methodes pour compatibilité qgis3 et 4 #####

def qt_horizontal():
    try:
        return Qt.Orientation.Horizontal
    except AttributeError:
        return getattr(Qt, "Horizontal")


def combo_no_insert():
    try:
        return QComboBox.InsertPolicy.NoInsert
    except AttributeError:
        return getattr(QComboBox, "NoInsert")


def qt_item_role(name):
    try:
        return getattr(Qt.ItemDataRole, name)
    except AttributeError:
        return getattr(Qt, name)


def qt_scroll_policy(name):
    try:
        return getattr(Qt.ScrollBarPolicy, name)
    except AttributeError:
        return getattr(Qt, name)


def qt_check_state(name):
    try:
        return getattr(Qt.CheckState, name)
    except AttributeError:
        return getattr(Qt, name)


def qt_user_role():
    try:
        return Qt.ItemDataRole.UserRole
    except AttributeError:
        return getattr(Qt, "UserRole")


def qt_size_policy(name):
    try:
        return getattr(QSizePolicy.Policy, name)
    except AttributeError:
        return getattr(QSizePolicy, name)


def qt_item_flag(name):
    try:
        return getattr(Qt.ItemFlag, name)
    except AttributeError:
        return getattr(Qt, name)


def qgis_message_level(name):
    try:
        return getattr(Qgis.MessageLevel, name)
    except AttributeError:
        return getattr(Qgis, name)


def message_box_icon(name):
    try:
        return getattr(QMessageBox.Icon, name)
    except AttributeError:
        return getattr(QMessageBox, name)


def message_box_button_role(name):
    try:
        return getattr(QMessageBox.ButtonRole, name)
    except AttributeError:
        return getattr(QMessageBox, name)