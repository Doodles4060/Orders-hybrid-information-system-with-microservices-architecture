import os, json
import httpx
import pika
from fastapi import FastAPI

app = FastAPI(title="orders-service")

USERS_URL = os.getenv("USERS_URL", "http://users:8000")
AMQP_URL = os.getenv("AMQP_URL")          # ❗ без дефолтного значення
QUEUE = "order_events"

def publish_event(event: dict):
    if not AMQP_URL:
        return                              # ❗ базовий (синхронний) режим

    params = pika.URLParameters(AMQP_URL)
    with pika.BlockingConnection(params) as conn:
        ch = conn.channel()
        ch.queue_declare(queue=QUEUE, durable=True)
        ch.basic_publish(
            exchange="",
            routing_key=QUEUE,
            body=json.dumps(event).encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2),
        )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/orders")
async def create_order(user_id: int, item: str):
    async with httpx.AsyncClient(timeout=5.0) as client:
        user = (await client.get(f"{USERS_URL}/users/{user_id}")).json()

    order = {"order_id": 123, "user_id": user_id, "item": item}

    publish_event({"type": "OrderCreated", "payload": order})

    return {"created": order, "user": user}
