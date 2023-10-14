from typing import Callable

import pika


class RMQConnection:
    def __init__(self, dsn_url: str, que: str):
        self._connection = pika.BlockingConnection(pika.URLParameters(dsn_url))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=que)

    def consume(self, que: str, call_back: Callable) -> None:
        self._channel.basic_consume(queue=que, on_message_callback=call_back, auto_ack=True)
        self._channel.start_consuming()

    def send_message(self, que: str, message: bytes) -> None:
        self._channel.basic_publish(exchange="", routing_key=que, body=message)

        