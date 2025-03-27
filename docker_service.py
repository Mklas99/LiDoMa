import docker
import subprocess
from docker.errors import NotFound, APIError
from typing import List, Dict, Tuple

class DockerService:
    def __init__(self):
        # Initialize Docker client from environment
        self.client = docker.from_env()

    def run_docker_command(self, args) -> Tuple[str, str]:
        """Execute Docker CLI commands with error handling."""
        try:
            process = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return process.stdout.strip(), ""
        except subprocess.CalledProcessError as e:
            return e.stdout.strip(), e.stderr.strip()

    def get_docker_contexts(self) -> Tuple[List[str], str]:
        """Dynamically retrieve Docker contexts."""
        output, err = self.run_docker_command(["docker", "context", "ls", "--format", "{{.Name}}"])
        if err:
            return [], err
        contexts = output.splitlines()
        return contexts, ""

    # Container operations
    def list_containers(self, all_containers: bool = True, context: str = None) -> List[Dict]:
        """Get containers using Python Docker SDK."""
        if context and context != "default":
            # For non-default contexts, use CLI approach
            return self.get_containers_for_context(context)
        
        try:
            containers = self.client.containers.list(all=all_containers)
            result = []
            for c in containers:
                result.append({
                    "id": c.short_id,
                    "name": c.name,
                    "status": c.status,
                    "ports": c.attrs.get("NetworkSettings", {}).get("Ports", {}),
                    "context": "default"
                })
            return result
        except Exception as e:
            print(f"Error listing containers: {e}")
            return []

    def get_containers_for_context(self, context: str) -> List[Dict]:
        """Get containers for a specific Docker context."""
        output, err = self.run_docker_command([
            "docker", "--context", context, "ps", "-a", "--format", "{{.Names}}\t{{.Status}}"
        ])
        containers = []
        if err:
            return containers
        if output:
            for line in output.splitlines():
                try:
                    name, status = line.split("\t")
                    containers.append({"name": name, "status": status, "context": context, "ports": {}})
                except ValueError:
                    continue
        return containers

    def start_container(self, container_name: str, context: str = "default") -> bool:
        """Start a container."""
        if context and context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "start", container_name]
            _, err = self.run_docker_command(cmd)
            return not err
        
        try:
            container = self.client.containers.get(container_name)
            container.start()
            return True
        except Exception as e:
            print(f"Failed to start container '{container_name}': {e}")
            return False

    def stop_container(self, container_name: str, context: str = "default") -> bool:
        """Stop a container."""
        if context and context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "stop", container_name]
            _, err = self.run_docker_command(cmd)
            return not err
            
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            return True
        except Exception as e:
            print(f"Failed to stop container '{container_name}': {e}")
            return False

    def remove_container(self, container_name: str, context: str = "default") -> bool:
        """Remove a container."""
        if context and context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "rm", container_name]
            _, err = self.run_docker_command(cmd)
            return not err
            
        try:
            container = self.client.containers.get(container_name)
            container.remove(force=True)
            return True
        except Exception as e:
            print(f"Error removing container '{container_name}': {e}")
            return False

    def inspect_container(self, container_name: str, context: str = "default") -> dict:
        """Return detailed container info as a dictionary."""
        if context and context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "inspect", container_name]
            output, err = self.run_docker_command(cmd)
            if err:
                return {}
            import json
            try:
                return json.loads(output)[0]
            except:
                return {"error": "Failed to parse inspect output"}
            
        try:
            container = self.client.containers.get(container_name)
            return container.attrs
        except Exception as e:
            print(f"Inspect failed: {e}")
            return {}

    # Image operations
    def list_images(self, context: str = "default") -> List[Dict]:
        """Get images using Python Docker SDK."""
        if context and context != "default":
            # For non-default contexts, use CLI approach
            return self.get_images_for_context(context)
            
        try:
            images = self.client.images.list()
            result = []
            for img in images:
                tags = img.tags if img.tags else ["<none>"]
                created = getattr(img, 'attrs', {}).get('Created', None)
                result.append({
                    "id": img.short_id,
                    "name": tags[0] if tags else "<none>:<none>",
                    "tags": tags,
                    "size": img.attrs.get("Size", ""),
                    "created": created,
                    "context": "default"
                })
            return result
        except Exception as e:
            print(f"Error listing images: {e}")
            return []

    def get_images_for_context(self, context: str) -> List[Dict]:
        """Get images for a specific Docker context."""
        output, err = self.run_docker_command([
            "docker", "--context", context, "images", "--format", "{{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.Size}}"
        ])
        images = []
        if err:
            return images
        if output:
            for line in output.splitlines():
                try:
                    name, image_id, size = line.split("\t")
                    images.append({
                        "name": name, 
                        "id": image_id, 
                        "tags": [name],
                        "size": size, 
                        "context": context
                    })
                except ValueError:
                    continue
        return images

    def remove_image(self, image_id: str, context: str = "default") -> bool:
        """Remove an image."""
        if context and context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "rmi", image_id]
            _, err = self.run_docker_command(cmd)
            return not err
            
        try:
            self.client.images.remove(image_id, force=True)
            return True
        except Exception as e:
            print(f"Failed to remove image '{image_id}': {e}")
            return False

    def create_container(self, image: str, name: str = None, context: str = "default") -> bool:
        """Create a container from an image."""
        if context and context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "create"]
            if name:
                cmd.extend(["--name", name])
            cmd.append(image)
            _, err = self.run_docker_command(cmd)
            return not err
            
        try:
            self.client.containers.create(image=image, name=name)
            return True
        except Exception as e:
            print(f"Failed to create container from '{image}': {e}")
            return False

    # Volume operations
    def list_volumes(self, context: str = "default") -> List[Dict]:
        """Get volumes using Python Docker SDK."""
        if context and context != "default":
            # For non-default contexts, use CLI approach
            return self.get_volumes_for_context(context)
            
        try:
            volumes_data = self.client.volumes.list()
            result = []
            for vol in volumes_data:
                result.append({
                    "name": vol.name,
                    "driver": vol.attrs.get("Driver", "unknown"),
                    "mountpoint": vol.attrs.get("Mountpoint", ""),
                    "context": "default"
                })
            return result
        except Exception as e:
            print(f"Error listing volumes: {e}")
            return []

    def get_volumes_for_context(self, context: str) -> List[Dict]:
        """Get volumes for a specific Docker context."""
        output, err = self.run_docker_command([
            "docker", "--context", context, "volume", "ls", "--format", "{{.Name}}\t{{.Driver}}\t{{.Mountpoint}}"
        ])
        volumes = []
        if err:
            return volumes
        if output:
            for line in output.splitlines():
                try:
                    parts = line.split("\t")
                    name = parts[0]
                    driver = parts[1] if len(parts) > 1 else "N/A"
                    mountpoint = parts[2] if len(parts) > 2 else "N/A"
                    
                    volumes.append({
                        "name": name, 
                        "driver": driver, 
                        "mountpoint": mountpoint, 
                        "context": context
                    })
                except ValueError:
                    continue
        return volumes

    def remove_volume(self, volume_name: str, context: str = "default") -> bool:
        """Remove a volume."""
        if context and context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "volume", "rm", volume_name]
            _, err = self.run_docker_command(cmd)
            return not err
            
        try:
            volume = self.client.volumes.get(volume_name)
            volume.remove(force=True)
            return True
        except Exception as e:
            print(f"Failed to remove volume '{volume_name}': {e}")
            return False

    # Network operations
    def list_networks(self, context: str = "default") -> List[Dict]:
        """Get networks using Python Docker SDK."""
        if context and context != "default":
            # For non-default contexts, use CLI approach
            return self.get_networks_for_context(context)
            
        try:
            networks_data = self.client.networks.list()
            result = []
            for net in networks_data:
                result.append({
                    "name": net.name,
                    "id": net.short_id,
                    "driver": net.attrs.get("Driver", "unknown"),
                    "scope": net.attrs.get("Scope", ""),
                    "context": "default"
                })
            return result
        except Exception as e:
            print(f"Error listing networks: {e}")
            return []

    def get_networks_for_context(self, context: str) -> List[Dict]:
        """Get networks for a specific Docker context."""
        output, err = self.run_docker_command([
            "docker", "--context", context, "network", "ls", "--format", "{{.Name}}\t{{.Driver}}\t{{.ID}}\t{{.Scope}}"
        ])
        networks = []
        if err:
            return networks
        if output:
            for line in output.splitlines():
                try:
                    parts = line.split("\t")
                    name = parts[0]
                    driver = parts[1] if len(parts) > 1 else "N/A"
                    network_id = parts[2] if len(parts) > 2 else "N/A"
                    scope = parts[3] if len(parts) > 3 else "N/A"
                    
                    networks.append({
                        "name": name,
                        "driver": driver,
                        "id": network_id,
                        "scope": scope,
                        "context": context
                    })
                except ValueError:
                    continue
        return networks

    def remove_network(self, network_name: str, context: str = "default") -> bool:
        """Remove a network."""
        if context and context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "network", "rm", network_name]
            _, err = self.run_docker_command(cmd)
            return not err
            
        try:
            network = self.client.networks.get(network_name)
            network.remove()
            return True
        except Exception as e:
            print(f"Failed to remove network '{network_name}': {e}")
            return False
