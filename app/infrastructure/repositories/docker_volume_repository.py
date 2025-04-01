from typing import List, Optional
import logging
import json

from app.domain.models import Volume
from app.domain.repositories import VolumeRepository
from app.infrastructure.docker_client import DockerClient, DockerCommandExecutor

class DockerVolumeRepository(VolumeRepository):
    """Implementation of VolumeRepository using Docker SDK and CLI."""
    
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
        self.logger = logging.getLogger(__name__)
    
    def list_volumes(self, context: str = "default") -> List[Volume]:
        try:
            if context != "default":
                return self._get_volumes_for_context(context)
                
            volumes = self.docker_client.client.volumes.list()
            result = []
            
            for vol in volumes:
                volume = Volume(
                    name=vol.name,
                    driver=vol.attrs.get("Driver", "local"),
                    mountpoint=vol.attrs.get("Mountpoint", ""),
                    context="default"
                )
                result.append(volume)
            
            return result
        except Exception as e:
            self.logger.error(f"Error listing volumes: {str(e)}")
            return []
        
    def get_volume(self, volume_name: str, context: str = "default") -> Optional[Volume]:
        """Get a specific volume by name."""
        try:
            if not self.docker_client or not self.docker_client.client:
                return None
                
            vol = self.docker_client.client.volumes.get(volume_name)
            if not vol:
                return None
                
            return Volume(
                name=vol.name,
                driver=vol.attrs.get('Driver', 'local'),
                mountpoint=vol.attrs.get('Mountpoint', ''),
                labels=vol.attrs.get('Labels', {}),
                options=vol.attrs.get('Options', {}),
                context=context
            )
        except Exception as e:
            print(f"Error getting volume: {str(e)}")
            return None
        
    def remove_volume(self, volume_name: str, context: str = "default") -> bool:
        """Remove a volume."""
        try:
            if context != "default":
                # Use CLI for non-default contexts
                _, error = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "volume", "rm", volume_name
                ])
                return not error
                
            # Use SDK for default context
            vol = self.docker_client.client.volumes.get(volume_name)
            vol.remove()
            return True
        except Exception as e:
            self.logger.error(f"Error removing volume {volume_name}: {str(e)}")
            return False
        

    def create_volume(self, name: str, driver: str = "local", context: str = "default", **kwargs) -> bool:
        """Create a new volume."""
        try:
            if not self.docker_client or not self.docker_client.client:
                return False
                
            self.docker_client.client.volumes.create(
                name=name,
                driver=driver,
                driver_opts=kwargs.get('driver_opts', {}),
                labels=kwargs.get('labels', {})
            )
            return True
        except Exception as e:
            self.logger.error(f"Error creating volume {name}: {str(e)}")

    def _get_volumes_for_context(self, context: str) -> List[Volume]:
            return False
            
    def _get_volumes_for_context(self, context: str) -> List[Volume]:
        """Get volumes for a specific Docker context using CLI."""
        output, err = DockerCommandExecutor.run_command([
            "docker", "--context", context, "volume", "ls", "--format", "{{json .}}"
        ])
        
        volumes = []
        if err:
            return volumes
            
        if output:
            for line in output.splitlines():
                try:
                    data = json.loads(line)
                    name = data.get('Name', '')
                    driver = data.get('Driver', 'local')
                    
                    # Get more details
                    detail_output, detail_err = DockerCommandExecutor.run_command([
                        "docker", "--context", context, "volume", "inspect", name
                    ])
                    
                    mountpoint = ""
                    options = {}
                    labels = {}
                    
                    if not detail_err and detail_output:
                        try:
                            volume_data = json.loads(detail_output)[0]
                            mountpoint = volume_data.get('Mountpoint', '')
                            options = volume_data.get('Options', {})
                            labels = volume_data.get('Labels', {})
                        except (json.JSONDecodeError, IndexError):
                            pass
                    
                    volumes.append(Volume(
                        name=name,
                        driver=driver,
                        mountpoint=mountpoint,
                        options=options,
                        labels=labels,
                        context=context
                    ))
                except json.JSONDecodeError:
                    continue
                    
        return volumes
