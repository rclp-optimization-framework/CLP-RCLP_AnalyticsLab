-- Compare the current Supabase schema with the expected application schema.
-- This is read-only.

SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN ('bateria', 'prueba', 'result')
ORDER BY table_name, ordinal_position;

SELECT conname AS constraint_name, conrelid::regclass AS table_name
FROM pg_constraint
WHERE conrelid::regclass::text IN ('bateria', 'prueba', 'result');
