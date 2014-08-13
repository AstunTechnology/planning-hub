import os
import re
import psycopg2
import psycopg2.extras
import pg2geojson
from flask.ext.misaka import Misaka
from werkzeug.urls import url_unquote_plus
from datetime import datetime, timedelta
from jinja2 import ChoiceLoader, FileSystemLoader
from flask import Flask, render_template, request, make_response, url_for, send_from_directory
from flask.ext.cors import CORS

import logging
from logging import StreamHandler

# Define the Flask app and add support for Markdown in templates
app = Flask(__name__)
md = Misaka(tables=True, autolink=True, toc=True)
md.init_app(app)

# Exposes all resources matching /developmentcontrol/* to CORS
CORS(app, resources=r'/developmentcontrol/*', headers=['Content-Type', 'X-Requested-With'])

# Configure logging to stderr
log_handler = StreamHandler()
log_handler.setLevel(logging.INFO)
app.logger.addHandler(log_handler)

# Add the to the template search path so that we can treat our built hubmap.js
# as a template without having to manually copy it to the standard template
# directory
DIST_DIR = os.path.join(app.static_folder, 'hubmap/dist')
template_loader = ChoiceLoader([
    app.jinja_loader,
    FileSystemLoader([DIST_DIR])
])
app.jinja_loader = template_loader

# Expose additional functions in templates
app.jinja_env.globals.update(url_unquote_plus=url_unquote_plus)

if 'CONNECTION_STRING' in os.environ:
    app.config['CONNECTION_STRING'] = os.environ['CONNECTION_STRING']


def sql_in(s):
    return ', '.join(map(str, map(psycopg2.extensions.adapt, s)))


def sql_date_range(val):
    token_to_days = {'last_7_days': 6, 'last_14_days': 13, 'last_30_days': 29, 'last_90_days': 89}
    val = datetime.now() - timedelta(days=token_to_days.get(val[0]))
    val = val.date()
    return psycopg2.extensions.adapt(val)


def sql_orderby(vals):
    vals = [s.replace('_', '') for s in vals]
    val = ', '.join(vals)
    return val


def sql_bbox(val):
    return '%s %s,%s %s' % tuple(val[0].split(','))


SQL = """
    SELECT
        ST_AsGeoJSON(wkb_geometry)::json As geom,
        agent, appealdecision, appealref,
        casedate, casereference, casetext, caseurl,
        classificationlabel, classificationuri, coordinatereferencesystem,
        decision, decisiondate, decisionnoticedate, decisiontargetdate, decisiontype,
        extractdate, geoarealabel,
        geoareauri, geopointlicensingurl, geox, geoy, groundarea, gsscode,
        locationtext,
        organisationlabel, organisationuri,
        publicconsultationenddate, publicconsultationstartdate, publisherlabel, publisheruri,
        responsesagainst, responsesfor, servicetypelabel,
        servicetypeuri, status, status_api,
        uprn
    FROM planning.applications %(where)s %(order)s
"""

date_range_pattern = 'last_7_days|last_14_days|last_30_days|last_90_days'

ARGS = {
    'status': {
        'pattern': 'live|withdrawn|decided|appeal|called_in|referred_to_sos|invalid|not_ours|registered',
        'sql': 'status_api IN (%s)',
        'prep_fn': sql_in,
        'type': 'predicate'
    },
    'gsscode': {
        'pattern': 'E\d{8}',
        'sql': 'gsscode IN (%s)',
        'prep_fn': sql_in,
        'type': 'predicate'
    },
    'casedate': {
        'pattern': date_range_pattern,
        'sql': 'casedate >= %s',
        'prep_fn': sql_date_range,
        'type': 'predicate'
    },
    'decisiontargetdate': {
        'pattern': date_range_pattern,
        'sql': 'decisiontargetdate >= %s',
        'prep_fn': sql_date_range,
        'type': 'predicate'
    },
    'decisionnoticedate': {
        'pattern': date_range_pattern,
        'sql': 'decisionnoticedate >= %s',
        'prep_fn': sql_date_range,
        'type': 'predicate'
    },
    'decisiondate': {
        'pattern': date_range_pattern,
        'sql': 'decisiondate >= %s',
        'prep_fn': sql_date_range,
        'type': 'predicate'
    },
    'publicconsultationstartdate': {
        'pattern': date_range_pattern,
        'sql': 'publicconsultationstartdate >= %s',
        'prep_fn': sql_date_range,
        'type': 'predicate'
    },
    'publicconsultationenddate': {
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
    'orderby': {
        'pattern': 'status|casedate',
        'sql': 'ORDER BY %s',
        'prep_fn': sql_orderby,
        'type': 'statement'
    },
    'sortorder': {
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
    args = [validate_arg(arg) for arg in args.items() if supported_arg(arg)]
    predicates = [to_sql(arg) for arg in args if is_predicate(arg)]
    where = 'WHERE %s' % ' AND '.join(predicates) if predicates else ''
    order = ''
    orderby = dict(args).get('orderby')
    if orderby:
        order = to_sql(('orderby', orderby))
        sortorder = dict(args).get('sortorder')
        if sortorder:
            order += ' %s' % to_sql(('sortorder', sortorder))
    sql = SQL % {'where': where, 'order': order}
    return sql


def get_geojson(sql):
    conn = psycopg2.connect(app.config['CONNECTION_STRING'])
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        json = pg2geojson.to_str(cur, rows, 'geom')
        return json


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/embed/<path:path>")
def embed(path):
    if path == 'hubmap.js':
        return make_response(render_template('hubmap.js'), 200, {'Content-Type': 'application/javascript'})
    else:
        return send_from_directory(DIST_DIR, path)


@app.route("/maps")
def maps():
    nocode_maps = [
        {
            'url': url_for('.search', status='decided', gsscode='E07000214'),
            'title': 'Decided planning applications in Surrey Heath'
        },
        {
            'url': url_for('.search', status='live', gsscode='E07000214', bbox='-0.806,51.286,-0.692,51.349'),
            'title': 'Live planning applications in the east of Surrey Heath'
        }
    ]
    manual_maps = [
        {
            'url': url_for('.search', status='decided', gsscode='E07000214', decisiondate='last_90_days'),
            'title': 'Decided planning applications in Surrey Heath with a decision date with the last 90 days',
            'type': 'manual'
        }
    ]
    return render_template('maps.html', nocode_maps=nocode_maps, manual_maps=manual_maps)


def _search(request, args):
    sql = build_sql(args)
    content = get_geojson(sql)
    headers = {'Content-Type': 'application/json'}
    callback = request.args.get('callback')
    if callback:
        content = '%s(%s);' % (callback, content)
        headers['Content-Type'] = 'application/javascript'
    return make_response(content, 200, headers)


def not_acceptable(reason):
    return make_response('HTTP 406: Not Acceptable. %s' % reason, 406, {'Content-Type': 'text/plain'})


@app.route("/developmentcontrol/0.1/applications/search")
def search():
    args = dict(request.args)
    return _search(request, args)


@app.route("/developmentcontrol/0.1/applications/gsscode/<code>")
def gsscode(code):
    k, v = validate_arg(['gsscode', code])
    if v:
        args = dict(request.args)
        args['gsscode'] = code.split(',')
        return _search(request, args)
    return not_acceptable('Invalid GSS code: %s' % code)


@app.route("/developmentcontrol/0.1/applications/status/<code>")
def status(code):
    k, v = validate_arg(['status', code])
    if v:
        args = dict(request.args)
        args['status'] = code.split(',')
        return _search(request, args)
    return not_acceptable('Invalid status code: %s' % code)


if __name__ == "__main__":
    app.debug = True
    app.run()
