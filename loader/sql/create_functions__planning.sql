CREATE OR REPLACE FUNCTION planning.version()
RETURNS numeric AS
$BODY$
  SELECT 0.18::numeric;
$BODY$
LANGUAGE sql;


CREATE OR REPLACE FUNCTION planning.update_applications_data(table_name text)
  RETURNS void AS
$BODY$
DECLARE
	update_sql text;
BEGIN
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
  NULLIF(publisherlabel,''''),
  NULLIF(casereference,''''),
  NULLIF(caseurl,''''),
  NULLIF(servicetypelabel,''''),
  NULLIF(casetext,''''),
  NULLIF(locationtext,''''),
  NULLIF(publisheruri,''''),
  NULLIF(organisationuri,''''),
  NULLIF(organisationlabel,''''),
  NULLIF(casedate,'''')::date,
  NULLIF(servicetypeuri,''''),
  NULLIF(classificationuri,''''),
  NULLIF(classificationlabel,''''),
  NULLIF(decisiontargetdate,'''')::date,
  NULLIF(coordinatereferencesystem,''''),
  NULLIF(geox,'''')::numeric,
  NULLIF(geoy,'''')::numeric,
  NULLIF(geopointlicensingurl,''''),
  NULLIF(decisiondate,'''')::date,
  NULLIF(decision,''''),
  NULLIF(decisiontype,''''),
  NULLIF(decisionnoticedate,'''')::date,
  NULLIF(appealref,''''),
  NULLIF(appealdecisiondate,'''')::date,
  NULLIF(appealdecision,''''),
  NULLIF(geoareauri,''''),
  NULLIF(geoarealabel,''''),
  NULLIF(groundarea,''''),
  NULLIF(uprn,''''),
  NULLIF(agent,''''),
  NULLIF(publicconsultationstartdate,'''')::date,
  NULLIF(publicconsultationenddate,'''')::date,
  NULLIF(responsesfor,'''')::int,
  NULLIF(responsesagainst,'''')::int,
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
