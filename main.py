#!/usr/bin/env python3
"""
Agentic Incident Simulation & Planning Framework
Main entry point for starting all components
"""

import os
import sys
import time
import signal
import subprocess
import threading
import requests
from typing import List, Dict, Any
import json

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SERVICES, DASHBOARD_PORT
from orchestrator.commander import IncidentCommander
from failures.injector import FailureInjector
from visualizer.graph_state import GraphState

class SystemOrchestrator:
    def __init__(self):
        self.service_processes = {}
        self.commander = None
        self.failure_injector = None
        self.graph_state = GraphState()
        self.running = False
        
        # Ensure data directory exists
        os.makedirs("data/logs", exist_ok=True)
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.shutdown()
        sys.exit(0)
    
    def start_services(self):
        """Start all microservices"""
        print("🚀 Starting microservices...")
        
        for service_name, config in SERVICES.items():
            try:
                # Start service in subprocess
                service_file = f"services/{service_name}.py"
                if os.path.exists(service_file):
                    process = subprocess.Popen(
                        [sys.executable, service_file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=os.getcwd()
                    )
                    
                    self.service_processes[service_name] = process
                    print(f"✅ Started {service_name} (PID: {process.pid})")
                    
                    # Wait a moment for service to start
                    time.sleep(2)
                else:
                    print(f"❌ Service file not found: {service_file}")
                    
            except Exception as e:
                print(f"❌ Failed to start {service_name}: {e}")
        
        # Wait for all services to be ready
        self._wait_for_services_ready()
        print("✅ All microservices started")
    
    def _wait_for_services_ready(self, timeout: int = 60):
        """Wait for all services to be ready"""
        print("⏳ Waiting for services to be ready...")
        
        start_time = time.time()
        ready_services = set()
        
        while len(ready_services) < len(SERVICES) and (time.time() - start_time) < timeout:
            for service_name, config in SERVICES.items():
                if service_name in ready_services:
                    continue
                
                try:
                    port = config["port"]
                    response = requests.get(f"http://localhost:{port}/health", timeout=2)
                    if response.status_code == 200:
                        ready_services.add(service_name)
                        print(f"✅ {service_name} is ready")
                except:
                    pass
            
            time.sleep(1)
        
        if len(ready_services) == len(SERVICES):
            print("✅ All services are ready")
        else:
            print(f"⚠️ Only {len(ready_services)}/{len(SERVICES)} services are ready")
    
    def start_failure_injector(self):
        """Start the failure injection system"""
        print("💥 Starting failure injector...")
        
        try:
            self.failure_injector = FailureInjector()
            self.failure_injector.start()
            print("✅ Failure injector started")
        except Exception as e:
            print(f"❌ Failed to start failure injector: {e}")
    
    def start_incident_commander(self):
        """Start the incident commander"""
        print("🎯 Starting incident commander...")
        
        try:
            self.commander = IncidentCommander()
            self.commander.start()
            print("✅ Incident commander started")
        except Exception as e:
            print(f"❌ Failed to start incident commander: {e}")
    
    def start_dashboard(self):
        """Start the Streamlit dashboard"""
        print("📊 Starting dashboard...")
        
        try:
            # Start dashboard in subprocess
            dashboard_process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "visualizer/dashboard.py", 
                 "--server.port", str(DASHBOARD_PORT), "--server.headless", "true"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            self.service_processes["dashboard"] = dashboard_process
            print(f"✅ Dashboard started on port {DASHBOARD_PORT}")
            
            # Wait for dashboard to be ready
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Failed to start dashboard: {e}")
    
    def start_system_monitoring(self):
        """Start background system monitoring"""
        print("📡 Starting system monitoring...")
        
        def monitoring_loop():
            while self.running:
                try:
                    # Update graph state with current service status
                    all_status = {}
                    for service_name, config in SERVICES.items():
                        try:
                            port = config["port"]
                            response = requests.get(f"http://localhost:{port}/health", timeout=2)
                            if response.status_code == 200:
                                all_status[service_name] = response.json()
                            else:
                                all_status[service_name] = {"status": "unknown", "error": f"HTTP {response.status_code}"}
                        except:
                            all_status[service_name] = {"status": "down", "error": "Connection failed"}
                    
                    # Update graph state
                    self.graph_state.update_all_services(all_status)
                    
                    time.sleep(5)  # Update every 5 seconds
                    
                except Exception as e:
                    print(f"❌ Monitoring error: {e}")
                    time.sleep(5)
        
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        print("✅ System monitoring started")
    
    def start(self):
        """Start the entire system"""
        print("🚀 Starting Agentic Incident Simulation & Planning Framework...")
        print("=" * 70)
        
        try:
            # Start services
            self.start_services()
            
            # Start failure injector
            self.start_failure_injector()
            
            # Start incident commander
            self.start_incident_commander()
            
            # Start dashboard
            self.start_dashboard()
            
            # Start system monitoring
            self.start_system_monitoring()
            
            self.running = True
            
            print("=" * 70)
            print("✅ System started successfully!")
            print(f"📊 Dashboard: http://localhost:{DASHBOARD_PORT}")
            print("🎯 Incident Commander: Running")
            print("💥 Failure Injector: Running")
            print("🌐 Microservices: Running")
            print("=" * 70)
            print("Press Ctrl+C to stop the system")
            
            # Keep main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
        except Exception as e:
            print(f"❌ System startup failed: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the entire system"""
        print("🛑 Shutting down system...")
        self.running = False
        
        # Stop incident commander
        if self.commander:
            try:
                self.commander.stop()
                print("✅ Incident commander stopped")
            except Exception as e:
                print(f"❌ Error stopping incident commander: {e}")
        
        # Stop failure injector
        if self.failure_injector:
            try:
                self.failure_injector.stop()
                print("✅ Failure injector stopped")
            except Exception as e:
                print(f"❌ Error stopping failure injector: {e}")
        
        # Stop all service processes
        for service_name, process in self.service_processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {service_name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️ {service_name} force killed")
            except Exception as e:
                print(f"❌ Error stopping {service_name}: {e}")
        
        print("✅ System shutdown complete")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        status = {
            "running": self.running,
            "services": {},
            "commander": self.commander.get_current_status() if self.commander else {},
            "failure_injector": self.failure_injector.get_active_failures() if self.failure_injector else {},
            "graph_state": self.graph_state.get_health_summary()
        }
        
        # Check service processes
        for service_name, process in self.service_processes.items():
            if service_name == "dashboard":
                continue
                
            try:
                # Check if process is still running
                if process.poll() is None:
                    status["services"][service_name] = "running"
                else:
                    status["services"][service_name] = "stopped"
            except:
                status["services"][service_name] = "unknown"
        
        return status

def main():
    """Main entry point"""
    try:
        orchestrator = SystemOrchestrator()
        orchestrator.start()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
