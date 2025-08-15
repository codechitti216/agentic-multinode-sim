from typing import Dict, Any, List
import time
from .llm_client import LLMClient
from .agent_hooks import custom_plan

class IncidentPlanner:
    def __init__(self):
        self.llm_client = LLMClient()
        self.plan_history = []
    
    def create_plan(self, incident_summary: str, service_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an incident response plan using LLM and custom logic
        
        Args:
            incident_summary: Natural language description of the incident
            service_status: Current status of all services
            
        Returns:
            Enhanced incident response plan
        """
        print(f"🤖 Creating incident response plan for: {incident_summary}")
        
        # Generate base plan using LLM
        try:
            llm_plan = self.llm_client.create_incident_plan(incident_summary, service_status)
            print(f"✅ LLM generated plan: {llm_plan.get('incident_id', 'unknown')}")
        except Exception as e:
            print(f"❌ LLM plan generation failed: {e}")
            llm_plan = self._create_fallback_plan(incident_summary, service_status)
        
        # Apply custom planning logic
        try:
            enhanced_plan = custom_plan(incident_summary, service_status, llm_plan)
            print(f"✅ Custom logic applied to plan")
        except Exception as e:
            print(f"❌ Custom planning failed: {e}")
            enhanced_plan = llm_plan
        
        # Add metadata
        enhanced_plan["created_at"] = time.time()
        enhanced_plan["planner_version"] = "1.0"
        enhanced_plan["llm_used"] = True
        enhanced_plan["custom_logic_applied"] = enhanced_plan != llm_plan
        
        # Store in history
        self.plan_history.append({
            "timestamp": time.time(),
            "incident_summary": incident_summary,
            "plan": enhanced_plan,
            "service_status": service_status
        })
        
        return enhanced_plan
    
    def _create_fallback_plan(self, incident_summary: str, service_status: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback plan when LLM is unavailable"""
        failed_services = [name for name, status in service_status.items() 
                          if status.get("status") in ["down", "degraded"]]
        
        return {
            "incident_id": f"fallback_{int(time.time())}",
            "severity": "medium",
            "summary": f"Fallback plan for: {incident_summary}",
            "steps": [
                {
                    "step_id": 1,
                    "action": "Investigate failed services",
                    "target_service": "all",
                    "expected_outcome": "Identify root cause",
                    "priority": "high"
                },
                {
                    "step_id": 2,
                    "action": "Restart failed services",
                    "target_service": ",".join(failed_services),
                    "expected_outcome": "Service recovery",
                    "priority": "high"
                },
                {
                    "step_id": 3,
                    "action": "Verify dependencies",
                    "target_service": "all",
                    "expected_outcome": "Dependency health confirmed",
                    "priority": "medium"
                }
            ],
            "estimated_resolution_time": "20 minutes"
        }
    
    def get_plan_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent plan history"""
        return self.plan_history[-limit:] if self.plan_history else []
    
    def get_plan_by_id(self, plan_id: str) -> Dict[str, Any]:
        """Get a specific plan by ID"""
        for plan_record in self.plan_history:
            if plan_record["plan"].get("incident_id") == plan_id:
                return plan_record
        return {}
