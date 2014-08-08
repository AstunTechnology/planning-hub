DROP TABLE IF EXISTS planning.areas CASCADE;
CREATE TABLE planning.areas
(
  id integer NOT NULL,
  gss_code character(9) NOT NULL,
  name text NOT NULL,
  CONSTRAINT areas_pkey PRIMARY KEY (id ),
  CONSTRAINT areas_gsscode_key UNIQUE (gss_code )
)
WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS planning.applications_statuses CASCADE;
CREATE TABLE planning.applications_statuses
(
  id integer NOT NULL,
  api_lookup character(20) NOT NULL,
  name text NOT NULL,
  description text,
  CONSTRAINT application_statuses_pkey PRIMARY KEY (id ),
  CONSTRAINT application_statuses_api_lookup_key UNIQUE (api_lookup )
)
WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS planning.applications_all_data CASCADE;
CREATE TABLE planning.applications_all_data
(
  id serial,
  wkb_geometry geometry,
  gsscode_id integer,
  status_id integer,
  agent text,
  appealdecision text,
  appealdecisiondate date,
  appealref text,
  casedate date,
  casereference text NOT NULL,
  casetext text NOT NULL,
  caseurl text NOT NULL,
  classificationlabel text,
  classificationuri text,
  coordinatereferencesystem text,
  decision text,
  decisiondate date,
  decisionnoticedate date,
  decisiontargetdate date,
  decisiontype text,
  extractdate text NOT NULL,
  geoarealabel text,
  geoareauri text,
  geopointlicensingurl text,
  geox numeric,
  geoy numeric,
  groundarea text,
  locationtext text NOT NULL,
  organisationlabel text,
  organisationuri text,
  publicconsultationenddate date,
  publicconsultationstartdate text,
  publisherlabel text NOT NULL,
  publisheruri text,
  responsesagainst int,
  responsesfor int,
  servicetypelabel text NOT NULL,
  servicetypeuri text,
  uprn character varying(12),
  CONSTRAINT applications_all_data_pkey PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
