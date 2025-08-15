import time
import threading
import random
import requests
from typing import Dict, Any, List
from config import SERVICES, FAILURE_INJECTION_INTERVAL, FAILURE_PROBABILITY
from .failure_scenarios import FailureScenarios
import json
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

# FastAPI app for HTTP endpoints
app = FastAPI(title="Failure Injector API", version="1.0.0")

class FailureInjector:
    def __init__(self, log_dir: str = "data/logs"):
        self.scenarios = FailureScenarios()
        self.running = False
        self.active_failures = {}
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, "failure_logs.csv")
        
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize log file
        self._init_log_file()
        
        # Setup FastAPI routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes for the failure injector API"""
        
        @app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "injector_running": self.running}
        
        @app.get("/active_failures")
        async def get_active_failures():
            """Get currently active failures"""
            return self.get_active_failures()
        
        @app.get("/failure_history")
        async def get_failure_history():
            """Get failure history"""
            return self.get_failure_history()
        
        @app.post("/inject_custom_failure")
        async def inject_custom_failure_endpoint(failure_data: dict):
            """Inject a custom failure via API"""
            try:
                service_names = failure_data.get("service_names", [])
                failure_type = failure_data.get("failure_type", "degraded")
                duration = failure_data.get("duration", 120)
                
                if not service_names:
                    raise HTTPException(status_code=400, detail="service_names is required")
                
                failure_id = self.inject_custom_failure(service_names, failure_type, duration)
                
                return {
                    "success": True,
                    "failure_id": failure_id,
                    "message": f"Failure injected into {', '.join(service_names)}"
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/clear_all_failures")
        async def clear_all_failures_endpoint():
            """Clear all active failures via API"""
            try:
                self.clear_all_failures()
                return {"success": True, "message": "All failures cleared"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/status")
        async def get_status():
            """Get injector status"""
            return {
                "running": self.running,
                "active_failures_count": len(self.active_failures),
                "scenarios_available": len(self.scenarios.get_all_scenarios()),
                "last_injection": time.time() if self.active_failures else None
            }
    
    def _init_log_file(self):
        """Initialize the log file with headers"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("timestamp,failure_id,scenario_name,type,target_services,failure_type,duration,status\n")
    
    def start(self):
        """Start the failure injector"""
        print("💥 Starting Failure Injector...")
        self.running = True
        
        # Start background failure injection
        injection_thread = threading.Thread(target=self._failure_injection_loop, daemon=True)
        injection_thread.start()
        
        # Start failure recovery monitoring
        recovery_thread = threading.Thread(target=self._failure_recovery_loop, daemon=True)
        recovery_thread.start()
        
        # Start FastAPI server in a separate thread
        api_thread = threading.Thread(target=self._start_api_server, daemon=True)
        api_thread.start()
        
        print("✅ Failure Injector started")
    
    def _start_api_server(self):
        """Start the FastAPI server"""
        try:
            uvicorn.run(app, host="0.0.0.0", port=8006, log_level="error")
        except Exception as e:
            print(f"❌ API server error: {e}")
    
    def stop(self):
        """Stop the failure injector"""
        print("🛑 Stopping Failure Injector...")
        self.running = False
        print("✅ Failure Injector stopped")
    
    def _failure_injection_loop(self):
        """Background loop for injecting failures"""
        while self.running:
            try:
                # Random chance to inject a failure
                if random.random() < FAILURE_PROBABILITY:
                    self._inject_random_failure()
                
                time.sleep(FAILURE_INJECTION_INTERVAL)
                
            except Exception as e:
                print(f"❌ Failure injection error: {e}")
                time.sleep(FAILURE_INJECTION_INTERVAL)
    
    def _failure_recovery_loop(self):
        """Background loop for monitoring and recovering from failures"""
        while self.running:
            try:
                current_time = time.time()
                failures_to_remove = []
                
                for failure_id, failure_data in self.active_failures.items():
                    # Check if failure duration has expired
                    if current_time - failure_data["start_time"] >= failure_data["duration"]:
                        self._recover_failure(failure_id, failure_data)
                        failures_to_remove.append(failure_id)
                
                # Remove recovered failures
                for failure_id in failures_to_remove:
                    del self.active_failures[failure_id]
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"❌ Failure recovery error: {e}")
                time.sleep(5)
    
    def _inject_random_failure(self):
        """Inject a random failure scenario"""
        try:
            scenario = self.scenarios.get_random_scenario()
            if scenario:
                self._inject_scenario(scenario)
        except Exception as e:
            print(f"❌ Random failure injection error: {e}")
    
    def _inject_scenario(self, scenario: Dict[str, Any]):
        """Inject a specific failure scenario"""
        try:
            failure_id = f"{scenario['id']}_{int(time.time())}"
            
            print(f"💥 Injecting failure: {scenario['name']}")
            
            if scenario["type"] == "cascade":
                self._inject_cascade_failure(failure_id, scenario)
            else:
                self._inject_simple_failure(failure_id, scenario)
            
            # Log the failure
            self._log_failure(failure_id, scenario, "injected")
            
        except Exception as e:
            print(f"❌ Scenario injection error: {e}")
    
    def _inject_simple_failure(self, failure_id: str, scenario: Dict[str, Any]):
        """Inject a simple failure (single service or multiple services)"""
        target_services = scenario["target_services"]
        failure_type = scenario["failure_type"]
        duration = scenario["duration"]
        
        for service_name in target_services:
            if service_name in SERVICES:
                try:
                    port = SERVICES[service_name]["port"]
                    response = requests.post(
                        f"http://localhost:{port}/inject_failure",
                        params={"failure_type": failure_type},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        print(f"✅ Injected {failure_type} failure into {service_name}")
                    else:
                        print(f"❌ Failed to inject failure into {service_name}: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error injecting failure into {service_name}: {e}")
        
        # Store failure data
        self.active_failures[failure_id] = {
            "scenario": scenario,
            "target_services": target_services,
            "failure_type": failure_type,
            "start_time": time.time(),
            "duration": duration,
            "type": "simple"
        }
    
    def _inject_cascade_failure(self, failure_id: str, scenario: Dict[str, Any]):
        """Inject a cascade failure with timing delays"""
        failure_sequence = scenario.get("failure_sequence", [])
        duration = scenario["duration"]
        
        # Store failure data
        self.active_failures[failure_id] = {
            "scenario": scenario,
            "target_services": scenario["target_services"],
            "failure_type": "cascade",
            "start_time": time.time(),
            "duration": duration,
            "type": "cascade",
            "sequence": failure_sequence
        }
        
        # Execute failure sequence with delays
        for step in failure_sequence:
            try:
                service_name = step["service"]
                failure_type = step["failure_type"]
                delay = step["delay"]
                
                # Wait for the specified delay
                time.sleep(delay)
                
                if service_name in SERVICES:
                    port = SERVICES[service_name]["port"]
                    response = requests.post(
                        f"http://localhost:{port}/inject_failure",
                        params={"failure_type": failure_type},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        print(f"✅ Cascade step: Injected {failure_type} failure into {service_name}")
                    else:
                        print(f"❌ Cascade step: Failed to inject failure into {service_name}")
                        
            except Exception as e:
                print(f"❌ Cascade failure step error: {e}")
    
    def _recover_failure(self, failure_id: str, failure_data: Dict[str, Any]):
        """Recover from a failure"""
        try:
            target_services = failure_data["target_services"]
            scenario_name = failure_data["scenario"]["name"]
            
            print(f"🔄 Recovering from failure: {scenario_name}")
            
            for service_name in target_services:
                if service_name in SERVICES:
                    try:
                        port = SERVICES[service_name]["port"]
                        response = requests.post(f"http://localhost:{port}/recover", timeout=10)
                        
                        if response.status_code == 200:
                            print(f"✅ Recovered {service_name}")
                        else:
                            print(f"❌ Failed to recover {service_name}: {response.status_code}")
                            
                    except Exception as e:
                        print(f"❌ Error recovering {service_name}: {e}")
            
            # Log the recovery
            self._log_failure(failure_id, failure_data["scenario"], "recovered")
            
        except Exception as e:
            print(f"❌ Failure recovery error: {e}")
    
    def _log_failure(self, failure_id: str, scenario: Dict[str, Any], status: str):
        """Log failure events to CSV file"""
        try:
            timestamp = datetime.now().isoformat()
            target_services = ",".join(scenario["target_services"])
            
            log_entry = f"{timestamp},{failure_id},{scenario['name']},{scenario['type']},{target_services},{scenario['failure_type']},{scenario['duration']},{status}\n"
            
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"❌ Logging error: {e}")
    
    def inject_custom_failure(self, service_names: List[str], failure_type: str, 
                             duration: int = 120) -> str:
        """Manually inject a custom failure"""
        try:
            # Create custom scenario
            scenario = self.scenarios.create_custom_scenario(
                f"Manual {failure_type} failure",
                service_names,
                failure_type,
                duration
            )
            
            failure_id = f"manual_{int(time.time())}"
            self._inject_simple_failure(failure_id, scenario)
            
            print(f"💥 Manually injected {failure_type} failure into {', '.join(service_names)}")
            return failure_id
            
        except Exception as e:
            print(f"❌ Custom failure injection error: {e}")
            return ""
    
    def get_active_failures(self) -> Dict[str, Any]:
        """Get currently active failures"""
        return self.active_failures.copy()
    
    def get_failure_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get failure history from log file"""
        try:
            history = []
            with open(self.log_file, 'r') as f:
                lines = f.readlines()[1:]  # Skip header
                
                for line in lines[-limit:]:
                    parts = line.strip().split(',')
                    if len(parts) >= 8:
                        history.append({
                            "timestamp": parts[0],
                            "failure_id": parts[1],
                            "scenario_name": parts[2],
                            "type": parts[3],
                            "target_services": parts[4].split(';'),
                            "failure_type": parts[5],
                            "duration": int(parts[6]) if parts[6].isdigit() else 0,
                            "status": parts[7]
                        })
            
            return history
            
        except Exception as e:
            print(f"❌ Error reading failure history: {e}")
            return []
    
    def clear_all_failures(self):
        """Clear all active failures and recover services"""
        print("🧹 Clearing all active failures...")
        
        for failure_id in list(self.active_failures.keys()):
            self._recover_failure(failure_id, self.active_failures[failure_id])
            del self.active_failures[failure_id]
        
        print("✅ All failures cleared")
