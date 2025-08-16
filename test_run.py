import requests, time, json
from config import PORTS

PLANNER = f"http://127.0.0.1:{PORTS['commander']}/planner/"
EXECUTE = f"http://127.0.0.1:{PORTS['commander']}/execute/"

incident = "Network latency spikes observed in ap-mumbai-1; API 503s for control plane"

def pretty_print(label, data):
    print(f"\n--- {label} ---")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    try:
        # 1) Ask planner for a plan
        r = requests.post(PLANNER, json={"incident_text": incident}, timeout=15)
        print("planner status:", r.status_code)
        plan = r.json()
        pretty_print("PLAN", plan)

        # 2) Execute plan
        r2 = requests.post(EXECUTE, json=plan, timeout=30)
        print("execute status:", r2.status_code)
        pretty_print("EXECUTION RESULT", r2.json())

    except requests.exceptions.RequestException as e:
        print("Error during test run:", e)
