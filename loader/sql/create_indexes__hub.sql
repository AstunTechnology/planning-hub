DROP INDEX IF EXISTS import_history_started_idx;
CREATE INDEX import_history_started_idx
  ON hub.import_history
  USING btree
  (started );

DROP INDEX IF EXISTS import_history_finished_idx;
CREATE INDEX import_history_finished_idx
  ON hub.import_history
  USING btree
  (finished );

DROP INDEX IF EXISTS import_history_logged_idx;
CREATE INDEX import_history_logged_idx
  ON hub.import_history
  USING btree
  (logged );

DROP INDEX IF EXISTS import_history_schema_category_publisher_idx;
CREATE INDEX import_history_schema_category_publisher_idx
  ON hub.import_history
  USING btree
  (schema, category, publisher );

DROP INDEX IF EXISTS import_history_successful_idx;
CREATE INDEX import_history_successful_idx
  ON hub.import_history
  USING btree
  (successful );
