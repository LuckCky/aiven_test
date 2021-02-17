from typing import Dict

import aiopg


async def save_data(db_credentials: str, data: Dict[str, str]) -> None:
    """
    Save data to db
    :param db_credentials: db credentials for connection
    :param data: data to save
    :return: None
    """
    pool = await aiopg.create_pool(db_credentials)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute('INSERT INTO urls (url) VALUES (%s) ON CONFLICT DO NOTHING RETURNING id', (data['url'],))
            data['url_id'] = await cur.fetchone()
            await cur.execute('INSERT INTO check_data ('
                              'error_code, '
                              'latency, '
                              'regexp, '
                              'url_id) VALUES (%s, %s, %s, %s)', (data['error_code'],
                                                                  data['latency'],
                                                                  data['regexp'],
                                                                  data['url_id'], ))
