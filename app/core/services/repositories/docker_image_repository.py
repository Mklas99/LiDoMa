from typing import List, Optional, Dict, Any
import json
from datetime import datetime

from domain.models import Image
from domain.repositories import ImageRepository
from infrastructure.docker_client import DockerClient, DockerCommandExecutor

class DockerImageRepository(ImageRepository):
    """Implementation of ImageRepository using Docker SDK and CLI."""
    
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
        
    def list_images(self, context: str = "default") -> List[Image]:
        """List all images."""
        if context != "default":
            return self._get_images_for_context(context)
            
        try:
            images = self.docker_client.client.images.list()
            result = []
            
            for img in images:
                tags = img.tags if img.tags else ["<none>:<none>"]
                created_ts = img.attrs.get("Created")
                created_date = None
                
                if created_ts:
                    try:
                        created_date = datetime.fromisoformat(created_ts.replace('Z', '+00:00'))
                    except (ValueError, TypeError):
                        pass
                        
                result.append(Image(
                    id=img.short_id,
                    name=tags[0] if tags else "<none>:<none>",
                    tags=tags,
                    size=img.attrs.get("Size", 0),
                    created=created_date,
                    context="default"
                ))
                
            return result
        except Exception as e:
            print(f"Error listing images: {e}")
            return []
            
    def _get_images_for_context(self, context: str) -> List[Image]:
        """Get images for a specific Docker context."""
        output, err = DockerCommandExecutor.run_command([
            "docker", "--context", context, "images", 
            "--format", "{{.ID}}\t{{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
        ])
        
        images = []
        if err:
            return images
            
        if output:
            for line in output.splitlines():
                try:
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        image_id, name, size = parts[0], parts[1], parts[2]
                        created_str = parts[3] if len(parts) > 3 else ""
                        
                        created_date = None
                        if created_str:
                            try:
                                created_date = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S %z")
                            except (ValueError, TypeError):
                                pass
                                
                        images.append(Image(
                            id=image_id,
                            name=name,
                            tags=[name] if name != "<none>:<none>" else [],
                            size=self._parse_size(size),
                            created=created_date,
                            context=context
                        ))
                except ValueError:
                    continue
                    
        return images
        
    def _parse_size(self, size_str: str) -> int:
        """Parse size string to bytes."""
        try:
            if "GB" in size_str:
                return int(float(size_str.replace("GB", "").strip()) * 1_000_000_000)
            elif "MB" in size_str:
                return int(float(size_str.replace("MB", "").strip()) * 1_000_000)
            elif "kB" in size_str or "KB" in size_str:
                return int(float(size_str.replace("kB", "").replace("KB", "").strip()) * 1_000)
            else:
                return int(float(size_str.split()[0].strip()))
        except (ValueError, IndexError):
            return 0
    
    def get_image(self, image_id: str, context: str = "default") -> Optional[Image]:
        """Get a specific image by ID or tag."""
        if context != "default":
            # Use CLI for non-default contexts
            images = self._get_images_for_context(context)
            for image in images:
                if image.id == image_id or image.name == image_id or image_id in image.tags:
                    return image
            return None
            
        try:
            img = self.docker_client.client.images.get(image_id)
            
            tags = img.tags if img.tags else ["<none>:<none>"]
            created_ts = img.attrs.get("Created")
            created_date = None
            
            if created_ts:
                try:
                    created_date = datetime.fromisoformat(created_ts.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    pass
                    
            return Image(
                id=img.short_id,
                name=tags[0] if tags else "<none>:<none>",
                tags=tags,
                size=img.attrs.get("Size", 0),
                created=created_date,
                context="default"
            )
        except Exception as e:
            print(f"Error getting image: {e}")
            return None
            
    def remove_image(self, image_id: str, context: str = "default") -> bool:
        """Remove an image."""
        if context != "default":
            # Use CLI for non-default contexts
            _, err = DockerCommandExecutor.run_command(["docker", "--context", context, "rmi", image_id])
            return not err
            
        try:
            self.docker_client.client.images.remove(image_id, force=True)
            return True
        except Exception as e:
            print(f"Failed to remove image '{image_id}': {e}")
            return False
            
    def pull_image(self, image_name: str, tag: str = "latest", context: str = "default") -> bool:
        """Pull an image from registry."""
        if context != "default":
            # Use CLI for non-default contexts
            _, err = DockerCommandExecutor.run_command(["docker", "--context", context, "pull", f"{image_name}:{tag}"])
            return not err
            
        try:
            self.docker_client.client.images.pull(image_name, tag=tag)
            return True
        except Exception as e:
            print(f"Failed to pull image '{image_name}:{tag}': {e}")
            return False
            
    def get_image_details(self, image_id: str, context: str = "default") -> Dict[str, Any]:
        """Get detailed image information."""
        if context != "default":
            # Use CLI for non-default contexts
            cmd = ["docker", "--context", context, "inspect", image_id]
            output, err = DockerCommandExecutor.run_command(cmd)
            if err:
                return {}
                
            try:
                return json.loads(output)[0]
            except:
                return {"error": "Failed to parse inspect output"}
                
        try:
            image = self.docker_client.client.images.get(image_id)
            return image.attrs
        except Exception as e:
            print(f"Inspect failed: {e}")
            return {}
