CREATE OR REPLACE FUNCTION version()
RETURNS numeric AS
$BODY$
  SELECT 0.17::numeric;
$BODY$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION import_attempted(
  schema text
  , category text
  , publisher text
  , uri text
  , successful bool
  , message text
  , started timestamp without time zone
  , finished timestamp without time zone
)
RETURNS void AS
$BODY$
  INSERT INTO hub.import_history (
    schema, category, publisher, uri, successful, message, started, finished
  )
  VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8
  )
$BODY$
LANGUAGE sql;
