from typing import Dict

import psycopg2

from utils.logger import init_sys_logger

logger = init_sys_logger(__name__)


def create_tables(db_credentials: str, tables: Dict[str, str]):
    """
    Creates all tables in db
    :param db_credentials: string for connection
    :param tables: dict with tables names and sql queries
    :return: None
    """
    conn = psycopg2.connect(db_credentials)
    cur = conn.cursor()
    for table, sql_query in tables.items():
        logger.info(f'creating table {table}')
        create_table(cur, conn, sql_query)

    cur.close()
    conn.close()


def create_table(cur, conn, query: str):
    """
    Executes sql statement for table creation
    :param cur: cursor
    :param conn: connection
    :param query: sql query text
    :return: None
    """
    try:
        cur.execute(query)
        conn.commit()
    except Exception as e:
        logger.error(f'error {e} for {query}')
        conn.rollback()
