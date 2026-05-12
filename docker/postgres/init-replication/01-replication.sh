#!/bin/sh
set -e
# Runs once on first primary cluster init (docker-entrypoint-initdb.d).
# Creates a replication role and allows streaming from any container address.
# Use a replication password without single quotes (') in the value.

if [ -z "${REPLICATION_PASSWORD}" ]; then
  echo "REPLICATION_PASSWORD must be set for streaming replicas" >&2
  exit 1
fi

exists="$(psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" -tAc "SELECT 1 FROM pg_roles WHERE rolname = 'replicator'")"
if [ "${exists}" != "1" ]; then
  psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" \
    -c "CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD '${REPLICATION_PASSWORD}';"
fi

{
  echo "host replication replicator 0.0.0.0/0 scram-sha-256"
} >> "${PGDATA}/pg_hba.conf"
