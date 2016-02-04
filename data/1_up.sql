
ALTER TABLE travel_log.item ADD COLUMN
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX ON travel_log.item (is_deleted)
  WHERE is_deleted = TRUE;
