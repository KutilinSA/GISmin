import folium
from Core.Exceptions import LayerAddingException, MapCreatingException, FileOpeningException
from Core.Utilities import image_to_data, split_data_to_blocks
from Core.Layers import VectorLayer, RasterLayer
from Core.Templates import DEFAULT_HTML, MAP_CREATION_SCRIPT, OSM_TILE_CREATION_SCRIPT, ADD_TILE_TO_MAP_SCRIPT,\
    GEOJSON_LAYER_CREATION_SCRIPT, GEOJSON_LAYER_ADD_DATA_SCRIPT, REMOVE_LAYER_SCRIPT, RASTER_LAYER_CREATION_SCRIPT
from PyQt5.QtWebEngineWidgets import QWebEngineScript
from PyQt5.QtCore import QDir, QUrl
import os


class View:
    TILES_STRING_TO_SCRIPT = {"OpenStreetMap": OSM_TILE_CREATION_SCRIPT}

    def __init__(self, window, map_tiles="OpenStreetMap", save_file_path=None, ui=None):
        if map_tiles not in View.TILES_STRING_TO_SCRIPT.keys(): #["OpenStreetMap", "Mapbox Bright", "Mapbox Control Room", "Stamen"]:
            raise MapCreatingException("Undefined map tiles")
        self.layers = []
        self.save_file_path = save_file_path
        self.ui = ui
        self.map_tiles = map_tiles
        self.window = window
        self.window.setHtml(DEFAULT_HTML)
        self.window.loadFinished.connect(self.on_load_finished)

    def on_load_finished(self, status):
        if status:
            if self.save_file_path is None:
                self.window.page().runJavaScript(MAP_CREATION_SCRIPT + View.TILES_STRING_TO_SCRIPT[self.map_tiles] +
                                                 ADD_TILE_TO_MAP_SCRIPT)
            else:
                try:
                    self.load(self.save_file_path)
                except FileOpeningException as ex:
                    self.ui.project_opened(False, self.window, ex.message)
                except MapCreatingException as ex:
                    self.ui.project_opened(False, self.window, ex.message)
                else:
                    self.ui.project_opened(True, self.window)

    def has_layer(self, layer_name):
        checker = False
        for layer in self.layers:
            if layer.name == layer_name:
                checker = True
        return checker

    def add_map_layer(self, layer_name, map_type):
        if self.has_layer(layer_name):
            raise LayerAddingException("Layer with this name is already added")

    def add_raster_layer(self, layer_name, file_path, upper_left_bound, lower_right_bound, data=None):
        if not self.check_layer_name(layer_name):
            raise LayerAddingException("Incorrect layer name")
        if self.has_layer(layer_name):
            raise LayerAddingException("Layer with this name is already added")
        if data is None and not os.path.exists(file_path):
            raise FileOpeningException("File not found!")
        else:
            bounds = [upper_left_bound, lower_right_bound]
            string_bounds = "[[" + str(bounds[0][0]) + ", " + str(bounds[0][1]) + "], [" +\
                            str(bounds[1][0]) + ", " + str(bounds[1][1]) + "]]"
            if data is None:
                data = image_to_data(file_path)
            file = open("create_layer.js", 'w')
            file.writelines(['var createLayerData = "' + data + '";\n1',
                            RASTER_LAYER_CREATION_SCRIPT % (layer_name, string_bounds, layer_name)])
            file.close()
            path = QDir.current().filePath("create_layer.js")
            local = QUrl.fromLocalFile(path).toString()
            self.window.page().runJavaScript('$("head").append("<script src=\'%s\'></script>");' % local)
            self.layers.append(RasterLayer(layer_name, data, bounds))

    def add_vector_layer(self, layer_name, file_path, data=None):
        if not self.check_layer_name(layer_name):
            raise LayerAddingException("Incorrect layer name")
        if self.has_layer(layer_name):
            raise LayerAddingException("Layer with this name is already added")
        if data is None:
            try:
                geo_file = folium.GeoJson(file_path, name=layer_name)
            except Exception:
                raise FileOpeningException("File can't be read!")
            else:
                self.layers.append(VectorLayer(layer_name, geo_file.data))
                self.window.page().runJavaScript(GEOJSON_LAYER_CREATION_SCRIPT % (layer_name, layer_name))
                self.window.page().runJavaScript(GEOJSON_LAYER_ADD_DATA_SCRIPT % (layer_name, geo_file.data))
        else:
            self.layers.append(VectorLayer(layer_name, data))
            self.window.page().runJavaScript(GEOJSON_LAYER_CREATION_SCRIPT % (layer_name, layer_name))
            self.window.page().runJavaScript(GEOJSON_LAYER_ADD_DATA_SCRIPT % (layer_name, data))

    def remove_layer(self, layer_name):
        index_to_delete = None
        for i in range(0, len(self.layers)):
            if self.layers[i].name == layer_name:
                index_to_delete = i
                break
        self.layers.pop(index_to_delete)
        self.window.page().runJavaScript(REMOVE_LAYER_SCRIPT % layer_name)

    @staticmethod
    def check_layer_name(layer_name):
        layer_name = layer_name.replace(" ", "")
        return len(layer_name) > 0

    def load_splitted_data(self, blocks, variable_name):
        self.window.page().runJavaScript("""
            var %s = "";
        """ % variable_name)
        for block in blocks:
            self.window.page().runJavaScript("""
                %s += "%s";
            """ % (variable_name, block))

    def save(self):
        file = open(self.save_file_path, 'w')
        lines = ['[GISmin save]\n', self.map_tiles + "\n"]
        for layer in self.layers:
            lines.append(layer.to_save() + "\n")
        file.writelines(lines)
        file.close()

    def load(self, path):
        try:
            file = open(path, 'r')
        except Exception:
            raise FileOpeningException("File can't be read!")
        try:
            lines = file.readlines()
            if lines[0] != "[GISmin save]\n":
                file.close()
                raise FileOpeningException("File is not save file")
            lines[1] = lines[1].replace("\n", "")
            if lines[1] not in View.TILES_STRING_TO_SCRIPT.keys():  # ["OpenStreetMap", "Mapbox Bright", "Mapbox Control Room", "Stamen"]:
                file.close()
                raise MapCreatingException("Undefined map tiles")
            self.map_tiles = lines[1]
            self.window.page().runJavaScript(MAP_CREATION_SCRIPT + View.TILES_STRING_TO_SCRIPT[self.map_tiles] +
                                             ADD_TILE_TO_MAP_SCRIPT)
            for i in range(2, len(lines)):
                line = lines[i]
                splitted_line = line.split(";")
                splitted_line[-1] = splitted_line[-1].replace("\n", "")
                if splitted_line[0] == "raster":
                    self.add_raster_layer(splitted_line[1], "", [splitted_line[3], splitted_line[4]],
                                          [splitted_line[5], splitted_line[6]], splitted_line[2])
                elif splitted_line[0] == "vector":
                    self.add_vector_layer(splitted_line[1], "", splitted_line[2])
        except Exception:
            file.close()
            raise FileOpeningException("Bad file!")
        file.close()
