from typing import Dict, Any, List
import time
import threading
from .planner import IncidentPlanner
from .executor import PlanExecutor
from .agent_hooks import custom_diagnose, custom_learn, custom_evaluate
import requests
from config import SERVICES, HEALTH_CHECK_INTERVAL
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

# FastAPI app for HTTP endpoints
app = FastAPI(title="Incident Commander API", version="1.0.0")

# Global commander instance for API routes
commander_instance = None

class IncidentCommander:
    def __init__(self):
        global commander_instance
        commander_instance = self
        
        self.planner = IncidentPlanner()
        self.executor = PlanExecutor()
        self.running = False
        self.incident_history = []
        self.current_incident = None
        self.service_status_cache = {}
        
        # Setup FastAPI routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup FastAPI routes for the commander API"""
        
        @app.get("/status")
        async def get_status():
            """Get current commander status"""
            if commander_instance:
                return {
                    "running": commander_instance.running,
                    "incidents_handled": len(commander_instance.incident_history),
                    "current_incident": commander_instance.current_incident,
                    "service_status": commander_instance.service_status_cache,
                    "timestamp": time.time()
                }
            return {"error": "Commander not initialized"}
        
        @app.get("/incident_history")
        async def get_incident_history():
            """Get incident history"""
            if commander_instance:
                return commander_instance.incident_history
            return []
        
        @app.get("/incident/{incident_id}")
        async def get_incident(incident_id: str):
            """Get specific incident by ID"""
            if commander_instance:
                for incident in commander_instance.incident_history:
                    if incident.get("id") == incident_id:
                        return incident
            raise HTTPException(status_code=404, detail="Incident not found")
        
        @app.post("/trigger_incident")
        async def trigger_incident():
            """Manually trigger an incident for testing"""
            if commander_instance:
                return commander_instance.manually_trigger_incident("test", ["service_a"], "Test incident for LLM output demonstration")
            return {"error": "Commander not initialized"}
        
        @app.get("/health")
        async def health_check():
            """Health check endpoint"""
            if commander_instance:
                return {"status": "healthy", "commander_running": commander_instance.running}
            return {"status": "error", "commander_running": False}
    
    def start(self):
        """Start the incident commander"""
        print("🚀 Starting Incident Commander...")
        self.running = True
        
        # Start background health monitoring
        health_thread = threading.Thread(target=self._health_monitoring_loop, daemon=True)
        health_thread.start()
        
        # Start incident detection loop
        incident_thread = threading.Thread(target=self._incident_detection_loop, daemon=True)
        incident_thread.start()
        
        # Start FastAPI server in a separate thread
        api_thread = threading.Thread(target=self._start_api_server, daemon=True)
        api_thread.start()
        
        print("✅ Incident Commander started")
    
    def _start_api_server(self):
        """Start the FastAPI server"""
        try:
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")
        except Exception as e:
            print(f"❌ API server error: {e}")
    
    def stop(self):
        """Stop the incident commander"""
        print("🛑 Stopping Incident Commander...")
        self.running = False
        print("✅ Incident Commander stopped")
    
    def _health_monitoring_loop(self):
        """Background loop for monitoring service health"""
        while self.running:
            try:
                self.service_status_cache = self._get_all_service_status()
                time.sleep(HEALTH_CHECK_INTERVAL)
            except Exception as e:
                print(f"❌ Health monitoring error: {e}")
                time.sleep(HEALTH_CHECK_INTERVAL)
    
    def _incident_detection_loop(self):
        """Background loop for detecting incidents"""
        while self.running:
            try:
                # Check for new incidents
                incidents = self._detect_incidents()
                
                for incident in incidents:
                    if not self._is_incident_already_handled(incident):
                        self._handle_incident(incident)
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"❌ Incident detection error: {e}")
                time.sleep(10)
    
    def _get_all_service_status(self) -> Dict[str, Any]:
        """Get current status of all services"""
        status = {}
        for service_name, config in SERVICES.items():
            try:
                port = config["port"]
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                if response.status_code == 200:
                    status[service_name] = response.json()
                else:
                    status[service_name] = {"status": "unknown", "error": f"HTTP {response.status_code}"}
            except:
                status[service_name] = {"status": "down", "error": "Connection failed"}
        
        return status
    
    def _detect_incidents(self) -> List[Dict[str, Any]]:
        """Detect incidents based on service status"""
        incidents = []
        
        # Check for down services
        down_services = [name for name, status in self.service_status_cache.items() 
                        if status.get("status") == "down"]
        
        if down_services:
            incidents.append({
                "id": f"down_{int(time.time())}",
                "type": "service_down",
                "severity": "high",
                "affected_services": down_services,
                "summary": f"Services {', '.join(down_services)} are down",
                "timestamp": time.time()
            })
        
        # Check for degraded services
        degraded_services = [name for name, status in self.service_status_cache.items() 
                           if status.get("status") == "degraded"]
        
        if degraded_services:
            incidents.append({
                "id": f"degraded_{int(time.time())}",
                "type": "service_degraded",
                "severity": "medium",
                "affected_services": degraded_services,
                "summary": f"Services {', '.join(degraded_services)} are degraded",
                "timestamp": time.time()
            })
        
        # Check for dependency chain failures
        dependency_incidents = self._detect_dependency_incidents()
        incidents.extend(dependency_incidents)
        
        return incidents
    
    def _detect_dependency_incidents(self) -> List[Dict[str, Any]]:
        """Detect incidents caused by dependency failures"""
        incidents = []
        
        for service_name, config in SERVICES.items():
            dependencies = config.get("dependencies", [])
            if dependencies:
                # Check if any dependencies are down
                down_deps = []
                for dep in dependencies:
                    if dep in self.service_status_cache:
                        dep_status = self.service_status_cache[dep].get("status")
                        if dep_status == "down":
                            down_deps.append(dep)
                
                if down_deps:
                    incidents.append({
                        "type": "dependency_failure",
                        "severity": "medium",
                        "affected_services": [service_name],
                        "root_cause_services": down_deps,
                        "summary": f"Service {service_name} affected by down dependencies: {', '.join(down_deps)}",
                        "timestamp": time.time()
                    })
        
        return incidents
    
    def _is_incident_already_handled(self, incident: Dict[str, Any]) -> bool:
        """Check if an incident is already being handled"""
        if not self.current_incident:
            return False
        
        # Check if this is the same type of incident affecting the same services
        current = self.current_incident
        if (current.get("type") == incident.get("type") and 
            set(current.get("affected_services", [])) == set(incident.get("affected_services", []))):
            return True
        
        return False
    
    def _handle_incident(self, incident: Dict[str, Any]):
        """Handle a detected incident"""
        print(f"🚨 New incident detected: {incident.get('summary')}")
        
        # Set as current incident
        self.current_incident = incident
        
        # Custom diagnosis
        try:
            diagnosis = custom_diagnose(self.service_status_cache)
            incident["custom_diagnosis"] = diagnosis
        except Exception as e:
            print(f"❌ Custom diagnosis failed: {e}")
            incident["custom_diagnosis"] = {"error": str(e)}
        
        # Create incident response plan
        try:
            plan = self.planner.create_plan(incident["summary"], self.service_status_cache)
            incident["response_plan"] = plan
        except Exception as e:
            print(f"❌ Plan creation failed: {e}")
            incident["response_plan"] = {"error": str(e)}
            return
        
        # Execute the plan
        try:
            execution_result = self.executor.execute_plan(plan, self.service_status_cache)
            incident["execution_result"] = execution_result
        except Exception as e:
            print(f"❌ Plan execution failed: {e}")
            incident["execution_result"] = {"error": str(e)}
        
        # Evaluate the response
        try:
            evaluation = custom_evaluate(
                incident, 
                self.service_status_cache, 
                execution_result.get("final_service_status", {})
            )
            incident["evaluation"] = evaluation
        except Exception as e:
            print(f"❌ Custom evaluation failed: {e}")
            incident["evaluation"] = {"error": str(e)}
        
        # Learn from the incident
        try:
            learning_result = custom_learn(
                self.executor.get_execution_history(),
                [incident]
            )
            incident["learning_result"] = learning_result
        except Exception as e:
            print(f"❌ Custom learning failed: {e}")
            incident["learning_result"] = {"error": str(e)}
        
        # Store in history
        incident["resolved_at"] = time.time()
        self.incident_history.append(incident)
        
        # Clear current incident
        self.current_incident = None
        
        print(f"✅ Incident resolved: {incident.get('summary')}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current status of the commander"""
        return {
            "running": self.running,
            "current_incident": self.current_incident,
            "service_status": self.service_status_cache,
            "incidents_handled": len(self.incident_history),
            "last_incident": self.incident_history[-1] if self.incident_history else None
        }
    
    def get_incident_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent incident history"""
        return self.incident_history[-limit:] if self.incident_history else []
    
    def manually_trigger_incident(self, incident_type: str, affected_services: List[str], 
                                 summary: str = None) -> Dict[str, Any]:
        """Manually trigger an incident for testing"""
        if not summary:
            summary = f"Manual {incident_type} incident for services: {', '.join(affected_services)}"
        
        incident = {
            "type": incident_type,
            "severity": "medium",
            "affected_services": affected_services,
            "summary": summary,
            "timestamp": time.time(),
            "manual_trigger": True
        }
        
        self._handle_incident(incident)
        return incident
