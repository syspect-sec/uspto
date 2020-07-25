-- Making sure the database exists
SELECT * from pg_database where datname = 'uspto'

-- Disallow new connections
UPDATE pg_database SET datallowconn = 'false' WHERE datname = 'uspto';
ALTER DATABASE uspto CONNECTION LIMIT 1;

-- Terminate existing connections
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'uspto';

-- Drop database
DROP DATABASE uspto
