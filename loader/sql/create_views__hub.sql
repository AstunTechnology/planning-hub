
CREATE OR REPLACE VIEW hub.last_import AS
  SELECT DISTINCT ON (schema, category, publisher)
    schema, category, publisher, uri, started, finished, message, successful
  FROM hub.import_history
  ORDER BY schema, category, publisher, logged DESC;


CREATE OR REPLACE VIEW hub.last_import_sucesses AS
  SELECT DISTINCT ON (schema, category, publisher)
    schema, category, publisher, uri, started, finished, message
  FROM hub.import_history
  WHERE successful = true
  ORDER BY schema, category, publisher, logged DESC;


CREATE OR REPLACE VIEW hub.last_import_failures AS
  SELECT DISTINCT ON (schema, category, publisher)
    schema, category, publisher, uri, started, finished, message
  FROM hub.import_history
  WHERE successful = false
  ORDER BY schema, category, publisher, logged DESC;
