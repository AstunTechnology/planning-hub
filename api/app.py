import os
import re
import psycopg2
import psycopg2.extras
import contextlib
from datetime import datetime, timedelta
from flask import Flask, render_template, request, make_response

app = Flask(__name__)

app.config['CONNECTION_STRING'] = "dbname='hub_test' user='hub_test' password='hub_test' host='localhost'"

if os.environ.get('CONFIG_FILE'):
    app.config.from_envvar('CONFIG_FILE')


def sql_in(s):
    return ', '.join(map(str, map(psycopg2.extensions.adapt, s)))


def sql_date_range(val):
    token_to_days = {'last_7_days': 7, 'last_14_days': 14, 'last_30_days': 30}
    val = datetime.now() - timedelta(days=token_to_days.get(val[0]))
    val = val.date()
    return psycopg2.extensions.adapt(val)


def sql_order_by(vals):
    vals = [s.replace('_', '') for s in vals]
    val = ', '.join(vals)
    return val


def sql_bbox(val):
    return '%s %s,%s %s' % tuple(val[0].split(','))


SQL = """WITH applications AS (SELECT * FROM planning.applications %(where)s %(order)s)
    SELECT row_to_json(fc, true)::text as features
        FROM (SELECT 'FeatureCollection' As type, array_to_json(array_agg(f), true) As features
            FROM (SELECT 'Feature' As type
            ,ST_AsGeoJSON(lg.wkb_geometry)::json As geometry
            ,row_to_json((SELECT l FROM (SELECT caseurl, geopointlicensingurl, publicconsultationstartdate, responsesfor, locationtext, agent, geoy, geox, decisiontargetdate, responsesagainst, geoareauri, organisationlabel, decision, servicetypeuri, classificationlabel, casereference, decisiontype, status, casetext, extractdate, publisherlabel, publicconsultationenddate, servicetypelabel, organisationuri, uprn, publisheruri, appealdecision, classificationuri, coordinatereferencesystem, casedate, geoarealabel, decisionnoticedate, groundarea, decisiondate, appealref, gsscode) As l), true) As properties
            FROM applications As lg) As f)  As fc;"""

date_range_pattern = 'last_7_days|last_14_days|last_30_days'

ARGS = {
    'status': {
        'pattern': 'live|withdrawn|decided|appeal|called_in|referred_to_sos|invalid|not_ours|registered',
        'sql': 'status_api IN (%s)',
        'prep_fn': sql_in,
        'type': 'predicate'
    },
    'gss_code': {
        'pattern': 'E\d{8}',
        'sql': 'gsscode IN (%s)',
        'prep_fn': sql_in,
        'type': 'predicate'
    },
    'case_date': {
        'pattern': date_range_pattern,
        'sql': 'casedate >= %s',
        'prep_fn': sql_date_range,
        'type': 'predicate'
    },
    'decision_target_date': {
        'pattern': date_range_pattern,
        'sql': 'decisiontargetdate >= %s',
        'prep_fn': sql_date_range,
        'type': 'predicate'
    },
    'decision_notice_date': {
        'pattern': date_range_pattern,
        'sql': 'decisionnoticedate >= %s',
        'prep_fn': sql_date_range,
        'type': 'predicate'
    },
    'public_consultation_start_date': {
        'pattern': date_range_pattern,
        'sql': 'publicconsultationstart_date >= %s',
        'prep_fn': sql_date_range,
        'type': 'predicate'
    },
    'public_consultation_end_date': {
        'pattern': date_range_pattern,
        'sql': 'publicconsultationenddate >= %s',
        'prep_fn': sql_date_range,
        'type': 'predicate'
    },
    'bbox': {
        'pattern': '-?\d+\.\d+,-?\d+\.\d+,-?\d+\.\d+,-?\d+\.\d+',
        'sql': 'ST_Intersects(ST_SetSRID(\'BOX(%s)\'::box2d, 4326), planning.applications.wkb_geometry)',
        'prep_fn': sql_bbox,
        'type': 'predicate'
    },
    'order_by': {
        'pattern': 'status|case_date',
        'sql': 'ORDER BY %s',
        'prep_fn': sql_order_by,
        'type': 'statement'
    },
    'sort_order': {
        'pattern': 'asc|desc',
        'sql': '%s',
        'prep_fn': lambda x: x[0].upper(),
        'type': 'statement'
    }
}


def to_sql(arg):
    k, v = arg
    prep_fn = ARGS.get(k).get('prep_fn')
    v = prep_fn(v)
    sql = ARGS.get(k).get('sql') % v
    return sql


def supported_arg(i):
    k, v = i
    return k in ARGS


def validate_arg(i):
    k, v = i
    regex = re.compile(ARGS.get(k).get('pattern'))
    return [k, regex.findall(''.join(v))]


def is_predicate(arg):
    k, v = arg
    return ARGS.get(k).get('type') == 'predicate'


def build_sql(args):
    predicates = [to_sql(arg) for arg in args if is_predicate(arg)]
    where = 'WHERE %s' % ' AND '.join(predicates) if predicates else ''
    order = ''
    order_by = dict(args).get('order_by')
    if order_by:
        order = to_sql(('order_by', order_by))
        sort_order = dict(args).get('sort_order')
        if sort_order:
            order += ' %s' % to_sql(('sort_order', sort_order))
    sql = SQL % {'where': where, 'order': order}
    return sql


def get_geojson(sql):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    with contextlib.closing(conn.cursor(cursor_factory=psycopg2.extras.DictCursor)) as cur:
        cur.execute(sql)
        result = cur.fetchall()
        return result[0].get('features')


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/developmentcontrol/0.1/applications/search")
def search():
    args = [validate_arg(arg) for arg in request.args.items() if supported_arg(arg)]
    sql = build_sql(args)
    features = get_geojson(sql)
    return make_response(features, 200, {'Content-Type': 'application/json'})


if __name__ == "__main__":
    app.debug = True
    app.run()
