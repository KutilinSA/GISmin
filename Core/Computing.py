from shapely.geometry import shape, mapping
from Core.Layers import VectorLayer
from Core.Exceptions import NotVectorLayer
import geojson


def buffer(layer, distance, segments=1, cap_style=1, join_style=1, mitre_limit=5.0):
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


def intersection(first_layer, second_layer):
    if type(first_layer) is not VectorLayer or type(second_layer) is not VectorLayer:
        raise NotVectorLayer("Layer is not the vector layer!")
    if first_layer.type != "vector" or second_layer.type != "vector":
        raise NotVectorLayer("Layer type is not vector")
    first_geo_data = geojson.loads(first_layer.data)
    second_geo_data = geojson.loads(second_layer.data)
    result_features = []
    for first_feature in first_geo_data["features"]:
        first_shapely_feature = shape(first_feature["geometry"])
        intersected_features = []
        for second_feature in second_geo_data["features"]:
            second_shapely_feature = shape(second_feature["geometry"])
            intersected_features.append(first_shapely_feature.intersection(second_shapely_feature))
        if len(intersected_features) > 0:
            union_feature = intersected_features[0]
            for i in range(1, len(intersected_features)):
                union_feature = union_feature.union(intersected_features[i])
            result_features.append(union_feature)
    result_geo_data = {"type": "FeatureCollection", "features": []}
    if len(result_features) > 0:
        result_feature = result_features[0]
        for i in range(1, len(result_features)):
            result_feature = result_feature.union(result_features[i])
        mapped_feature = mapping(result_feature)
        result_geo_data["features"].append({"type": "Feature",
                                            "geometry": {"coordinates": mapped_feature["coordinates"],
                                                         "type": mapped_feature["type"]}})
    return result_geo_data
