
DROP SCHEMA IF EXISTS app CASCADE;
CREATE SCHEMA app;



CREATE TABLE app.user (
  id_user   INTEGER PRIMARY KEY,
  user_name TEXT NOT NULL,
  email     TEXT NOT NULL,
  pw_hash   TEXT NOT NULL
);



CREATE TABLE app.album (
  id_album    INTEGER PRIMARY KEY,
  album_title TEXT NOT NULL,
  fk_user     INTEGER NOT NULL
);

ALTER TABLE app.album ADD FOREIGN KEY (fk_user) REFERENCES app.user (id_user);



CREATE TABLE app.item (
  id_item     INTEGER PRIMARY KEY,
  fk_album    INTEGER NOT NULL,
  image       TEXT NOT NULL,
  ts          TIMESTAMP WITH TIME ZONE,
  lat         NUMERIC(9, 6),
  lon         NUMERIC(9, 6),
  description TEXT
);

ALTER TABLE app.item ADD FOREIGN KEY (fk_album) REFERENCES app.album (id_album);



CREATE TABLE app.share_type (
  id_share_type   SMALLINT PRIMARY KEY,
  share_type_name TEXT
);



CREATE TABLE app.share (
  fk_album      INTEGER NOT NULL,
  fk_share_type SMALLINT NOT NULL,
  url           TEXT,
  email         TEXT,
  fk_user       INTEGER
);

ALTER TABLE app.share ADD FOREIGN KEY (fk_album) REFERENCES app.album (id_album);
ALTER TABLE app.share ADD FOREIGN KEY (fk_share_type) REFERENCES app.share_type (id_share_type);
ALTER TABLE app.share ADD FOREIGN KEY (fk_user) REFERENCES app.user (id_user);
