from PyQt5 import uic
from PyQt5.QtWidgets import QPushButton, QTabWidget, QDoubleSpinBox, QDialog, QFileDialog, QMessageBox,\
    QListWidget, QComboBox, QSpinBox, QLineEdit, QCheckBox, QMenu
from Core.Exceptions import FileOpeningException, LayerAddingException, LayerNotFoundException


class Element:
    def __init__(self, elements, ui_path, element_type):
        self.element = element_type
        uic.loadUi(ui_path, self.element)
        self.elements = dict()
        for element in elements:
            self.elements[element[1]] = self.element.findChild(element[0], element[1])


class AddLayerWindow(Element):
    OBJECTS = [(QLineEdit, "vectorLayerName"), (QLineEdit, "vectorFilePathName"),
               (QPushButton, "openVectorFileButton"), (QPushButton, "addVectorLayerButton"),
               (QTabWidget, "layerTypeTabMenu"), (QLineEdit, "rasterLayerName"),
               (QLineEdit, "rasterFilePathName"), (QPushButton, "openRasterFileButton"),
               (QPushButton, "addRasterLayerButton"), (QDoubleSpinBox, "upperBound"),
               (QDoubleSpinBox, "leftBound"), (QDoubleSpinBox, "lowerBound"),
               (QDoubleSpinBox, "rightBound")]

    def __init__(self, ui_path, parent, ui):
        self.parent = parent
        self.ui = ui
        super().__init__(AddLayerWindow.OBJECTS, ui_path, QDialog(self.parent.element))

    def initialize(self):
        self.elements["openVectorFileButton"].clicked.connect(self.open_vector_file)
        self.elements["addVectorLayerButton"].clicked.connect(self.add_vector_layer)
        self.elements["openRasterFileButton"].clicked.connect(self.open_raster_file)
        self.elements["addRasterLayerButton"].clicked.connect(self.add_raster_layer)

    def open_vector_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.parent.element, "Open File", "",
                                                   "GeoJSON (*.geojson)", options=options)
        if file_name:
            self.elements["vectorFilePathName"].setText(file_name)

    def open_raster_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.parent.element, "Open File", "",
                                                   "IMG (*.jpeg *.jpg *.tiff *.tif *.bmp *.png)", options=options)
        if file_name:
            self.elements["rasterFilePathName"].setText(file_name)

    def show(self, tab=0):
        self.elements["layerTypeTabMenu"].setCurrentIndex(tab)
        self.elements["vectorLayerName"].setText("")
        self.elements["vectorFilePathName"].setText("")
        self.elements["rasterLayerName"].setText("")
        self.elements["rasterFilePathName"].setText("")
        self.elements["upperBound"].setValue(0.0)
        self.elements["leftBound"].setValue(0.0)
        self.elements["lowerBound"].setValue(0.0)
        self.elements["rightBound"].setValue(0.0)
        self.element.show()

    def hide(self):
        self.element.hide()

    def add_raster_layer(self):
        try:
            self.ui.view.add_raster_layer(self.elements['rasterLayerName'].text(),
                                          self.elements['rasterFilePathName'].text(),
                                          (self.elements["upperBound"].value(),
                                           self.elements["leftBound"].value()),
                                          (self.elements["lowerBound"].value(),
                                           self.elements["rightBound"].value()))
        except FileOpeningException as ex:
            self.ui.show_message(ex.message, "Error!", QMessageBox.Critical, self.element)
        except LayerAddingException as ex:
            self.ui.show_message(ex.message, "Error!", QMessageBox.Critical, self.element)
        else:
            self.hide()
            self.ui.update_layers_list()

    def add_vector_layer(self):
        try:
            self.ui.view.add_vector_layer(self.elements['vectorLayerName'].text(),
                                          self.elements['vectorFilePathName'].text())
        except FileOpeningException as ex:
            self.ui.show_message(ex.message, "Error!", QMessageBox.Critical, self.element)
        except LayerAddingException as ex:
            self.ui.show_message(ex.message, "Error!", QMessageBox.Critical, self.element)
        else:
            self.hide()
            self.ui.update_layers_list()


class LayersWindow(Element):
    OBJECTS = [(QPushButton, "addLayerButton"), (QPushButton, "removeLayerButton"),
               (QListWidget, "layersList")]

    def __init__(self, ui_path, parent, ui):
        self.parent = parent
        self.ui = ui
        super().__init__(LayersWindow.OBJECTS, ui_path, QDialog(self.parent.element))

    def initialize(self):
        self.elements["addLayerButton"].clicked.connect(self.ui.show_add_layer_window)
        self.elements["removeLayerButton"].clicked.connect(self.remove_layer)
        self.element.rejected.connect(self.hide)

    def show(self):
        self.update_layers_list()
        self.element.show()

    def hide(self):
        self.element.hide()

    def update_layers_list(self):
        self.elements["layersList"].clear()
        for layer in self.ui.view.layers:
            self.elements["layersList"].addItem(layer.name)

    def remove_layer(self):
        if self.elements["layersList"].currentItem() is not None:
            result = QMessageBox.question(self.element, 'Confirmation', "Are you sure?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if result == QMessageBox.No:
                return
            self.ui.view.remove_layer(self.elements["layersList"].currentItem().text())
            self.ui.update_layers_list()


class BufferWindow(Element):
    OBJECTS = [(QComboBox, "layerName"), (QDoubleSpinBox, "distance"), (QSpinBox, "segments"), (QComboBox, "capStyle"),
               (QComboBox, "joinStyle"), (QDoubleSpinBox, "mitreLimit"), (QPushButton, "performButton"),
               (QCheckBox, "resultToAnotherLayer"), (QLineEdit, "resultLayerName")]

    def __init__(self, ui_path, parent, ui):
        self.parent = parent
        self.ui = ui
        super().__init__(BufferWindow.OBJECTS, ui_path, QDialog(self.parent.element))

    def initialize(self):
        self.elements["resultLayerName"].setEnabled(False)
        self.elements["resultToAnotherLayer"].stateChanged.connect(
            lambda state: self.elements["resultLayerName"].setEnabled(True) if state == 2 else
            self.elements["resultLayerName"].setEnabled(False))
        self.elements['performButton'].clicked.connect(self.perform)

    def update_layers_list(self):
        self.elements["layerName"].clear()
        for layer in self.ui.view.layers:
            if layer.type == "vector":
                self.elements["layerName"].addItem(layer.name)

    def show(self):
        self.update_layers_list()
        self.elements["distance"].setValue(0.0)
        self.elements["segments"].setValue(1)
        self.elements["capStyle"].setCurrentIndex(0)
        self.elements["joinStyle"].setCurrentIndex(0)
        self.elements["mitreLimit"].setValue(0.0)
        self.elements["resultToAnotherLayer"].setCheckState(0)
        self.elements["resultLayerName"].setText("")
        self.elements["resultLayerName"].setEnabled(False)
        self.element.show()

    def hide(self):
        self.element.hide()

    def perform(self):
        try:
            layer_name = self.elements['layerName'].currentText()
            distance = self.elements['distance'].value()
            segments = self.elements['segments'].value()
            cap_style = self.elements['capStyle'].currentIndex() + 1
            join_style = self.elements['joinStyle'].currentIndex() + 1
            mitre_limit = self.elements['mitreLimit'].value()
            result_layer_name = None
            if self.elements["resultToAnotherLayer"].checkState() == 2:
                result_layer_name = self.elements["resultLayerName"].text()
                if self.ui.view.has_layer(result_layer_name):
                    result = QMessageBox.question(self.element, 'Confirmation',
                                                  "Result will be added to existing layer",
                                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if result == QMessageBox.No:
                        return
                else:
                    result = QMessageBox.question(self.element, 'Confirmation',
                                                  "Result will be added to new layer",
                                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if result == QMessageBox.No:
                        return
            self.ui.view.buffer_layer(layer_name, distance, segments, cap_style, join_style,
                                      mitre_limit, result_layer_name)
            self.ui.update_layers_list()
            self.hide()
        except LayerNotFoundException as ex:
            self.ui.show_message(ex.message, "Error", QMessageBox.Critical, self.element)
        except LayerAddingException as ex:
            self.ui.show_message(ex.message, "Error", QMessageBox.Critical, self.element)
