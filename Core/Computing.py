from shapely.geometry import shape, mapping
from Core.Layers import VectorLayer
from Core.Exceptions import NotVectorLayer
import geojson


def buffer(layer, distance, segments=1, cap_style=1, join_style=1, mitre_limit=1.0):
    if type(layer) is not VectorLayer:
        raise NotVectorLayer("Layer is not the vector layer!")
    if layer.type != "vector":
        raise NotVectorLayer("Layer type is not vector")
    geo_data = geojson.loads(layer.data)
    for feature in geo_data['features']:
        shapely_feature = shape(feature['geometry'])
        shapely_feature = shapely_feature.buffer(distance, resolution=segments, cap_style=cap_style,
                                                 join_style=join_style, mitre_limit=mitre_limit)
        mapped_feature = mapping(shapely_feature)
        feature['geometry']['coordinates'] = mapped_feature['coordinates']
        feature['geometry']['type'] = mapped_feature['type']
    return geo_data
