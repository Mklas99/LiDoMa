import os
import subprocess
import shutil
from app.core.docker.installation.steps.base import DockerStep

class WindowsDockerUninstaller:
    """Handles uninstallation of Docker components on Windows."""
    
    @staticmethod
    def uninstall_docker_engine(worker, install_dir=None):
        """Uninstall Docker Engine from Windows."""
        worker.log_message.emit("Uninstalling Docker Engine...")
        if not install_dir:
            install_dir = os.path.join(os.environ["ProgramFiles"], "Docker")
        
        try:
            worker.log_message.emit("Stopping Docker service...")
            subprocess.run(["sc", "stop", "docker"], check=False)
        except Exception as e:
            worker.log_message.emit(f"Warning: Failed to stop Docker service: {str(e)}")
            
        try:
            worker.log_message.emit("Removing Docker installation directory...")
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir, ignore_errors=True)
        except Exception as e:
            worker.log_message.emit(f"Warning: Failed to remove Docker directory: {str(e)}")

class WindowsDockerUninstallStep(DockerStep):
    """Uninstalls Docker Engine on Windows."""
    def __init__(self, worker):
        super().__init__("Uninstalling Docker Engine", worker)

    def execute(self):
        """Uninstall Docker Engine."""
        self.worker.log_message.emit("Uninstalling Docker Engine...")
        try:
            subprocess.run(["sc", "stop", "docker"], check=False)
            subprocess.run(["sc", "delete", "docker"], check=False)
            self.worker.log_message.emit("Docker Engine uninstalled successfully.")
        except Exception as e:
            self.worker.log_message.emit(f"Error during Docker Engine uninstallation: {str(e)}")
            raise

    def rollback(self):
        """Rollback is not applicable for uninstallation."""
        self.worker.log_message.emit("Rollback not applicable for uninstallation.")
