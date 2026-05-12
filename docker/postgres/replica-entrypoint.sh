#!/bin/sh
set -e
# First boot: pg_basebackup from PRIMARY_HOST, then start postgres in recovery.
# Reuses the official image entrypoint after data exists.

if [ -z "${PRIMARY_HOST}" ] || [ -z "${REPLICATION_PASSWORD}" ]; then
  echo "PRIMARY_HOST and REPLICATION_PASSWORD are required" >&2
  exit 1
fi

if [ ! -s "${PGDATA}/PG_VERSION" ]; then
  echo "Waiting for primary ${PRIMARY_HOST}..."
  until pg_isready -h "${PRIMARY_HOST}" -p 5432 -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; do
    sleep 1
  done
  mkdir -p "${PGDATA}"
  chown -R postgres:postgres "${PGDATA}" 2>/dev/null || true
  export PGPASSWORD="${REPLICATION_PASSWORD}"
  echo "Running pg_basebackup from ${PRIMARY_HOST}..."
  if command -v gosu >/dev/null 2>&1; then
    gosu postgres pg_basebackup -h "${PRIMARY_HOST}" -p 5432 -U replicator -D "${PGDATA}" -Fp -Xs -P -R
  else
    su-exec postgres pg_basebackup -h "${PRIMARY_HOST}" -p 5432 -U replicator -D "${PGDATA}" -Fp -Xs -P -R
  fi
  unset PGPASSWORD
fi

exec docker-entrypoint.sh postgres
