from PyQt5.QtWidgets import QMainWindow, QMenuBar, QAction, QMessageBox, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from UI.Elements import Element, AddLayerWindow, LayersWindow, BufferWindow
from Core.View import View
import webbrowser


class UI:
    MAIN_WINDOW_OBJECTS = [(QMenuBar, "menuBar")]

    def __init__(self):
        self.main_window = Element(UI.MAIN_WINDOW_OBJECTS, "UI/GISmin.ui", QMainWindow())
        self.layers_window = LayersWindow("UI/LayersWindow.ui", self.main_window, self)
        self.add_layer_window = AddLayerWindow("UI/AddLayerWindow.ui", self.main_window, self)
        self.buffer_window = BufferWindow("UI/BufferWindow.ui", self.main_window, self)

        self.main_window.element.setCentralWidget(QWebEngineView())

        self.loading_view = None
        self.view = View(self.main_window.element.centralWidget(), ui=self)

        self.initialize_main_content()
        self.initialize_menu_bar()

        self.main_window.element.show()

    def initialize_main_content(self):
        self.layers_window.initialize()
        self.add_layer_window.initialize()
        self.buffer_window.initialize()

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

        self.main_window.element.findChild(QAction, "actionBuffer").triggered. \
            connect(self.show_buffer_window)

        self.main_window.element.findChild(QAction, "actionOpen_geojson_io").triggered.connect(UI.open_geojson_io)

    @staticmethod
    def open_geojson_io():
        webbrowser.open_new_tab("http://geojson.io")

    def new_project(self):
        self.hide_layers_window()
        self.add_layer_window.element.hide()
        self.view = View(self.main_window.element.centralWidget(), ui=self)
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
        else:
            self.save_project_as()

    def save_project_as(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self.main_window.element, "Save File", "",
                                                   "GISmin (*.gismin)", options=options)
        if file_name:
            self.view.save_file_path = file_name
            self.save_project()

    def show_add_layer_window(self):
        self.add_layer_window.show()

    def show_add_raster_layer_window(self):
        self.add_layer_window.show(0)

    def show_add_vector_layer_window(self):
        self.add_layer_window.show(1)

    def show_layers_window(self):
        self.main_window.element.findChild(QAction, "actionLayers_Window").setChecked(True)
        self.layers_window.show()

    def hide_layers_window(self):
        self.main_window.element.findChild(QAction, "actionLayers_Window").setChecked(False)
        self.layers_window.hide()

    def show_buffer_window(self):
        self.buffer_window.show()

    def hide_buffer_window(self):
        self.buffer_window.hide()

    def update_layers_list(self):
        self.layers_window.update_layers_list()
        self.buffer_window.update_layers_list()

    def show_message(self, string, caption, icon, parent=None):
        if parent is None:
            parent = self.main_window.element
        message_box = QMessageBox(parent)
        message_box.setIcon(icon)
        message_box.setText(caption)
        message_box.setInformativeText(string)
        message_box.setWindowTitle(caption)
        message_box.exec_()
