CREATE INDEX applications_all_data_casedate_idx
  ON planning.applications_all_data
  USING btree
  (casedate );


CREATE INDEX applications_all_data_gsscode_id_idx
  ON planning.applications_all_data
  USING btree
  (gsscode_id );


CREATE INDEX applications_all_data_status_id_gsscode_id_idx
  ON planning.applications_all_data
  USING btree
  (status_id, gsscode_id );


CREATE INDEX applications_all_data_status_id_idx
  ON planning.applications_all_data
  USING btree
  (status_id );


CREATE INDEX applications_all_data_wkb_geometry_idx
  ON planning.applications_all_data
  USING gist
  (wkb_geometry );

CREATE INDEX areas_id_idx
  ON planning.areas
  USING btree
  (id );

CREATE INDEX applications_statuses_id_idx
  ON planning.applications_statuses
  USING btree
  (id );
