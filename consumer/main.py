import asyncio
import json

from aiokafka import AIOKafkaConsumer
from aiokafka.helpers import create_ssl_context

from config import kafka_topic, tables
from db.create_tables import create_tables
from db.save_data import save_data
from utils.form_credentials import form_db_credentials, form_message_broker_credentials
from utils.logger import init_sys_logger

logger = init_sys_logger(__name__)

context = create_ssl_context(
    cafile="./.ca-cert",
    certfile="./.cert-signed",
    keyfile="./.cert-key",
)


async def consume():
    db_credentials = form_db_credentials()
    create_tables(db_credentials, tables)
    message_broker_credentials = form_message_broker_credentials()
    consumer = AIOKafkaConsumer(
        kafka_topic,
        bootstrap_servers=message_broker_credentials,
        security_protocol="SSL", ssl_context=context
    )
    await consumer.start()
    try:
        async for msg in consumer:
            message = json.loads(msg.value)
            logger.info(f'saving message {message.get("url", "error")}')
            await save_data(db_credentials, message)
    finally:
        await consumer.stop()

asyncio.run(consume())
