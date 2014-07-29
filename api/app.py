import re
import psycopg2
from datetime import datetime, timedelta
from flask import Flask, render_template, request, make_response

app = Flask(__name__)


def sql_in_str(s):
    return ', '.join(map(str, map(psycopg2.extensions.adapt, s)))


def sql_date_range(val):
    token_to_days = {'last_7_days': 7, 'last_14_days': 14, 'last_30_days': 30}
    val = datetime.now() - timedelta(days=token_to_days.get(val[0]))
    val = val.date()
    return psycopg2.extensions.adapt(val)


def sql_bbox(val):
    return '%s %s,%s %s' % tuple(val[0].split(','))


date_range_pattern = 'last_7_days|last_14_days|last_30_days'

SQL = """SELECT * FROM apps %(where)s %(order)s;"""

ARGS = {
    'status': {
        'pattern': 'live|withdrawn|decided|appeal|called_in|referred_to_sos|invalid|not_ours|registered',
        'sql': 'status IN (%s)',
        'prep_fn': sql_in_str,
        'type': 'predicate'
    },
    'gss_code': {
        'pattern': 'E\d{8}',
        'sql': 'gsscode IN (%s)',
        'prep_fn': sql_in_str,
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
        'sql': 'ST_Intersects(ST_AsText(ST_SetSRID(\'BOX(%s)\'::box2d, 4326)), wkb_geometry)',
        'prep_fn': sql_bbox,
        'type': 'predicate'
    },
    'order_by': {
        'pattern': 'status|case_date',
        'sql': 'ORDER BY %s',
        'prep_fn': lambda x: ', '.join(x),
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


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/developmentcontrol/0.1/applications/search")
def search():
    args = [validate_arg(arg) for arg in request.args.items() if supported_arg(arg)]
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
    return make_response(sql, 200, {'Content-Type': 'text/plain'})


if __name__ == "__main__":
    app.debug = True
    app.run()
