from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
from commander.llm_client import call_llm_simple
import requests, time, json, os, re
from utils.logger import get_logger, jlog
from config import PORTS, DATA_DIR

LOGFILE = os.path.join(DATA_DIR, "logs", "commander.log")
logger = get_logger("commander", logfile=LOGFILE)

app = FastAPI(title="commander")


# -------------------------------
# Port validation and URL building
# -------------------------------

def build_service_url(service_name: str, endpoint: str) -> str:
    """Build service URL with validation and logging"""
    port = PORTS.get(service_name)
    
    if port is None:
        logger.error(f"FATAL MISROUTING: Service '{service_name}' not found in PORTS config")
        logger.error(f"Available services: {list(PORTS.keys())}")
        raise ValueError(f"Unknown service: {service_name}")
    
    if port <= 0 or port > 65535:
        logger.error(f"FATAL MISROUTING: Invalid port {port} for service {service_name}")
        raise ValueError(f"Invalid port: {port}")
    
    url = f"http://127.0.0.1:{port}{endpoint}"
    
    # Log the URL being built for debugging
    logger.info(f"URL_BUILT: service={service_name}, port={port}, endpoint={endpoint}, full_url={url}")
    
    return url

def log_request_start(step_id: str, agent_type: str, method: str, target_url: str, service_name: str, expected_port: int):
    """Log structured request information before making HTTP call"""
    logger.info(json.dumps({
        "event": "REQUEST_START",
        "step_id": step_id,
        "agent_type": agent_type,
        "method": method,
        "target_url": target_url,
        "service_name": service_name,
        "expected_port": expected_port,
        "timestamp": time.time()
    }))

def log_request_result(step_id: str, status_code: int, response_time: float, error: str = None):
    """Log structured response information after HTTP call"""
    log_data = {
        "event": "REQUEST_RESULT",
        "step_id": step_id,
        "status_code": status_code,
        "response_time_ms": round(response_time * 1000, 2),
        "timestamp": time.time()
    }
    if error:
        log_data["error"] = error
        logger.error(json.dumps(log_data))
    else:
        logger.info(json.dumps(log_data))


# -------------------------------
# Models
# -------------------------------

class PlannerRequest(BaseModel):
    incident_text: str

class PlanStep(BaseModel):
    step_id: str
    title: str
    agent_type: str
    params: Dict[str, Any]
    depends_on: List[str] = []

class Plan(BaseModel):
    plan_id: str
    incident_text: str
    steps: List[PlanStep]


# -------------------------------
# Routes
# -------------------------------

@app.get("/healthz")
def healthz():
    """Commander health endpoint"""
    return {
        "service": "commander",
        "status": "ok",
        "timestamp": time.time()
    }


@app.post("/planner/")
def planner(req: PlannerRequest):
    """Generate a remediation plan for an incident"""
    jlog(logger, "commander", "planner_called", "INFO", incident=req.incident_text)

    llm_out = call_llm_simple(req.incident_text)
    if llm_out:
        try:
            # Find JSON object/array inside LLM output
            m = re.search(r'(\{.*\}|\[.*\])', llm_out, flags=re.S)
            if m:
                parsed = json.loads(m.group(0))
                if isinstance(parsed, dict) and "steps" in parsed:
                    return parsed
                elif isinstance(parsed, list):
                    return {
                        "plan_id": f"plan_{int(time.time())}",
                        "incident_text": req.incident_text,
                        "steps": parsed
                    }
        except Exception:
            pass

    # Fallback heuristic plan
    plan = {
        "plan_id": f"plan_{int(time.time())}",
        "incident_text": req.incident_text,
        "steps": [
            {
                "step_id": "s1",
                "title": "Analyze networking logs",
                "agent_type": "log-agent",
                "params": {"service": "networking"},
                "depends_on": []
            },
            {
                "step_id": "s2",
                "title": "Fetch networking metrics",
                "agent_type": "metric-agent",
                "params": {"service": "networking"},
                "depends_on": ["s1"]
            },
            {
                "step_id": "s3",
                "title": "Restart networking",
                "agent_type": "action-agent",
                "params": {"service": "networking", "action": "recover"},
                "depends_on": ["s2"]
            }
        ]
    }
    jlog(logger, "commander", "planner_fallback", "WARN", plan=plan["plan_id"])
    return plan


@app.post("/execute/")
def execute(plan: Plan):
    """Execute a given plan step by step"""
    execution_id = f"exec_{int(time.time())}"
    jlog(logger, "commander", "exec_started", "INFO", execution_id=execution_id, plan_id=plan.plan_id)

    results = {}
    for step in plan.steps:
        svc = step.params.get("service")
        agent = step.agent_type
        
        # Validate service exists in config
        if svc not in PORTS:
            error_msg = f"Service '{svc}' not found in PORTS config. Available: {list(PORTS.keys())}"
            logger.error(f"FATAL MISROUTING: {error_msg}")
            results[step.step_id] = {"status": "error", "error": error_msg}
            continue
            
        expected_port = PORTS[svc]
        
        try:
            if agent == "log-agent":
                target_url = build_service_url(svc, "/logs")
                log_request_start(step.step_id, agent, "GET", target_url, svc, expected_port)
                
                start_time = time.time()
                r = requests.get(target_url, timeout=4)
                response_time = time.time() - start_time
                
                log_request_result(step.step_id, r.status_code, response_time)
                results[step.step_id] = {"status": "ok", "raw": r.json()}

            elif agent == "metric-agent":
                target_url = build_service_url(svc, "/metrics")
                log_request_start(step.step_id, agent, "GET", target_url, svc, expected_port)
                
                start_time = time.time()
                r = requests.get(target_url, timeout=4)
                response_time = time.time() - start_time
                
                log_request_result(step.step_id, r.status_code, response_time)
                results[step.step_id] = {"status": "ok", "raw": r.json()}

            elif agent == "action-agent":
                action = step.params.get("action", "recover")
                target_url = build_service_url(svc, f"/{action}")
                log_request_start(step.step_id, agent, "POST", target_url, svc, expected_port)
                
                start_time = time.time()
                r = requests.post(target_url, timeout=6)
                response_time = time.time() - start_time
                
                log_request_result(step.step_id, r.status_code, response_time)
                results[step.step_id] = {"status": "ok", "raw": r.json()}

            else:
                results[step.step_id] = {"status": "skipped", "reason": "unknown agent"}

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Request failed for step {step.step_id}: {error_msg}")
            log_request_result(step.step_id, 0, 0, error_msg)
            results[step.step_id] = {"status": "error", "error": error_msg}

        jlog(logger, "commander", "step_executed", "INFO", step_id=step.step_id, result=results[step.step_id])

    jlog(logger, "commander", "exec_complete", "INFO", execution_id=execution_id)
    return {"execution_id": execution_id, "status": "done", "results": results}
