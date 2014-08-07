CREATE OR REPLACE FUNCTION planning.version()
RETURNS numeric AS
$BODY$
  SELECT 0.21::numeric;
$BODY$
LANGUAGE sql;


CREATE OR REPLACE FUNCTION planning.update_applications_data(table_name text)
  RETURNS void AS
$BODY$
DECLARE
	update_sql text;
  incorrect_statuses text[];
BEGIN
  EXECUTE 'SELECT array_agg(DISTINCT status)
FROM "planning".'|| quote_ident(table_name) ||'
WHERE status IS NOT NULL AND status NOT IN (
	SELECT name
	FROM "planning"."applications_statuses"
);' INTO incorrect_statuses;
  IF array_length(incorrect_statuses, 1) > 0 THEN
    RAISE data_exception
      USING
        MESSAGE='Statuses not found in allowed list: ''' || array_to_string(incorrect_statuses, ''', ''') || '''.'
        , HINT='Replace invalid values with allowed ones.';
  END IF;

	update_sql := '
DELETE FROM "planning"."applications_all_data"
WHERE gsscode_id IN (
	SELECT id
	FROM "planning"."areas"
	WHERE name IN (
		SELECT DISTINCT publisherlabel
		FROM "planning".'|| quote_ident(table_name) ||'
	)
);

INSERT INTO "planning"."applications_all_data"
(
  extractdate,
  publisherlabel,
  casereference,
  caseurl,
  servicetypelabel,
  casetext,
  locationtext,
  publisheruri,
  organisationuri,
  organisationlabel,
  casedate,
  servicetypeuri,
  classificationuri,
  classificationlabel,
  decisiontargetdate,
  coordinatereferencesystem,
  geox,
  geoy,
  geopointlicensingurl,
  decisiondate,
  decision,
  decisiontype,
  decisionnoticedate,
  appealref,
  appealdecisiondate,
  appealdecision,
  geoareauri,
  geoarealabel,
  groundarea,
  uprn,
  agent,
  publicconsultationstartdate,
  publicconsultationenddate,
  responsesfor,
  responsesagainst,
  status_id,
  gsscode_id,
  wkb_geometry
)

SELECT
  extractdate::date,
  publisherlabel,
  casereference,
  caseurl,
  servicetypelabel,
  casetext,
  locationtext,
  publisheruri,
  organisationuri,
  organisationlabel,
  casedate::date,
  servicetypeuri,
  classificationuri,
  classificationlabel,
  decisiontargetdate::date,
  coordinatereferencesystem,
  geox::numeric,
  geoy::numeric,
  geopointlicensingurl,
  decisiondate::date,
  decision,
  decisiontype,
  decisionnoticedate::date,
  appealref,
  appealdecisiondate::date,
  appealdecision,
  geoareauri,
  geoarealabel,
  groundarea,
  uprn,
  agent,
  publicconsultationstartdate::date,
  publicconsultationenddate::date,
  responsesfor::int,
  responsesagainst::int,
  status.id,
  areas.id,
  ST_SetSRID(ST_MakePoint(geox::numeric, geoy::numeric), 4326)
FROM "planning".'|| quote_ident(table_name) ||' app
 JOIN "planning"."areas" areas ON areas.name = app.publisherlabel
 LEFT JOIN "planning"."applications_statuses" status ON status.name = app.status;';
	EXECUTE update_sql;
END
$BODY$
  LANGUAGE plpgsql;
