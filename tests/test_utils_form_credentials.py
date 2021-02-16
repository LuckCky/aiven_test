import os

from utils.form_credentials import form_db_credentials, form_message_broker_credentials


def test_form_db_credentials():
    os.environ['DBNAME'] = 'test_db'
    os.environ['DBUSER'] = 'test_user'
    os.environ['DBPASSWORD'] = 'test_pwd'
    os.environ['DBHOST'] = 'test_host'
    os.environ['DBPORT'] = 'test_port'
    test_db_credentials = form_db_credentials()

    assert 'test_db' in test_db_credentials
    assert 'test_user' in test_db_credentials
    assert 'test_pwd' in test_db_credentials
    assert 'test_host' in test_db_credentials
    assert 'test_port' in test_db_credentials


def test_form_message_broker_credentials():
    os.environ['KAFKAHOST'] = 'test_host'
    os.environ['KAFKAPORT'] = 'test_port'

    test_mb_credentials = form_message_broker_credentials()

    assert 'test_host' in test_mb_credentials
    assert 'test_port' in test_mb_credentials
