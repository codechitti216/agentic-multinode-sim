from fastapi import FastAPI
import psutil, time, random, datetime

app = FastAPI()
service_name = "database"

def get_metrics():
    return {
        "cpu_usage": round(psutil.cpu_percent(interval=0.2), 2),
        "memory_usage": round(psutil.virtual_memory().percent, 2),
        "active_queries": random.randint(50, 200),
    }

@app.get("/health")
def health():
    # Simulate occasional DB degradation
    status = "ok"
    if random.random() < 0.05:  # 5% chance DB randomly degrades
        status = "degraded"

    return {
        "service": service_name,
        "status": status,
        "timestamp": time.time(),
    }

@app.get("/metrics")
def metrics():
    return {
        "service": "database",
        "cpu_usage": round(random.uniform(5, 50), 2),
        "memory_usage": round(random.uniform(10, 70), 2),
        "active_sessions": random.randint(10, 200),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/logs")
def logs():
    """Return simulated recent database service logs"""
    fake_logs = [
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "INFO", "msg": "Database service check started"},
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "INFO", "Query executed successfully: SELECT * FROM users"},
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "WARN", "Slow query detected: execution_time=2.5s"},
    ]
    if random.random() < 0.3:
        fake_logs.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": "ERROR", "msg": "Connection reset by peer"
        })
    return {"service": "database", "logs": fake_logs}

@app.post("/recover")
def recover():
    """Simulate a recovery/restart action"""
    time.sleep(1)
    return {
        "service": "database",
        "action": "recover",
        "status": "ok",
        "message": "Database service successfully restarted",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
