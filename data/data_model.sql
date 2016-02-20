
CREATE EXTENSION IF NOT EXISTS pgcrypto;

DROP SCHEMA IF EXISTS travel_log CASCADE;
CREATE SCHEMA travel_log;

DROP SCHEMA IF EXISTS fn CASCADE;
CREATE SCHEMA fn;

-------------------------------------------------------------------------------


CREATE OR REPLACE FUNCTION fn.update_last_modified()
RETURNS TRIGGER AS $$
BEGIN
  NEW.last_modified = clock_timestamp();
  RETURN NEW;
END;
$$ language 'plpgsql';


-------------------------------------------------------------------------------


CREATE TABLE travel_log.user (
  id_user       SERIAL PRIMARY KEY,
  user_name     TEXT NOT NULL UNIQUE,
  email         TEXT NOT NULL UNIQUE,
  pw_hash       TEXT NOT NULL,
  last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TRIGGER travel_log_user_update_last_modified BEFORE INSERT OR UPDATE ON travel_log.USER
  FOR EACH ROW EXECUTE PROCEDURE fn.update_last_modified();
CREATE INDEX ON travel_log.user (user_name);

INSERT INTO travel_log.user (user_name, email, pw_hash) VALUES
  ('admin', 'admin@travel_log', crypt('@1@3%kgq\\|EH\tt{LO|PjZwn\x0c\tZPluh4(', gen_salt('bf', 12)));



CREATE TABLE travel_log.signup (
  email         TEXT NOT NULL UNIQUE,
  is_user       BOOLEAN NOT NULL,
  last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TRIGGER travel_log_signup_update_last_modified BEFORE INSERT OR UPDATE ON travel_log.signup
  FOR EACH ROW EXECUTE PROCEDURE fn.update_last_modified();



CREATE TABLE travel_log.album (
  id_album       SERIAL PRIMARY KEY,
  album_title    TEXT NOT NULL,
  album_desc     TEXT,
  fk_user        INTEGER NOT NULL,
  is_deleted     BOOLEAN NOT NULL DEFAULT FALSE,
  last_modified  TIMESTAMP WITH TIME ZONE NOT NULL,
  background     TEXT NOT NULL DEFAULT '#dbd1b4',
  autoplay_delay SMALLINT NOT NULL DEFAULT 5
);
CREATE TRIGGER travel_log_album_update_last_modified BEFORE INSERT OR UPDATE ON travel_log.album
  FOR EACH ROW EXECUTE PROCEDURE fn.update_last_modified();
ALTER TABLE travel_log.album ADD FOREIGN KEY (fk_user) REFERENCES travel_log.user (id_user);
CREATE INDEX ON travel_log.album (album_title);
CREATE INDEX ON travel_log.album (is_deleted) WHERE is_deleted = TRUE;



CREATE TABLE travel_log.item (
  id_item       SERIAL PRIMARY KEY,
  fk_album      INTEGER NOT NULL,
  image         TEXT NOT NULL,
  ts            TIMESTAMP WITH TIME ZONE,
  lat           NUMERIC(9, 6),
  lon           NUMERIC(9, 6),
  zoom          SMALLINT,
  description   TEXT,
  is_deleted    BOOLEAN NOT NULL DEFAULT FALSE,
  last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TRIGGER travel_log_item_update_last_modified BEFORE INSERT OR UPDATE ON travel_log.item
  FOR EACH ROW EXECUTE PROCEDURE fn.update_last_modified();
ALTER TABLE travel_log.item ADD FOREIGN KEY (fk_album) REFERENCES travel_log.album (id_album);



CREATE TABLE travel_log.share_type (
  id_share_type   SERIAL PRIMARY KEY,
  share_type_name TEXT,
  last_modified   TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TRIGGER travel_log_type_update_last_modified BEFORE INSERT OR UPDATE ON travel_log.share_type FOR EACH ROW EXECUTE PROCEDURE fn.update_last_modified();

INSERT INTO travel_log.share_type VALUES
  (1, 'Private'),
  (2, 'Public');


CREATE TABLE travel_log.share (
  fk_album      SERIAL NOT NULL,
  fk_share_type SMALLINT NOT NULL,
  url           TEXT,
  email         TEXT,
  fk_user       INTEGER,
  last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TRIGGER travel_log_share_update_last_modified BEFORE INSERT OR UPDATE ON travel_log.share
  FOR EACH ROW EXECUTE PROCEDURE fn.update_last_modified();
ALTER TABLE travel_log.share ADD FOREIGN KEY (fk_album) REFERENCES travel_log.album (id_album);
ALTER TABLE travel_log.share ADD FOREIGN KEY (fk_share_type) REFERENCES travel_log.share_type (id_share_type);
ALTER TABLE travel_log.share ADD FOREIGN KEY (fk_user) REFERENCES travel_log.user (id_user);


-------------------------------------------------------------------------------

DROP OWNED BY travel_log CASCADE;
DROP USER IF EXISTS travel_log;
CREATE USER travel_log;
GRANT ALL PRIVILEGES ON ALL tables IN SCHEMA travel_log TO travel_log;
GRANT USAGE ON SCHEMA travel_log to travel_log;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA travel_log to travel_log;
