import asyncio
import json
import re
from typing import Dict

from aiohttp import ClientSession, TraceConfig
from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context

from config import kafka_topic
from utils.logger import init_sys_logger

logger = init_sys_logger(__name__)


context = create_ssl_context(
    cafile="./.ca-cert",
    certfile="./.cert-signed",
    keyfile="./.cert-key",
)


class Website:
    """
    Class for checking info and storing check data
    """

    def __init__(self, url: str, message_broker: str, regexp: str):
        self.url = url
        self.message_broker = message_broker
        self.regexp = regexp
        self.latency = -1
        self.error_code = -1
        self.trace_config = TraceConfig()

    async def _on_request_start(self, session, trace_config_ctx, params):
        trace_config_ctx.start = asyncio.get_event_loop().time()

    async def _on_request_end(self, session, trace_config_ctx, params):
        self.latency = asyncio.get_event_loop().time() - trace_config_ctx.start

    async def perform_check(self):
        """
        Website check pipeline
        :return: None
        """
        try:
            text, error_code = await self.fetch()
            self.set_error_code(error_code)
            regexp_found = self.check_regexp(text)
            message = self.form_message(regexp_found)
        except Exception as e:
            logger.error(f'error with check {self.url}: {e}')
            message = self.form_message(False)
        try:
            await self.send_message(message)
            logger.info(f'url {self.url} checked, message sent')
        except Exception as e:
            logger.error(f'error with sending message {self.url}: {e}')

    async def fetch(self):
        """
        Asynchronously fetch url
        :return: response text and status code
        """
        self.trace_config.on_request_start.append(self._on_request_start)
        self.trace_config.on_request_end.append(self._on_request_end)
        async with ClientSession(trace_configs=[self.trace_config]) as session:
            async with session.get(self.url) as response:
                status_code = response.status
                html = await response.text()
                return html, status_code

    def set_error_code(self, response_code):
        self.error_code = response_code

    def check_regexp(self, html) -> bool:
        """
        Check if regexp matches html string
        :param html: html string
        :return: check result
        """
        compiled_regexp = re.compile(self.regexp)
        return True if compiled_regexp.findall(html) else False

    def form_message(self, regexp_found):
        """
        Forms Kafka message
        :param regexp_found: status if regexp was found
        :return: Kafka message
        """
        return {'error_code': self.error_code, 'latency': self.latency, 'regexp': regexp_found, 'url': self.url}

    async def send_message(self, message: Dict[str, str]):
        """
        Asynchronously send message to Kafka topic
        :param message: Kafka message
        :return: None
        """
        producer = AIOKafkaProducer(bootstrap_servers=self.message_broker,
                                    security_protocol="SSL", ssl_context=context)
        await producer.start()
        try:
            await producer.send_and_wait(kafka_topic, json.dumps(message).encode())
        finally:
            await producer.stop()
