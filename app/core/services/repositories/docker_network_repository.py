from typing import List, Optional
import json

from domain.models import Network
from domain.repositories import NetworkRepository
from infrastructure.docker_client import DockerClient, DockerCommandExecutor

class DockerNetworkRepository(NetworkRepository):
    """Implementation of NetworkRepository using Docker SDK and CLI."""
    
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
        
    def list_networks(self, context: str = "default") -> List[Network]:
        """List all networks."""
        if context != "default":
            return self._get_networks_for_context(context)
            
        try:
            networks_data = self.docker_client.client.networks.list()
            result = []
            
            for net in networks_data:
                result.append(Network(
                    name=net.name,
                    id=net.short_id,
                    driver=net.attrs.get("Driver", "bridge"),
                    scope=net.attrs.get("Scope", "local"),
                    context="default"
                ))
                
            return result
        except Exception as e:
            print(f"Error listing networks: {e}")
            return []
            
    def _get_networks_for_context(self, context: str) -> List[Network]:
        """Get networks for a specific Docker context."""
        output, err = DockerCommandExecutor.run_command([
            "docker", "--context", context, "network", "ls", 
            "--format", "{{.ID}}\t{{.Name}}\t{{.Driver}}\t{{.Scope}}"
        ])
        
        networks = []
        if err:
            return networks
            
        if output:
            for line in output.splitlines():
                try:
                    parts = line.split("\t")
                    if len(parts) >= 4:
                        network_id, name, driver, scope = parts[0], parts[1], parts[2], parts[3]
                        
                        networks.append(Network(
                            name=name,
                            id=network_id,
                            driver=driver,
                            scope=scope,
                            context=context
                        ))
                except ValueError:
                    continue
                    
        return networks
    
    def get_network(self, network_id: str, context: str = "default") -> Optional[Network]:
        """Get a specific network by ID or name."""
        if context != "default":
            # Use CLI for non-default contexts
            networks = self._get_networks_for_context(context)
            for network in networks:
                if network.id == network_id or network.name == network_id:
                    return network
            return None
            
        try:
            net = self.docker_client.client.networks.get(network_id)
            return Network(
                name=net.name,
                id=net.short_id,
                driver=net.attrs.get("Driver", "bridge"),
                scope=net.attrs.get("Scope", "local"),
                context="default"
            )
        except Exception as e:
            print(f"Error getting network: {e}")
            return None
            
    def remove_network(self, network_id: str, context: str = "default") -> bool:
        """Remove a network."""
        if context != "default":
            # Use CLI for non-default contexts
            _, err = DockerCommandExecutor.run_command(["docker", "--context", context, "network", "rm", network_id])
            return not err
            
        try:
            network = self.docker_client.client.networks.get(network_id)
            network.remove()
            return True
        except Exception as e:
            print(f"Failed to remove network '{network_id}': {e}")
            return False
            
    def create_network(self, name: str, driver: str = "bridge", context: str = "default") -> bool:
        """Create a new network."""
        if context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "network", "create"]
            if driver and driver != "bridge":
                cmd.extend(["--driver", driver])
            cmd.append(name)
            _, err = DockerCommandExecutor.run_command(cmd)
            return not err
            
        try:
            self.docker_client.client.networks.create(name=name, driver=driver)
            return True
        except Exception as e:
            print(f"Failed to create network '{name}': {e}")
            return False
