from typing import List, Tuple

import psycopg2

from config import default_timeout
from utils.logger import init_sys_logger

logger = init_sys_logger(__name__)


def get_data_to_check(db_credentials: str) -> List[Tuple[str]]:
    conn = psycopg2.connect(db_credentials)
    cur = conn.cursor()
    cur.execute('SELECT u.url, r.regexp_text FROM urls u'
                ' LEFT OUTER JOIN regexps r ON u.id=r.url_id'
                ' ORDER BY u.id;')
    return cur.fetchall()


def get_sleep_time(db_credentials: str) -> int:
    conn = psycopg2.connect(db_credentials)
    cur = conn.cursor()
    cur.execute('SELECT timeout FROM timeouts ORDER BY id DESC LIMIT 1;')
    try:
        return cur.fetchone()[0]
    except Exception as e:
        logger.error(f'error while getting sleep time: {e}')
        return default_timeout
