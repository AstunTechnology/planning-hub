import datetime
import simplejson as json


def to_obj(cur, rows, geom_col):
    """ Creates a feature collection as a dict. Assumes rows is a dict """

    feature_collection = {'type': 'FeatureCollection', 'features': []}

    for row in rows:
        geom = row.pop(geom_col)
        feature = {
            'type': 'Feature',
            'geometry': geom,
            'properties': row,
        }
        feature_collection['features'].append(feature)

    return feature_collection


def to_str(cur, rows, geom_col):
    """ Creates a feature collection as a string. Assumes rows is a dict """

    feature_collection = to_obj(cur, rows, geom_col)

    def encode(obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        raise TypeError(repr(obj) + " is not JSON serializable")

    return json.dumps(feature_collection, indent=2, use_decimal=True, default=encode)
