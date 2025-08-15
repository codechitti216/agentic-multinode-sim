# 🚨 Agentic Incident Simulation & Planning Framework

A cloud operations triage simulator where an agentic system reasons, plans, and acts to mitigate cascading service failures across a network of dependent services.

## 🌟 Features

- **Microservice Simulation**: 5 HTTP microservices with realistic dependencies
- **Failure Injection**: OATS-generated combinatorial failure scenarios
- **AI-Powered Planning**: LLM integration for incident response planning
- **Visual Network Graph**: Real-time network topology visualization
- **Agentic Orchestration**: Automated incident detection and response
- **Custom Logic Hooks**: Extensible framework for RL/policy logic

## 🏗️ Architecture

```
agentic-incident-sim/
│
├── services/                # Microservice definitions
│   ├── service_template.py  # Base service class
│   ├── service_a.py         # Service A (depends on B)
│   ├── service_b.py         # Service B (depends on C)
│   ├── service_c.py         # Service C (depends on D)
│   ├── service_d.py         # Service D (depends on A)
│   └── service_e.py         # Service E (depends on B, C)
│
├── orchestrator/            # Incident management
│   ├── commander.py         # Main control loop
│   ├── planner.py           # LLM-based planning
│   ├── executor.py          # Plan execution
│   └── agent_hooks.py       # 🔥 YOUR CUSTOM LOGIC HERE
│
├── visualizer/              # Dashboard & visualization
│   ├── dashboard.py         # Streamlit dashboard
│   └── graph_state.py       # Network topology management
│
├── failures/                # Failure injection system
│   ├── failure_scenarios.py # OATS-generated scenarios
│   └── injector.py          # Failure injection engine
│
├── data/logs/               # Incident and failure logs
├── main.py                  # System entry point
├── config.py                # Configuration
└── requirements.txt         # Dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- LM Studio running on localhost:1234 (for LLM integration)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agentic-incident-sim
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start LM Studio** (if using LLM features)
   - Download and install [LM Studio](https://lmstudio.ai/)
   - Start a local server on port 1234
   - Load your preferred model

4. **Run the system**
   ```bash
   python main.py
   ```

### What Happens Next

1. **Services Start**: 5 microservices start on ports 8001-8005
2. **Failure Injector**: Begins injecting random failures
3. **Incident Commander**: Monitors services and detects incidents
4. **Dashboard**: Opens at http://localhost:8501
5. **AI Planning**: LLM generates incident response plans
6. **Auto-Recovery**: System attempts to resolve incidents

## 🎯 Customization Points

### Agent Hooks (`orchestrator/agent_hooks.py`)

This is where **YOU** implement custom logic:

```python
def custom_diagnose(service_status):
    # 🔥 YOUR DIAGNOSTIC LOGIC HERE
    # Pattern recognition, dependency analysis, etc.
    pass

def custom_plan(incident_summary, service_status, llm_plan):
    # 🔥 YOUR PLANNING LOGIC HERE
    # RL-based action selection, policy modification, etc.
    pass

def custom_execute(step, service_status):
    # 🔥 YOUR EXECUTION LOGIC HERE
    # Adaptive strategies, learning, etc.
    pass

def custom_learn(execution_history, incident_outcomes):
    # 🔥 YOUR LEARNING LOGIC HERE
    # Model updates, policy refinement, etc.
    pass
```

### Failure Scenarios

Add custom failure scenarios in `failures/failure_scenarios.py`:

```python
def create_custom_scenario(self, name, target_services, failure_type, duration):
    # Create your own failure patterns
    pass
```

## 🎮 Usage

### Dashboard Controls

- **Network Graph**: Real-time service dependency visualization
- **Manual Failures**: Inject specific failures for testing
- **System Status**: Monitor overall health
- **Incident History**: View past incidents and responses

### API Endpoints

Each service exposes:
- `GET /health` - Service health status
- `GET /metrics` - CPU, memory, error rates
- `POST /inject_failure` - Inject failures
- `POST /recover` - Recover from failures

### Failure Types

- **degraded**: Service performance reduced
- **down**: Service completely unavailable
- **cascade**: Dependency chain failures
- **load**: High resource utilization
- **config**: Configuration drift

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Service ports and dependencies
SERVICES = {
    "service_a": {"port": 8001, "dependencies": ["service_b"]},
    # ... more services
}

# LLM settings
LLM_BASE_URL = "http://localhost:1234"
LLM_MODEL = "local-llm"

# Failure injection
FAILURE_INJECTION_INTERVAL = 10  # seconds
FAILURE_PROBABILITY = 0.3
```

## 📊 Monitoring

### Service Health

- 🟢 **Healthy**: Normal operation
- 🟡 **Degraded**: Performance issues
- 🔴 **Down**: Service unavailable

### Incident Severity

- **High**: Service down, affecting users
- **Medium**: Service degraded, reduced performance
- **Low**: Minor issues, monitoring

## 🧪 Testing

### Manual Failure Injection

```python
# Via dashboard sidebar
# Select service → Choose failure type → Set duration → Inject

# Via API
POST /inject_custom_failure
{
    "service_names": ["service_a"],
    "failure_type": "down",
    "duration": 120
}
```

### Scenario Testing

```python
# Test specific failure scenarios
scenario = failure_scenarios.get_scenario_by_id("cascade_failure_a_b")
failure_injector.inject_scenario(scenario)
```

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports 8001-8005 are available
2. **LLM connection**: Ensure LM Studio is running on port 1234
3. **Service startup**: Check logs for service initialization errors
4. **Dashboard access**: Verify Streamlit is accessible on port 8501

### Debug Mode

```bash
# Run with verbose logging
python main.py --debug

# Check individual components
python services/service_a.py  # Test single service
python visualizer/dashboard.py  # Test dashboard
```

## 🔮 Future Enhancements

- **Multi-node simulation**: Distributed service deployment
- **Advanced RL**: Deep reinforcement learning integration
- **Metrics collection**: Prometheus/Grafana integration
- **Alerting**: Slack/Teams notifications
- **Chaos engineering**: Advanced failure patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your custom logic in `agent_hooks.py`
4. Test with various failure scenarios
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OATS methodology** for failure scenario generation
- **NetworkX** for dependency graph analysis
- **Streamlit** for the interactive dashboard
- **Pyvis** for network visualization

---

**Ready to build intelligent incident response systems? Start with the agent hooks and let your creativity flow! 🚀**
