"""Translation utilities."""

import os

from qgis.PyQt.QtCore import QCoreApplication, QTranslator


def install_translation(settings, plugin_dir, plugin_name):
    """Load and install plugin translation.

    Args:
        settings: QSettings instance.
        plugin_dir (str): Plugin directory.
        plugin_name (str): Translation file prefix.

    Returns:
        QTranslator | None: Installed translator.
    """
    locale = settings.value("locale/userLocale", "en")[0:2]

    locale_path = os.path.join(
        plugin_dir,
        "i18n",
        f"{plugin_name}_{locale}.qm"
    )

    if not os.path.exists(locale_path):
        return None

    translator = QTranslator()

    if translator.load(locale_path):
        QCoreApplication.installTranslator(translator)
        return translator

    return None


def uninstall_translation(translator):
    """Remove translator.

    Args:
        translator (QTranslator | None): Translator to remove.
    """
    if translator:
        QCoreApplication.removeTranslator(translator)