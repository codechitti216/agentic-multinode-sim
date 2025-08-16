from fastapi import FastAPI
import uvicorn
from config import PORTS
import random
import time
import datetime

AUTH_URL = f"http://127.0.0.1:{PORTS['auth']}/health"
DB_URL   = f"http://127.0.0.1:{PORTS['database']}/health"

TIMEOUT_S = 1.5
RETRIES   = 2
BACKOFF   = 0.15

app = FastAPI(title="User Service")

def check_ok(url: str, timeout=TIMEOUT_S, retries=RETRIES) -> bool:
    for _ in range(retries):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200 and r.json().get("status") == "ok":
                return True
        except Exception:
            time.sleep(BACKOFF)
    return False

@app.get("/health")
def health_check():
    return {
        "service": "user",
        "status": "ok",
        "timestamp": time.time()
    }

@app.get("/metrics")
def metrics():
    return {
        "service": "user",
        "cpu_usage": round(random.uniform(5, 50), 2),
        "memory_usage": round(random.uniform(10, 70), 2),
        "active_sessions": random.randint(10, 200),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/users")
def get_users():
    return {
        "users": [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
        ]
    }

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    }

@app.get("/logs")
def logs():
    """Return simulated recent user service logs"""
    fake_logs = [
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "INFO", "msg": "User service check started"},
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "INFO", "msg": "User profile updated: user_id=123"},
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "WARN", "msg": "User session expired: user_id=456"},
    ]
    if random.random() < 0.3:
        fake_logs.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": "ERROR", "msg": "Connection reset by peer"
        })
    return {"service": "user", "logs": fake_logs}

@app.post("/recover")
def recover():
    """Simulate a recovery/restart action"""
    time.sleep(1)
    return {
        "service": "user",
        "action": "recover",
        "status": "ok",
        "message": "User service successfully restarted",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORTS["user"])
