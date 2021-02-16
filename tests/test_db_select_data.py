import os

import psycopg2

from config import tables, default_timeout
from db.create_tables import create_tables
from db.select_data import get_data_to_check, get_sleep_time
from utils.form_credentials import form_db_credentials


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


def delete_tables(cur):
    query = 'DROP TABLE IF EXISTS urls, timeouts, regexps, check_data CASCADE;'
    cur.execute(query)


def test_get_data_to_check():
    # TODO: set_up and tear_down test case
    set_envs()
    conn = get_conn()
    cur = conn.cursor()
    delete_tables(cur)
    conn.commit()

    test_db_credentials = form_db_credentials()
    create_tables(test_db_credentials, tables)
    for url in ['url1', 'url2']:
        cur.execute('INSERT INTO urls (url) VALUES (%s) ON CONFLICT DO NOTHING;', (url,))
    cur.execute("INSERT INTO regexps (regexp_text, url_id) VALUES ('.', (SELECT id FROM urls WHERE url='url2'))")
    conn.commit()

    assert get_data_to_check(test_db_credentials) == [('url1', None), ('url2', '.')]

    delete_tables(cur)
    conn.commit()
    cur.close()
    conn.close()


def test_get_urls_none():
    # TODO: set_up and tear_down test case
    set_envs()
    conn = get_conn()
    cur = conn.cursor()
    delete_tables(cur)
    conn.commit()

    test_db_credentials = form_db_credentials()
    create_tables(test_db_credentials, tables)

    assert get_data_to_check(test_db_credentials) == []

    delete_tables(cur)
    conn.commit()
    cur.close()
    conn.close()


def test_get_sleep_time_last():
    # TODO: set_up and tear_down test case
    set_envs()
    conn = get_conn()
    cur = conn.cursor()
    delete_tables(cur)
    conn.commit()

    test_db_credentials = form_db_credentials()
    create_tables(test_db_credentials, tables)
    for timeout in range(4):
        cur.execute('INSERT INTO timeouts (timeout) VALUES (%s);', (timeout,))
    conn.commit()

    assert get_sleep_time(test_db_credentials) == 3

    delete_tables(cur)
    conn.commit()
    cur.close()
    conn.close()


def test_get_sleep_time_one():
    # TODO: set_up and tear_down test case
    set_envs()
    conn = get_conn()
    cur = conn.cursor()
    delete_tables(cur)
    conn.commit()

    test_db_credentials = form_db_credentials()
    create_tables(test_db_credentials, tables)
    cur.execute('INSERT INTO timeouts (timeout) VALUES (3);')
    conn.commit()

    assert get_sleep_time(test_db_credentials) == 3

    delete_tables(cur)
    conn.commit()
    cur.close()
    conn.close()


def test_get_sleep_time_none():
    # TODO: set_up and tear_down test case
    set_envs()
    conn = get_conn()
    cur = conn.cursor()
    delete_tables(cur)
    conn.commit()

    test_db_credentials = form_db_credentials()
    create_tables(test_db_credentials, tables)

    assert get_sleep_time(test_db_credentials) == default_timeout

    delete_tables(cur)
    conn.commit()
    cur.close()
    conn.close()
