# Agentic Multi-Node Simulation

## Executive Summary

Build a local "mini-cloud" (Docker Compose / Kind Kubernetes) that runs toy microservices producing _real_ logs and Prometheus-style metrics. Use LM Studio as your local planner LLM that ingests a messy natural-language incident report and outputs a structured, ordered triage plan (JSON DAG). A deterministic scheduler on the laptop validates and executes steps by delegating to domain agents (LogAgent, MetricAgent, ActionAgent). Agents actually run commands (docker exec, container restart, HTTP checks). A monitor observes execution, triggers replanning if results deviate, logs everything (prompts + responses hashed), and displays a dashboard. You'll have a reproducible harness to inject failures and measure recovery (SR, MRL, TGED). The system must be auditable and safe: HMAC-signed task envelopes, key rotation, and explicit fallbacks (rulebook).

## Table of Contents

1. [Why This Matters](#why-this-matters)
2. [Scope: What We Will Build](#1--scope-what-we-will-build-concrete)
3. [Conceptual Model](#2--conceptual-model-the-mental-map)
4. [Data Contracts](#3--data-contracts-telemetry--plan-schemas)
5. [LLM Design & LM Studio Role](#4--llm-design--lm-studio-role)
6. [Agents & Architecture](#5--agents--what-each-does)
7. [Scheduler & Execution](#6--scheduler--execution-semantics)
8. [Failure Injection](#7--failure-injector--simulation)
9. [Observability & Dashboard](#8--observability--dashboard)
10. [Security & Provenance](#9--security--provenance)
11. [Metrics & Evaluation](#10--metrics--evaluation-harness)
12. [CI & Reproducibility](#11--ci--reproducibility)
13. [Error Handling](#12--errors-failure-modes--safety-nets)
14. [Demo Choreography](#13--demo-choreography)
15. [Implementation Blueprint](#14--implementation-blueprint)
16. [Code Snippets](#15--minimal-code-snippets)
17. [Learning Path](#16--learning-path)
18. [CI & Long-term Engineering](#17--ci--long-term-engineering)
19. [Common Pitfalls](#18--common-pitfalls--how-to-avoid-them)
20. [Documentation](#19--hand-off--documentation)
21. [Skills & Artifacts](#20--what-youll-walk-away-with)
22. [Quick Reference](#appendix--quick-reference-cheat-sheets)

## Why This Matters

This project demonstrates three hard-to-fake skills:

- **Agentic orchestration**: designing agents that decompose, ask, plan, act, and adapt
- **Planning under uncertainty**: turning messy human text into actionable DAGs, then re-planning when the world changes
- **Engineering discipline**: telemetry format, reproducible harness, security/provenance, measurable metrics, and a stage-grade demo

It's both researchy (LLM planning) and engineering-heavy (orchestration + reproducibility), which is exactly the combination interviewers like Abhishek will respect.

## 1 — Scope: What We Will Build (Concrete)

### Target Environment
- A local system that runs on a developer laptop (optionally extendable to minikube/kind)

### Components

#### Simulation
- 3–6 Dockerized microservices (API, DB, cache, MQ)
- Prometheus + Grafana + log collectors

#### Failure Injector
- Programmable fault sequences (network partition, CPU load, container stop, config drift)

#### Orchestrator/Controller
- Python FastAPI app + PostgreSQL (simple state store)

#### Planner
- LM Studio instance running a chosen model (local API)
- Planner returns JSON plan (DAG)

#### Agents
- Modular Python agents (LogAgent, MetricAgent, ActionAgent, RAG provider)

#### Auditor/Provenance
- Log prompt + response + plan version + hashes
- HMAC-signed envelopes

#### Dashboard
- Lightweight web UI showing topology, plan, action timeline

#### Harness
- Scenario loader, replay mode, CI tests

### Deliverables

- Repo with code, decisions.md, telemetry schema, harness scenarios
- Demo script + video + README

## 2 — Conceptual Model: The Mental Map

Think in layers:

1. **Physical/Simulated world** — running services produce metrics and logs
2. **Sensors** — collectors (prometheus exporters, filebeat) provide telemetry and logs
3. **Control plane (laptop)** — orchestrator + database + LM Studio instance
4. **Planner (LLM)** — reads text incident + context + telemetry snapshot → outputs plan (DAG) with tasks and device assignments
5. **Scheduler/Executor** — deterministic engine that validates plan and issues tasks to agents (passes through HMAC envelopes)
6. **Agents** — perform reads and actions (read logs, query metrics, run docker restart)
7. **Monitor** — checks task outcomes, triggers replanning loop when necessary
8. **Auditor** — stores full provenance for every decision

### Flow
Natural-language incident → Planner returns plan → Scheduler executes → Agents perform actions → Monitor collects results → If not solved, loop back to Planner for re-plan.

## 3 — Data Contracts: Telemetry & Plan Schemas

### Telemetry JSON Schema

```json
{
  "device_id": "string",
  "timestamp": "ISO8601",
  "status": "string (OK|WARN|ERROR)",
  "metrics": {
    "cpu_load": "float",
    "mem_usage": "float",
    "latency_ms": "float"
  },
  "error_code": "optional string",
  "log_sample": "optional string",
  "note": "optional string"
}
```

### Log Line Structure

Prefer container stdout logs as JSON with fields:

```json
{
  "ts": "ISO8601",
  "level": "ERROR",
  "service": "service-a",
  "msg": "error connecting to db",
  "meta": {...}
}
```

### Plan JSON (Planner → Scheduler)

```json
{
  "plan_id": "uuid",
  "root_goal": "string",
  "created_at": "ISO8601",
  "plan_version": 1,
  "tasks": [
    {
      "task_id": "t1",
      "type": "check_logs",
      "target": "service-a",
      "args": {
        "pattern": "ERROR 500",
        "lookback": "5m"
      },
      "dependencies": ["t0"],
      "assigned_to": "LogAgent",
      "estimated_cost_ms": 200
    }
  ]
}
```

**Note**: Plan must be DAG (no cycles). Scheduler must reject cycles or convert request into deterministic fallback.

## 4 — LLM Design & LM Studio Role

### Why LM Studio
Runs local LLMs so your demo is self-contained, private, and offline-capable. It gives you full control over prompting, temperature, reproducibility, and prompt hashing.

### Model Choice Guidelines

- **If laptop is modest**: Mistral/RedPajama 7B Instruct or similar small 7–13B models. Use lower temperature for CI determinism.
- **For clarity**: keep temperature=0 in CI/regression, temperature=0.2 for demo flexibility.

### Planner Prompt Design

Prompt structure is critical: include schema, constraints, relevant telemetry snapshot, and instructions.

**Example prompt template:**

```
You are an incident triage planner. Input: raw incident text, recent telemetry (structured JSON). Output: JSON plan following the exact schema shown.

Constraints:
- Use atomic tasks
- Avoid cycles
- Assign to agents: LogAgent, MetricAgent, ActionAgent
- Maximum 8 tasks for initial plan
- If missing info, include clarifying_task: { "task_id":"...", "question":"..."}

Return valid JSON only.
```

### Provenance

- Store prompt + model_id + model_config + response + prompt_hash + response_hash + timestamp
- Log as `llm_runs` table in postgres: `run_id | model | prompt_hash | response_hash | temp | tokens | created_at`

## 5 — Agents & What Each Does

Build agents as modular Python classes with a common interface: `ask(agent_action)` returns `ActionResult`.

### Agent Types

- **LogAgent**: queries logs (supports regex/filter/lookback), summarizes matches, returns top-k lines and a short rationale sentence
- **MetricAgent**: queries Prometheus-like API (or parse generated metrics JSON), returns metric trends, alerts if thresholds crossed, computes anomalies
- **ActionAgent**: runs deterministic actions: docker exec, docker restart, kubectl rollout restart, HTTP healthcheck. Ensures idempotence and signs envelopes
- **RAGAgent** (optional): searches playbook or runbook docs in a vector DB for guided actions
- **MonitorAgent**: checks outcomes, marks task success/failure

Each agent logs inputs & outputs to the orchestrator.

### Sample Agent Interface

```python
class BaseAgent:
    def execute(self, task: dict) -> dict:
        # returns {"status":"OK|FAIL","out":"...","meta":{...}}
        raise NotImplementedError
```

## 6 — Scheduler & Execution Semantics

### Scheduler Responsibilities

- **Validate plan** (DAG check)
- **Convert plan** into executable order that respects dependencies
- **Wrap task** in signed envelope:

```json
{
  "envelope": {...},
  "key_version": 1,
  "hmac": "...",
  "seq": 1234
}
```

- **Dispatch to agent** & wait for result (with timeout)
- **If agent fails**, record failure and trigger monitor logic:
  - Retries: up to 2 with exponential backoff
  - If repeated fails or root_goal jeopardized → call Planner for replan (include failure context)
- **Maintain plan_version** and use Lamport-like increment numbering: increment at each successful commit

### Edge Rules

- If two replans arrive, tie-break by plan_version, then by plan_id lexicographic

## 7 — Failure Injector / Simulation

Use real services inside containers; then apply real failure actions.

### Examples

- **Stop container process** → real ECONNREFUSED logs appear in dependent services
- **Add env var misconfig** (wrong DB URL) then send requests → authentication or connection errors
- **Throttle network** using tc inside container network namespace to create latency
- **Create CPU hog** processes that push CPU to 95%
- **Coins**: random dropout of 1% requests to generate intermittent errors

### Important Note
Do not print fake "ERROR: something bad" lines — produce errors that the real software actually emits. Use busybox `yes > /dev/null` or microservice code that raises real exceptions on demand.

### Failure Scenarios (scenarios.json)

- **db_conn_drift**: swap DB host env var to wrong hostname, cause API 500s
- **cache_poison**: inject bad object into Redis to cause serialization errors
- **network_partition**: iptables rules to drop traffic between containers

## 8 — Observability & Dashboard

### Data Collection

- Collect logs via `docker logs` + structured JSON; or forward via Fluentd to Loki
- Expose metrics via Prometheus exporters (simple Python process exposing `/metrics`)

### Dashboard Features

- **Topology** (services, agents)
- **Live plan DAG** with colored task statuses
- **LLM prompt + planner response** panel (collapsible)
- **Timeline of actions** with timestamps and HMAC+hash view

### Technology
Simple React + FastAPI backend or Flask + socket.io to stream updates.

## 9 — Security & Provenance (Must-Haves)

- **HMAC-SHA256 envelopes** on tasks using key_version. Store keys encrypted in local file (demo) and provide rotate_key script
- **Include timestamp, nonce, seq** in envelope; TTL default 120s; skew tolerance 5s for demo
- **Persist LLM prompts & responses** to DB with SHA256 hashes for auditing
- **Use decision_tag** per action (LLM_DECISION vs DETERMINISTIC) so you can grep logs for AI decisions

## 10 — Metrics & Evaluation Harness

### Primary Metrics

- **Success Rate (SR)**: fraction of scenarios where final verification == OK
- **Mean Replan Latency (MRL)**: weighted by TGED (see below)
- **Task Graph Edit Distance (TGED)**: normalized edit count, weighted by impact depth

### Concrete Definitions

**SR**:
```
SR = (#scenarios where root_verified == true AND 
      (#tasks_completed/total_tasks >= 0.8) AND 
      (leaf_fail_pct <= 0.2)) / total_scenarios
```

**MRL (weighted)**:
```
MRL = sum_i ((t_replan_complete_i - t_trigger_i) * TGED_i) / sum_i (TGED_i)
```

Define `t_trigger`: monotonic timestamp when monitor first detects a deviation (heartbeat expiry or sensor alert).

**TGED**: normalized sum of edits with cap `edit_weight(node) = min(2^depth, 16)`. Normalize by `(orig_nodes + orig_edges)`.

### Test Harness

- **JSON scenario files**: list of failure injections + timings + noise settings + seed
- **Replay mode**: deterministic RNG seed; snapshot initial telemetry buffer and replay events
- **CI**: run 3 required scenarios nightly; report metrics. Gate if SR < threshold

## 11 — CI / Reproducibility

- Use `docker-compose` to stand up full stack deterministically
- **Seed all synthetic generators** with RNG seed; record seed in scenario_run table
- **"Record-run" mode**: run scenario, persist all telemetry, prompts, responses. Replay mode replays data feeds with exact timestamps
- **CI pipeline**: run harness headless, run `./harness --scenario chaos1.json --seed 42 --noise 0.2`, assert metric gates

## 12 — Errors, Failure Modes, & Safety Nets

- **LLM hallucination**: reject LLM plan if it contains cycles, unsupported action types, or invalid targets (not present in device inventory). If rejected 2x → fallback to rulebook
- **Agent hangs**: heartbeat frequency 2s, timeout 5s. On timeout, scheduler reassigns or replans
- **Flapping**: if same plan diff repeats within 5s from same origin → reject (anti-flap)

## 13 — Demo Choreography

### Sequence (6 minutes, double-peak emotional arc):

- **0:00–0:30** — Hook: "Give messy natural language — it triages & recovers autonomously."
- **0:30–1:30** — Context: show topology + baseline green.
- **1:30–2:30** — First peak: live kill / watchdog F12 triggers; amber fallback cue shows; system reassigns tasks.
- **2:30–3:00** — Latency meter mic-drop (overlay timestamps <250ms).
- **3:00–4:00** — Audience injection: volunteer types messy incident; system responds.
- **4:00–4:40** — Second peak: show run startup banner with today's stats (e.g., 73% recovery over 30 injected faults).
- **4:40–6:00** — Psychological kill-shot silence + prepared rebuttals for crypto, data, scale.

Pre-rehearse, incorporate pre-captured telemetry fallback, implement surgical kill-switch for node termination.

## 14 — Implementation Blueprint

### Repo Skeleton

```
/agentic-triage
  /simulator
    docker-compose.yml
    services/
  /orchestrator
    app.py (FastAPI)
    scheduler.py
    agents/
      log_agent.py
      metric_agent.py
      action_agent.py
  /planner
    lm_studio_prompt_templates/
    planner_client.py  # calls LM Studio
  /harness
    scenarios/
    harness.py
  /ui
    dashboard/
  /docs
    decisions.md
    telemetry.json
    runbook.md
  Dockerfile (for orchestrator)
  README.md
```

### Key Commands

- **Start stack**: `docker-compose up --build`
- **Start orchestrator**: `python orchestrator/app.py`
- **Start LM Studio**: `lmstudio serve --model mistral-7b-instruct` (example)
- **Run scenario**: `python harness/harness.py --scenario scenarios/chaos1.json --seed 42`

## 15 — Minimal Code Snippets

### scheduler.validate_plan (pseudo)

```python
def validate_plan(plan, inventory):
    # DAG check
    if has_cycles(plan['tasks']):
        raise ValueError("Plan contains cycles")
    # target validation
    for t in plan['tasks']:
        if t['target'] not in inventory:
            raise ValueError("Invalid target: %s" % t['target'])
    return True
```

### Call LM Studio (simple)

```python
import requests, json

LM_URL = "http://localhost:8080/v1/generate"

def call_planner(prompt):
    resp = requests.post(LM_URL, json={
        "prompt": prompt, 
        "max_tokens": 1024, 
        "temperature": 0
    })
    return resp.json()['text']
```

### Envelope Signing

```python
import hmac, hashlib, json, time

def sign_envelope(payload, key):
    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    return hmac.new(key, payload_bytes, hashlib.sha256).hexdigest()
```

## 16 — Learning Path

### Days 0–2: Foundation
- Install Docker, Docker Compose, Python 3.10+, VSCode
- Learn Linux basics: ls, cd, tail, grep, ps, kill
- Learn SSH conceptually (we won't need it for local demo)

### Days 3–5: Local Services & Logs
- Build 2 simple containers: a Flask service that logs errors on trigger, a small Redis container
- Learn `docker-compose up`; read logs via `docker-compose logs -f`
- Create a simple Python script to tail container logs and print JSON samples

### Days 6–8: LM Studio & Planner Prompt
- Install LM Studio (follow docs); load a 7B instruct model
- Write a simple prompt template that converts incident text + telemetry snapshot to JSON plan
- Call the model from Python and parse output

### Days 9–11: Scheduler + Agents
- Implement `scheduler.validate_plan` and deterministic executor
- Implement LogAgent (reads logs) and ActionAgent (can run docker restart)
- Connect planner → scheduler → agent flow manually

### Days 12–14: Harness + Demo
- Create 2 failure scenarios and harness runner
- Build small UI or CLI output to show the plan & timeline
- Rehearse demo script, implement F12 kill switch for live failure theater

## 17 — CI & Long-term Engineering

- Add pytest tests for harness scenarios (headless)
- Add GitHub Actions to bring up stack via docker-compose and run harness
- Nightly CI runs scenarios; outputs SR/MRL/TGED as artifacts
- Add a `docs/decisions.md` describing the deterministic boundaries (LLM decisions vs deterministic ones)

## 18 — Common Pitfalls & How to Avoid Them

- **Pitfall**: LLM gives inconsistent JSON  
  **Fix**: wrap output in strict validation schema, use temperature=0 in CI, and use a small repair parser to fix minor schema failures

- **Pitfall**: Demo brittle because of network variance  
  **Fix**: pre-captured telemetry fallback + local-only demo

- **Pitfall**: Too many moving parts → nothing works  
  **Fix**: make minimum viable loop first: 1 service, 1 agent, 1 simple plan

- **Pitfall**: Presenters ramble  
  **Fix**: follow 6-minute demo sequence; rehearse kill and fallback

## 19 — Hand-off & Documentation

### Required Files

- **README.md** with "Run this in 10 minutes" quick start
- **decisions.md** listing decision boundaries: what LLM decides, what deterministic code decides, logging tags
- **telemetry.json** schema file
- **scenarios/** with at least 3 JSON scenarios and seeds
- **harness/** script with replay & record mode
- **demo_script.md** (minute-by-minute) with exact commands and lines to say
- **security.md** with HMAC, key rotation example

## 20 — What You'll Walk Away With

- A working repo demonstrating LLM-driven planning and multi-agent execution
- A reproducible harness and CI that proves you're not doing theatre
- Deep practical knowledge: Docker, logs & metrics, LM Studio integration, prompt engineering for structured output, task scheduling, deterministic fallback rules, and demo choreography
- A demo script and short video for recruiters

## Appendix — Quick Reference Cheat-Sheets

### Prompt Template (Copy Me)

```
SYSTEM: You are a triage planner that MUST output valid JSON. Schema: {plan_id, root_goal, created_at, tasks[]}. Tasks must contain task_id,type,target,args,dependencies,assigned_to.

USER: INCIDENT_TEXT: {{raw_text}}

TELEMETRY_SNAPSHOT: {{json telemetry}}

RULES:
1. If not enough info, include clarifying_task with question field.
2. Max 8 tasks.
3. Use agents: LogAgent, MetricAgent, ActionAgent.
4. No cycles allowed.

Return JSON only.
```

### Minimal docker-compose (idea)

- **service-a**: flask:py
- **postgres**
- **redis**
- **prometheus** (scrapes /metrics on service-a)

### Quick Checklist Before Demo

- [ ] All containers healthy
- [ ] LM Studio running & model loaded
- [ ] Orchestrator running
- [ ] Harness ready with scenario seed
- [ ] Presentation laptop plugged in, latency meter green
- [ ] Kill switch (F12) works