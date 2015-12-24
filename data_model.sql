
CREATE USER app WITH SUPERUSER;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

DROP SCHEMA IF EXISTS app CASCADE;
CREATE SCHEMA app;

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


CREATE TABLE app.user (
  id_user       SERIAL PRIMARY KEY,
  user_name     TEXT NOT NULL UNIQUE,
  email         TEXT NOT NULL UNIQUE,
  pw_hash       TEXT NOT NULL,
  last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TRIGGER app_user_update_last_modified BEFORE INSERT OR UPDATE ON app.USER
  FOR EACH ROW EXECUTE PROCEDURE fn.update_last_modified();
CREATE INDEX ON app.user (user_name);

INSERT INTO app.user (user_name, email, pw_hash) VALUES
  ('admin', 'admin@app', crypt('|l@y^DAbtdtEgUamFe*.0_yaq:y\n~\n^N', gen_salt('bf', 12)));



CREATE TABLE app.signup (
  email         TEXT NOT NULL UNIQUE,
  is_user       BOOLEAN NOT NULL,
  last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TRIGGER app_signup_update_last_modified BEFORE INSERT OR UPDATE ON app.signup
  FOR EACH ROW EXECUTE PROCEDURE fn.update_last_modified();



CREATE TABLE app.album (
  id_album      SERIAL PRIMARY KEY,
  album_title   TEXT NOT NULL,
  fk_user       INTEGER NOT NULL,
  last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TRIGGER app_album_update_last_modified BEFORE INSERT OR UPDATE ON app.album
  FOR EACH ROW EXECUTE PROCEDURE fn.update_last_modified();
ALTER TABLE app.album ADD FOREIGN KEY (fk_user) REFERENCES app.user (id_user);
ALTER TABLE app.album ADD UNIQUE (album_title, fk_user);



CREATE TABLE app.item (
  id_item       SERIAL PRIMARY KEY,
  fk_album      INTEGER NOT NULL,
  image         TEXT NOT NULL,
  ts            TIMESTAMP WITH TIME ZONE,
  lat           NUMERIC(9, 6),
  lon           NUMERIC(9, 6),
  description   TEXT,
  last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TRIGGER app_item_update_last_modified BEFORE INSERT OR UPDATE ON app.item
  FOR EACH ROW EXECUTE PROCEDURE fn.update_last_modified();
ALTER TABLE app.item ADD FOREIGN KEY (fk_album) REFERENCES app.album (id_album);



CREATE TABLE app.share_type (
  id_share_type   SERIAL PRIMARY KEY,
  share_type_name TEXT,
  last_modified   TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TRIGGER app_type_update_last_modified BEFORE INSERT OR UPDATE ON app.share_type FOR EACH ROW EXECUTE PROCEDURE fn.update_last_modified();



CREATE TABLE app.share (
  fk_album      SERIAL NOT NULL,
  fk_share_type SMALLINT NOT NULL,
  url           TEXT,
  email         TEXT,
  fk_user       INTEGER,
  last_modified TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE TRIGGER app_share_update_last_modified BEFORE INSERT OR UPDATE ON app.share
  FOR EACH ROW EXECUTE PROCEDURE fn.update_last_modified();
ALTER TABLE app.share ADD FOREIGN KEY (fk_album) REFERENCES app.album (id_album);
ALTER TABLE app.share ADD FOREIGN KEY (fk_share_type) REFERENCES app.share_type (id_share_type);
ALTER TABLE app.share ADD FOREIGN KEY (fk_user) REFERENCES app.user (id_user);
