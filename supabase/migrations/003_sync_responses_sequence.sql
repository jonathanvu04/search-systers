-- Fix: sequence was out of sync after manual inserts with explicit IDs.
-- Sync responses_id_seq so next INSERT gets max(id)+1.

SELECT setval(
  pg_get_serial_sequence('responses', 'id'),
  COALESCE((SELECT MAX(id) FROM responses), 0)
);
