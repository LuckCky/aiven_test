from typing import Dict

import psycopg2

from utils.logger import init_sys_logger

logger = init_sys_logger(__name__)


def create_tables(db_credentials: str, tables: Dict[str, str]):
    conn = psycopg2.connect(db_credentials)
    cur = conn.cursor()
    for table, sql_query in tables.items():
        logger.info(f'creating table {table}')
        create_table(cur, conn, sql_query)

    cur.close()
    conn.close()


def create_table(cur, conn, query: str):
    try:
        cur.execute(query)
        conn.commit()
    except Exception as e:
        logger.error(f'error {e} for {query}')
        conn.rollback()
