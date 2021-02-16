import json
import os
import pytest

from aiohttp.client_exceptions import InvalidURL
from aiokafka import AIOKafkaConsumer
from aiokafka.helpers import create_ssl_context

from config import kafka_topic
from producer.website import Website
from utils.form_credentials import form_message_broker_credentials


def set_envs():
    with open('.env.test') as file:
        data = dict(line.split('=') for line in file.readlines() if not line.startswith('#'))

    os.environ['KAFKAHOST'] = data['KAFKAHOST'].strip()
    os.environ['KAFKAPORT'] = data['KAFKAPORT'].strip()


@pytest.mark.asyncio
async def test_perform_check_ok(httpserver, caplog):
    httpserver.expect_request('/foobar').respond_with_data('<head></head>', content_type="text/plain")
    url = httpserver.url_for('/foobar')
    set_envs()
    test_message_broker_credentials = form_message_broker_credentials()
    website = Website(url, test_message_broker_credentials, 'bar')
    await website.perform_check()
    captured = caplog.records[-1].message

    assert 'checked, message sent' in captured


@pytest.mark.asyncio
async def test_perform_check_fetch_exception(caplog):
    url = 'localhost'
    test_message_broker_credentials = form_message_broker_credentials()
    website = Website(url, test_message_broker_credentials, 'bar')
    await website.perform_check()
    message_sent_msg = caplog.records[-1].message
    url_check_error = caplog.records[-2].message

    assert message_sent_msg == 'url localhost checked, message sent'
    assert url_check_error == 'error with check localhost: localhost'


@pytest.mark.asyncio
async def test_perform_check_kafka_exception(caplog):
    url = 'localhost'
    website = Website(url, 'foo', 'bar')
    await website.perform_check()
    error_msg = caplog.records[-2].message

    assert 'error with sending message' in error_msg


@pytest.mark.asyncio
async def test_fetch(httpserver):
    httpserver.expect_request('/foobar').respond_with_data('<head></head>', content_type="text/plain")
    url = httpserver.url_for('/foobar')
    website = Website(url, 'foo', 'bar')
    text, status_code = await website.fetch()
    assert isinstance(text, str)
    assert status_code == 200


@pytest.mark.asyncio
async def test_fetch_not_working_site():
    url = 'localhost'
    website = Website(url, 'foo', 'bar')
    with pytest.raises(InvalidURL):
        await website.fetch()


@pytest.mark.asyncio
async def test_set_error_code_200(httpserver):
    httpserver.expect_request('/foobar').respond_with_data('<head></head>', content_type="text/plain")
    url = httpserver.url_for('/foobar')
    website = Website(url, 'foo', 'bar')
    _, status_code = await website.fetch()
    website.set_error_code(status_code)
    assert website.error_code == 200


@pytest.mark.asyncio
async def test_set_error_code_418(httpserver):
    httpserver.expect_request('/foobar').respond_with_data('<head></head>', status=418, content_type="text/plain")
    url = httpserver.url_for('/foobar')
    website = Website(url, 'foo', 'bar')
    _, status_code = await website.fetch()
    website.set_error_code(status_code)
    assert website.error_code == 418


@pytest.mark.asyncio
async def test_check_regexp_true(httpserver):
    httpserver.expect_request('/foobar').respond_with_data('<head>42</head>', content_type="text/plain")
    url = httpserver.url_for('/foobar')
    website = Website(url, 'foo', '\\d')
    text, _ = await website.fetch()
    assert website.check_regexp(text)


@pytest.mark.asyncio
async def test_check_regexp_false(httpserver):
    httpserver.expect_request('/foobar').respond_with_data('<head>forty two</head>', content_type="text/plain")
    url = httpserver.url_for('/foobar')
    website = Website(url, 'foo', '\\d')
    text, _ = await website.fetch()
    assert not website.check_regexp(text)


def test_form_message():
    url = 'localhost'
    website = Website(url, 'foo', 'bar')
    test_message = website.form_message(True)

    assert len(test_message) == 4
    assert list(test_message.keys()) == ['error_code', 'latency', 'regexp', 'url']
    assert test_message['error_code'] == -1
    assert test_message['latency'] == -1
    assert test_message['regexp']
    assert test_message['url'] == url


def message_sent():
    return False


@pytest.mark.asyncio
async def test_send_message():
    set_envs()
    url = 'localhost'
    test_message_broker_credentials = form_message_broker_credentials()
    context = create_ssl_context(
        cafile="./.ca-cert",
        certfile="./.cert-signed",
        keyfile="./.cert-key",
    )

    consumer = AIOKafkaConsumer(
        kafka_topic,
        bootstrap_servers=test_message_broker_credentials,
        security_protocol="SSL", ssl_context=context
    )
    await consumer.start()

    website = Website(url, test_message_broker_credentials, 'bar')
    test_message = website.form_message(True)
    await website.send_message(test_message)
    async for msg in consumer:
        received_message = json.loads(msg.value)
        await consumer.stop()

    assert received_message == test_message
