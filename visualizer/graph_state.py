from typing import Dict, Any, List, Tuple
import networkx as nx
from config import SERVICES, STATUS_COLORS
import time

class GraphState:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.service_status = {}
        self.last_update = 0
        self._build_graph()
    
    def _build_graph(self):
        """Build the initial network graph from service configuration"""
        # Add nodes (services)
        for service_name in SERVICES.keys():
            self.graph.add_node(service_name, 
                              status="healthy", 
                              cpu=20.0, 
                              memory=30.0, 
                              error_rate=0.0)
        
        # Add edges (dependencies)
        for service_name, config in SERVICES.items():
            for dependency in config.get("dependencies", []):
                if dependency in SERVICES:
                    self.graph.add_edge(dependency, service_name, 
                                      type="dependency", 
                                      weight=1)
    
    def update_service_status(self, service_name: str, status_data: Dict[str, Any]):
        """Update the status of a specific service"""
        if service_name in self.graph:
            # Update node attributes
            self.graph.nodes[service_name].update({
                "status": status_data.get("status", "unknown"),
                "cpu": status_data.get("cpu", 0.0),
                "memory": status_data.get("memory", 0.0),
                "error_rate": status_data.get("error_rate", 0.0),
                "last_update": time.time()
            })
            
            # Update service status cache
            self.service_status[service_name] = status_data
            self.last_update = time.time()
    
    def update_all_services(self, all_status: Dict[str, Any]):
        """Update status of all services at once"""
        for service_name, status_data in all_status.items():
            self.update_service_status(service_name, status_data)
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get current status of a specific service"""
        if service_name in self.graph:
            node_data = self.graph.nodes[service_name]
            return {
                "status": node_data.get("status", "unknown"),
                "cpu": node_data.get("cpu", 0.0),
                "memory": node_data.get("memory", 0.0),
                "error_rate": node_data.get("error_rate", 0.0),
                "last_update": node_data.get("last_update", 0)
            }
        return {}
    
    def get_all_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        return self.service_status.copy()
    
    def get_network_topology(self) -> Dict[str, Any]:
        """Get the complete network topology for visualization with cascading failure effects"""
        nodes = []
        edges = []
        
        # Process nodes
        for node, data in self.graph.nodes(data=True):
            status = data.get("status", "unknown")
            nodes.append({
                "id": node,
                "label": node.upper().replace("_", " "),
                "status": status,
                "color": STATUS_COLORS.get(status, "#888888"),
                "cpu": data.get("cpu", 0.0),
                "memory": data.get("memory", 0.0),
                "error_rate": data.get("error_rate", 0.0),
                "size": self._get_node_size(status),
                "title": self._get_node_tooltip(node, data)
            })
        
        # Process edges with cascading failure visualization
        for source, target, data in self.graph.edges(data=True):
            # Get source service status for edge styling
            source_status = self.graph.nodes[source].get("status", "unknown")
            target_status = self.graph.nodes[target].get("status", "unknown")
            
            # Edge styling based on dependency health and cascading effects
            if source_status == "down":
                edge_color = "#ff0000"  # Red for broken dependencies
                edge_width = 4
                edge_title = f"BROKEN: {source} ({source_status}) → {target} ({target_status})"
            elif source_status == "degraded":
                edge_color = "#ff8800"  # Orange for degraded dependencies
                edge_width = 3
                edge_title = f"DEGRADED: {source} ({source_status}) → {target} ({target_status})"
            else:
                edge_color = "#666666"  # Gray for healthy dependencies
                edge_width = 2
                edge_title = f"Healthy: {source} ({source_status}) → {target} ({target_status})"
            
            edges.append({
                "from": source,
                "to": target,
                "arrows": "to",
                "color": edge_color,
                "width": edge_width,
                "title": edge_title
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "last_update": self.last_update
        }
    
    def _get_node_size(self, status: str) -> int:
        """Get node size based on status"""
        if status == "down":
            return 30
        elif status == "degraded":
            return 25
        else:
            return 20
    
    def _get_node_tooltip(self, service_name: str, data: Dict[str, Any]) -> str:
        """Generate tooltip for a node"""
        status = data.get("status", "unknown")
        cpu = data.get("cpu", 0.0)
        memory = data.get("memory", 0.0)
        error_rate = data.get("error_rate", 0.0)
        
        tooltip = f"""
        <b>{service_name.upper()}</b><br>
        Status: {status}<br>
        CPU: {cpu:.1f}%<br>
        Memory: {memory:.1f}%<br>
        Error Rate: {error_rate:.1f}%
        """
        
        # Add dependency information
        dependencies = SERVICES.get(service_name, {}).get("dependencies", [])
        if dependencies:
            tooltip += f"<br>Dependencies: {', '.join(dependencies)}"
        
        return tooltip
    
    def get_affected_services(self, service_name: str) -> List[str]:
        """Get all services affected by a service failure (downstream)"""
        if service_name not in self.graph:
            return []
        
        # Find all reachable nodes from the failed service
        affected = set()
        for node in nx.descendants(self.graph, service_name):
            affected.add(node)
        
        return list(affected)
    
    def get_root_cause_services(self, service_name: str) -> List[str]:
        """Get all services that could be root cause for a service failure (upstream)"""
        if service_name not in self.graph:
            return []
        
        # Find all nodes that can reach the failed service
        root_causes = set()
        for node in nx.ancestors(self.graph, service_name):
            root_causes.add(node)
        
        return list(root_causes)
    
    def get_dependency_chain(self, service_name: str) -> List[str]:
        """Get the dependency chain for a service"""
        if service_name not in self.graph:
            return []
        
        # Get all dependencies in topological order
        try:
            dependencies = list(nx.topological_sort(self.graph))
            # Filter to only include dependencies of the target service
            service_deps = []
            for dep in dependencies:
                if dep in nx.ancestors(self.graph, service_name):
                    service_deps.append(dep)
            return service_deps
        except nx.NetworkXError:
            # Graph has cycles, return empty list
            return []
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary of the network"""
        total_services = len(self.graph.nodes)
        healthy_count = 0
        degraded_count = 0
        down_count = 0
        
        for node, data in self.graph.nodes(data=True):
            status = data.get("status", "unknown")
            if status == "healthy":
                healthy_count += 1
            elif status == "degraded":
                degraded_count += 1
            elif status == "down":
                down_count += 1
        
        return {
            "total_services": total_services,
            "healthy": healthy_count,
            "degraded": degraded_count,
            "down": down_count,
            "overall_health": "healthy" if down_count == 0 and degraded_count == 0 else "degraded" if down_count == 0 else "critical"
        }
    
    def get_critical_paths(self) -> List[List[str]]:
        """Get critical dependency paths in the network"""
        critical_paths = []
        
        # Find all paths between services
        for source in self.graph.nodes():
            for target in self.graph.nodes():
                if source != target:
                    try:
                        paths = list(nx.all_simple_paths(self.graph, source, target))
                        # Keep only the longest paths (most critical)
                        if paths:
                            longest_path = max(paths, key=len)
                            if len(longest_path) > 2:  # Only paths with more than 2 nodes
                                critical_paths.append(longest_path)
                    except nx.NetworkXError:
                        continue
        
        # Remove duplicates and sort by length
        unique_paths = []
        for path in critical_paths:
            if path not in unique_paths:
                unique_paths.append(path)
        
        return sorted(unique_paths, key=len, reverse=True)
    
    def is_graph_healthy(self) -> bool:
        """Check if the entire network graph is healthy"""
        health_summary = self.get_health_summary()
        return health_summary["overall_health"] == "healthy"
    
    def get_last_update_time(self) -> float:
        """Get timestamp of last update"""
        return self.last_update
