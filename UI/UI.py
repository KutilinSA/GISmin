from PyQt5.QtWidgets import QMainWindow, QListWidget, QPushButton, QComboBox, QMenuBar, QAction, QDialog, QPlainTextEdit,\
    QMessageBox, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from UI.Elements import Element
from Core.Exceptions import LayerAddingException, FileOpeningException
from Core.View import View


class UI:
    MAIN_WINDOW_OBJECTS = [(QMenuBar, "menuBar")]
    LAYERS_WINDOW_OBJECTS = [(QPushButton, "addLayerButton"), (QPushButton, "removeLayerButton"),
                             (QListWidget, "layersList")]
    ADD_LAYER_WINDOW_OBJECTS = [(QPlainTextEdit, "vectorLayerName"), (QPlainTextEdit, "vectorFilePathName"),
                                (QPushButton, "openVectorFileButton"), (QPushButton, "addVectorLayerButton")]

    def __init__(self):
        self.main_window = Element(UI.MAIN_WINDOW_OBJECTS, "UI/GISmin.ui", QMainWindow())
        self.layers_window = Element(UI.LAYERS_WINDOW_OBJECTS, "UI/LayersWindow.ui", QDialog(self.main_window.element))
        self.add_layer_window = Element(UI.ADD_LAYER_WINDOW_OBJECTS, "UI/AddLayerWindow.ui",
                                        QDialog(self.main_window.element))

        self.main_window.element.setCentralWidget(QWebEngineView())

        self.view = View(self.main_window.element.centralWidget())

        self.initialize_main_content()
        self.initialize_menu_bar()

        self.main_window.element.show()

    def initialize_main_content(self):
        # layers window
        self.layers_window.elements["addLayerButton"].clicked.connect(self.open_add_layer_window)
        self.layers_window.elements["removeLayerButton"].clicked.connect(self.remove_layer)
        self.layers_window.element.rejected.connect(self.hide_layers_window)

        # add layer window
        self.add_layer_window.elements["openVectorFileButton"].clicked.connect(self.open_vector_file)
        self.add_layer_window.elements["addVectorLayerButton"].clicked.connect(self.add_vector_layer)

    def open_vector_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.main_window.element, "QFileDialog.getOpenFileName()", "",
                                                   "All Files (*)", options=options)
        if file_name:
            self.add_layer_window.elements["vectorFilePathName"].setPlainText(file_name)

    def initialize_menu_bar(self):
        self.main_window.element.findChild(QAction, "actionLayers_Window").setChecked(False)
        self.main_window.element.findChild(QAction, "actionLayers_Window").toggled.connect(
            lambda checked: self.show_layers_window() if checked else self.hide_layers_window())

    def show_layers_window(self):
        self.layers_window.element.show()
        self.main_window.element.findChild(QAction, "actionLayers_Window").setChecked(True)

    def hide_layers_window(self):
        self.layers_window.element.hide()
        self.main_window.element.findChild(QAction, "actionLayers_Window").setChecked(False)

    def open_add_layer_window(self):
        self.add_layer_window.elements["vectorLayerName"].setPlainText("")
        self.add_layer_window.elements["vectorFilePathName"].setPlainText("")
        self.add_layer_window.element.show()

    def add_map_layer(self):
        try:
            self.view.add_map_layer(self.add_layer_window.elements['mapLayerName'].toPlainText(),
                                    self.add_layer_window.elements['mapTypeBox'].currentText())
        except LayerAddingException as ex:
            self.show_message(ex.message)
        else:
            self.add_layer_window.element.hide()
            self.update_layers_list()

    def add_vector_layer(self):
        try:
            self.view.add_vector_layer(self.add_layer_window.elements['vectorLayerName'].toPlainText(),
                                       self.add_layer_window.elements['vectorFilePathName'].toPlainText())
        except FileOpeningException as ex:
            self.show_message(ex.message)
        except LayerAddingException as ex:
            self.show_message(ex.message)
        else:
            self.add_layer_window.element.hide()
            self.update_layers_list()

    def show_message(self, string):
        message_box = QMessageBox(self.add_layer_window.element)
        message_box.setIcon(QMessageBox.Critical)
        message_box.setText("Error!")
        message_box.setInformativeText(string)
        message_box.setWindowTitle("Error!")
        message_box.exec_()

    def update_layers_list(self):
        self.layers_window.elements["layersList"].clear()
        for layer in self.view.layers:
            self.layers_window.elements["layersList"].addItem(layer.name)

    def remove_layer(self):
        if self.layers_window.elements["layersList"].currentItem() is None:
            return
        self.view.remove_layer(self.layers_window.elements["layersList"].currentItem().text())
        self.update_layers_list()


