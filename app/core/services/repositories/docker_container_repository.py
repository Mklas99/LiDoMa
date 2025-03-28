from typing import List, Optional, Dict, Any
import json
from datetime import datetime

from domain.models import Container, Port
from domain.repositories import ContainerRepository
from infrastructure.docker_client import DockerClient, DockerCommandExecutor

class DockerContainerRepository(ContainerRepository):
    """Implementation of ContainerRepository using Docker SDK and CLI."""
    
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
        
    def list_containers(self, all_containers: bool = True, context: str = "default") -> List[Container]:
        """List all containers."""
        if context != "default":
            return self._get_containers_for_context(context)
            
        try:
            containers = self.docker_client.client.containers.list(all=all_containers)
            result = []
            
            for c in containers:
                ports = []
                ports_dict = c.attrs.get("NetworkSettings", {}).get("Ports", {})
                
                for container_port, host_bindings in ports_dict.items():
                    if host_bindings:
                        for binding in host_bindings:
                            ports.append(Port(
                                container_port=container_port,
                                host_port=binding.get("HostPort"),
                                host_ip=binding.get("HostIp", "0.0.0.0")
                            ))
                    else:
                        ports.append(Port(container_port=container_port))
                        
                result.append(Container(
                    id=c.short_id,
                    name=c.name,
                    status=c.status,
                    image=c.image.tags[0] if c.image.tags else c.image.short_id,
                    ports=ports,
                    context="default"
                ))
                
            return result
        except Exception as e:
            print(f"Error listing containers: {e}")
            return []
            
    def _get_containers_for_context(self, context: str) -> List[Container]:
        """Get containers for a specific Docker context."""
        output, err = DockerCommandExecutor.run_command([
            "docker", "--context", context, "ps", "-a", 
            "--format", "{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}"
        ])
        
        containers = []
        if err:
            return containers
            
        if output:
            for line in output.splitlines():
                try:
                    parts = line.split("\t")
                    if len(parts) >= 4:
                        cid, name, status, image = parts[0], parts[1], parts[2], parts[3]
                        containers.append(Container(
                            id=cid,
                            name=name,
                            status=status,
                            image=image,
                            context=context
                        ))
                except ValueError:
                    continue
                    
        return containers
    
    def get_container(self, container_id: str, context: str = "default") -> Optional[Container]:
        """Get a specific container by ID or name."""
        if context != "default":
            # Use CLI for non-default contexts
            containers = self._get_containers_for_context(context)
            for container in containers:
                if container.id == container_id or container.name == container_id:
                    return container
            return None
            
        try:
            c = self.docker_client.client.containers.get(container_id)
            
            ports = []
            ports_dict = c.attrs.get("NetworkSettings", {}).get("Ports", {})
            for container_port, host_bindings in ports_dict.items():
                if host_bindings:
                    for binding in host_bindings:
                        ports.append(Port(
                            container_port=container_port,
                            host_port=binding.get("HostPort"),
                            host_ip=binding.get("HostIp", "0.0.0.0")
                        ))
                else:
                    ports.append(Port(container_port=container_port))
                    
            return Container(
                id=c.short_id,
                name=c.name,
                status=c.status,
                image=c.image.tags[0] if c.image.tags else c.image.short_id,
                ports=ports,
                context="default"
            )
        except Exception as e:
            print(f"Error getting container: {e}")
            return None
            
    def start_container(self, container_id: str, context: str = "default") -> bool:
        """Start a container."""
        if context != "default":
            # Use CLI for non-default contexts
            _, err = DockerCommandExecutor.run_command(["docker", "--context", context, "start", container_id])
            return not err
            
        try:
            container = self.docker_client.client.containers.get(container_id)
            container.start()
            return True
        except Exception as e:
            print(f"Failed to start container '{container_id}': {e}")
            return False
            
    def stop_container(self, container_id: str, context: str = "default") -> bool:
        """Stop a container."""
        if context != "default":
            # Use CLI for non-default contexts
            _, err = DockerCommandExecutor.run_command(["docker", "--context", context, "stop", container_id])
            return not err
            
        try:
            container = self.docker_client.client.containers.get(container_id)
            container.stop()
            return True
        except Exception as e:
            print(f"Failed to stop container '{container_id}': {e}")
            return False
            
    def remove_container(self, container_id: str, context: str = "default") -> bool:
        """Remove a container."""
        if context != "default":
            # Use CLI for non-default contexts
            _, err = DockerCommandExecutor.run_command(["docker", "--context", context, "rm", container_id])
            return not err
            
        try:
            container = self.docker_client.client.containers.get(container_id)
            container.remove(force=True)
            return True
        except Exception as e:
            print(f"Error removing container '{container_id}': {e}")
            return False
            
    def create_container(self, image_id: str, name: Optional[str] = None, 
                        context: str = "default", **kwargs) -> bool:
        """Create a new container."""
        if context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "create"]
            if name:
                cmd.extend(["--name", name])
                
            # Add additional parameters
            for key, value in kwargs.items():
                if key == "ports":
                    for port_mapping in value:
                        cmd.extend(["-p", port_mapping])
                elif key == "environment":
                    for env_var in value:
                        cmd.extend(["-e", env_var])
                elif key == "volumes":
                    for volume in value:
                        cmd.extend(["-v", volume])
                        
            cmd.append(image_id)
            _, err = DockerCommandExecutor.run_command(cmd)
            return not err
            
        try:
            self.docker_client.client.containers.create(image=image_id, name=name, **kwargs)
            return True
        except Exception as e:
            print(f"Failed to create container from '{image_id}': {e}")
            return False
            
    def get_container_details(self, container_id: str, context: str = "default") -> Dict[str, Any]:
        """Get detailed container information."""
        if context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "inspect", container_id]
            output, err = DockerCommandExecutor.run_command(cmd)
            if err:
                return {}
                
            try:
                return json.loads(output)[0]
            except:
                return {"error": "Failed to parse inspect output"}
                
        try:
            container = self.docker_client.client.containers.get(container_id)
            return container.attrs
        except Exception as e:
            print(f"Inspect failed: {e}")
            return {}
