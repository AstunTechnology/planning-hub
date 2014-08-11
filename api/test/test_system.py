import os
import datetime
from functools import partial
from nose.tools import eq_, ok_
from flask import json
import psycopg2
import psycopg2.extras
import testing.postgresql
import app

db = None
client = None


def setUp(self):
    global db, client
    # Create a temporary PG database and populate it with the test data if a
    # connection string is not defined in the environment
    if 'CONNECTION_STRING' not in os.environ:
        db = testing.postgresql.Postgresql()
        conn = psycopg2.connect(**db.dsn())
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute(open("test/fixtures/populate_test_db.sql", "r").read())
        app.app.config['CONNECTION_STRING'] = ' '.join(map(lambda t: '%s=%s' % t, db.dsn().items()))
    app.app.config['TESTING'] = True
    client = app.app.test_client()


def tearDown(self):
    if db:
        db.stop()


# Helpers

def get_property(k, f):
    return f.get('properties').get(k)


def assert_valid_values(feats, prop, expected_vals):
    get_prop = partial(get_property, prop)
    feat_vals = set(map(get_prop, feats.get('features')))
    ok_(set(expected_vals) == feat_vals)


# Tests

def test_index():
    r = client.get('/')
    eq_(r.status_code, 200)


def test_search_status():
    r = client.get('/developmentcontrol/0.1/applications/search?status=live')
    eq_(r.status_code, 200)
    feats = json.loads(r.data)
    assert_valid_values(feats, 'status_api', ['live'])
    r = client.get('/developmentcontrol/0.1/applications/search?status=decided')
    eq_(r.status_code, 200)
    feats = json.loads(r.data)
    assert_valid_values(feats, 'status_api', ['decided'])
    r = client.get('/developmentcontrol/0.1/applications/search?status=live,decided')
    eq_(r.status_code, 200)
    feats = json.loads(r.data)
    assert_valid_values(feats, 'status_api', ['live', 'decided'])


def test_search_gss_code():
    gss_code = 'E07000214'
    r = client.get('/developmentcontrol/0.1/applications/search?gss_code=%s' % gss_code)
    eq_(r.status_code, 200)
    feats = json.loads(r.data)
    assert_valid_values(feats, 'gsscode', [gss_code])


def test_search_case_date():
    get_case_date = partial(get_property, 'casedate')
    days = 'last_7_days'
    last_7_days = [(datetime.datetime.today() - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(0, 7)]
    r = client.get('/developmentcontrol/0.1/applications/search?case_date=%s' % days)
    eq_(r.status_code, 200)
    feats = json.loads(r.data)
    case_dates = set(map(get_case_date, feats.get('features')))
    ok_(case_dates.issubset(last_7_days))


def test_search_decision_target_date():
    get_decision_target_date = partial(get_property, 'decisiontargetdate')
    days = 14
    all_days = [(datetime.datetime.today() - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(0, days)]
    r = client.get('/developmentcontrol/0.1/applications/search?decision_target_date=last_%s_days' % days)
    eq_(r.status_code, 200)
    feats = json.loads(r.data)
    decision_target_date = set(map(get_decision_target_date, feats.get('features')))
    ok_(decision_target_date.issubset(all_days))


def test_search_order_case_date():
    get_case_date = partial(get_property, 'case_date')
    r = client.get('/developmentcontrol/0.1/applications/search?order_by=case_date')
    eq_(r.status_code, 200)
    feats = json.loads(r.data)
    pg_sorted = map(get_case_date, feats.get('features'))
    py_sorted = sorted(pg_sorted)
    eq_(pg_sorted, py_sorted)
    r = client.get('/developmentcontrol/0.1/applications/search?order_by=case_date&sort_order=desc')
    eq_(r.status_code, 200)
    feats = json.loads(r.data)
    pg_sorted = map(get_case_date, feats.get('features'))
    py_sorted = list(reversed(sorted(pg_sorted)))
    eq_(pg_sorted, py_sorted)


def test_search_order_status():
    get_status = partial(get_property, 'status')
    r = client.get('/developmentcontrol/0.1/applications/search?order_by=status')
    eq_(r.status_code, 200)
    feats = json.loads(r.data)
    pg_sorted = map(get_status, feats.get('features'))
    py_sorted = sorted(pg_sorted)
    eq_(pg_sorted, py_sorted)
    r = client.get('/developmentcontrol/0.1/applications/search?order_by=status&sort_order=desc')
    eq_(r.status_code, 200)
    feats = json.loads(r.data)
    pg_sorted = map(get_status, feats.get('features'))
    py_sorted = list(reversed(sorted(pg_sorted)))
    eq_(pg_sorted, py_sorted)


def test_search_no_features():
    # Search for a gss_code that does not exist
    r = client.get('/developmentcontrol/0.1/applications/search?gss_code=E07000000')
    eq_(r.status_code, 200)
    feats = json.loads(r.data)
    eq_(len(feats.get('features')), 0)


def test_search_json():
    r = client.get('/developmentcontrol/0.1/applications/search?')
    eq_(r.status_code, 200)
    eq_(r.headers.get('Content-Type'), 'application/json')


def test_search_jsonp():
    callback = 'foo'
    r = client.get('/developmentcontrol/0.1/applications/search?callback=%s' % callback)
    eq_(r.status_code, 200)
    eq_(r.headers.get('Content-Type'), 'application/javascript')
    head = '%s(' % callback
    tail = ');'
    eq_(head, r.data[0:len(head)])
    eq_(tail, r.data[-len(tail):])
