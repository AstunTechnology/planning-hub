CREATE OR REPLACE VIEW planning.applications AS
  SELECT apps.*
         , trim(status.api_lookup) AS status_api
         , status.description AS status
         , areas.gss_code AS gsscode
  FROM planning.applications_all_data apps
    JOIN planning.areas areas ON (apps.gsscode_id = areas."id")
    JOIN planning.applications_statuses status ON (apps.status_id = status."id");
