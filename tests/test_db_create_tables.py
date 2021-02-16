import os

import psycopg2

from db.create_tables import create_tables, create_table
from utils.form_credentials import form_db_credentials

test_tables = {
    'foo': 'CREATE TABLE IF NOT EXISTS foo (name VARCHAR, url VARCHAR);',
    'bar': 'CREATE TABLE IF NOT EXISTS bar (name VARCHAR, count INT);',
    'foo_bar': 'CREATE TABLE IF NOT EXISTS foo_bar (last_name VARCHAR, amount INT);'
}


def set_envs():
    with open('.env.test') as file:
        data = dict(line.split('=') for line in file.readlines() if not line.startswith('#'))

    os.environ['DBNAME'] = data['DBNAME'].strip()
    os.environ['DBUSER'] = data['DBUSER'].strip()
    os.environ['DBPASSWORD'] = data['DBPASSWORD'].strip()
    os.environ['DBHOST'] = data['DBHOST'].strip()
    os.environ['DBPORT'] = data['DBPORT'].strip()


def get_conn():
    dbname = os.environ['DBNAME']
    user = os.environ['DBUSER']
    password = os.environ['DBPASSWORD']
    host = os.environ['DBHOST']
    port = os.environ['DBPORT']

    return psycopg2.connect(f'dbname={dbname} user={user} password={password} host={host} port={port}')


def table_exists(cur, table_name: str) -> bool:
    query = 'SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = %s);'
    cur.execute(query, (table_name,))

    return cur.fetchone()[0]


def delete_tables(cur):
    query = 'DROP TABLE IF EXISTS foo, bar, foo_bar;'
    cur.execute(query)


def test_create_tables_one_table():
    # TODO: set_up and tear_down tast case
    set_envs()
    conn = get_conn()
    cur = conn.cursor()
    for table in ['foo', 'bar']:
        cur.execute(test_tables[table])
    conn.commit()

    test_db_credentials = form_db_credentials()
    create_tables(test_db_credentials, test_tables)

    assert table_exists(cur, 'foo_bar')

    delete_tables(cur)
    conn.commit()
    cur.close()
    conn.close()


def test_create_tables_two_tables():
    # TODO: set_up and tear_down tast case
    set_envs()
    conn = get_conn()
    cur = conn.cursor()
    for table in ['foo_bar']:
        cur.execute(test_tables[table])
    conn.commit()

    test_db_credentials = form_db_credentials()
    create_tables(test_db_credentials, test_tables)

    assert table_exists(cur, 'foo')
    assert table_exists(cur, 'bar')

    delete_tables(cur)
    conn.commit()
    cur.close()
    conn.close()


def test_create_table():
    # TODO: set_up and tear_down tast case
    set_envs()
    conn = get_conn()
    cur = conn.cursor()

    create_table(cur, conn, test_tables['foo'])

    assert table_exists(cur, 'foo')

    delete_tables(cur)
    conn.commit()
    cur.close()
    conn.close()
