import os


def form_db_credentials() -> str:
    """
    Forms DB credentials for connection
    :return: credentials
    """
    dbname = os.environ['DBNAME']
    user = os.environ['DBUSER']
    password = os.environ['DBPASSWORD']
    host = os.environ['DBHOST']
    port = os.environ['DBPORT']

    return f'dbname={dbname} user={user} password={password} host={host} port={port}'


def form_message_broker_credentials() -> str:
    """
    Forms Kafka credentials for connection
    :return: credentials
    """
    host = os.environ['KAFKAHOST']
    port = os.environ['KAFKAPORT']

    return f'{host}:{port}'
