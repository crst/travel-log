
INSERT INTO travel_log.share_type VALUES
  (3, 'Hidden');

ALTER TABLE travel_log.share RENAME COLUMN url TO secret;
