import requests, time, json, os
from datetime import datetime
from config import PORTS, DATA_DIR

LOG_FILE = os.path.join(DATA_DIR, "logs", "health.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def poll_health():
    results = {}
    for service, port in PORTS.items():
        url = f"http://127.0.0.1:{port}/health"
        try:
            r = requests.get(url, timeout=1)
            data = r.json()
            results[service] = {"ok": True, "data": data}
        except Exception as e:
            results[service] = {"ok": False, "error": str(e)}
    return results

def log_results(results):
    ts = datetime.utcnow().isoformat()
    entry = {"timestamp": ts, "results": results}
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry, indent=2))  # easy to copy-paste

if __name__ == "__main__":
    print(f"[health_logger] Writing logs to {LOG_FILE}")
    while True:
        results = poll_health()
        log_results(results)
        time.sleep(5)  # poll every 5 sec
