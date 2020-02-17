from Core.Exceptions import LayerCreatingException


class Layer:
    def __init__(self, name, layer_type):
        if layer_type not in ['raster', 'vector']:
            raise LayerCreatingException("undefined type of layer")
        self.name = name
        self.type = layer_type


class RasterLayer(Layer):
    def __init__(self, name, bounds):
        super().__init__(name, "raster")
        self.bounds = bounds


class VectorLayer(Layer):
    def __init__(self, name):
        super().__init__(name, "vector")
