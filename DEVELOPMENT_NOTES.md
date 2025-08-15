# 🚨 Agentic Incident Simulation & Planning Framework - Developer Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- All dependencies installed: `pip install -r requirements.txt`

### Start the System
```bash
# Terminal 1: Start the main system
python main.py

# Terminal 2: Run the demo scenario
python demo_scenario.py
```

### Access Points
- **Dashboard**: http://localhost:8501
- **Incident Commander API**: http://localhost:8000
- **Failure Injector API**: http://localhost:8006
- **Microservices**: localhost:8001-8005

---

## 🏗️ Architecture Overview

### Core Components
```
main.py                    # Entry point - starts all components
├── services/             # Simulated microservices
├── orchestrator/         # AI agent brain (commander, planner, executor)
├── failures/             # Failure injection and scenarios
├── visualizer/           # Real-time dashboard
└── data/logs/            # Incident and failure logs
```

### Data Flow
1. **Services** expose health/metrics endpoints
2. **Commander** monitors health and detects incidents
3. **Planner** calls LLM to generate response plans
4. **Executor** runs recovery steps
5. **Dashboard** visualizes everything in real-time

---

## 🔧 Development Workflow

### 1. Start Development Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Start the system
python main.py

# In another terminal, run demo
python demo_scenario.py
```

### 2. Add Your RL/Agentic Logic
**Primary file to modify**: `orchestrator/agent_hooks.py`

This file contains 5 key functions where you implement your logic:

```python
def custom_diagnose(service_status) -> Dict:
    # TODO: Add your diagnostic ML/RL models
    # Called when incidents are detected
    
def custom_plan(incident_summary, service_status, llm_plan) -> Dict:
    # TODO: Add your planning algorithms
    # Called to enhance LLM-generated plans
    
def custom_execute(step, service_status) -> Dict:
    # TODO: Add your execution strategies
    # Called for each plan step
    
def custom_learn(execution_history, incidents) -> Dict:
    # TODO: Add your learning algorithms
    # Called after incident resolution
    
def custom_evaluate(incident, before_status, after_status) -> Dict:
    # TODO: Add your evaluation metrics
    # Called to assess response effectiveness
```

### 3. Test Your Changes
```bash
# The system auto-reloads your changes
# Monitor the dashboard for real-time updates
# Check console output for your custom logic execution
```

---

## 🤖 LLM Integration

### Enable Real AI Planning
Currently, the system uses fallback plans when LLM Studio isn't running.

**To enable real AI planning:**

1. **Install LM Studio** from https://lmstudio.ai/
2. **Start LM Studio** and load a model
3. **Set API endpoint** to `http://localhost:1234`
4. **Restart the system**: `python main.py`

**Expected behavior:**
- Planner will call real LLM instead of fallback
- Response plans will be AI-generated
- Dashboard will show real LLM output

### LLM Configuration
- **Endpoint**: `http://localhost:1234/v1/chat/completions`
- **Model**: Any model loaded in LM Studio
- **Timeout**: 30 seconds (configurable in `config.py`)

---

## 🧪 Testing & Debugging

### Manual Testing
```bash
# Test incident commander API
curl http://localhost:8000/status

# Test failure injector API
curl http://localhost:8006/health

# Trigger test incident
curl -X POST http://localhost:8000/trigger_incident
```

### Dashboard Testing
1. **Open dashboard**: http://localhost:8501
2. **Use sidebar controls** to inject failures
3. **Monitor network graph** for cascading effects
4. **Check incident history** for your custom logic

### Debugging Tips
- **Check console output** for detailed logs
- **Monitor API endpoints** for component health
- **Use dashboard metrics** to verify service status
- **Check logs** in `data/logs/` directory

---

## 📁 Key Files for Development

### 🔴 Files You SHOULD Modify
```
orchestrator/agent_hooks.py    # YOUR RL/AGENTIC LOGIC HERE
config.py                      # Configuration parameters
```

### 🟡 Files You MIGHT Modify
```
failures/failure_scenarios.py  # Custom failure patterns
visualizer/dashboard.py        # Dashboard enhancements
```

### 🟢 Files to IGNORE (Infrastructure)
```
main.py                       # System startup (don't touch)
services/*.py                 # Microservice definitions (don't touch)
orchestrator/commander.py     # Core orchestration (don't touch)
orchestrator/planner.py       # LLM integration (don't touch)
orchestrator/executor.py      # Plan execution (don't touch)
failures/injector.py          # Failure injection (don't touch)
visualizer/graph_state.py     # Network visualization (don't touch)
```

---

## 🎯 RL/Agentic Development Path

### Phase 1: Basic Integration
1. **Implement `custom_diagnose()`** with simple rule-based logic
2. **Test** with dashboard and console output
3. **Verify** function is called during incidents

### Phase 2: ML/RL Models
1. **Add your ML models** to the custom functions
2. **Implement learning** in `custom_learn()`
3. **Add evaluation metrics** in `custom_evaluate()`

### Phase 3: Advanced Features
1. **Multi-agent coordination** across functions
2. **Online learning** from real-time data
3. **A/B testing** for strategy validation

---

## 📊 Monitoring & Metrics

### Dashboard Sections
- **Network Topology**: Real-time service dependency graph
- **Service Metrics**: CPU, memory, error rates
- **LLM Output**: AI-generated plans and responses
- **Incident History**: Past incidents and resolutions
- **Analytics**: Performance patterns and trends

### Key Metrics to Track
- **Response Time**: Time from incident to resolution
- **Success Rate**: Percentage of successful resolutions
- **Resource Efficiency**: Steps executed vs. successful
- **Learning Progress**: Model improvement over time

---

## 🚨 Common Issues & Solutions

### Issue: "Cannot connect to incident commander"
**Solution**: Check if `main.py` is running and port 8000 is available

### Issue: "Failed to inject failure: 404"
**Solution**: Verify failure injector is running on port 8006

### Issue: LLM timeouts
**Solution**: 
1. Start LM Studio on port 1234, OR
2. Increase timeout in `config.py`, OR
3. System will use fallback plans automatically

### Issue: Dashboard not updating
**Solution**: 
1. Check if all services are running
2. Verify network connectivity
3. Check browser console for errors

---

## 🔮 Future Enhancements

### Potential Additions
- **Real-time streaming** of incident data
- **Advanced visualization** with 3D network graphs
- **Multi-environment support** (dev, staging, prod)
- **Integration** with real monitoring systems
- **Custom dashboards** for different user roles

### Performance Optimizations
- **Async processing** for high-volume incidents
- **Caching** of frequently accessed data
- **Database backend** for persistent storage
- **Distributed processing** for large-scale deployments

---

## 📚 Resources & References

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://docs.streamlit.io/
- **Pyvis**: https://pyvis.readthedocs.io/
- **NetworkX**: https://networkx.org/

### RL/ML Libraries to Consider
- **Stable Baselines3**: https://stable-baselines3.readthedocs.io/
- **Ray RLlib**: https://docs.ray.io/en/latest/rllib/
- **Gymnasium**: https://gymnasium.farama.org/
- **PyTorch**: https://pytorch.org/

---

## 🆘 Getting Help

### Debugging Steps
1. **Check system health** with `python demo_scenario.py`
2. **Review console output** for error messages
3. **Verify API endpoints** are responding
4. **Check dashboard** for visual feedback

### Support
- **Console logs** show detailed execution flow
- **API endpoints** provide component status
- **Dashboard** gives real-time system view
- **Demo script** validates end-to-end functionality

---

**Happy coding! 🚀**

Remember: This framework is designed to be your playground for RL/agentic research. The infrastructure handles all the complexity - you focus on the intelligence!
