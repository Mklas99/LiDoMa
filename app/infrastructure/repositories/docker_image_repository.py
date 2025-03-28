from typing import List, Optional, Dict
from datetime import datetime
import json

from app.domain.models import Image
from app.domain.repositories import ImageRepository
from app.infrastructure.docker_client import DockerClient, DockerCommandExecutor

class DockerImageRepository(ImageRepository):
    """Implementation of ImageRepository using Docker SDK and CLI."""
    
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
    
    def list_images(self, context: str = "default") -> List[Image]:
        """List all images."""
        if context != "default":
            return self._get_images_for_context(context)
            
        try:
            if not self.docker_client or not self.docker_client.client:
                return []
                
            images = self.docker_client.client.images.list()
            result = []
            
            for img in images:
                # Get basic info
                id = img.id
                tags = img.tags
                name = tags[0].split(':')[0] if tags else "none"
                
                # Get size
                size = img.attrs.get('Size', 0)
                
                # Get created timestamp
                try:
                    created_timestamp = img.attrs.get('Created', None)
                    if created_timestamp:
                        created = datetime.fromisoformat(created_timestamp.replace('Z', '+00:00'))
                    else:
                        created = datetime.now()
                except (ValueError, TypeError):
                    created = datetime.now()
                
                # Get labels
                labels = img.attrs.get('Config', {}).get('Labels', {}) or {}
                
                # Create Image object
                image = Image(
                    id=id,
                    name=name,
                    tags=tags,
                    size=size,
                    created=created,
                    labels=labels,
                    context="default"
                )
                result.append(image)
            
            return result
        except Exception as e:
            print(f"Error listing images: {str(e)}")
            return []
        
    def get_image(self, image_id: str, context: str = "default") -> Optional[Image]:
        """Get a specific image by ID."""
        try:
            if not self.docker_client or not self.docker_client.client:
                return None
                
            img = self.docker_client.client.images.get(image_id)
            if not img:
                return None
                
            # Get basic info
            id = img.id
            tags = img.tags
            name = tags[0].split(':')[0] if tags else "none"
            
            # Get size
            size = img.attrs.get('Size', 0)
            
            # Get created timestamp
            try:
                created_timestamp = img.attrs.get('Created', None)
                if created_timestamp:
                    created = datetime.fromisoformat(created_timestamp.replace('Z', '+00:00'))
                else:
                    created = datetime.now()
            except (ValueError, TypeError):
                created = datetime.now()
            
            # Get labels
            labels = img.attrs.get('Config', {}).get('Labels', {}) or {}
            
            # Create Image object
            return Image(
                id=id,
                name=name,
                tags=tags,
                size=size,
                created=created,
                labels=labels,
                context=context
            )
        except Exception as e:
            print(f"Error getting image: {str(e)}")
            return None
        
    def remove_image(self, image_id: str, context: str = "default") -> bool:
        """Remove an image."""
        try:
            if not self.docker_client or not self.docker_client.client:
                return False
                
            self.docker_client.client.images.remove(image_id)
            return True
        except Exception as e:
            print(f"Error removing image: {str(e)}")
            return False
        
    def pull_image(self, image_name: str, tag: str = "latest", context: str = "default") -> bool:
        """Pull an image from a registry."""
        try:
            if not self.docker_client or not self.docker_client.client:
                return False
                
            self.docker_client.client.images.pull(image_name, tag=tag)
            return True
        except Exception as e:
            print(f"Error pulling image: {str(e)}")
            return False
            
    def _get_images_for_context(self, context: str) -> List[Image]:
        """Get images for a specific Docker context using CLI."""
        output, err = DockerCommandExecutor.run_command([
            "docker", "--context", context, "image", "ls", "--format", "{{json .}}"
        ])
        
        images = []
        if err:
            return images
            
        if output:
            for line in output.splitlines():
                try:
                    data = json.loads(line)
                    id = data.get('ID', '')
                    repo_tag = data.get('Repository', '') + ":" + data.get('Tag', '')
                    
                    # Parse size
                    size_str = data.get('Size', '0B')
                    size = self._parse_size(size_str)
                    
                    # Parse created time
                    created_str = data.get('CreatedAt', '')
                    try:
                        created = datetime.strptime(created_str, '%Y-%m-%d %H:%M:%S %z')
                    except ValueError:
                        created = datetime.now()
                    
                    images.append(Image(
                        id=id,
                        name=repo_tag.split(':')[0],
                        tags=[repo_tag] if repo_tag != ":" else [],
                        size=size,
                        created=created,
                        context=context
                    ))
                except json.JSONDecodeError:
                    continue
                    
        return images
        
    def _parse_size(self, size_str: str) -> int:
        """Parse a human-readable size string into bytes."""
        try:
            if 'KB' in size_str:
                return int(float(size_str.replace('KB', '')) * 1024)
            elif 'MB' in size_str:
                return int(float(size_str.replace('MB', '')) * 1024 * 1024)
            elif 'GB' in size_str:
                return int(float(size_str.replace('GB', '')) * 1024 * 1024 * 1024)
            elif 'TB' in size_str:
                return int(float(size_str.replace('TB', '')) * 1024 * 1024 * 1024 * 1024)
            else:
                return int(size_str.replace('B', ''))
        except (ValueError, TypeError):
            return 0
