import json
import time
import traceback
from typing import Dict, Any

import requests

BASE = "http://127.0.0.1:8000/api"
TIMEOUT = 8


def call(method: str, path: str, name: str) -> Dict[str, Any]:
	url = f"{BASE}{path}"
	start = time.time()
	try:
		resp = requests.request(method, url, timeout=TIMEOUT)
		elapsed = time.time() - start
		try:
			data = resp.json()
		except Exception:
			data = resp.text
		return {
			"step": name,
			"url": url,
			"status_code": resp.status_code,
			"elapsed_s": round(elapsed, 3),
			"data": data,
		}
	except Exception as e:
		elapsed = time.time() - start
		return {
			"step": name,
			"url": url,
			"error": str(e),
			"elapsed_s": round(elapsed, 3),
		}


def pretty(o: Dict[str, Any]) -> str:
	try:
		return json.dumps(o, ensure_ascii=False, separators=(",", ":"))
	except Exception:
		return str(o)


def main():
	steps = []
	steps.append(call("GET", "/health", "health"))
	steps.append(call("GET", "/status", "status_before"))
	steps.append(call("POST", "/actions/stop/echo_service", "stop_echo"))
	time.sleep(0.8)
	steps.append(call("GET", "/status", "status_after_stop"))
	steps.append(call("POST", "/actions/start/echo_service", "start_echo"))
	time.sleep(0.8)
	steps.append(call("GET", "/status", "status_after_start"))
	steps.append(call("POST", "/actions/kill/echo_service", "kill_echo"))
	time.sleep(0.8)
	steps.append(call("GET", "/status", "status_after_kill"))
	steps.append(call("POST", "/actions/inject/echo_service/logical_failure", "inject_failure"))
	steps.append(call("GET", "/metrics", "metrics_after_inject"))
	steps.append(call("POST", "/actions/recover/echo_service", "recover_echo"))
	steps.append(call("POST", "/actions/latency/echo_service/500", "latency_500"))
	steps.append(call("POST", "/actions/cpu-stress/echo_service/50", "cpu_stress_50"))
	steps.append(call("POST", "/actions/memory-leak/echo_service/50", "memory_leak_50"))
	steps.append(call("GET", "/metrics", "metrics_after_actions"))

	for s in steps:
		print(pretty(s))


if __name__ == "__main__":
	main()
