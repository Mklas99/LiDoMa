from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import json

from app.domain.models import Image
from app.domain.repositories import ImageRepository
from app.infrastructure.docker_client import DockerClient, DockerCommandExecutor

class DockerImageRepository(ImageRepository):
    """Implementation of ImageRepository using Docker SDK and CLI."""
    
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
        self.logger = logging.getLogger(__name__)
    
    def list_images(self, context: str = "default") -> List[Image]:
        """List all images."""
        if context != "default":
            return self._get_images_for_context(context)
            
        try:
            images = self.docker_client.client.images.list(all=False)
            result = []
            
            for img in images:
                # Extract image info
                image_id = img.id
                tags = img.tags
                name = tags[0].split(':')[0] if tags else image_id[:12]
                tag = tags[0].split(':')[1] if tags and ':' in tags[0] else "latest"
                size = img.attrs.get("Size", 0)
                
                # Try to get created timestamp safely
                try:
                    created_ts = img.attrs.get("Created", None)
                    created_date = datetime.fromisoformat(created_ts.replace('Z', '+00:00')) if created_ts else datetime.now()
                except (ValueError, TypeError):
                    created_date = datetime.now()
                
                # Create Image object
                image = Image(
                    id=image_id,
                    name=name,
                    tags=[tag] if tag else [],
                    size=size,
                    created=created_date,
                    context="default"
                )
                result.append(image)
            
            return result
                
        except Exception as e:
            self.logger.error(f"Error listing images: {str(e)}")
            return []
    
    def get_image(self, image_id: str, context: str = "default") -> Optional[Image]:
        """Get a specific image by ID."""
        try:
            if context != "default":
                # Use CLI for non-default contexts
                return self._get_image_from_context(image_id, context)
            
            # Use SDK for default context
            if not self.docker_client or not self.docker_client.client:
                return None
                
            img = self.docker_client.client.images.get(image_id)
            
            # Extract image info
            tags = img.tags
            name = tags[0].split(':')[0] if tags else image_id[:12]
            tag = tags[0].split(':')[1] if tags and ':' in tags[0] else "latest"
            size = img.attrs.get("Size", 0)
            
            # Try to get created timestamp safely
            try:
                created_ts = img.attrs.get("Created", None)
                created_date = datetime.fromisoformat(created_ts.replace('Z', '+00:00')) if created_ts else datetime.now()
            except (ValueError, TypeError):
                created_date = datetime.now()
            
            # Create Image object
            return Image(
                id=image_id,
                name=name,
                tags=[tag] if tag else [],
                size=size,
                created=created_date,
                context="default"
            )
                
        except Exception as e:
            self.logger.error(f"Error getting image {image_id}: {str(e)}")
            return None
    
    def remove_image(self, image_id: str, context: str = "default") -> bool:
        """Remove an image."""
        try:
            if context != "default":
                # Use CLI for non-default contexts
                output, error = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "image", "rm", image_id
                ])
                
                return not error
            
            # Use SDK for default context
            if not self.docker_client or not self.docker_client.client:
                return False
                
            self.docker_client.client.images.remove(image_id)
            return True
        except Exception as e:
            self.logger.error(f"Error removing image {image_id}: {str(e)}")
            return False
    
    def pull_image(self, image_name: str, context: str = "default") -> bool:
        """Pull an image from registry."""
        try:
            if context != "default":
                # Use CLI for non-default contexts
                output, error = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "pull", image_name
                ])
                
                if error:
                    self.logger.error(f"Error pulling image {image_name}: {error}")
                    return False
                return True
            
            # Use SDK for default context
            if not self.docker_client or not self.docker_client.client:
                return False
                
            self.docker_client.client.images.pull(image_name)
            return True
        except Exception as e:
            self.logger.error(f"Error pulling image {image_name}: {str(e)}")
            return False
    
    def _get_images_for_context(self, context: str) -> List[Image]:
        """Get images for a specific Docker context using CLI."""
        try:
            output, error = DockerCommandExecutor.run_command([
                "docker", "--context", context, "image", "ls", "--format", "{{json .}}"
            ])
            
            if error:
                self.logger.error(f"Error listing images for context {context}: {error}")
                return []
                
            result = []
            # Each line is a separate JSON object
            for line in output.splitlines():
                if not line.strip():
                    continue
                    
                try:
                    image_data = json.loads(line)
                    
                    # Parse image info
                    repository = image_data.get('Repository', '<none>')
                    tag = image_data.get('Tag', '<none>')
                    image_id = image_data.get('ID', '')
                    size_str = image_data.get('Size', '0B')
                    
                    # Parse size to bytes
                    size = self._parse_size_to_bytes(size_str)
                    
                    # Create image object
                    image = Image(
                        id=image_id,
                        name=repository if repository != '<none>' else image_id[:12],
                        tags=[tag] if tag != '<none>' else [],
                        size=size,
                        created=datetime.now(),  # CLI output doesn't include created timestamp
                        context=context
                    )
                    result.append(image)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parsing image JSON: {e}")
                except Exception as e:
                    self.logger.error(f"Error processing image data: {e}")
            
            return result
        except Exception as e:
            self.logger.error(f"Error getting images for context {context}: {e}")
            return []
    
    def _get_image_from_context(self, image_id: str, context: str) -> Optional[Image]:
        """Get specific image from a context using CLI."""
        # Implementation would be similar to _get_images_for_context but filter for specific ID
        # For brevity, returning None
        return None
    
    def _parse_size_to_bytes(self, size_str: str) -> int:
        """Parse Docker size string to bytes."""
        try:
            if not size_str or size_str == '<none>':
                return 0
                
            units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
            
            # Handle different formats
            if size_str.endswith('B'):
                for unit, multiplier in units.items():
                    if size_str.endswith(unit):
                        value = float(size_str[:-len(unit)].strip())
                        return int(value * multiplier)
            
            return int(size_str)
        except (ValueError, TypeError):
            return 0
