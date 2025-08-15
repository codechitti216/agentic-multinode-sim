from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
import random
from typing import Dict, Any
import uvicorn
import threading
import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SERVICES, SERVICE_STATES

class ServiceStatus(BaseModel):
    status: str
    cpu: float
    memory: float
    error_rate: float
    timestamp: float
    dependencies: Dict[str, str]

class MicroserviceTemplate:
    def __init__(self, service_name: str, port: int, dependencies: list):
        self.service_name = service_name
        self.port = port
        self.dependencies = dependencies
        self.status = "healthy"
        self.cpu = 20.0
        self.memory = 30.0
        self.error_rate = 0.0
        self.app = FastAPI(title=f"{service_name.upper()}")
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.get("/health")
        async def health_check():
            return {
                "service": self.service_name,
                "status": self.status,
                "timestamp": time.time()
            }
        
        @self.app.get("/metrics")
        async def get_metrics():
            return {
                "service": self.service_name,
                "cpu": self.cpu,
                "memory": self.memory,
                "error_rate": self.error_rate,
                "timestamp": time.time()
            }
        
        @self.app.post("/inject_failure")
        async def inject_failure(failure_type: str = "random"):
            if failure_type == "random":
                failure_type = random.choice(["degraded", "down"])
            
            self.status = failure_type
            if failure_type == "down":
                self.cpu = 100.0
                self.memory = 95.0
                self.error_rate = 100.0
            elif failure_type == "degraded":
                self.cpu = 80.0
                self.memory = 70.0
                self.error_rate = 25.0
                
            return {"message": f"Failure injected: {failure_type}", "status": self.status}
        
        @self.app.post("/recover")
        async def recover():
            self.status = "healthy"
            self.cpu = 20.0
            self.memory = 30.0
            self.error_rate = 0.0
            return {"message": "Service recovered", "status": self.status}
        
        @self.app.get("/dependencies")
        async def get_dependencies():
            dep_status = {}
            for dep in self.dependencies:
                try:
                    dep_port = SERVICES[dep]["port"]
                    response = requests.get(f"http://localhost:{dep_port}/health", timeout=2)
                    dep_status[dep] = response.json()["status"]
                except:
                    dep_status[dep] = "down"
            return {"dependencies": dep_status}
    
    def check_dependencies(self):
        """Check dependency health and update own status accordingly"""
        for dep in self.dependencies:
            try:
                dep_port = SERVICES[dep]["port"]
                response = requests.get(f"http://localhost:{dep_port}/health", timeout=2)
                dep_status = response.json()["status"]
                
                if dep_status == "down" and self.status == "healthy":
                    self.status = "degraded"
                    self.cpu = 60.0
                    self.memory = 50.0
                    self.error_rate = 15.0
                elif dep_status == "healthy" and self.status == "degraded":
                    # Only recover if all dependencies are healthy
                    all_healthy = True
                    for other_dep in self.dependencies:
                        try:
                            other_port = SERVICES[other_dep]["port"]
                            other_response = requests.get(f"http://localhost:{other_port}/health", timeout=2)
                            if other_response.json()["status"] != "healthy":
                                all_healthy = False
                                break
                        except:
                            all_healthy = False
                            break
                    
                    if all_healthy:
                        self.status = "healthy"
                        self.cpu = 20.0
                        self.memory = 30.0
                        self.error_rate = 0.0
                        
            except:
                if self.status == "healthy":
                    self.status = "degraded"
                    self.cpu = 60.0
                    self.memory = 50.0
                    self.error_rate = 15.0
    
    def update_metrics(self):
        """Update service metrics based on current status"""
        if self.status == "healthy":
            self.cpu = max(15.0, min(35.0, self.cpu + random.uniform(-2, 2)))
            self.memory = max(25.0, min(40.0, self.memory + random.uniform(-1, 1)))
            self.error_rate = max(0.0, min(5.0, self.error_rate + random.uniform(-0.5, 0.5)))
        elif self.status == "degraded":
            self.cpu = max(50.0, min(90.0, self.cpu + random.uniform(-5, 5)))
            self.memory = max(45.0, min(80.0, self.memory + random.uniform(-3, 3)))
            self.error_rate = max(10.0, min(40.0, self.error_rate + random.uniform(-2, 2)))
        # down status doesn't change metrics
    
    def start(self):
        """Start the service"""
        uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="info")
    
    def run_background_tasks(self):
        """Run background health checks and metric updates"""
        def background_loop():
            while True:
                self.check_dependencies()
                self.update_metrics()
                time.sleep(5)
        
        thread = threading.Thread(target=background_loop, daemon=True)
        thread.start()
