# Chaos Triage Arena

A comprehensive microservices chaos engineering and incident response platform built in Python. This system simulates real-world service failures and provides automated incident detection and recovery capabilities.

## 🎭 Overview

Chaos Triage Arena consists of:

- **5 Python Microservices** with realistic interdependencies
- **SuperTool Orchestrator** for service lifecycle and failure injection
- **Dashboard API** with real-time monitoring and control interface
- **Villain Agent** for automated chaos injection following a curriculum
- **Felix Commander** for intelligent incident detection and response
- **Recovery Agents** (Log, Metric, Probe, Action) for automated remediation
- **Web Dashboard** for visualization and manual control

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Virtual environment (recommended)

### Installation

1. **Clone and setup environment:**
   ```bash
   git clone <repository-url>
   cd chaos-triage-arena
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start the system:**
   ```bash
   # Terminal 1: Start services and monitoring
   python main.py
   
   # Terminal 2: Start dashboard API
   python dashboard_api.py
   
   # Terminal 3: Open dashboard
   open http://127.0.0.1:8000
   ```

### First Run Verification

1. **Check services started:** Look for PID output in Terminal 1
2. **Verify dashboard:** Should show all 5 services as healthy
3. **Test manual actions:** Click "Start/Stop" buttons in dashboard
4. **Watch chaos unfold:** Villain will begin attacks after 15 seconds
5. **Observe recovery:** Felix will detect incidents and spawn recovery agents

## 🏗️ Architecture

### Services (Ports 8001-8005)

- **API Gateway (8001):** Entry point, calls User and Payment services
- **Database Service (8002):** Data layer, no dependencies
- **User Service (8003):** Business logic, depends on Database
- **Payment Service (8004):** Business logic, depends on Database  
- **Echo Service (8005):** Simple service for testing

### Core Components

- **SuperTool (`super_tool.py`):** Process management, health checks, failure injection
- **Dashboard API (`dashboard_api.py`):** FastAPI backend serving web interface
- **Main Monitor (`main.py`):** Orchestrates services and agents
- **Villain (`agents/villain_agent.py`):** Chaos injection with escalating curriculum
- **Felix (`agents/felix_agent.py`):** Incident detection and response coordination

### Recovery Agents

- **LogAgent:** Analyzes service logs for error patterns
- **MetricAgent:** Monitors performance and resource usage
- **ProbeAgent:** Tests connectivity and dependencies
- **ActionAgent:** Executes recovery actions (restart, recover, optimize)

## 🎯 Features

### Chaos Engineering

- **Failure Types:** Kill, logical failures, latency injection, CPU stress, memory leaks
- **Attack Curriculum:** Escalating complexity from simple kills to cascading failures
- **Realistic Dependencies:** Services call each other creating failure propagation

### Incident Response

- **Automated Detection:** Felix monitors health and metrics continuously
- **Smart Planning:** Generates recovery plans using stub planner or LLM integration
- **Agent Orchestration:** Spawns specialized agents for diagnosis and recovery
- **Action Tracking:** Complete audit trail of all actions and their outcomes

### Monitoring & Visualization

- **Real-time Dashboard:** Live service status, metrics, and action controls
- **Time-series Charts:** Action duration tracking per service or overview mode
- **Performance Metrics:** CPU, memory, latency monitoring
- **Action History:** Complete log of all system actions with timing

### Persistence & Configuration

- **Optional JSONL Persistence:** Enable with `ACTION_HISTORY_PERSIST=jsonl`
- **Configurable Intervals:** Adjust Villain and Felix timing via environment
- **LLM Integration:** Connect to LM Studio on port 1234 with `USE_LLM=true`

## ⚙️ Configuration

### Environment Variables

Create `.env` file from `.env.template`:

```bash
# Persistence
ACTION_HISTORY_PERSIST=false  # Set to 'jsonl' to enable

# Agent intervals (seconds)
VILLAIN_INTERVAL=15
FELIX_INTERVAL=5

# LLM integration
USE_LLM=false  # Set to 'true' for LM Studio integration

# Dashboard
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=8000
```

### Service Configuration

Edit `arena.json` to modify services, ports, or dependencies:

```json
{
  "services": {
    "service_name": {
      "port": 8001,
      "script": "services/service_script.py",
      "dependencies": ["other_service"]
    }
  }
}
```

## 🧪 Testing

Run the test suite:

```bash
# All tests
pytest

# Specific test files
pytest tests/test_api.py -v
pytest tests/test_super_tool.py -v

# With coverage
pip install pytest-cov
pytest --cov=. tests/
```

### Manual Testing

```bash
# Test SuperTool directly
python super_tool.py start api_gateway
python super_tool.py status
python super_tool.py stop api_gateway

# Test individual agents
python agents/villain_agent.py
python agents/felix_agent.py

# Test dashboard API
curl http://127.0.0.1:8000/api/health
curl -X POST http://127.0.0.1:8000/api/actions/start/echo_service
```

## 🔧 Advanced Usage

### Running Components Separately

```bash
# Start only services (no agents)
python -c "from super_tool import SuperTool; st = SuperTool(); [st.start_service(s) for s in st.arena_config['services']]"

# Run Villain standalone
python agents/villain_agent.py

# Run Felix standalone  
python agents/felix_agent.py

# Start dashboard only
python dashboard_api.py --host 0.0.0.0 --port 8080
```

### LM Studio Integration

1. **Install LM Studio** and load a model
2. **Start LM Studio server** on port 1234
3. **Enable LLM mode:** `export USE_LLM=true`
4. **Restart Felix:** Felix will use LLM for plan generation

### Persistence Deep Dive

When `ACTION_HISTORY_PERSIST=jsonl`:

- Actions logged to `data/action_history.jsonl`
- Files rotated at 5MB, keeping 5 historical files
- On startup, last 30 minutes reconstructed from JSONL
- Background flusher writes new events every second

### Custom Failure Scenarios

Add custom failure types by extending service endpoints:

```python
@app.post("/fail")
async def fail(request: FailureRequest):
    if request.type == "custom_failure":
        # Your custom failure logic
        pass
```

## 📊 Monitoring

### Dashboard Features

- **Service Cards:** Real-time status, metrics, and action buttons
- **Action Charts:** Duration tracking with time-series visualization
- **Overview Mode:** Combined view across all services
- **Toast Notifications:** Success/error feedback for actions
- **Optimistic UI:** Immediate feedback with background verification

### Metrics Available

- **System:** CPU, memory, disk usage
- **Service:** Individual CPU/memory, health status, artificial conditions
- **Actions:** Duration, success rate, frequency per service
- **Dependencies:** Health of service dependencies

## 🛠️ Development

### Adding New Services

1. **Create service script** in `services/`
2. **Extend BaseService** class
3. **Add to `arena.json`** with port and dependencies
4. **Update dashboard** if custom UI needed

### Adding New Agents

1. **Create agent script** in `agents/`
2. **Implement HTTP server** with `/run` endpoint
3. **Add to Felix** agent spawning logic
4. **Update planner** to use new agent type

### Extending Failure Types

1. **Add endpoint** to BaseService or specific services
2. **Update SuperTool** injection methods
3. **Add to Villain** curriculum if desired
4. **Update dashboard** UI for new actions

## 🐛 Troubleshooting

### Common Issues

**Services won't start:**
- Check Python path and virtual environment
- Verify ports aren't already in use: `netstat -tulpn | grep 800[1-5]`
- Check service logs in `service_logs/` directory

**Dashboard not loading:**
- Ensure dashboard_api.py is running on port 8000
- Check firewall settings
- Verify `dashboard/index.html` exists

**Agents not working:**
- Check agent scripts have execute permissions
- Verify Felix can spawn processes
- Look for port conflicts in 9000+ range

**Persistence issues:**
- Ensure `data/` directory is writable
- Check disk space for JSONL files
- Verify JSON format in action history

### Debug Mode

Enable verbose logging:

```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run with debug output
python main.py 2>&1 | tee debug.log
```

### Performance Tuning

- **Reduce intervals** for faster testing: `VILLAIN_INTERVAL=5 FELIX_INTERVAL=2`
- **Disable persistence** for better performance: `ACTION_HISTORY_PERSIST=false`
- **Limit history** by modifying deque maxlen in SuperTool

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Development Setup

```bash
# Install development dependencies
pip install pytest pytest-cov flake8 black

# Run code formatting
black .

# Run linting
flake8 .

# Run tests with coverage
pytest --cov=. tests/
```

## 🎓 Learning Resources

- **Chaos Engineering:** [Principles of Chaos](https://principlesofchaos.org/)
- **Incident Response:** [Google SRE Book](https://sre.google/sre-book/)
- **FastAPI:** [Official Documentation](https://fastapi.tiangolo.com/)
- **Microservices:** [Building Microservices](https://www.oreilly.com/library/view/building-microservices/9781491950340/)

---

**Built with ❤️ for chaos engineering education and incident response training.**

