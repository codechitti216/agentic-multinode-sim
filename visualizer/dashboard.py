import streamlit as st
import time
import requests
import json
from datetime import datetime
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
from graph_state import GraphState
from config import SERVICES, REFRESH_INTERVAL, DASHBOARD_PORT
import os
from typing import Dict, List
import plotly.graph_objects as go
import plotly.express as px

class IncidentDashboard:
    def __init__(self):
        self.graph_state = GraphState()
        self.setup_page()
        
    def setup_page(self):
        """Setup the Streamlit page configuration"""
        st.set_page_config(
            page_title="Agentic Incident Simulator",
            page_icon="🚨",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🚨 Agentic Incident Simulation & Planning Framework")
        st.markdown("---")
    
    def run(self):
        """Run the main dashboard"""
        # Sidebar controls
        self.render_sidebar()
        
        # Main content - Single page with everything
        self.render_network_section()
        self.render_metrics_section()
        self.render_llm_section()
        self.render_commander_section()
        self.render_incident_section()
        self.render_analytics_section()
        
        # Auto-refresh every 5 seconds
        time.sleep(5)
        st.experimental_rerun()
    
    def render_sidebar(self):
        """Render the sidebar with all controls"""
        st.sidebar.header("🎛️ Control Panel")
        
        # Manual failure injection
        st.sidebar.subheader("💥 Manual Failure Injection")
        
        selected_service = st.sidebar.selectbox(
            "Select Service",
            list(SERVICES.keys()),
            format_func=lambda x: x.upper().replace("_", " ")
        )
        
        failure_type = st.sidebar.selectbox(
            "Failure Type",
            ["degraded", "down"]
        )
        
        duration = st.sidebar.slider(
            "Duration (seconds)",
            min_value=30,
            max_value=300,
            value=120
        )
        
        if st.sidebar.button("Inject Failure"):
            self.inject_manual_failure(selected_service, failure_type, duration)
        
        # Emergency controls
        st.sidebar.subheader("🚨 Emergency Controls")
        if st.sidebar.button("🧹 Clear All Failures"):
            self.clear_all_failures()
        
        if st.sidebar.button("🔄 Force All Healthy"):
            self.force_all_healthy()
        
        # Simulation controls
        st.sidebar.subheader("⚙️ Simulation Controls")
        if st.sidebar.button("⏸️ Pause Failure Injection"):
            self.pause_failure_injection()
        
        if st.sidebar.button("▶️ Resume Failure Injection"):
            self.resume_failure_injection()
        
        # Health check
        st.sidebar.subheader("🏥 Health Check")
        if st.sidebar.button("Check All Services"):
            self.check_all_services()
        
        # System status
        st.sidebar.subheader("📊 System Status")
        health_summary = self.graph_state.get_health_summary()
        
        st.sidebar.metric("Total Services", health_summary["total_services"])
        st.sidebar.metric("Healthy", health_summary["healthy"], delta=None)
        st.sidebar.metric("Degraded", health_summary["degraded"], delta=None)
        st.sidebar.metric("Down", health_summary["down"], delta=None)
        
        # Overall health indicator
        overall_health = health_summary["overall_health"]
        if overall_health == "healthy":
            st.sidebar.success("✅ System Healthy")
        elif overall_health == "degraded":
            st.sidebar.warning("⚠️ System Degraded")
        else:
            st.sidebar.error("🚨 System Critical")
    
    def render_network_section(self):
        """Render the compact network graph section"""
        st.subheader("🌐 Network Topology")
        
        # Get current network topology
        topology = self.graph_state.get_network_topology()
        
        # Create pyvis network (small size as requested)
        net = Network(height="300px", width="100%", bgcolor="#ffffff", font_color="#000000")
        net.set_options("""
        var options = {
            "nodes": {
                "font": {"size": 12, "face": "arial"},
                "borderWidth": 2,
                "shadow": true
            },
            "edges": {
                "color": {"color": "#666666", "highlight": "#ff0000"},
                "smooth": {"type": "continuous"}
            },
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.08
                },
                "maxVelocity": 50,
                "minVelocity": 0.1,
                "solver": "forceAtlas2Based",
                "timestep": 0.35
            }
        }
        """)
        
        # Add nodes
        for node in topology["nodes"]:
            net.add_node(
                node["id"],
                label=node["label"],
                title=node["title"],
                color=node["color"],
                size=node["size"]
            )
        
        # Add edges
        for edge in topology["edges"]:
            net.add_edge(
                edge["from"],
                edge["to"],
                title=edge["title"],
                color=edge["color"],
                width=edge["width"]
            )
        
        # Generate HTML and display
        html = net.generate_html()
        components.html(html, height=300)
        
        # Last update info
        last_update = datetime.fromtimestamp(topology["last_update"]).strftime("%H:%M:%S")
        st.caption(f"Last updated: {last_update}")
    
    def render_metrics_section(self):
        """Render service metrics in all formats"""
        st.subheader("📊 Service Metrics")
        
        # Get current service status
        service_status = self.graph_state.get_all_service_status()
        
        if service_status:
            # Create metrics dataframe
            metrics_data = []
            for service_name, status in service_status.items():
                metrics_data.append({
                    "Service": service_name.upper().replace("_", " "),
                    "Status": status.get("status", "unknown"),
                    "CPU %": status.get('cpu', 0),
                    "Memory %": status.get('memory', 0),
                    "Error Rate %": status.get('error_rate', 0)
                })
            
            df = pd.DataFrame(metrics_data)
            
            # Display as table
            st.write("**Service Status Table:**")
            st.dataframe(df, use_container_width=True)
            
            # Display as gauges
            st.write("**Service Health Gauges:**")
            cols = st.columns(len(metrics_data))
            for i, (_, row) in enumerate(df.iterrows()):
                with cols[i]:
                    # Create gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=row['CPU %'],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': row['Service']},
                        delta={'reference': 20},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 50], 'color': "lightgray"},
                                {'range': [50, 80], 'color': "yellow"},
                                {'range': [80, 100], 'color': "red"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ))
                    fig.update_layout(height=200)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Display as progress bars
            st.write("**Resource Usage Progress Bars:**")
            for _, row in df.iterrows():
                st.write(f"**{row['Service']}:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.progress(row['CPU %'] / 100, text=f"CPU: {row['CPU %']:.1f}%")
                with col2:
                    st.progress(row['Memory %'] / 100, text=f"Memory: {row['Memory %']:.1f}%")
                with col3:
                    st.progress(row['Error Rate %'] / 100, text=f"Errors: {row['Error Rate %']:.1f}%")
        else:
            st.info("No service metrics available")
    
    def render_llm_section(self):
        """Render LLM output and planning section"""
        st.subheader("🤖 AI Planning & LLM Output")
        
        try:
            # Get recent incident history to show LLM plans
            incident_history = self.get_incident_history()
            
            if incident_history:
                # Show most recent incident with LLM output
                latest_incident = incident_history[-1]
                
                st.write("**Latest Incident Response:**")
                st.write(f"**Type:** {latest_incident.get('type', 'Unknown')}")
                st.write(f"**Summary:** {latest_incident.get('summary', 'Unknown')}")
                
                if "response_plan" in latest_incident:
                    plan = latest_incident["response_plan"]
                    
                    # Show formatted plan
                    st.write("**📋 Formatted Response Plan:**")
                    st.write(f"**Plan ID:** {plan.get('incident_id', 'Unknown')}")
                    st.write(f"**Severity:** {plan.get('severity', 'Unknown')}")
                    st.write(f"**Estimated Time:** {plan.get('estimated_resolution_time', 'Unknown')}")
                    
                    # Show plan steps
                    if "steps" in plan:
                        st.write("**Steps:**")
                        for step in plan["steps"]:
                            st.write(f"  {step.get('step_id')}. {step.get('action')} → {step.get('target_service')}")
                    
                    # Show raw LLM output
                    st.write("**🔍 Raw LLM Output:**")
                    st.json(plan)
                else:
                    st.warning("No response plan available")
            else:
                st.info("No incidents recorded yet")
                
        except Exception as e:
            st.warning(f"⚠️ Cannot fetch incident history: {e}")
    
    def render_commander_section(self):
        """Render commander agent status section"""
        st.subheader("🎯 Incident Commander Status")
        
        try:
            commander_status = self.get_commander_status()
            
            if commander_status:
                # Commander running status
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Status", "🟢 Running" if commander_status.get("running") else "🔴 Stopped")
                    st.metric("Incidents Handled", commander_status.get("incidents_handled", 0))
                
                with col2:
                    st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))
                
                # Current incident
                if commander_status.get("current_incident"):
                    incident = commander_status["current_incident"]
                    st.error(f"🚨 ACTIVE INCIDENT: {incident.get('summary', 'Unknown')}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Type:** {incident.get('type', 'Unknown')}")
                    with col2:
                        st.write(f"**Severity:** {incident.get('severity', 'Unknown')}")
                    with col3:
                        st.write(f"**Affected:** {', '.join(incident.get('affected_services', []))}")
                else:
                    st.success("✅ No active incidents")
                
                # Service status overview
                if "service_status" in commander_status:
                    st.write("**Service Status Overview:**")
                    service_df = pd.DataFrame([
                        {
                            "Service": k.upper().replace("_", " "),
                            "Status": v.get("status", "unknown"),
                            "Last Check": datetime.fromtimestamp(v.get("timestamp", 0)).strftime("%H:%M:%S")
                        }
                        for k, v in commander_status["service_status"].items()
                    ])
                    st.dataframe(service_df, use_container_width=True)
            else:
                st.warning("⚠️ Cannot connect to incident commander")
                
        except Exception as e:
            st.warning(f"⚠️ Error fetching commander status: {e}")
    
    def render_incident_section(self):
        """Render incident monitoring and history section"""
        st.subheader("🚨 Incident Monitor & History")
        
        # Current incidents
        try:
            incident_history = self.get_incident_history()
            
            if incident_history:
                # Show recent incidents
                st.write("**Recent Incidents:**")
                for incident in incident_history[-5:]:  # Show last 5
                    with st.expander(f"{incident.get('type', 'Unknown')} - {incident.get('summary', 'Unknown')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Timestamp:** {datetime.fromtimestamp(incident.get('timestamp', 0)).strftime('%H:%M:%S')}")
                            st.write(f"**Severity:** {incident.get('severity', 'Unknown')}")
                            st.write(f"**Status:** {'Resolved' if incident.get('resolved_at') else 'Active'}")
                        
                        with col2:
                            if "response_plan" in incident:
                                plan = incident["response_plan"]
                                st.write(f"**Plan ID:** {plan.get('incident_id', 'Unknown')}")
                                st.write(f"**Steps:** {len(plan.get('steps', []))}")
                                st.write(f"**LLM Used:** {'Yes' if plan.get('llm_used') else 'No'}")
                        
                        # Show execution results if available
                        if "execution_result" in incident:
                            exec_result = incident["execution_result"]
                            st.write("**Execution Results:**")
                            st.write(f"  - Steps Executed: {exec_result.get('steps_executed', 0)}")
                            st.write(f"  - Successful: {exec_result.get('steps_successful', 0)}")
                            st.write(f"  - Failed: {exec_result.get('steps_failed', 0)}")
                            st.write(f"  - Total Time: {exec_result.get('execution_time', 0):.2f}s")
            else:
                st.info("No incidents recorded yet")
                
        except Exception as e:
            st.warning(f"⚠️ Cannot fetch incident history: {e}")
        
        # Failure history
        try:
            failure_history = self.get_failure_history()
            
            if failure_history:
                st.write("**Recent Failures:**")
                failure_df = pd.DataFrame(failure_history[:10])  # Show last 10
                if not failure_df.empty:
                    st.dataframe(
                        failure_df[['timestamp', 'scenario_name', 'type', 'status']],
                        use_container_width=True
                    )
            else:
                st.info("No failure history available")
                
        except Exception as e:
            st.warning(f"⚠️ Cannot fetch failure history: {e}")
    
    def render_analytics_section(self):
        """Render analytics and performance metrics"""
        st.subheader("📈 Analytics & Performance")
        
        try:
            # Get failure history for analytics
            failure_history = self.get_failure_history()
            
            if failure_history and len(failure_history) > 1:
                # Convert to DataFrame for analysis
                df = pd.DataFrame(failure_history)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Failure patterns over time
                st.write("**Failure Patterns Over Time:**")
                failure_counts = df.groupby(df['timestamp'].dt.date)['scenario_name'].count()
                st.line_chart(failure_counts)
                
                # Failure types distribution
                st.write("**Failure Types Distribution:**")
                type_counts = df['type'].value_counts()
                st.bar_chart(type_counts)
                
                # Service impact analysis
                st.write("**Service Impact Analysis:**")
                service_impact = {}
                for failure in failure_history:
                    services = failure.get('target_services', [])
                    if isinstance(services, str):
                        services = services.split(',')
                    for service in services:
                        if service not in service_impact:
                            service_impact[service] = 0
                        service_impact[service] += 1
                
                if service_impact:
                    impact_df = pd.DataFrame([
                        {"Service": k.upper().replace("_", " "), "Failures": v}
                        for k, v in service_impact.items()
                    ])
                    st.bar_chart(impact_df.set_index("Service"))
                
                # Recovery time analysis
                st.write("**Recovery Performance:**")
                recovered_failures = df[df['status'] == 'recovered']
                if not recovered_failures.empty:
                    st.write(f"Total Failures Recovered: {len(recovered_failures)}")
                    st.write(f"Recovery Success Rate: {len(recovered_failures)/len(df)*100:.1f}%")
            else:
                st.info("Not enough data for analytics yet")
                
        except Exception as e:
            st.warning(f"⚠️ Error generating analytics: {e}")
    
    # Helper methods for API calls
    def inject_manual_failure(self, service_name: str, failure_type: str, duration: int):
        """Inject a manual failure"""
        try:
            response = requests.post(
                "http://localhost:8006/inject_custom_failure",
                json={
                    "service_names": [service_name],
                    "failure_type": failure_type,
                    "duration": duration
                },
                timeout=10
            )
            
            if response.status_code == 200:
                st.success(f"✅ Failure injected into {service_name}")
            else:
                st.error(f"❌ Failed to inject failure: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Error injecting failure: {str(e)}")
    
    def clear_all_failures(self):
        """Clear all active failures"""
        try:
            response = requests.post("http://localhost:8006/clear_all_failures", timeout=10)
            
            if response.status_code == 200:
                st.success("✅ All failures cleared")
            else:
                st.error(f"❌ Failed to clear failures: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Error clearing failures: {str(e)}")
    
    def force_all_healthy(self):
        """Force all services to healthy state"""
        try:
            for service_name in SERVICES.keys():
                port = SERVICES[service_name]["port"]
                requests.post(f"http://localhost:{port}/recover", timeout=10)
            st.success("✅ All services forced to healthy")
        except Exception as e:
            st.error(f"❌ Error forcing services healthy: {str(e)}")
    
    def pause_failure_injection(self):
        """Pause automatic failure injection"""
        st.info("⏸️ Failure injection paused (feature to be implemented)")
    
    def resume_failure_injection(self):
        """Resume automatic failure injection"""
        st.info("▶️ Failure injection resumed (feature to be implemented)")
    
    def check_all_services(self):
        """Check health of all services"""
        try:
            all_status = {}
            for service_name, config in SERVICES.items():
                try:
                    port = config["port"]
                    response = requests.get(f"http://localhost:{port}/health", timeout=5)
                    if response.status_code == 200:
                        all_status[service_name] = response.json()
                    else:
                        all_status[service_name] = {"status": "unknown", "error": f"HTTP {response.status_code}"}
                except:
                    all_status[service_name] = {"status": "down", "error": "Connection failed"}
            
            # Update graph state
            self.graph_state.update_all_services(all_status)
            st.success("✅ Service health check completed")
            
        except Exception as e:
            st.error(f"❌ Error checking services: {str(e)}")
    
    def get_commander_status(self) -> Dict:
        """Get status from incident commander"""
        try:
            response = requests.get("http://localhost:8000/status", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {}
    
    def get_incident_history(self) -> List:
        """Get incident history from commander"""
        try:
            response = requests.get("http://localhost:8000/incident_history", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def get_failure_history(self) -> List:
        """Get failure history from injector"""
        try:
            response = requests.get("http://localhost:8006/failure_history", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []

def main():
    """Main function to run the dashboard"""
    dashboard = IncidentDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
