from Core.Exceptions import LayerCreatingException


class Layer:
    def __init__(self, name, layer_type):
        if layer_type not in ['raster', 'vector']:
            raise LayerCreatingException("undefined type of layer")
        self.name = name
        self.type = layer_type

    def to_save(self):
        return self.type


class RasterLayer(Layer):
    def __init__(self, name, data, bounds):
        super().__init__(name, "raster")
        self.data = data
        self.bounds = bounds

    def to_save(self):
        return "%s;%s;%s;%s;%s;%s;%s" % (self.type, self.name, self.data, self.bounds[0][0], self.bounds[0][1],
                                         self.bounds[1][0], self.bounds[1][1])


class VectorLayer(Layer):
    def __init__(self, name, data):
        super().__init__(name, "vector")
        self.data = data

    def to_save(self):
        return "%s;%s;%s" % (self.type, self.name, self.data)
