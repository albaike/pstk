#!/bin/bash
set -e

until pg_isready -q -U postgres
do
    echo "Waiting for PostgreSQL to start..."
    sleep 1
done

psql -v ON_ERROR_STOP=1

echo "PostgreSQL started. Running pstk..."
. ~/poetry_path.sh
$POETRY_PATH/bin/pstk --extension --schema-path=postxml--1.0.sql --host=/var/run/postgresql /postxml test