from fastapi import FastAPI
import uvicorn
from config import PORTS
import random
import time
import datetime

USER_URL = f"http://127.0.0.1:{PORTS['user']}/health"
DB_URL   = f"http://127.0.0.1:{PORTS['database']}/health"

TIMEOUT_S = 1.5
RETRIES   = 2
BACKOFF   = 0.15

app = FastAPI(title="Payment Service")

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
        "service": "payment",
        "status": "ok",
        "timestamp": time.time()
    }

@app.get("/metrics")
def metrics():
    return {
        "service": "payment",
        "cpu_usage": round(random.uniform(5, 50), 2),
        "memory_usage": round(random.uniform(10, 70), 2),
        "active_sessions": random.randint(10, 200),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/payments")
def get_payments():
    return {
        "payments": [
            {"id": 1, "amount": 100.00, "status": "completed"},
            {"id": 2, "amount": 250.50, "status": "pending"}
        ]
    }

@app.get("/payments/{payment_id}")
def get_payment(payment_id: int):
    return {
        "id": payment_id,
        "amount": random.uniform(10, 1000),
        "status": "completed"
    }

@app.get("/logs")
def logs():
    """Return simulated recent payment service logs"""
    fake_logs = [
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "INFO", "msg": "Payment service check started"},
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "INFO", "msg": "Payment processed successfully: payment_id=789"},
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "WARN", "msg": "Payment declined: insufficient_funds"},
    ]
    if random.random() < 0.3:
        fake_logs.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": "ERROR", "msg": "Connection reset by peer"
        })
    return {"service": "payment", "logs": fake_logs}

@app.post("/recover")
def recover():
    """Simulate a recovery/restart action"""
    time.sleep(1)
    return {
        "service": "payment",
        "action": "recover",
        "status": "ok",
        "message": "Payment service successfully restarted",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORTS["payment"])
