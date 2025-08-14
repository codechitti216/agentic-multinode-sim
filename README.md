# Distributed Systems + RL Recovery Simulation

## Overview
This project is a **12-microservice distributed system simulation** with **AI-driven fault detection and recovery**. It’s designed to model real-world service dependencies, failure modes, and observability, while enabling automated recovery via a Planner/Agent control plane enhanced by Reinforcement Learning.

## Architecture
**Core Services:**
1. **Config Service** – Central runtime configuration store.
2. **Auth Service** – Issues/validates short-TTL JWTs.
3. **Gateway/API** – Front-door orchestrator for requests.
4. **Message Queue (MQ)** – Asynchronous backbone.
5. **Job Worker** – Executes jobs from MQ.
6. **DB (Postgres)** – Durable data store.
7. **Cache (Redis)** – Hot-path cache for sessions & results.
8. **External Service Stub** – Simulated 3rd-party dependency.
9. **Log Ingest (LogProc)** – Structured log collection/normalization.
10. **Metrics (Prometheus)** – Metric scraping & alerting.
11. **Dashboard (UI)** – Live topology & incident view.
12. **Incident Generator (IncidentGen)** – Injects realistic cascading failures.

**Control Plane Components:**
- **Planner (LLM)** – Converts NL incidents into JSON DAG recovery plans.
- **Orchestrator/Scheduler** – Validates & dispatches plans.
- **Agents** – Specialized executors (Logs, Metrics, Actions).

## Features
- **Realistic Dependency Spine** – Failures propagate through defined upstream/downstream chains.
- **Service-Specific Failure Modes** – e.g., config poisoning, JWT expiry storms, backlog growth.
- **Orthogonal Array Testing Strategy (OATS)** – Systematic failure scenario coverage.
- **Observability Stack** – Prometheus metrics, structured logging, Grafana dashboards.
- **Chaos Engineering** – Controlled, reproducible fault injection with blast-radius controls.
- **RL Integration** – Adaptive recovery strategies based on past incident outcomes.

## Tech Stack
- **Languages:** Python (Flask/FastAPI), SQL
- **Datastores:** Postgres, Redis
- **Messaging:** RabbitMQ/NATS/Kafka
- **Monitoring:** Prometheus, Grafana
- **Logging:** Loki/Elasticsearch
- **Orchestration:** Docker Compose
- **AI/Planning:** LM Studio (LLM), optional RL agent

## Getting Started
1. Clone repository.
2. Install Docker & Docker Compose.
3. Run:
   ```bash
   docker-compose up --build

````

4. Access dashboard at [http://localhost:3000](http://localhost:3000/) and API at [http://localhost:8000](http://localhost:8000/).

## Development Roadmap

1. **Phase 1:** Core microservices, message bus, DB, cache, metrics/logging.
2. **Phase 2:** IncidentGen + OATS-based scenario generation.
3. **Phase 3:** Planner/Agents integration.
4. **Phase 4:** RL policy learning & adaptive recovery.

## License

MIT
