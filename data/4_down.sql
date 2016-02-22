
DELETE FROM travel_log.share_type
WHERE id_share_type = 3 AND share_type_name = 'Hidden';

ALTER TABLE travel_log.share RENAME COLUMN secret TO url;
