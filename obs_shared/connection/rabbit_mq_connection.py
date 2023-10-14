import urllib.parse
from typing import Callable

import pika


class RMQConnection:
    def __init__(self, host: str, username: str, password: str):
        credentials = pika.PlainCredentials(username, password)
        self._connection_parameters = pika.ConnectionParameters(host, credentials=credentials)
        self._connection: pika.BlockingConnection = None
        self._channel: pika.adapters.blocking_connection.BlockingChannel = None

    def consume(self, que: str, call_back: Callable) -> None:
        self._connection = pika.BlockingConnection(self._connection_parameters)
        self._channel = self._connection.channel()
        self._channel.queue_declare(que)
        self._channel.basic_consume(queue=que, on_message_callback=call_back, auto_ack=True)
        self._channel.start_consuming()

    def send_message(self, que: str, message: bytes) -> None:
        self._connection = pika.BlockingConnection(self._connection_parameters)
        self._channel = self._connection.channel()
        self._channel.queue_declare(que)
        self._channel.basic_publish(exchange="", routing_key=que, body=message)
        self._connection.close()

        