from typing import List, Optional, Dict, Any
import json
from datetime import datetime
import logging

from app.domain.models import Container, Port
from app.domain.repositories import ContainerRepository
from app.infrastructure.docker_client import DockerClient, DockerCommandExecutor

class DockerContainerRepository(ContainerRepository):
    """Implementation of ContainerRepository using Docker SDK and CLI."""
    
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
        self.logger = logging.getLogger(__name__)
    
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
                
                # Get image name safely
                image_name = ""
                if hasattr(c, 'image') and hasattr(c.image, 'tags') and c.image.tags:
                    image_name = c.image.tags[0]
                elif hasattr(c, 'image') and hasattr(c.image, 'id'):
                    image_name = c.image.id

                # Try to get created timestamp safely
                try:
                    created_ts = int(c.attrs.get("Created", 0)) 
                    created_date = datetime.fromtimestamp(created_ts)
                except (ValueError, TypeError):
                    # If created is not a valid timestamp
                    created_date = datetime.now()
                
                # Create Container object with the data
                container = Container(
                    id=c.id,
                    name=c.name,
                    image=image_name,
                    status=c.status,
                    created=created_date,
                    ports=ports,
                    networks=list(c.attrs.get("NetworkSettings", {}).get("Networks", {}).keys()),
                    labels=c.labels,
                    context="default"  # Make sure this is always set correctly
                )
                result.append(container)
            
            return result
                
        except Exception as e:
            print(f"Error listing containers: {str(e)}")
            return []
    
    def get_container(self, container_id: str, context: str = "default") -> Optional[Container]:
        """Get a specific container by ID."""
        try:
            if context != "default":
                # Use CLI for non-default contexts
                output, error = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "container", "inspect", container_id
                ])
                
                if error:
                    self.logger.error(f"Error getting container {container_id}: {error}")
                    return None
                    
                try:
                    container_data = json.loads(output)[0]
                    # Create Container object from data
                    # This would be a simplified implementation
                    return Container(
                        id=container_data.get("Id", ""),
                        name=container_data.get("Name", "").lstrip('/'),
                        image=container_data.get("Config", {}).get("Image", ""),
                        status=container_data.get("State", {}).get("Status", ""),
                        created=datetime.fromisoformat(container_data.get("Created", "").replace('Z', '+00:00')),
                        ports=[],  # Would need to parse port bindings
                        networks=list(container_data.get("NetworkSettings", {}).get("Networks", {}).keys()),
                        labels=container_data.get("Config", {}).get("Labels", {}),
                        context=context
                    )
                except (json.JSONDecodeError, IndexError) as e:
                    self.logger.error(f"Error parsing container JSON: {e}")
                    return None
            
            # Use SDK for default context
            if not self.docker_client or not self.docker_client.client:
                return None
                
            c = self.docker_client.client.containers.get(container_id)
            
            # Build Port objects
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
                    
            # Get image name safely
            image_name = ""
            if hasattr(c, 'image') and hasattr(c.image, 'tags') and c.image.tags:
                image_name = c.image.tags[0]
            elif hasattr(c, 'image') and hasattr(c.image, 'id'):
                image_name = c.image.id
            
            # Try to get created timestamp safely
            try:
                created_ts = c.attrs.get("Created", "")
                created_date = datetime.fromisoformat(created_ts.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                created_date = datetime.now()
                
            return Container(
                id=c.id,
                name=c.name,
                image=image_name,
                status=c.status,
                created=created_date,
                ports=ports,
                networks=list(c.attrs.get("NetworkSettings", {}).get("Networks", {}).keys()),
                labels=c.labels,
                context="default"
            )
        except Exception as e:
            self.logger.error(f"Error getting container {container_id}: {str(e)}")
            return None
        
    def start_container(self, container_id: str, context: str = "default") -> bool:
        """Start a container."""
        try:
            if context != "default":
                # Use CLI for non-default contexts
                _, err = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "start", container_id
                ])
                
                if err:
                    self.logger.error(f"Error starting container {container_id}: {err}")
                    return False
                return True
            
            # Use SDK for default context
            if not self.docker_client or not self.docker_client.client:
                return False
                
            container = self.docker_client.client.containers.get(container_id)
            container.start()
            return True
        except Exception as e:
            self.logger.error(f"Error starting container {container_id}: {str(e)}")
            return False
        
    def stop_container(self, container_id: str, context: str = "default") -> bool:
        """Stop a container."""
        try:
            if context != "default":
                # Use CLI for non-default contexts
                _, err = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "stop", container_id
                ])
                
                if err:
                    self.logger.error(f"Error stopping container {container_id}: {err}")
                    return False
                return True
            
            # Use SDK for default context
            if not self.docker_client or not self.docker_client.client:
                return False
                
            container = self.docker_client.client.containers.get(container_id)
            container.stop()
            return True
        except Exception as e:
            self.logger.error(f"Error stopping container {container_id}: {str(e)}")
            return False
        
    def remove_container(self, container_id: str, context: str = "default") -> bool:
        """Remove a container."""
        try:
            if context != "default":
                # Use CLI for non-default contexts
                _, err = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "rm", container_id
                ])
                
                if err:
                    self.logger.error(f"Error removing container {container_id}: {err}")
                    return False
                return True
            
            # Use SDK for default context
            if not self.docker_client or not self.docker_client.client:
                return False
                
            container = self.docker_client.client.containers.get(container_id)
            container.remove()
            return True
        except Exception as e:
            self.logger.error(f"Error removing container {container_id}: {str(e)}")
            return False
    
    def create_container(self, image_id: str, name: Optional[str] = None, 
                       context: str = "default", **kwargs) -> bool:
        """Create a new container."""
        try:
            if context != "default":
                # Use CLI for non-default contexts
                cmd = ["docker", "--context", context, "create"]
                
                # Add name parameter if provided
                if name:
                    cmd.extend(["--name", name])
                    
                # Add image as last parameter
                cmd.append(image_id)
                
                _, err = DockerCommandExecutor.run_command(cmd)
                
                if err:
                    self.logger.error(f"Error creating container from image {image_id}: {err}")
                    return False
                return True
            
            # Use SDK for default context
            if not self.docker_client or not self.docker_client.client:
                return False
                
            # Prepare container parameters
            params = {}
            if name:
                params["name"] = name
                
            # Create container
            self.docker_client.client.containers.create(image_id, **params)
            return True
        except Exception as e:
            self.logger.error(f"Error creating container from image {image_id}: {str(e)}")
            return False
        
    def get_container_details(self, container_id: str, context: str = "default") -> Dict[str, Any]:
        """Get detailed container information."""
        try:
            if context != "default":
                # Use CLI for non-default contexts
                output, err = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "container", "inspect", container_id
                ])
                
                if err:
                    return {}
                    
                try:
                    return json.loads(output)[0]
                except (json.JSONDecodeError, IndexError):
                    return {}
            
            # Use SDK for default context
            if not self.docker_client or not self.docker_client.client:
                return {}
                
            container = self.docker_client.client.containers.get(container_id)
            return container.attrs
        except Exception as e:
            print(f"Error getting container details: {str(e)}")
            return {}
        
    def _get_containers_for_context(self, context: str) -> List[Container]:
        """Get containers for a specific Docker context using CLI."""
        try:
            output, error = DockerCommandExecutor.run_command([
                "docker", "--context", context, "container", "ls", "--all", "--format", "{{json .}}"
            ])
            
            if error:
                self.logger.error(f"Error listing containers for context {context}: {error}")
                return []
                
            result = []
            # Each line is a separate JSON object
            for line in output.splitlines():
                if not line.strip():
                    continue
                    
                try:
                    container_data = json.loads(line)
                    
                    # Parse port information
                    ports = []
                    if 'Ports' in container_data and container_data['Ports']:
                        port_strings = container_data['Ports'].split(', ')
                        for port_str in port_strings:
                            if '->>' in port_str:  # Format: "0.0.0.0:8080->80/tcp"
                                host, container = port_str.split('->>')
                                host_ip, host_port = host.split(':') if ':' in host else ('0.0.0.0', host)
                                ports.append(Port(
                                    container_port=container,
                                    host_port=host_port,
                                    host_ip=host_ip
                                ))
                            else:
                                ports.append(Port(container_port=port_str))
                    
                    # Parse created timestamp - fix for timestamp parsing error
                    created_date = datetime.now()
                    created_str = container_data.get('CreatedAt', '')
                    
                    if created_str:
                        try:
                            # Try parsing as integer timestamp first
                            if created_str.isdigit():
                                created_date = datetime.fromtimestamp(int(created_str))
                            # Try parsing various date formats
                            elif '+' in created_str:
                                # Format like: '2025-03-26 20:43:42 +0100 CET'
                                # Extract the date part without timezone
                                date_part = created_str.split('+')[0].strip()
                                try:
                                    created_date = datetime.strptime(date_part, '%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    # Try other common formats
                                    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%a %b %d %H:%M:%S %Y']
                                    for fmt in formats:
                                        try:
                                            created_date = datetime.strptime(date_part, fmt)
                                            break
                                        except ValueError:
                                            continue
                            else:
                                # Try ISO format
                                created_date = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                        except (ValueError, TypeError) as e:
                            self.logger.warning(f"Unable to parse container creation date '{created_str}': {str(e)}")
                            created_date = datetime.now()
                    
                    # Create container object
                    container = Container(
                        id=container_data.get('ID', ''),
                        name=container_data.get('Names', '').strip('/'),
                        image=container_data.get('Image', ''),
                        status=container_data.get('Status', ''),
                        created=created_date,
                        ports=ports,
                        networks=container_data.get('Networks', '').split(',') if container_data.get('Networks') else [],
                        labels={},  # Would need another command to get labels
                        context=context
                    )
                    result.append(container)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parsing container JSON: {e}")
                except Exception as e:
                    self.logger.error(f"Error processing container data: {e}")
            
            return result
        except Exception as e:
            self.logger.error(f"Error getting containers for context {context}: {e}")
            return []
        
    def get_container_logs(self, container_id: str, context: str = "default") -> str:
        """Get logs from a container."""
        try:
            if context != "default":
                # Use CLI for non-default contexts
                output, err = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "logs", container_id
                ])
                
                if err:
                    return f"Error: {err}"
                    
                return output
            
            # Use SDK for default context
            if not self.docker_client or not self.docker_client.client:
                return "Error: Docker client is not initialized"
                
            container = self.docker_client.client.containers.get(container_id)
            return container.logs().decode('utf-8', errors='replace')
        except Exception as e:
            return f"Error getting container logs: {str(e)}"
