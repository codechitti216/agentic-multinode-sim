from typing import Dict, Any, List
import time
import requests
import json
from config import SERVICES
from .agent_hooks import custom_execute

class PlanExecutor:
    def __init__(self):
        self.execution_history = []
        self.current_execution = None
    
    def execute_plan(self, plan: Dict[str, Any], service_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete incident response plan
        
        Args:
            plan: The incident response plan to execute
            service_status: Current status of all services
            
        Returns:
            Execution results and final status
        """
        print(f"🚀 Executing plan: {plan.get('incident_id', 'unknown')}")
        
        execution_start = time.time()
        execution_results = []
        final_status = service_status.copy()
        
        # Execute each step in order
        for step in plan.get("steps", []):
            print(f"📋 Executing step {step.get('step_id')}: {step.get('action')}")
            
            step_result = self._execute_step(step, final_status)
            execution_results.append(step_result)
            
            # Update service status after each step
            final_status = self._get_updated_service_status()
            
            # Check if step was successful
            if step_result.get("status") == "failed":
                print(f"❌ Step {step.get('step_id')} failed, stopping execution")
                break
            
            # Small delay between steps
            time.sleep(1)
        
        execution_time = time.time() - execution_start
        
        # Create execution summary
        execution_summary = {
            "plan_id": plan.get("incident_id"),
            "execution_start": execution_start,
            "execution_end": time.time(),
            "execution_time": execution_time,
            "steps_executed": len(execution_results),
            "steps_successful": len([r for r in execution_results if r.get("status") == "success"]),
            "steps_failed": len([r for r in execution_results if r.get("status") == "failed"]),
            "final_service_status": final_status,
            "step_results": execution_results
        }
        
        # Store in history
        self.execution_history.append(execution_summary)
        
        print(f"✅ Plan execution completed in {execution_time:.2f}s")
        return execution_summary
    
    def _execute_step(self, step: Dict[str, Any], service_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single plan step
        
        Args:
            step: The step to execute
            service_status: Current service status
            
        Returns:
            Step execution result
        """
        step_start = time.time()
        
        try:
            # Apply custom execution logic first
            custom_result = custom_execute(step, service_status)
            
            # Execute the actual action
            action_result = self._execute_action(step, service_status)
            
            # Combine results
            step_result = {
                "step_id": step.get("step_id"),
                "action": step.get("action"),
                "target_service": step.get("target_service"),
                "status": "success" if action_result.get("success") else "failed",
                "execution_time": time.time() - step_start,
                "custom_logic_applied": custom_result.get("custom_logic_applied", False),
                "action_result": action_result,
                "custom_result": custom_result,
                "timestamp": time.time()
            }
            
            print(f"✅ Step {step.get('step_id')} completed: {action_result.get('message', 'Success')}")
            
        except Exception as e:
            step_result = {
                "step_id": step.get("step_id"),
                "action": step.get("action"),
                "target_service": step.get("target_service"),
                "status": "failed",
                "execution_time": time.time() - step_start,
                "error": str(e),
                "timestamp": time.time()
            }
            print(f"❌ Step {step.get('step_id')} failed: {e}")
        
        return step_result
    
    def _execute_action(self, step: Dict[str, Any], service_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the actual action specified in the step
        
        Args:
            step: The step containing action details
            service_status: Current service status
            
        Returns:
            Action execution result
        """
        action = step.get("action", "").lower()
        target_service = step.get("target_service", "")
        
        if "restart" in action or "recover" in action:
            return self._restart_service(target_service)
        elif "investigate" in action:
            return self._investigate_service(target_service)
        elif "verify" in action:
            return self._verify_service(target_service)
        else:
            return {"success": False, "message": f"Unknown action: {action}"}
    
    def _restart_service(self, target_service: str) -> Dict[str, Any]:
        """Restart a specific service"""
        if target_service == "all":
            # Restart all services
            results = []
            for service_name in SERVICES.keys():
                result = self._restart_single_service(service_name)
                results.append(result)
            
            success_count = len([r for r in results if r.get("success")])
            return {
                "success": success_count > 0,
                "message": f"Restarted {success_count}/{len(results)} services",
                "details": results
            }
        else:
            return self._restart_single_service(target_service)
    
    def _restart_single_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a single service"""
        if service_name not in SERVICES:
            return {"success": False, "message": f"Service {service_name} not found"}
        
        try:
            port = SERVICES[service_name]["port"]
            response = requests.post(f"http://localhost:{port}/recover", timeout=10)
            
            if response.status_code == 200:
                return {"success": True, "message": f"Service {service_name} restarted"}
            else:
                return {"success": False, "message": f"Failed to restart {service_name}: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error restarting {service_name}: {str(e)}"}
    
    def _investigate_service(self, target_service: str) -> Dict[str, Any]:
        """Investigate a service's health and dependencies"""
        if target_service == "all":
            # Investigate all services
            results = {}
            for service_name in SERVICES.keys():
                results[service_name] = self._investigate_single_service(service_name)
            return {"success": True, "message": "Investigation completed", "details": results}
        else:
            return self._investigate_single_service(target_service)
    
    def _investigate_single_service(self, service_name: str) -> Dict[str, Any]:
        """Investigate a single service"""
        if service_name not in SERVICES:
            return {"success": False, "message": f"Service {service_name} not found"}
        
        try:
            port = SERVICES[service_name]["port"]
            
            # Get health status
            health_response = requests.get(f"http://localhost:{port}/health", timeout=10)
            health_data = health_response.json() if health_response.status_code == 200 else {}
            
            # Get metrics
            metrics_response = requests.get(f"http://localhost:{port}/metrics", timeout=10)
            metrics_data = metrics_response.json() if metrics_response.status_code == 200 else {}
            
            # Get dependencies
            deps_response = requests.get(f"http://localhost:{port}/dependencies", timeout=10)
            deps_data = deps_response.json() if deps_response.status_code == 200 else {}
            
            return {
                "success": True,
                "health": health_data,
                "metrics": metrics_data,
                "dependencies": deps_data
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error investigating {service_name}: {str(e)}"}
    
    def _verify_service(self, target_service: str) -> Dict[str, Any]:
        """Verify a service is working correctly"""
        if target_service == "all":
            # Verify all services
            results = {}
            for service_name in SERVICES.keys():
                results[service_name] = self._verify_single_service(service_name)
            
            success_count = len([r for r in results.values() if r.get("success")])
            return {"success": success_count > 0, "message": f"Verified {success_count}/{len(results)} services", "details": results}
        else:
            return self._verify_single_service(target_service)
    
    def _verify_single_service(self, service_name: str) -> Dict[str, Any]:
        """Verify a single service"""
        if service_name not in SERVICES:
            return {"success": False, "message": f"Service {service_name} not found"}
        
        try:
            port = SERVICES[service_name]["port"]
            response = requests.get(f"http://localhost:{port}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get("status", "unknown")
                is_healthy = status == "healthy"
                
                return {
                    "success": is_healthy,
                    "message": f"Service {service_name} status: {status}",
                    "status": status
                }
            else:
                return {"success": False, "message": f"Failed to verify {service_name}: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error verifying {service_name}: {str(e)}"}
    
    def _get_updated_service_status(self) -> Dict[str, Any]:
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
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-limit:] if self.execution_history else []
