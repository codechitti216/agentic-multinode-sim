#!/usr/bin/env python3
import json
import threading
import time
import signal
import sys
from pathlib import Path
from logging_config import setup_logging
from super_tool import SuperTool
from agents.villain_agent import VillainAgent
from agents.felix_agent import FelixAgent

logger = setup_logging(enable_file_logging=False)

def log_and_print(level: str, msg: str):
    ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(f'{ts} [{level}] {msg}', flush=True)

ARENA_PATH = Path(__file__).parent / 'arena.json'
if not ARENA_PATH.exists():
    log_and_print('ERROR', f'arena.json not found at {ARENA_PATH}. Exiting.')
    sys.exit(1)

try:
    arena = json.loads(ARENA_PATH.read_text())
    services_list = arena.get('services', [])
    log_and_print('INFO', f'Loaded arena.json with {len(services_list)} services')
except Exception as e:
    log_and_print('ERROR', f'Failed to read/parse arena.json: {e}')
    raise

st = SuperTool()

def start_all_services():
    for svc in services_list:
        name = svc.get('name')
        if not name:
            log_and_print('WARNING', f'Skipping service entry with no name: {svc}')
            continue
        try:
            log_and_print('INFO', f'[MAIN] Starting service from arena.json: {name}')
            r = st.start_service(name)
            log_and_print('INFO', f'[MAIN] start_service returned for {name}: {r}')
        except Exception as e:
            log_and_print('ERROR', f'[MAIN] Exception starting service {name}: {e}')

shutdown_event = threading.Event()
agent_threads = []
agent_instances = []

def agent_runner(agent_instance, agent_name: str):
    log_and_print('INFO', f'[AGENT:{agent_name}] Starting agent main loop')
    try:
        agent_instance.start()
    except Exception as e:
        log_and_print('ERROR', f'[AGENT:{agent_name}] crashed: {e}')

def start_agents():
    try:
        villain = VillainAgent(st)
        agent_instances.append(('villain', villain))
        t = threading.Thread(target=agent_runner, args=(villain, 'VILLAIN'), daemon=True)
        t.start()
        agent_threads.append(t)
        log_and_print('INFO', '[MAIN] Villain agent thread started')
    except Exception as e:
        log_and_print('ERROR', f'[MAIN] Failed to launch Villain agent: {e}')

    try:
        felix = FelixAgent(st)
        agent_instances.append(('felix', felix))
        t = threading.Thread(target=agent_runner, args=(felix, 'FELIX'), daemon=True)
        t.start()
        agent_threads.append(t)
        log_and_print('INFO', '[MAIN] Felix agent thread started')
    except Exception as e:
        log_and_print('ERROR', f'[MAIN] Failed to launch Felix agent: {e}')

def monitor_loop(poll_interval: float = 5.0):
    log_and_print('INFO', f'[MAIN] Entering monitor loop (poll_interval={poll_interval}s). Press Ctrl-C to exit.')
    try:
        while not shutdown_event.is_set():
            try:
                status = st.get_all_statuses()
                log_and_print('INFO', f'[MONITOR] status snapshot: {status}')
                time.sleep(poll_interval)
            except Exception as e:
                log_and_print('ERROR', f'[MONITOR] unexpected error: {e}')
                time.sleep(poll_interval)
    except KeyboardInterrupt:
        log_and_print('INFO', '[MAIN] KeyboardInterrupt in monitor loop.')
    finally:
        log_and_print('INFO', '[MAIN] Exiting monitor loop.')

def _shutdown(signum=None, frame=None):
    log_and_print('INFO', f'[MAIN] Shutdown signal received: {signum}.')
    shutdown_event.set()
    time.sleep(1.0)
    log_and_print('INFO', '[MAIN] Graceful shutdown complete. Exiting.')
    sys.exit(0)

signal.signal(signal.SIGINT, _shutdown)
try:
    signal.signal(signal.SIGTERM, _shutdown)
except Exception:
    pass

def main():
    log_and_print('INFO', '[MAIN] Starting Chaos Triage Arena main.py')
    start_all_services()
    start_agents()
    time.sleep(0.5)
    monitor_loop()

if __name__ == '__main__':
    main()
