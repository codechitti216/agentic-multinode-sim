#!/usr/bin/env python3
"""
Test script for the Agentic Incident Simulation Framework
Run this to verify all components are working correctly
"""

import sys
import os
import time
import requests
import json

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SERVICES
from visualizer.graph_state import GraphState
from failures.failure_scenarios import FailureScenarios

def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    
    try:
        from config import SERVICES, LLM_ENDPOINT, DASHBOARD_PORT
        print(f"✅ Configuration loaded successfully")
        print(f"   Services: {len(SERVICES)} configured")
        print(f"   LLM Endpoint: {LLM_ENDPOINT}")
        print(f"   Dashboard Port: {DASHBOARD_PORT}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_graph_state():
    """Test graph state management"""
    print("\n🌐 Testing graph state...")
    
    try:
        graph_state = GraphState()
        
        # Test basic functionality
        topology = graph_state.get_network_topology()
        health_summary = graph_state.get_health_summary()
        
        print(f"✅ Graph state initialized successfully")
        print(f"   Nodes: {len(topology['nodes'])}")
        print(f"   Edges: {len(topology['edges'])}")
        print(f"   Health: {health_summary['overall_health']}")
        return True
    except Exception as e:
        print(f"❌ Graph state error: {e}")
        return False

def test_failure_scenarios():
    """Test failure scenario generation"""
    print("\n💥 Testing failure scenarios...")
    
    try:
        scenarios = FailureScenarios()
        all_scenarios = scenarios.get_all_scenarios()
        random_scenario = scenarios.get_random_scenario()
        
        print(f"✅ Failure scenarios generated successfully")
        print(f"   Total scenarios: {len(all_scenarios)}")
        print(f"   Random scenario: {random_scenario.get('name', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Failure scenarios error: {e}")
        return False

def test_service_ports():
    """Test if service ports are available"""
    print("\n🔌 Testing service ports...")
    
    available_ports = []
    for service_name, config in SERVICES.items():
        port = config["port"]
        try:
            # Try to bind to the port to see if it's available
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            available_ports.append(service_name)
        except:
            print(f"   ⚠️ Port {port} ({service_name}) is not available")
    
    if available_ports:
        print(f"✅ Available ports: {', '.join(available_ports)}")
        return True
    else:
        print("❌ No service ports are available")
        return False

def test_llm_connection():
    """Test LLM connection (if LM Studio is running)"""
    print("\n🤖 Testing LLM connection...")
    
    try:
        from config import LLM_ENDPOINT
        response = requests.get(LLM_ENDPOINT.replace("/v1/chat/completions", ""), timeout=5)
        
        if response.status_code == 200:
            print("✅ LLM connection successful")
            return True
        else:
            print(f"⚠️ LLM endpoint responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️ LLM not accessible (LM Studio may not be running)")
        print("   This is expected if LM Studio is not started")
        return True  # Not a critical failure
    except Exception as e:
        print(f"❌ LLM connection error: {e}")
        return False

def test_dependencies():
    """Test if all required packages are available"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'pyvis', 
        'networkx', 'pandas', 'requests', 'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are available")
        return True

def main():
    """Run all tests"""
    print("🧪 Testing Agentic Incident Simulation Framework")
    print("=" * 60)
    
    tests = [
        test_dependencies,
        test_config,
        test_graph_state,
        test_failure_scenarios,
        test_service_ports,
        test_llm_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to run.")
        print("\n🚀 To start the system, run:")
        print("   python main.py")
    else:
        print("⚠️ Some tests failed. Please fix the issues before running.")
        print("\n💡 Common solutions:")
        print("   - Install dependencies: pip install -r requirements.txt")
        print("   - Check if ports 8001-8005 are available")
        print("   - Start LM Studio if you want LLM features")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
