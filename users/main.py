from fastapi import FastAPI

app = FastAPI(title="users-service")

FAKE_USERS = {
    1: {"id": 1, "name": "Vlad"},
    2: {"id": 2, "name": "Anna"},
}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = FAKE_USERS.get(user_id)
    return user or {"error": "not found"}


