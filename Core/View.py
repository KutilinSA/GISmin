import folium
from Core.Exceptions import LayerAddingException, MapCreatingException, FileOpeningException
from PyQt5.QtWebEngineWidgets import QWebEngineView
from Core.Layers import VectorLayer
from Core.Templates import DEFAULT_HTML, MAP_CREATION_SCRIPT, OSM_TILE_CREATION_SCRIPT, ADD_TILE_TO_MAP_SCRIPT,\
    GEOJSON_LAYER_CREATION_SCRIPT, GEOJSON_LAYER_ADD_DATA_SCRIPT, REMOVE_LAYER_SCRIPT


class View:
    TILES_STRING_TO_SCRIPT = {"OpenStreetMap": OSM_TILE_CREATION_SCRIPT}

    def __init__(self, window, map_tiles="OpenStreetMap"):
        if map_tiles not in View.TILES_STRING_TO_SCRIPT.keys(): #["OpenStreetMap", "Mapbox Bright", "Mapbox Control Room", "Stamen"]:
            raise MapCreatingException("Undefined map tiles")
        self.layers = []
        self.map_tiles = map_tiles
        self.window = window
        self.window.setHtml(DEFAULT_HTML)
        self.window.loadFinished.connect(self.on_load_finished)

    def on_load_finished(self, status):
        if status:
            self.window.page().runJavaScript(MAP_CREATION_SCRIPT + View.TILES_STRING_TO_SCRIPT[self.map_tiles] +
                                             ADD_TILE_TO_MAP_SCRIPT)

    def has_layer(self, layer_name):
        checker = False
        for layer in self.layers:
            if layer.name == layer_name:
                checker = True
        return checker

    def add_map_layer(self, layer_name, map_type):
        if self.has_layer(layer_name):
            raise LayerAddingException("Layer with this name is already added")

    def add_vector_layer(self, layer_name, file_path):
        if not self.check_layer_name(layer_name):
            raise LayerAddingException("Incorrect layer name")
        if self.has_layer(layer_name):
            raise LayerAddingException("Layer with this name is already added")
        try:
            geo_file = folium.GeoJson(file_path, name=layer_name)
        except Exception:
            raise FileOpeningException("File can't be read!")
        else:
            self.layers.append(VectorLayer(layer_name))
            self.window.page().runJavaScript(GEOJSON_LAYER_CREATION_SCRIPT % (layer_name, layer_name))
            self.window.page().runJavaScript(GEOJSON_LAYER_ADD_DATA_SCRIPT % (layer_name, geo_file.data))

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
