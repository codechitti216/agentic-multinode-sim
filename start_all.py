import subprocess, sys, time, os
from config import PORTS

PY = sys.executable
procs = []

def start(module, port):
    cmd = [
        PY, "-m", "uvicorn", f"{module}:app",
        "--host", "127.0.0.1", "--port", str(port),
        "--log-level", "info", "--reload"
    ]
    p = subprocess.Popen(cmd)
    print("started", module, "pid", p.pid, "on port", port)
    procs.append(p)

if __name__ == "__main__":
    os.makedirs("data/logs", exist_ok=True)

    # Order matters because of dependencies
    start("services.database_service", PORTS["database"])
    time.sleep(0.5)
    start("services.auth_service", PORTS["auth"])
    time.sleep(0.5)
    start("services.user_service", PORTS["user"])
    time.sleep(0.5)
    start("services.payment_service", PORTS["payment"])
    time.sleep(0.5)
    start("services.notification_service", PORTS["notification"])
    time.sleep(0.5)

    # Support layers
    start("services.networking", PORTS["networking"])
    time.sleep(0.8)

    # Agent commander (brain)
    start("commander.main", PORTS["commander"])

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("shutting down...")
        for p in procs:
            p.terminate()
        sys.exit(0)
