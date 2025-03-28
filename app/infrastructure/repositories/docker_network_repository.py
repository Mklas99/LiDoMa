from typing import List, Optional, Dict
from app.domain.models import Network
from app.domain.repositories import NetworkRepository
from app.infrastructure.docker_client import DockerClient, DockerCommandExecutor
import json

class DockerNetworkRepository(NetworkRepository):
    """Implementation of NetworkRepository using Docker SDK and CLI."""
    
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
    
    def list_networks(self, context: str = "default") -> List[Network]:
        """List all networks."""
        if context != "default":
            return self._get_networks_for_context(context)
            
        try:
            if not self.docker_client or not self.docker_client.client:
                return []
                
            networks = self.docker_client.client.networks.list()
            result = []
            
            for net in networks:
                # Get containers
                container_ids = list(net.attrs.get('Containers', {}).keys())
                
                # Get subnet and gateway
                ipam_config = net.attrs.get('IPAM', {}).get('Config', [{}])
                subnet = ipam_config[0].get('Subnet', '') if ipam_config else ''
                gateway = ipam_config[0].get('Gateway', '') if ipam_config else ''
                
                network = Network(
                    id=net.id,
                    name=net.name,
                    driver=net.attrs.get('Driver', ''),
                    scope=net.attrs.get('Scope', ''),
                    subnet=subnet,
                    gateway=gateway,
                    containers=container_ids,
                    labels=net.attrs.get('Labels', {}),
                    context="default"
                )
                result.append(network)
            
            return result
        except Exception as e:
            print(f"Error listing networks: {str(e)}")
            return []
        
    def get_network(self, network_id: str, context: str = "default") -> Optional[Network]:
        """Get a specific network by ID."""
        try:
            if not self.docker_client or not self.docker_client.client:
                return None
                
            net = self.docker_client.client.networks.get(network_id)
            if not net:
                return None
                
            # Get containers
            container_ids = list(net.attrs.get('Containers', {}).keys())
            
            # Get subnet and gateway
            ipam_config = net.attrs.get('IPAM', {}).get('Config', [{}])
            subnet = ipam_config[0].get('Subnet', '') if ipam_config else ''
            gateway = ipam_config[0].get('Gateway', '') if ipam_config else ''
            
            return Network(
                id=net.id,
                name=net.name,
                driver=net.attrs.get('Driver', ''),
                scope=net.attrs.get('Scope', ''),
                subnet=subnet,
                gateway=gateway,
                containers=container_ids,
                labels=net.attrs.get('Labels', {}),
                context=context
            )
        except Exception as e:
            print(f"Error getting network: {str(e)}")
            return None
        
    def remove_network(self, network_id: str, context: str = "default") -> bool:
        """Remove a network."""
        try:
            if not self.docker_client or not self.docker_client.client:
                return False
                
            self.docker_client.client.networks.get(network_id).remove()
            return True
        except Exception as e:
            print(f"Error removing network: {str(e)}")
            return False
        
    def create_network(self, name: str, driver: str = "bridge", context: str = "default", **kwargs) -> bool:
        """Create a new network."""
        try:
            if not self.docker_client or not self.docker_client.client:
                return False
                
            self.docker_client.client.networks.create(
                name=name,
                driver=driver,
                options=kwargs.get('options', {}),
                labels=kwargs.get('labels', {})
            )
            return True
        except Exception as e:
            print(f"Error creating network: {str(e)}")
            return False
            
    def _get_networks_for_context(self, context: str) -> List[Network]:
        """Get networks for a specific Docker context using CLI."""
        output, err = DockerCommandExecutor.run_command([
            "docker", "--context", context, "network", "ls", "--format", "{{json .}}"
        ])
        
        networks = []
        if err:
            return networks
            
        if output:
            for line in output.splitlines():
                try:
                    data = json.loads(line)
                    network_id = data.get('ID', '')
                    name = data.get('Name', '')
                    driver = data.get('Driver', '')
                    scope = data.get('Scope', '')
                    
                    # Get more details
                    detail_output, detail_err = DockerCommandExecutor.run_command([
                        "docker", "--context", context, "network", "inspect", network_id
                    ])
                    
                    subnet = ""
                    gateway = ""
                    containers = []
                    labels = {}
                    
                    if not detail_err and detail_output:
                        try:
                            network_data = json.loads(detail_output)[0]
                            ipam_config = network_data.get('IPAM', {}).get('Config', [{}])
                            subnet = ipam_config[0].get('Subnet', '') if ipam_config else ''
                            gateway = ipam_config[0].get('Gateway', '') if ipam_config else ''
                            containers = list(network_data.get('Containers', {}).keys())
                            labels = network_data.get('Labels', {})
                        except (json.JSONDecodeError, IndexError):
                            pass
                    
                    networks.append(Network(
                        id=network_id,
                        name=name,
                        driver=driver,
                        scope=scope,
                        subnet=subnet,
                        gateway=gateway,
                        containers=containers,
                        labels=labels,
                        context=context
                    ))
                except json.JSONDecodeError:
                    continue
                    
        return networks
