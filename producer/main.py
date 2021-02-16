import asyncio
from time import sleep

from config import tables
from db.create_tables import create_tables
from db.select_data import get_data_to_check, get_sleep_time
from website import Website
from utils.form_credentials import form_db_credentials, form_message_broker_credentials
from utils.logger import init_sys_logger

logger = init_sys_logger(__name__)


def main():
    db_credentials = form_db_credentials()
    message_broker_credentials = form_message_broker_credentials()
    create_tables(db_credentials, tables)
    while True:
        data_to_check = get_data_to_check(db_credentials)
        time_to_sleep = get_sleep_time(db_credentials)
        if not data_to_check:
            sleep(time_to_sleep)
            logger.info(f'sleeping {time_to_sleep} seconds')
            continue
        tasks = []
        for row in data_to_check:
            url, regexp = row
            website = Website(url, message_broker_credentials, regexp)
            tasks.append(website.perform_check())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*tasks))
        logger.info(f'sleeping {time_to_sleep} seconds')
        sleep(time_to_sleep)


if __name__ == '__main__':
    main()
