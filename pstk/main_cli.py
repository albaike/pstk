import argparse
import psycopg2
from pathlib import Path
import re
from dotenv import load_dotenv
import os
import subprocess
import shutil

def exec_sudo(*args):
    val = subprocess.run(
        ('sudo', *args),
        # check=True,
        capture_output=True,
    )
    # print(f'`{" ".join(args)}`: {val}')
    if val.returncode != 0:
        raise Exception(val)

def main(
    root: Path,
    mode: str, # test | install
    host: str,
    port: int,
    replace: bool,
    extension: bool,
    schema_path: str,
    # dbname: str,
    # user: str,
    # password: str,
    **conn_args,
):
    load_dotenv(root / '.env')
    for key in {'dbname', 'user', 'password',}:
        if (value := os.getenv(f'POSTGRES_{key.upper()}')):
            conn_args[key] = value

    conn_args['host'] = host
    conn_args['port'] = port

    print(conn_args)
    conn = psycopg2.connect(**conn_args)

    schema = root / schema_path

    if not schema.exists():
        raise FileNotFoundError(schema)
    
    schema_name_match = re.search(r'^create schema (\w+);', schema.read_text())
    if not schema_name_match:
        raise ValueError('Schema missing initial \'create schema (name)\'')
    
    schema_name = schema_name_match.group(1)

    tmp_path = Path('/tmp')
    files_path = root / 'files'
    if files_path.exists():
        for file_path in files_path.iterdir():
            tmp_file_path = tmp_path / file_path.name
            # print(f'Copy {file_path} to {tmp_file_path}')
            shutil.copy(file_path, tmp_file_path)
            exec_sudo('chmod', '700', str(tmp_file_path))
            exec_sudo('chown', 'postgres:postgres', str(tmp_file_path))
            # tmp_file_path.chmod(700)

    # os.system('ls -l /tmp')

    if extension:
        os.chdir(root)
        print(f'Building extension {schema_name}.')
        exec_sudo('make')

    with conn.cursor() as cur:
        if extension:
            print(f'Checking if extension {schema_name} exists.')
            cur.execute(
                'SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = %s)',
                (schema_name,)
            )
            if cur.fetchone()[0]:
                if replace:
                    print(f'Dropping extension {schema_name}.')
                    cur.execute(f'drop extension {schema_name} cascade')
                else:
                    raise Exception(f'Extension {schema_name} already exists. Run with --replace to replace.')

            print(f'Installing binaries from extension {schema_name}.')
            exec_sudo('make', 'install')

            print(f'Creating extension {schema_name}.')
            cur.execute(f'create extension {schema_name}')
        else:
            print(f'Checking if schema {schema_name} exists.')
            cur.execute(
                'SELECT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = %s)',
                (schema_name,)
            )
            if cur.fetchone()[0]:
                if replace:
                    print(f'Dropping schema {schema_name}.')
                    cur.execute(f'drop schema {schema_name} cascade')
                else:
                    raise Exception(f'Schema {schema_name} already exists. Run with --replace to replace.')

            print(f'Creating schema {schema_name}.')
            cur.execute(schema.read_text())

        conn.commit()

        if mode == 'test':
            print(f'Testing')
            cur.execute((root / 'test.sql').read_text())

def main_cli():
    parser = argparse.ArgumentParser(
        prog='pstk',
        description='Postgres project toolkit.'
    )
    parser.add_argument('root', type=Path)
    parser.add_argument('mode', type=str)
    parser.add_argument('--dbname', default='postgres')
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password', default='postgres')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--socket')
    parser.add_argument('--replace', action='store_true')
    parser.add_argument('--extension', action='store_true')
    parser.add_argument('--schema-path', default='schema.sql')

    main(**vars(parser.parse_args()))