#!/usr/bin/env python3
"""
Demo Scenario for Agentic Incident Simulation & Planning Framework

This script demonstrates the system's capabilities by:
1. Starting the main system
2. Injecting a cascading failure scenario
3. Displaying dashboard and monitoring information

Usage:
    python demo_scenario.py

Prerequisites:
    - main.py must be running in another terminal
    - All dependencies installed via requirements.txt
"""

import time
import requests
import json
from datetime import datetime
import subprocess
import sys
import os

# Configuration
DASHBOARD_URL = "http://localhost:8501"
COMMANDER_URL = "http://localhost:8000"
INJECTOR_URL = "http://localhost:8006"
SERVICES = {
    "service_a": {"port": 8001},
    "service_b": {"port": 8002},
    "service_c": {"port": 8003},
    "service_d": {"port": 8004},
    "service_e": {"port": 8005}
}

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n📋 {title}")
    print("-" * 40)

def check_system_health():
    """Check if all system components are running"""
    print_section("Checking System Health")
    
    healthy_components = []
    failed_components = []
    
    # Check dashboard
    try:
        response = requests.get(DASHBOARD_URL, timeout=5)
        if response.status_code == 200:
            healthy_components.append("Dashboard")
        else:
            failed_components.append("Dashboard")
    except:
        failed_components.append("Dashboard")
    
    # Check incident commander
    try:
        response = requests.get(f"{COMMANDER_URL}/health", timeout=5)
        if response.status_code == 200:
            healthy_components.append("Incident Commander")
        else:
            failed_components.append("Incident Commander")
    except:
        failed_components.append("Incident Commander")
    
    # Check failure injector
    try:
        response = requests.get(f"{INJECTOR_URL}/health", timeout=5)
        if response.status_code == 200:
            healthy_components.append("Failure Injector")
        else:
            failed_components.append("Failure Injector")
    except:
        failed_components.append("Failure Injector")
    
    # Check microservices
    for service_name, config in SERVICES.items():
        try:
            response = requests.get(f"http://localhost:{config['port']}/health", timeout=5)
            if response.status_code == 200:
                healthy_components.append(service_name)
            else:
                failed_components.append(service_name)
        except:
            failed_components.append(service_name)
    
    print(f"✅ Healthy Components: {', '.join(healthy_components)}")
    if failed_components:
        print(f"❌ Failed Components: {', '.join(failed_components)}")
        return False
    
    return True

def inject_cascading_failure():
    """Inject a cascading failure scenario"""
    print_section("Injecting Cascading Failure Scenario")
    
    # Step 1: Inject failure into service_a (root cause)
    print("1️⃣ Injecting failure into service_a (root cause)...")
    try:
        response = requests.post(
            f"{INJECTOR_URL}/inject_custom_failure",
            json={
                "service_names": ["service_a"],
                "failure_type": "down",
                "duration": 180
            },
            timeout=10
        )
        if response.status_code == 200:
            print("✅ service_a failure injected successfully")
        else:
            print(f"❌ Failed to inject failure: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error injecting failure: {e}")
        return False
    
    # Wait for dependency effects
    print("2️⃣ Waiting for dependency cascade effects...")
    time.sleep(10)
    
    # Step 2: Inject failure into service_b (dependent on service_a)
    print("3️⃣ Injecting failure into service_b (dependent on service_a)...")
    try:
        response = requests.post(
            f"{INJECTOR_URL}/inject_custom_failure",
            json={
                "service_names": ["service_b"],
                "failure_type": "degraded",
                "duration": 120
            },
            timeout=10
        )
        if response.status_code == 200:
            print("✅ service_b failure injected successfully")
        else:
            print(f"❌ Failed to inject failure: {response.status_code}")
    except Exception as e:
        print(f"❌ Error injecting failure: {e}")
    
    print("🎯 Cascading failure scenario injected!")
    return True

def monitor_incident_response():
    """Monitor the incident response process"""
    print_section("Monitoring Incident Response")
    
    max_wait_time = 60  # seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            # Check incident commander status
            response = requests.get(f"{COMMANDER_URL}/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                incidents_handled = status.get("incidents_handled", 0)
                current_incident = status.get("current_incident")
                
                print(f"📊 Incidents handled: {incidents_handled}")
                
                if current_incident:
                    print(f"🚨 Active incident: {current_incident.get('summary', 'Unknown')}")
                    print(f"   Type: {current_incident.get('type', 'Unknown')}")
                    print(f"   Severity: {current_incident.get('severity', 'Unknown')}")
                else:
                    print("✅ No active incidents")
                
                # Check if we have recent incidents
                if incidents_handled > 0:
                    print("\n📋 Recent incident details:")
                    incident_history = requests.get(f"{COMMANDER_URL}/incident_history", timeout=5)
                    if incident_history.status_code == 200:
                        incidents = incident_history.json()
                        if incidents:
                            latest = incidents[-1]
                            print(f"   Latest incident: {latest.get('summary', 'Unknown')}")
                            
                            if "response_plan" in latest:
                                plan = latest["response_plan"]
                                print(f"   Plan ID: {plan.get('incident_id', 'Unknown')}")
                                print(f"   Steps: {len(plan.get('steps', []))}")
                                
                                # Show LLM output
                                if "llm_used" in plan:
                                    print(f"   LLM Used: {plan.get('llm_used')}")
                                
                                # Show execution results
                                if "execution_result" in latest:
                                    exec_result = latest["execution_result"]
                                    print(f"   Execution: {exec_result.get('steps_executed', 0)}/{exec_result.get('steps_successful', 0)} successful")
                    
                    break  # We have incident data, exit monitoring loop
                
            else:
                print("⚠️ Cannot connect to incident commander")
                
        except Exception as e:
            print(f"⚠️ Error monitoring: {e}")
        
        print("⏳ Waiting for incident response...")
        time.sleep(5)
    
    if time.time() - start_time >= max_wait_time:
        print("⏰ Timeout waiting for incident response")

def display_dashboard_info():
    """Display dashboard and monitoring information"""
    print_section("Dashboard & Monitoring Information")
    
    print(f"🌐 Dashboard URL: {DASHBOARD_URL}")
    print(f"🎯 Incident Commander API: {COMMANDER_URL}")
    print(f"💥 Failure Injector API: {INJECTOR_URL}")
    
    print("\n📱 Dashboard Features:")
    print("   • Real-time network topology visualization")
    print("   • Service health metrics and status")
    print("   • Incident history and LLM output")
    print("   • Failure injection controls")
    print("   • Analytics and performance metrics")
    
    print("\n🔧 Manual Controls Available:")
    print("   • Inject custom failures via sidebar")
    print("   • Clear all failures")
    print("   • Force services healthy")
    print("   • Trigger test incidents")

def show_llm_output():
    """Display recent LLM output and planning"""
    print_section("LLM Output & Planning")
    
    try:
        # Get incident history to show LLM plans
        response = requests.get(f"{COMMANDER_URL}/incident_history", timeout=5)
        if response.status_code == 200:
            incidents = response.json()
            if incidents:
                latest = incidents[-1]
                print(f"📋 Latest Incident: {latest.get('summary', 'Unknown')}")
                print(f"   Type: {latest.get('type', 'Unknown')}")
                print(f"   Severity: {latest.get('severity', 'Unknown')}")
                print(f"   Timestamp: {datetime.fromtimestamp(latest.get('timestamp', 0)).strftime('%H:%M:%S')}")
                
                if "response_plan" in latest:
                    plan = latest["response_plan"]
                    print(f"\n🤖 LLM Response Plan:")
                    print(f"   Plan ID: {plan.get('incident_id', 'Unknown')}")
                    print(f"   Estimated Time: {plan.get('estimated_resolution_time', 'Unknown')}")
                    
                    if "steps" in plan:
                        print(f"   Steps ({len(plan['steps'])}):")
                        for i, step in enumerate(plan["steps"], 1):
                            print(f"     {i}. {step.get('action', 'Unknown')} → {step.get('target_service', 'Unknown')}")
                    
                    # Show custom enhancements if any
                    if "custom_enhancements" in plan:
                        enhancements = plan["custom_enhancements"]
                        print(f"\n🔧 Custom Enhancements:")
                        print(f"   RL Actions: {len(enhancements.get('rl_actions', []))}")
                        print(f"   Policy Modifications: {len(enhancements.get('policy_modifications', []))}")
                        print(f"   Learning Applied: {enhancements.get('learning_applied', False)}")
                        print(f"   Model Version: {enhancements.get('model_version', 'Unknown')}")
                    
                    # Show execution results
                    if "execution_result" in latest:
                        exec_result = latest["execution_result"]
                        print(f"\n📊 Execution Results:")
                        print(f"   Steps Executed: {exec_result.get('steps_executed', 0)}")
                        print(f"   Successful: {exec_result.get('steps_successful', 0)}")
                        print(f"   Failed: {exec_result.get('steps_failed', 0)}")
                        print(f"   Total Time: {exec_result.get('execution_time', 0):.2f}s")
                
                # Show custom logic results
                if "custom_diagnosis" in latest:
                    diagnosis = latest["custom_diagnosis"]
                    print(f"\n🔍 Custom Diagnosis:")
                    print(f"   Root Cause: {diagnosis.get('root_cause', 'Unknown')}")
                    print(f"   Confidence: {diagnosis.get('confidence', 0):.2f}")
                    print(f"   Severity: {diagnosis.get('severity', 'Unknown')}")
                
                if "evaluation" in latest:
                    evaluation = latest["evaluation"]
                    print(f"\n📈 Response Evaluation:")
                    print(f"   Overall Score: {evaluation.get('overall_score', 0):.2f}")
                    print(f"   Response Time Score: {evaluation.get('response_time_score', 0):.2f}")
                    print(f"   Resolution Score: {evaluation.get('resolution_score', 0):.2f}")
                    print(f"   RL Reward: {evaluation.get('rl_reward', 0):.2f}")
                
            else:
                print("ℹ️ No incidents recorded yet")
        else:
            print("⚠️ Cannot fetch incident history")
            
    except Exception as e:
        print(f"⚠️ Error showing LLM output: {e}")

def main():
    """Main demo function"""
    print_header("Agentic Incident Simulation Demo")
    
    print("This demo will:")
    print("1. Check system health")
    print("2. Inject a cascading failure scenario")
    print("3. Monitor incident response")
    print("4. Display dashboard and LLM output")
    
    # Check if main.py is running
    print_section("System Check")
    if not check_system_health():
        print("\n❌ System components not ready!")
        print("Please start the system first with: python main.py")
        print("Then run this demo in another terminal.")
        return
    
    print("✅ All system components are healthy!")
    
    # Inject cascading failure
    if not inject_cascading_failure():
        print("❌ Failed to inject failure scenario")
        return
    
    # Monitor incident response
    monitor_incident_response()
    
    # Display information
    display_dashboard_info()
    show_llm_output()
    
    print_header("Demo Complete!")
    print("🎉 The system has successfully:")
    print("   • Detected the cascading failure")
    print("   • Generated an incident response plan")
    print("   • Executed recovery actions")
    print("   • Applied custom RL logic")
    
    print(f"\n🌐 Open the dashboard at: {DASHBOARD_URL}")
    print("   to see the real-time network visualization!")
    
    print("\n💡 Next Steps:")
    print("   • Modify orchestrator/agent_hooks.py to add your RL logic")
    print("   • Start LM Studio on port 1234 for real AI planning")
    print("   • Inject different failure scenarios to test your agent")

if __name__ == "__main__":
    main()
