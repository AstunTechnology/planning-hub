CREATE TABLE IF NOT EXISTS hub.import_history
(
  id SERIAL,
  schema text NOT NULL,
  category text NOT NULL,
  publisher text NOT NULL,
  uri text NOT NULL,
  started timestamp NOT NULL,
  finished timestamp NOT NULL,
  logged timestamp NOT NULL DEFAULT now(),
  successful bool NOT NULL,
  message text NOT NULL,
  CONSTRAINT import_history_pkey PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
