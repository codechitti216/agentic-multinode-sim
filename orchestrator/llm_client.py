import requests
import json
from typing import List, Dict, Any
from config import LLM_ENDPOINT, LLM_MODEL

class LLMClient:
    def __init__(self):
        self.endpoint = LLM_ENDPOINT
        self.model = LLM_MODEL
    
    def chat_with_llm(self, messages: List[Dict[str, str]]) -> str:
        """
        Send a chat completion request to the local LLM
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            The LLM's response content
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(self.endpoint, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "No response from LLM"
                
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with LLM: {e}")
            return f"LLM Error: {str(e)}"
        except Exception as e:
            print(f"Unexpected error: {e}")
            return f"Error: {str(e)}"
    
    def create_incident_plan(self, incident_summary: str, service_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an incident response plan using the LLM
        
        Args:
            incident_summary: Natural language description of the incident
            service_status: Current status of all services
            
        Returns:
            Structured plan with ordered steps
        """
        system_prompt = """You are an expert incident response coordinator. 
        Create a structured incident response plan based on the incident summary and current service status.
        
        Return your response as a valid JSON object with this structure:
        {
            "incident_id": "unique_identifier",
            "severity": "high|medium|low",
            "summary": "brief_description",
            "steps": [
                {
                    "step_id": 1,
                    "action": "action_description",
                    "target_service": "service_name",
                    "expected_outcome": "what_should_happen",
                    "priority": "high|medium|low"
                }
            ],
            "estimated_resolution_time": "time_estimate"
        }
        
        Focus on practical, actionable steps that can be executed by automation."""
        
        user_prompt = f"""
        Incident Summary: {incident_summary}
        
        Current Service Status:
        {json.dumps(service_status, indent=2)}
        
        Create an incident response plan to resolve this issue.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.chat_with_llm(messages)
        
        try:
            # Try to parse JSON response
            plan = json.loads(response)
            return plan
        except json.JSONDecodeError:
            # If LLM didn't return valid JSON, create a fallback plan
            return {
                "incident_id": "fallback_plan",
                "severity": "medium",
                "summary": "Fallback plan due to LLM response parsing error",
                "steps": [
                    {
                        "step_id": 1,
                        "action": "Investigate service health",
                        "target_service": "all",
                        "expected_outcome": "Identify root cause",
                        "priority": "high"
                    },
                    {
                        "step_id": 2,
                        "action": "Restart failed services",
                        "target_service": "failed_services",
                        "expected_outcome": "Service recovery",
                        "priority": "high"
                    }
                ],
                "estimated_resolution_time": "15 minutes"
            }
