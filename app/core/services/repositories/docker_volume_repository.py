from typing import List, Optional
import json

from domain.models import Volume
from domain.repositories import VolumeRepository
from infrastructure.docker_client import DockerClient, DockerCommandExecutor

class DockerVolumeRepository(VolumeRepository):
    """Implementation of VolumeRepository using Docker SDK and CLI."""
    
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
        
    def list_volumes(self, context: str = "default") -> List[Volume]:
        """List all volumes."""
        if context != "default":
            return self._get_volumes_for_context(context)
            
        try:
            volumes_data = self.docker_client.client.volumes.list()
            result = []
            
            for vol in volumes_data:
                result.append(Volume(
                    name=vol.name,
                    driver=vol.attrs.get("Driver", "local"),
                    mountpoint=vol.attrs.get("Mountpoint", ""),
                    context="default"
                ))
                
            return result
        except Exception as e:
            print(f"Error listing volumes: {e}")
            return []
            
    def _get_volumes_for_context(self, context: str) -> List[Volume]:
        """Get volumes for a specific Docker context."""
        output, err = DockerCommandExecutor.run_command([
            "docker", "--context", context, "volume", "ls", 
            "--format", "{{.Name}}\t{{.Driver}}\t{{.Mountpoint}}"
        ])
        
        volumes = []
        if err:
            return volumes
            
        if output:
            for line in output.splitlines():
                try:
                    parts = line.split("\t")
                    name = parts[0]
                    driver = parts[1] if len(parts) > 1 else "local"
                    mountpoint = parts[2] if len(parts) > 2 else ""
                    
                    volumes.append(Volume(
                        name=name,
                        driver=driver,
                        mountpoint=mountpoint,
                        context=context
                    ))
                except ValueError:
                    continue
                    
        return volumes
    
    def get_volume(self, volume_name: str, context: str = "default") -> Optional[Volume]:
        """Get a specific volume by name."""
        if context != "default":
            # Use CLI for non-default contexts
            volumes = self._get_volumes_for_context(context)
            for volume in volumes:
                if volume.name == volume_name:
                    return volume
            return None
            
        try:
            vol = self.docker_client.client.volumes.get(volume_name)
            return Volume(
                name=vol.name,
                driver=vol.attrs.get("Driver", "local"),
                mountpoint=vol.attrs.get("Mountpoint", ""),
                context="default"
            )
        except Exception as e:
            print(f"Error getting volume: {e}")
            return None
            
    def remove_volume(self, volume_name: str, context: str = "default") -> bool:
        """Remove a volume."""
        if context != "default":
            # Use CLI for non-default contexts
            _, err = DockerCommandExecutor.run_command(["docker", "--context", context, "volume", "rm", volume_name])
            return not err
            
        try:
            volume = self.docker_client.client.volumes.get(volume_name)
            volume.remove(force=True)
            return True
        except Exception as e:
            print(f"Failed to remove volume '{volume_name}': {e}")
            return False
            
    def create_volume(self, name: str, driver: str = "local", context: str = "default") -> bool:
        """Create a new volume."""
        if context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "volume", "create"]
            if driver and driver != "local":
                cmd.extend(["--driver", driver])
            cmd.append(name)
            _, err = DockerCommandExecutor.run_command(cmd)
            return not err
            
        try:
            self.docker_client.client.volumes.create(name=name, driver=driver)
            return True
        except Exception as e:
            print(f"Failed to create volume '{name}': {e}")
            return False
