import os

import psycopg2
import pytest

from config import tables
from db.create_tables import create_tables
from db.save_data import save_data
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


@pytest.mark.asyncio
async def test_save_data():
    set_envs()
    set_envs()
    conn = get_conn()
    cur = conn.cursor()
    delete_tables(cur)
    conn.commit()

    test_db_credentials = form_db_credentials()
    create_tables(test_db_credentials, tables)
    test_data = {
        'error_code': 200,
        'latency': 0.004029075000289595,
        'regexp': False,
        'url': 'http://localhost:56319/foobar',
        'checked_at': '1970-01-01_16:20'
    }

    await save_data(test_db_credentials, test_data)

    cur.execute('SELECT id, url FROM urls;')
    url_id, url = cur.fetchone()
    assert url == test_data['url']

    cur.execute('SELECT error_code, latency, regexp, checked_at, url_id FROM check_data;')
    error_code, latency, regexp, checked_at, url_id_check = cur.fetchone()
    assert error_code == test_data['error_code']
    assert latency == test_data['latency']
    assert regexp == test_data['regexp']
    assert checked_at == test_data['checked_at']
    assert url_id_check == url_id

    delete_tables(cur)
    conn.commit()
