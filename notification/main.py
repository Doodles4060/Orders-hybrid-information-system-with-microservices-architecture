import os
import json
import threading
import time
import pika
from fastapi import FastAPI
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("notification")


app = FastAPI(title="notification-service")

AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE = "order_events"


def connect_with_retry(retries=30, delay=2):
    params = pika.URLParameters(AMQP_URL)

    for attempt in range(1, retries + 1):
        try:
            log.info("AMQP connect attempt %s/%s", attempt, retries)
            return pika.BlockingConnection(params)
        except Exception as e:
            log.error(f"[notification] AMQP not ready yet: {e}")
            time.sleep(delay)

    raise RuntimeError("RabbitMQ is not available after retries")


def consume():
    connection = connect_with_retry()
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE, durable=True)

    def on_message(ch, method, properties, body):
        event = json.loads(body.decode())
        log.info("NOTIFICATION GOT EVENT: %s", event)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE, on_message_callback=on_message)

    log.info("Waiting for events…")
    channel.start_consuming()


@app.on_event("startup")
def startup():
    threading.Thread(target=consume, daemon=True).start()


@app.get("/health")
def health():
    return {"status": "ok"}
