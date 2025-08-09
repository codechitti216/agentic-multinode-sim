# Agentic Multi-Node Operations Simulation (Local)

A **learning-by-building** project to simulate how distributed, self-healing infrastructure works — all **on a single laptop**.  
Think of it as a mini version of what cloud SRE teams use, but simple enough to run locally and understand fully.

---

## 🎯 Project Goal
To build a **Detect → Plan → Act → Verify** loop:
1. Node agents send telemetry (CPU, network, storage)
2. Control plane detects problems
3. Control plane sends remediation commands
4. Actions are taken, and results are verified
5. Incidents are recorded in a local database

---

## 📦 Current Features (v1)
- **Python node agents** that send fake CPU metrics
- **Control plane** (FastAPI) to receive metrics and detect failures
- **Local PostgreSQL** database via Docker
- **Failure injection**: CPU spike, fake network delay, storage latency
- **Runbook** to launch everything in under 10 minutes

---

## 🗺 Roadmap
- **Aug 9–10, 2025** — Setup PostgreSQL + connect from Python
- **Aug 11–13, 2025** — Node agents sending telemetry
- **Aug 14–16, 2025** — Control plane detects and logs events
- **Aug 17–18, 2025** — Add failure simulation
- **Aug 19–20, 2025** — Full Detect → Plan → Act → Verify loop
- **Aug 23–24, 2025** *(Stretch)* — Basic LLM meta-agent for reasoning

---

## 🚀 Quick Start

### 1️⃣ Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/agentic-multinode-sim.git
cd agentic-multinode-sim
