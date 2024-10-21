# Empty the test database by dropping all tables
echo "Emptying the test database by dropping all tables..."

# Check if the necessary environment variables are passed
if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_DB" ]; then
  echo "Error: POSTGRES_USER and POSTGRES_DB must be provided."
  exit 1
fi


psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
DO \$\$ 
DECLARE
    r RECORD;
BEGIN
    -- Loop through all tables and drop them
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END 
\$\$;"
