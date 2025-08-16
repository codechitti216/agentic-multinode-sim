from fastapi import FastAPI
import uvicorn
import random
import time
import datetime
from config import PORTS

app = FastAPI(title="Auth Service")

@app.get("/health")
def health_check():
    return {
        "service": "auth",
        "status": "ok",
        "timestamp": time.time()
    }

@app.get("/metrics")
def metrics():
    return {
        "service": "auth",
        "cpu_usage": round(random.uniform(5, 50), 2),
        "memory_usage": round(random.uniform(10, 70), 2),
        "active_sessions": random.randint(10, 200),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/logs")
def logs():
    """Return simulated recent auth service logs"""
    fake_logs = [
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "INFO", "msg": "Authentication service check started"},
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "INFO", "User login successful: john.doe@example.com"},
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "WARN", "Multiple failed login attempts from IP: 192.168.1.100"},
    ]
    if random.random() < 0.3:
        fake_logs.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": "ERROR", "msg": "Connection reset by peer"
        })
    return {"service": "auth", "logs": fake_logs}

@app.post("/recover")
def recover():
    """Simulate a recovery/restart action"""
    time.sleep(1)
    return {
        "service": "auth",
        "action": "recover",
        "status": "ok",
        "message": "Auth service successfully restarted",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORTS["auth"])
