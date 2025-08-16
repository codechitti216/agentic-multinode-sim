from fastapi import FastAPI
import uvicorn
from config import PORTS
import random
import time
import datetime

USER_URL    = f"http://127.0.0.1:{PORTS['user']}/health"
PAYMENT_URL = f"http://127.0.0.1:{PORTS['payment']}/health"

app = FastAPI(title="Notification Service")

@app.get("/health")
def health_check():
    return {
        "service": "notification",
        "status": "ok",
        "timestamp": time.time()
    }

@app.get("/metrics")
def metrics():
    return {
        "service": "notification",
        "cpu_usage": round(random.uniform(5, 50), 2),
        "memory_usage": round(random.uniform(10, 70), 2),
        "active_sessions": random.randint(10, 200),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/notifications")
def get_notifications():
    return {
        "notifications": [
            {"id": 1, "type": "email", "status": "sent"},
            {"id": 2, "type": "sms", "status": "pending"}
        ]
    }

@app.get("/notifications/{notification_id}")
def get_notification(notification_id: int):
    return {
        "id": notification_id,
        "type": "email",
        "status": "sent"
    }

@app.get("/logs")
def logs():
    """Return simulated recent notification service logs"""
    fake_logs = [
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "INFO", "msg": "Notification service check started"},
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "INFO", "Email notification sent: user_id=123"},
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "WARN", "SMS delivery failed: phone=+1234567890"},
    ]
    if random.random() < 0.3:
        fake_logs.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": "ERROR", "msg": "Connection reset by peer"
        })
    return {"service": "notification", "logs": fake_logs}

@app.post("/recover")
def recover():
    """Simulate a recovery/restart action"""
    time.sleep(1)
    return {
        "service": "notification",
        "action": "recover",
        "status": "ok",
        "message": "Notification service successfully restarted",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORTS["notification"])
