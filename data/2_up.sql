
ALTER TABLE travel_log.album ADD COLUMN
  background TEXT NOT NULL DEFAULT '#dbd1b4';

ALTER TABLE travel_log.album ADD COLUMN
  autoplay_delay SMALLINT NOT NULL DEFAULT 5;
