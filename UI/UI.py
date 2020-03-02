from PyQt5.QtWidgets import QMainWindow, QListWidget, QPushButton, QComboBox, QMenuBar, QAction, QDialog,\
    QPlainTextEdit, QMessageBox, QFileDialog, QTabWidget, QDoubleSpinBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from UI.Elements import Element
from Core.Exceptions import LayerAddingException, FileOpeningException
from Core.View import View
import webbrowser


class UI:
    MAIN_WINDOW_OBJECTS = [(QMenuBar, "menuBar")]
    LAYERS_WINDOW_OBJECTS = [(QPushButton, "addLayerButton"), (QPushButton, "removeLayerButton"),
                             (QListWidget, "layersList")]
    ADD_LAYER_WINDOW_OBJECTS = [(QPlainTextEdit, "vectorLayerName"), (QPlainTextEdit, "vectorFilePathName"),
                                (QPushButton, "openVectorFileButton"), (QPushButton, "addVectorLayerButton"),
                                (QTabWidget, "layerTypeTabMenu"), (QPlainTextEdit, "rasterLayerName"),
                                (QPlainTextEdit, "rasterFilePathName"), (QPushButton, "openRasterFileButton"),
                                (QPushButton, "addRasterLayerButton"), (QDoubleSpinBox, "upperBound"),
                                (QDoubleSpinBox, "leftBound"), (QDoubleSpinBox, "lowerBound"),
                                (QDoubleSpinBox, "rightBound")]

    def __init__(self):
        self.main_window = Element(UI.MAIN_WINDOW_OBJECTS, "UI/GISmin.ui", QMainWindow())
        self.layers_window = Element(UI.LAYERS_WINDOW_OBJECTS, "UI/LayersWindow.ui", QDialog(self.main_window.element))
        self.add_layer_window = Element(UI.ADD_LAYER_WINDOW_OBJECTS, "UI/AddLayerWindow.ui",
                                        QDialog(self.main_window.element))

        self.main_window.element.setCentralWidget(QWebEngineView())

        self.loading_view = None
        self.view = View(self.main_window.element.centralWidget())

        self.initialize_main_content()
        self.initialize_menu_bar()

        self.main_window.element.show()

    def initialize_main_content(self):
        # layers window
        self.layers_window.elements["addLayerButton"].clicked.connect(self.show_add_layer_window)
        self.layers_window.elements["removeLayerButton"].clicked.connect(self.remove_layer)
        self.layers_window.element.rejected.connect(self.hide_layers_window)

        # add layer window
        self.add_layer_window.elements["openVectorFileButton"].clicked.connect(self.open_vector_file)
        self.add_layer_window.elements["addVectorLayerButton"].clicked.connect(self.add_vector_layer)
        self.add_layer_window.elements["openRasterFileButton"].clicked.connect(self.open_raster_file)
        self.add_layer_window.elements["addRasterLayerButton"].clicked.connect(self.add_raster_layer)

    def initialize_menu_bar(self):
        self.main_window.element.findChild(QAction, "actionNew_project").triggered.connect(self.new_project)
        self.main_window.element.findChild(QAction, "actionOpen_project").triggered.connect(self.open_project)
        self.main_window.element.findChild(QAction, "actionSave_project").triggered.connect(self.save_project)
        self.main_window.element.findChild(QAction, "actionSave_project_as").triggered.connect(self.save_project_as)
        self.main_window.element.findChild(QAction, "actionLayers_Window").setChecked(False)
        self.main_window.element.findChild(QAction, "actionLayers_Window").toggled.connect(
            lambda checked: self.show_layers_window() if checked else self.hide_layers_window())
        self.main_window.element.findChild(QAction, "actionRaster_Layer").triggered.\
            connect(self.show_add_raster_layer_window)
        self.main_window.element.findChild(QAction, "actionVector_Layer").triggered. \
            connect(self.show_add_vector_layer_window)
        self.main_window.element.findChild(QAction, "actionOpen_geojson_io").triggered.connect(UI.open_geojson_io)

    @staticmethod
    def open_geojson_io():
        webbrowser.open_new_tab("http://geojson.io")

    def new_project(self):
        self.hide_layers_window()
        self.add_layer_window.element.hide()
        self.view = View(self.main_window.element.centralWidget())
        self.update_layers_list()

    def open_project(self):
        self.hide_layers_window()
        self.add_layer_window.element.hide()
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.main_window.element, "Open File", "",
                                                   "GISmin (*.gismin)", options=options)
        if file_name:
            self.loading_view = View(QWebEngineView(), save_file_path=file_name, ui=self)

    def project_opened(self, status, web_engine, error_message=None):
        if status:
            self.main_window.element.setCentralWidget(web_engine)
            self.view = self.loading_view
            self.loading_view = None
            self.update_layers_list()
        else:
            self.show_message(error_message, "Error!", QMessageBox.Critical)

    def save_project(self):
        if self.view.save_file_path is not None:
            self.view.save()
            self.show_message("File saved!", "Success", QMessageBox.Information)
        else:
            self.save_project_as()

    def save_project_as(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self.main_window.element, "Save File", "",
                                                   "GISmin (*.gismin)", options=options)
        if file_name:
            self.view.save_file_path = file_name
            self.view.save()
            self.show_message("File saved!", "Success", QMessageBox.Information)

    def open_vector_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.main_window.element, "Open File", "",
                                                   "GeoJSON (*.geojson)", options=options)
        if file_name:
            self.add_layer_window.elements["vectorFilePathName"].setPlainText(file_name)

    def open_raster_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.main_window.element, "Open File", "",
                                                   "IMG (*.jpeg *.jpg *.tiff *.tif *.bmp *.png)", options=options)
        if file_name:
            self.add_layer_window.elements["rasterFilePathName"].setPlainText(file_name)

    def show_layers_window(self):
        self.layers_window.element.show()
        self.main_window.element.findChild(QAction, "actionLayers_Window").setChecked(True)

    def hide_layers_window(self):
        self.layers_window.element.hide()
        self.main_window.element.findChild(QAction, "actionLayers_Window").setChecked(False)

    def show_add_layer_window(self):
        self.add_layer_window.elements["vectorLayerName"].setPlainText("")
        self.add_layer_window.elements["vectorFilePathName"].setPlainText("")
        self.add_layer_window.elements["rasterLayerName"].setPlainText("")
        self.add_layer_window.elements["rasterFilePathName"].setPlainText("")
        self.add_layer_window.elements["upperBound"].setValue(0.0)
        self.add_layer_window.elements["leftBound"].setValue(0.0)
        self.add_layer_window.elements["lowerBound"].setValue(0.0)
        self.add_layer_window.elements["rightBound"].setValue(0.0)
        self.add_layer_window.element.show()

    def show_add_raster_layer_window(self):
        self.add_layer_window.elements["layerTypeTabMenu"].setCurrentIndex(0)
        self.show_add_layer_window()

    def show_add_vector_layer_window(self):
        self.add_layer_window.elements["layerTypeTabMenu"].setCurrentIndex(1)
        self.show_add_layer_window()

    def add_raster_layer(self):
        try:
            self.view.add_raster_layer(self.add_layer_window.elements['rasterLayerName'].toPlainText(),
                                       self.add_layer_window.elements['rasterFilePathName'].toPlainText(),
                                       (self.add_layer_window.elements["upperBound"].value(),
                                        self.add_layer_window.elements["leftBound"].value()),
                                       (self.add_layer_window.elements["lowerBound"].value(),
                                        self.add_layer_window.elements["rightBound"].value()))
        except FileOpeningException as ex:
            self.show_message(ex.message, "Error!", QMessageBox.Critical)
        except LayerAddingException as ex:
            self.show_message(ex.message, "Error!", QMessageBox.Critical)
        else:
            self.add_layer_window.element.hide()
            self.update_layers_list()

    def add_vector_layer(self):
        try:
            self.view.add_vector_layer(self.add_layer_window.elements['vectorLayerName'].toPlainText(),
                                       self.add_layer_window.elements['vectorFilePathName'].toPlainText())
        except FileOpeningException as ex:
            self.show_message(ex.message, "Error!", QMessageBox.Critical)
        except LayerAddingException as ex:
            self.show_message(ex.message, "Error!", QMessageBox.Critical)
        else:
            self.add_layer_window.element.hide()
            self.update_layers_list()

    def show_message(self, string, caption, icon):
        message_box = QMessageBox(self.add_layer_window.element)
        message_box.setIcon(icon)
        message_box.setText(caption)
        message_box.setInformativeText(string)
        message_box.setWindowTitle(caption)
        message_box.exec_()

    def update_layers_list(self):
        self.layers_window.elements["layersList"].clear()
        for layer in self.view.layers:
            self.layers_window.elements["layersList"].addItem(layer.name)

    def remove_layer(self):
        if self.layers_window.elements["layersList"].currentItem() is not None:
            self.view.remove_layer(self.layers_window.elements["layersList"].currentItem().text())
            self.update_layers_list()


