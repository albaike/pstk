# pstk -- Postgres Toolkit
A toolkit for developing Postgres schemas & extensions, with single-command deployment and testing.

## Install

`pip install --user pstk`

## Usage
Create a `.env` file in the your postgres project directory with `POSTGRES_PASSWORD` if you are not using the default `postgres:postgres`

To install:

- a schema:

`pstk . install`

- an extension:

`pstk --extension --schema-path=path-to-schema-data--1.0.sql . install`

To test

`pstk . test --replace`