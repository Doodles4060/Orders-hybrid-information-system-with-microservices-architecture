import os
import httpx
from fastapi import FastAPI

app = FastAPI(title="api-gateway")
ORDERS_URL = os.getenv("ORDERS_URL", "http://orders:8000")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/orders")
async def create_order(user_id: int, item: str):
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.post(f"{ORDERS_URL}/orders", params={"user_id": user_id, "item": item})
        return r.json()
