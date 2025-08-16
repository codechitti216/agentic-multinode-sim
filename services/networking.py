from fastapi import FastAPI
import requests, datetime, random, time
from config import PORTS

# Centralized service health map (use PORTS from config, not hardcoded)
TARGETS = {
    "auth":         f"http://127.0.0.1:{PORTS['auth']}/health",
    "user":         f"http://127.0.0.1:{PORTS['user']}/health",
    "database":     f"http://127.0.0.1:{PORTS['database']}/health",
    "payment":      f"http://127.0.0.1:{PORTS['payment']}/health",
    "notification": f"http://127.0.0.1:{PORTS['notification']}/health",
    "networking":   f"http://127.0.0.1:{PORTS['networking']}/health",  # self-check now correct
    "commander":    f"http://127.0.0.1:{PORTS['commander']}/healthz",
}

AGG_TIMEOUT = 3.0

app = FastAPI(title="Networking Service")

@app.get("/ping")
def ping():
    return {"ok": True}

@app.get("/health")
def health():
    return {
        "service": "networking",
        "status": "ok",
        "port": PORTS["networking"],
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/all_health")
def all_health():
    """Aggregate health from all known services"""
    out = {}
    for name, url in TARGETS.items():
        try:
            r = requests.get(url, timeout=AGG_TIMEOUT)
            if r.status_code == 200:
                out[name] = {"ok": True, "data": r.json()}
            else:
                out[name] = {"ok": False, "error": f"status={r.status_code}"}
        except Exception as e:
            out[name] = {"ok": False, "error": str(e)}

    return {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "results": out
    }

@app.get("/logs")
def logs():
    """Return simulated recent networking logs"""
    fake_logs = [
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "INFO", "msg": "Networking service check started"},
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "WARN", "msg": "Latency spike detected on ap-mumbai-1"},
        {"timestamp": datetime.datetime.utcnow().isoformat(),
         "level": "ERROR", "msg": "Transient packet loss > 5%"},
    ]
    if random.random() < 0.3:
        fake_logs.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": "ERROR", "msg": "Connection reset by peer"
        })
    return {"service": "networking", "logs": fake_logs}

@app.get("/metrics")
def metrics():
    """Simulated metrics for networking"""
    return {
        "service": "networking",
        "cpu_usage": round(random.uniform(5, 50), 2),
        "memory_usage": round(random.uniform(30, 80), 2),
        "active_sessions": random.randint(50, 250),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.post("/recover")
def recover():
    """Simulate a recovery/restart action"""
    time.sleep(1)
    return {
        "service": "networking",
        "action": "recover",
        "status": "ok",
        "message": "Networking service successfully restarted",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
