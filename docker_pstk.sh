#!/bin/bash
set -e

until pg_isready -q -U postgres
do
    echo "Waiting for PostgreSQL to start..."
    sleep 1
done

psql -v ON_ERROR_STOP=1

echo "PostgreSQL started. Running pstk..."
source ~/.env

$POETRY_PATH/bin/pstk  --host=/var/run/postgresql $PSTK_ARGS