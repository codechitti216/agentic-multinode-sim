import os
from typing import Dict, List

# Service Configuration
SERVICES = {
    "service_a": {"port": 8001, "dependencies": ["service_b"]},
    "service_b": {"port": 8002, "dependencies": ["service_c"]},
    "service_c": {"port": 8003, "dependencies": ["service_d"]},
    "service_d": {"port": 8004, "dependencies": ["service_a"]},
    "service_e": {"port": 8005, "dependencies": ["service_b", "service_c"]}
}

# LLM Configuration
LLM_BASE_URL = "http://localhost:1234"
LLM_ENDPOINT = f"{LLM_BASE_URL}/v1/chat/completions"
LLM_MODEL = "local-llm"

# Dashboard Configuration
DASHBOARD_PORT = 8501
REFRESH_INTERVAL = 2  # seconds

# Failure Injection Configuration
FAILURE_INJECTION_INTERVAL = 60  # seconds (1 minute)
FAILURE_PROBABILITY = 0.05  # 5% chance instead of 20%

# Logging Configuration
LOG_DIR = "data/logs"
LOG_FILE = "incident_logs.csv"

# Health Check Configuration
HEALTH_CHECK_INTERVAL = 20  # seconds

# Service States
SERVICE_STATES = {
    "healthy": "🟢",
    "degraded": "🟡", 
    "down": "🔴"
}

# Colors for visualization
STATUS_COLORS = {
    "healthy": "#00ff00",
    "degraded": "#ffff00",
    "down": "#ff0000"
}
