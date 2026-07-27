from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QHBoxLayout
)
from qgis.PyQt.QtCore import Qt
from qgis.core import (
    QgsProject, QgsVectorLayer,
    QgsLayerTreeGroup, QgsLayerTreeLayer
)

from ..qt_utils import qt_check_state, qt_user_role, qt_item_flag


class LayerSelectionDialog(QDialog):

    def __init__(self, iface, selected_layers):
        super().__init__(iface.mainWindow())

        self.iface = iface
        self.layer_selection = set(selected_layers)
        self._is_updating = False

        self.setWindowTitle(self.tr("Layers to filter"))
        self.resize(400, 500)

        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        layout.addWidget(self.tree)

        self._is_updating = True
        root = QgsProject.instance().layerTreeRoot()
        self._populate_tree(root, None)

        tree_root = self.tree.invisibleRootItem()
        self._update_all_parents(tree_root)

        self.tree.expandAll()
        self._is_updating = False

        self.tree.expandAll()
        self.tree.itemChanged.connect(self._on_item_changed)

        buttons_layout = QHBoxLayout()

        select_all_btn = QPushButton(self.tr("Select all"))
        select_visible_btn = QPushButton(self.tr("Active layers"))
        unselect_all_btn = QPushButton(self.tr("Deselect all"))
        validate_btn = QPushButton(self.tr("Validate"))

        select_all_btn.clicked.connect(
            lambda: self._set_all_layers_state(qt_check_state("Checked"))
        )

        unselect_all_btn.clicked.connect(
            lambda: self._set_all_layers_state(qt_check_state("Unchecked"))
        )

        select_visible_btn.clicked.connect(
            self._select_visible_layers
        )

        validate_btn.clicked.connect(self.accept)

        buttons_layout.addWidget(select_all_btn)
        buttons_layout.addWidget(select_visible_btn)
        buttons_layout.addWidget(unselect_all_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(validate_btn)

        layout.addLayout(buttons_layout)

    def get_selection(self):
        selection = set()
        self._collect_selection(self.tree.invisibleRootItem(), selection)
        return selection

    def _set_all_layers_state(self, state):
        self._is_updating = True

        root = self.tree.invisibleRootItem()

        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, state)
            self._set_children_state(item, state)

        self._update_all_parents(root)

        self._is_updating = False

    def _select_visible_layers(self):
        visible_layer_ids = {
            layer.id()
            for layer in self.iface.mapCanvas().layers()
            if isinstance(layer, QgsVectorLayer)
        }

        self._set_all_layers_state(qt_check_state("Unchecked"))

        self._is_updating = True

        root = self.tree.invisibleRootItem()
        self._check_visible_layers_recursive(root, visible_layer_ids)
        self._update_all_parents(root)

        self._is_updating = False

    def _update_all_parents(self, item):
        for i in range(item.childCount()):
            child = item.child(i)
            if child.childCount():
                self._update_all_parents(child)
                self._update_parent_state(child)

    def _check_visible_layers_recursive(self, item, visible_layer_ids):
        for i in range(item.childCount()):
            child = item.child(i)

            layer_id = child.data(0, qt_user_role())

            if layer_id and layer_id in visible_layer_ids:
                child.setCheckState(0, qt_check_state("Checked"))

            self._check_visible_layers_recursive(child, visible_layer_ids)

    def _populate_tree(self, node, parent_item):
        for child in node.children():

            if isinstance(child, QgsLayerTreeGroup):
                item = QTreeWidgetItem([child.name()])
                item.setFlags(item.flags() | qt_item_flag("ItemIsUserCheckable"))
                item.setCheckState(0, qt_check_state("Unchecked"))
                item.setExpanded(True)

                if parent_item is None:
                    self.tree.addTopLevelItem(item)
                else:
                    parent_item.addChild(item)

                self._populate_tree(child, item)

            elif isinstance(child, QgsLayerTreeLayer):
                layer = child.layer()
                if not isinstance(layer, QgsVectorLayer):
                    continue

                item = QTreeWidgetItem([layer.name()])
                item.setFlags(item.flags() | qt_item_flag("ItemIsUserCheckable"))
                item.setData(0, qt_user_role(), layer.id())
                item.setCheckState(
                    0,
                    qt_check_state("Checked") if layer.id() in self.layer_selection else qt_check_state("Unchecked")
                )

                if parent_item is None:
                    self.tree.addTopLevelItem(item)
                else:
                    parent_item.addChild(item)

    def _on_item_changed(self, item, column):
        if self._is_updating:
            return

        self._is_updating = True
        state = item.checkState(0)

        if item.childCount() > 0:
            self._set_children_state(item, state)

        parent = item.parent()
        while parent:
            self._update_parent_state(parent)
            parent = parent.parent()

        self._is_updating = False

    def _set_children_state(self, parent, state):
        for i in range(parent.childCount()):
            child = parent.child(i)
            child.setCheckState(0, state)
            if child.childCount():
                self._set_children_state(child, state)

    def _update_parent_state(self, parent):
        checked = 0
        unchecked = 0
        for i in range(parent.childCount()):
            st = parent.child(i).checkState(0)
            if st == qt_check_state("Checked"):
                checked += 1
            elif st == qt_check_state("Unchecked"):
                unchecked += 1

        if checked and unchecked:
            parent.setCheckState(0, qt_check_state("PartiallyChecked"))
        elif checked:
            parent.setCheckState(0, qt_check_state("Checked"))
        else:
            parent.setCheckState(0, qt_check_state("Unchecked"))

    def _collect_selection(self, item, selection):
        layer_id = item.data(0, qt_user_role())
        if layer_id and item.checkState(0) == qt_check_state("Checked"):
            selection.add(layer_id)

        for i in range(item.childCount()):
            self._collect_selection(item.child(i), selection)
