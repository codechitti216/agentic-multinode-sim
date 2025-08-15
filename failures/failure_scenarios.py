import random
import time
from typing import List, Dict, Any
from config import SERVICES

class FailureScenarios:
    def __init__(self):
        self.scenarios = self._generate_scenarios()
    
    def _generate_scenarios(self) -> List[Dict[str, Any]]:
        """Generate OATS-based failure scenarios"""
        scenarios = []
        
        # Single service failures
        for service_name in SERVICES.keys():
            scenarios.extend([
                {
                    "id": f"single_{service_name}_down",
                    "name": f"{service_name.upper()} Service Down",
                    "type": "single_service",
                    "target_services": [service_name],
                    "failure_type": "down",
                    "description": f"Simulate {service_name} service being completely down",
                    "probability": 0.3,
                    "duration": random.randint(30, 120)  # 30 seconds to 2 minutes
                },
                {
                    "id": f"single_{service_name}_degraded",
                    "name": f"{service_name.upper()} Service Degraded",
                    "type": "single_service",
                    "target_services": [service_name],
                    "failure_type": "degraded",
                    "description": f"Simulate {service_name} service being degraded",
                    "probability": 0.4,
                    "duration": random.randint(60, 300)  # 1 to 5 minutes
                }
            ])
        
        # Dependency chain failures
        dependency_scenarios = [
            {
                "id": "cascade_failure_a_b",
                "name": "Cascade Failure A → B",
                "type": "cascade",
                "target_services": ["service_a", "service_b"],
                "failure_sequence": [
                    {"service": "service_b", "failure_type": "down", "delay": 0},
                    {"service": "service_a", "failure_type": "degraded", "delay": 10}
                ],
                "description": "Service B fails, causing Service A to degrade",
                "probability": 0.2,
                "duration": 180
            },
            {
                "id": "cascade_failure_b_c_d",
                "name": "Cascade Failure B → C → D",
                "type": "cascade",
                "target_services": ["service_b", "service_c", "service_d"],
                "failure_sequence": [
                    {"service": "service_c", "failure_type": "down", "delay": 0},
                    {"service": "service_b", "failure_type": "degraded", "delay": 15},
                    {"service": "service_d", "failure_type": "degraded", "delay": 30}
                ],
                "description": "Cascade failure through the dependency chain",
                "probability": 0.15,
                "duration": 240
            }
        ]
        scenarios.extend(dependency_scenarios)
        
        # Load-based failures
        load_scenarios = [
            {
                "id": "high_load_all",
                "name": "High Load All Services",
                "type": "load",
                "target_services": list(SERVICES.keys()),
                "failure_type": "degraded",
                "description": "Simulate high load causing all services to degrade",
                "probability": 0.1,
                "duration": 300
            },
            {
                "id": "memory_pressure",
                "name": "Memory Pressure",
                "type": "resource",
                "target_services": ["service_a", "service_e"],
                "failure_type": "degraded",
                "description": "Simulate memory pressure on frontend services",
                "probability": 0.25,
                "duration": 180
            }
        ]
        scenarios.extend(load_scenarios)
        
        # Configuration drift
        config_scenarios = [
            {
                "id": "config_drift_timeout",
                "name": "Configuration Drift - Timeout",
                "type": "config",
                "target_services": ["service_b", "service_c"],
                "failure_type": "degraded",
                "description": "Simulate configuration drift causing timeouts",
                "probability": 0.2,
                "duration": 240
            }
        ]
        scenarios.extend(config_scenarios)
        
        # Network issues
        network_scenarios = [
            {
                "id": "network_partition",
                "name": "Network Partition",
                "type": "network",
                "target_services": ["service_a", "service_d"],
                "failure_type": "down",
                "description": "Simulate network partition between services",
                "probability": 0.1,
                "duration": 120
            }
        ]
        scenarios.extend(network_scenarios)
        
        return scenarios
    
    def get_random_scenario(self) -> Dict[str, Any]:
        """Get a random failure scenario based on probabilities"""
        # Filter scenarios based on probability
        valid_scenarios = [s for s in self.scenarios if random.random() < s.get("probability", 0.5)]
        
        if not valid_scenarios:
            return random.choice(self.scenarios)
        
        return random.choice(valid_scenarios)
    
    def get_scenario_by_id(self, scenario_id: str) -> Dict[str, Any]:
        """Get a specific scenario by ID"""
        for scenario in self.scenarios:
            if scenario["id"] == scenario_id:
                return scenario
        return {}
    
    def get_scenarios_by_type(self, scenario_type: str) -> List[Dict[str, Any]]:
        """Get scenarios of a specific type"""
        return [s for s in self.scenarios if s["type"] == scenario_type]
    
    def get_all_scenarios(self) -> List[Dict[str, Any]]:
        """Get all available scenarios"""
        return self.scenarios.copy()
    
    def create_custom_scenario(self, name: str, target_services: List[str], 
                              failure_type: str, duration: int = 120) -> Dict[str, Any]:
        """Create a custom failure scenario"""
        scenario = {
            "id": f"custom_{int(time.time())}",
            "name": name,
            "type": "custom",
            "target_services": target_services,
            "failure_type": failure_type,
            "description": f"Custom scenario: {name}",
            "probability": 1.0,  # Custom scenarios always execute
            "duration": duration
        }
        
        self.scenarios.append(scenario)
        return scenario
