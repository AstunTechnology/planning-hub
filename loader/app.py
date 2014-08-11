import StringIO
import logging
import os
import re

from datetime import datetime
from decimal import *

import psycopg2
import psycopg2.extras
import requests

from lxml import etree

from postgres_logging import PostgresHandler

NULL = '\N'
DELIMITER = '\t'
CONNECTION_STRING = os.environ['CONNECTION_STRING']
LOG_LEVEL = next(val for val in [os.environ.get('HUB_LOG_LEVEL'), 'INFO']
                 if val is not None)
VERSION = {'hub': Decimal('0.16'), 'planning': Decimal('0.21')}


assert CONNECTION_STRING
log_format = '%(asctime)s %(name)-12s %(levelname)-8s ''%(message)s'
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper()),
                    format=log_format, datefmt='%m-%d %H:%M',
                    filename='app.log', filemode='w', backupCount=9)
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
log = {}
for schema_name in VERSION.keys():
    log[schema_name] = logging.getLogger(schema_name)
    log[schema_name].addHandler(PostgresHandler(CONNECTION_STRING,
                                                schema='hub'))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIR = os.path.join(SCRIPT_DIR, 'sql')


def init_schema(conn, schema_name):
    sql = '''
        SELECT exists(select schema_name
        FROM information_schema.schemata
        WHERE schema_name = %s);'''
    with conn:
        with conn.cursor() as curs:
            curs.execute(sql, (schema_name,))
            schema_exists = curs.fetchone()[0]
            if not schema_exists:
                curs.execute('CREATE SCHEMA "{}";'.format(schema_name))


def check_version(conn, schema_name, expected):
    with conn:
        with conn.cursor() as curs:
            try:
                curs.execute('SELECT "{}".version();'.format(schema_name))
            except psycopg2.ProgrammingError:
                logging.info('{} version missing - assuming functions '
                             'not installed'.format(schema_name))
                is_correct = False
            else:
                version = curs.fetchone()[0]
                is_correct = (version == expected)
    if is_correct:
        logging.info('"{}" schema version up-to-date ({})'.format(
            schema_name, str(expected)))
    elif version < expected:
        logging.info('"{}" schema version out of date ({} < {})'.format(
                     schema_name, str(version), str(expected)))
    else:
        err_msg = 'SQL {} version is newer than app ({} > {})'.format(
            schema_name, str(version), str(expected))
        logging.error(err_msg)
        raise ValueError(err_msg)
    return is_correct


def sql_create_script(conn, name, schema_name, not_found_err=False):
    filename = 'create_{}__{}.sql'.format(name, schema_name)
    path = os.path.join(SQL_DIR, filename)
    try:
        with open(path, 'r') as f:
            sql = f.read()
    except IOError as e:
        if not_found_err:
            raise
        else:
            logging.info('Ignoring missing file: {}'.format(path))
    else:
        if sql.strip():
            logging.info('Running {}'. format(path))
            logging.debug('Creating/replacing {}:\n{}'.format(name, sql))
            with conn.cursor() as curs:
                curs.execute(sql)
        else:
            logging.info('Ignoring empty file: {}'.format(path))


def prepare_db(conn):
    for schema_name in VERSION.keys():
        prepare_db_schema(conn, schema_name)


def prepare_db_schema(conn, schema_name):
    init_schema(conn, schema_name)
    pattern = r'' + re.escape(schema_name) + '_(?P<table>\w+)__data.txt'
    if not check_version(conn, schema_name, VERSION[schema_name]):
        logging.info('Installing "{}" schema components'.format(schema_name))
        data_files = [f for f in os.listdir(SQL_DIR)
                      if f.startswith(schema_name)
                      and f.endswith('__data.txt')]
        try:
            with conn:
                sql_create_script(conn, 'tables', schema_name)
                for filename in data_files:
                    m = re.match(pattern, filename)
                    table = '"{}"."{}"'.format(schema_name, m.group('table'))
                    copy_sql = "COPY {} FROM STDIN DELIMITER '|';".format(
                        table)
                    logging.info('Copying data from {} into {}'.format(
                        filename, table))
                    with conn.cursor() as curs:
                        with open(os.path.join(SQL_DIR, filename)) as f:
                            curs.copy_expert(copy_sql, f)
                    sql_create_script(conn, 'indexes', schema_name)
                    sql_create_script(conn, 'views', schema_name)
                    sql_create_script(conn, 'functions', schema_name)
        except Exception as e:
            logging.critical(e)
            raise


def log_import(conn, schema_name, category, publisher, uri, start, finish,
               successful, message):
    func_name = '"hub"."import_attempted"'
    with conn:
        with conn.cursor() as curs:
            try:
                curs.callproc(func_name, [schema_name, category, publisher,
                                          uri, successful, message,
                                          start, finish])
            except Exception as e:
                crit_msg = 'Abort: Failure logging import: {}'.format(e)
                log['hub'].critical(crit_msg)
                raise


def get_feed_values(parent, fields, required, schema_name=None):
    if(schema_name):
        log_handler = log[schema_name]
    else:
        log_handler = logging
    values = []
    for field in fields:
        node = parent.find(field)
        text = '' if node is None else node.text.strip() if node.text else ''
        if required and not text:
            err_msg = 'Required "{}" value missing or empty '.format(field)
            log_handler.error(err_msg)
        else:
            value = text if text else NULL
            values.append(value)
    if required:
        assert len(fields) == len(values)
    return values


def sql_import_feed(conn, schema_name, category, publisher, fields, values):
    field_names = ', '.join(fields)
    field_defs = ' text, '.join(fields) + ' text'
    table_name = '{}_{}'.format(category, publisher)
    fqtn = '"{}"."{}"'.format(schema_name, table_name)
    drop_sql = 'DROP TABLE IF EXISTS {}'.format(fqtn)
    create_sql = 'CREATE TABLE {} ({})'.format(fqtn, field_defs)
    copy_sql = "COPY {} ({}) FROM STDIN DELIMITER '{}' NULL '{}'".format(
        fqtn, field_names, DELIMITER, NULL)
    formatted_values = '\n'.join([DELIMITER.join(row) for row in values])
    pseudo_file = StringIO.StringIO(formatted_values)
    with conn:
        with conn.cursor() as curs:
            curs.execute(drop_sql)
            curs.execute(create_sql)
            curs.copy_expert(copy_sql, pseudo_file)
            log[schema_name].info('Feed data imported into database')
            update_sp = '"{}"."update_{}_data"'.format(schema_name, category)
            curs.callproc(update_sp, [table_name])
            log[schema_name].info('Feed data pushed to live')


def import_feed(conn, schema_name, category, publisher, uri,
                required_fields=[], optional_fields=[]):
    message = 'Import successful'
    successful = True
    start = datetime.utcnow()
    if not required_fields and not optional_fields:
        message = 'No fields configured for this import!'
    log[schema_name].info('Attempting load of {}'.format(uri))
    resp = requests.get(uri)
    root = etree.fromstring(resp.text)
    all_values = []
    nodes = root.findall('{}_hub_feed'.format(schema_name))
    count = 0
    error = False
    for node in nodes:
        count = count + 1
        try:
            required_values = get_feed_values(node, required_fields,
                                              True, schema_name)
        except AssertionError as e:
            error = True
            err_msg = 'Missing required values in record {}'.format(count)
            log[schema_name].error(err_msg)
        else:
            optional_values = get_feed_values(node, optional_fields,
                                              False, schema_name)
            values = required_values + optional_values
            all_values.append(values)

    if len(all_values) != len(nodes):
        successful = False
        message = ('XML for {} from {} ({}) does not contain '
                   'all required values').format(category, publisher, uri)
        log[schema_name].error(message)
    else:
        log[schema_name].info('Feed loaded')
        try:
            sql_import_feed(conn, schema_name, category, publisher,
                            required_fields + optional_fields, all_values)
            log[schema_name].info(message)
        except (psycopg2.ProgrammingError, psycopg2.DataError) as e:
            successful = False
            message = 'Import of feed for {} from {} ({}) failed: {}'.format(
                category, publisher, uri, e)
            log[schema_name].error(message)

    finish = datetime.utcnow()
    log_import(conn, schema_name, category, publisher, uri, start, finish,
               successful, message)


if __name__ == '__main__':
    logging.info('>>> Hub data load commencing <<<')
    conn = psycopg2.connect(CONNECTION_STRING)
    prepare_db(conn)
    filename = 'planning_applications_feeds.txt'
    required_fields = ['extractdate', 'publisherlabel', 'casereference',
                       'caseurl', 'servicetypelabel', 'casetext',
                       'locationtext']
    optional_fields = ['publisheruri', 'organisationuri', 'organisationlabel',
                       'casedate', 'servicetypeuri', 'classificationuri',
                       'classificationlabel', 'decisiontargetdate', 'status',
                       'coordinatereferencesystem', 'geox', 'geoy',
                       'geopointlicensingurl', 'decisiondate', 'decision',
                       'decisiontype', 'decisionnoticedate', 'appealref',
                       'appealdecisiondate', 'appealdecision', 'geoareauri',
                       'geoarealabel', 'groundarea', 'uprn', 'agent',
                       'publicconsultationstartdate',
                       'publicconsultationenddate', 'responsesfor',
                       'responsesagainst']
    try:
        with open(os.path.join(SCRIPT_DIR, filename)) as f:
            lines = f.read().splitlines()
    except IOError as e:
        planning_log.error('Planning applications feed file '
                           'could not be opened')
    if lines:
        for line in lines:
            publisher, uri = line.split('|')
            import_feed(conn, 'planning', 'applications', publisher, uri,
                        required_fields=required_fields,
                        optional_fields=optional_fields)
    else:
        planning_log.error('No planning applications feeds configured')
    logging.info('<<< Hub data load completed >>>')