
import psycopg2
import logging
import time

## Logging handler for PostgreSQL
#
#
class PostgresHandler(logging.Handler):

  initial_sql = '''
    CREATE TABLE IF NOT EXISTS "{0}"."{1}"(
      created timestamp,
      name text,
      log_level int,
      log_level_name text,
      message text,
      args text,
      module text,
      func_name text,
      line_no int,
      exception text,
      process int,
      thread text,
      thread_name text
    );

    DO $$
      BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM   pg_class c
            JOIN   pg_namespace n ON n.oid = c.relnamespace
            WHERE  c.relname = '{1}_name_idx'
            AND    n.nspname = '{0}'
        )
        THEN CREATE INDEX {1}_name_idx ON "{0}"."{1}" (name);
        END IF;
      END
    $$;'''

  insertion_sql = '''
    INSERT INTO "{}"."{}"(
      created,
      name,
      log_level,
      log_level_name,
      message,
      module,
      func_name,
      line_no,
      exception,
      process,
      thread,
      thread_name)
    VALUES (
      to_timestamp(%(created)s),
      %(name)s,
      %(levelno)s,
      %(levelname)s,
      %(msg)s,
      %(module)s,
      %(funcName)s,
      %(lineno)s,
      %(exc_text)s,
      %(process)s,
      %(thread)s,
      %(threadName)s
     );'''


  def __init__(self, conn_string, schema='public', table='log'):
    if not conn_string:
      raise Exception('No DSN provided')

    self.__connection = psycopg2.connect(conn_string)

    self.__schema = schema
    self.__table = table

    logging.Handler.__init__(self)
    sql = PostgresHandler.initial_sql.format(self.__schema, self.__table)
    self.__connection.cursor().execute(sql)
    self.__connection.commit()
    self.__connection.cursor().close()

  def emit(self, record):
    self.format(record)
    if record.exc_info:
      record.exc_text = logging._defaultFormatter.formatException(
        record.exc_info)
    else:
      record.exc_text = ''

    try:
      cur = self.__connection.cursor()
    except:
      self.__connection = psycopg2.connect(conn_string)
      cur = self.__connection.cursor()

    sql = PostgresHandler.insertion_sql.format(self.__schema, self.__table)
    cur.execute(sql, record.__dict__)

    self.__connection.commit()
    self.__connection.cursor().close()
