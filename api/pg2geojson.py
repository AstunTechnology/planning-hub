from flask import json


def to_obj(cur, rows, geom_col):

    col_names = [desc[0] for desc in cur.description]
    geom_idx = col_names.index(geom_col)

    feature_collection = {'type': 'FeatureCollection', 'features': []}

    for row in rows:
        feature = {
            'type': 'Feature',
            'geometry': row[geom_idx],
            'properties': {},
        }

        for index, col_name in enumerate(col_names):
            if col_name != geom_col:
                feature['properties'][col_name] = row[index]

        feature_collection['features'].append(feature)

    return feature_collection


def to_str(cur, rows, geom_col):
    """ Creates a feature collection as a string containing all rows. Assumes all values
        can be serialised by json.dumps """

    feature_collection = to_obj(cur, rows, geom_col)

    return json.dumps(feature_collection, indent=2)

# Based on https://github.com/jczaplew/postgis2geojson
