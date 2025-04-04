import subprocess
from .base import InstallationStep, DockerStep

class WindowsWSL2Step(InstallationStep):
    """Installs and configures WSL2 on Windows."""
    def __init__(self, worker):
        super().__init__("WSL2 Setup", worker)
        self.wsl_was_installed = False
        
    def execute(self):
        """Enable and configure WSL2."""
        try:
            result = subprocess.run(
                ["wsl", "--status"], 
                capture_output=True, 
                text=True
            )
            self.wsl_was_installed = "WSL 2" in result.stdout or "WSL 2" in result.stderr
            
            if not self.wsl_was_installed:
                self.worker.log_message.emit("Enabling WSL2...")
                subprocess.run(
                    ["dism.exe", "/online", "/enable-feature", "/featurename:Microsoft-Windows-Subsystem-Linux", "/all", "/norestart"],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                subprocess.run(
                    ["dism.exe", "/online", "/enable-feature", "/featurename:VirtualMachinePlatform", "/all", "/norestart"],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                subprocess.run(
                    ["wsl", "--set-default-version", "2"],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
        except subprocess.CalledProcessError as e:
            if e.returncode == 740:
                self.worker.log_message.emit("Error: Administrator privileges are required to enable WSL2.")
            else:
                self.worker.log_message.emit(f"Error configuring WSL2: {str(e)}")
            raise
        except Exception as e:
            self.worker.log_message.emit(f"Unexpected error during WSL2 setup: {str(e)}")
            raise

    def rollback(self):
        """Roll back WSL2 changes if we installed it."""
        if not self.wsl_was_installed:
            self.worker.log_message.emit("Skipping rollback: WSL2 was already installed.")
            return
        self.worker.log_message.emit("Rolling back WSL2 configuration...")
        try:
            subprocess.run(
                ["dism.exe", "/online", "/disable-feature", "/featurename:Microsoft-Windows-Subsystem-Linux", "/norestart"],
                check=False
            )
            subprocess.run(
                ["dism.exe", "/online", "/disable-feature", "/featurename:VirtualMachinePlatform", "/norestart"],
                check=False
            )
        except Exception as e:
            self.worker.log_message.emit(f"Warning: Failed to roll back WSL2: {str(e)}")

class WindowsDockerEngineStep(DockerStep):
    """Installs Docker Engine on Windows."""
    def __init__(self, worker):
        super().__init__("Installing Docker Engine", worker)
        self.service_registered = False

    def execute(self):
        """Install Docker Engine."""
        try:
            self.worker.log_message.emit("Installing Docker Engine...")
            # Example: Run Docker installer
            subprocess.run(["docker-installer.exe", "/quiet"], check=True)
            self.service_registered = True
        except Exception as e:
            self.worker.log_message.emit(f"Error during Docker Engine installation: {str(e)}")
            raise

    def rollback(self):
        """Roll back Docker Engine installation."""
        if self.service_registered:
            try:
                self.worker.log_message.emit("Rolling back Docker Engine installation...")
                subprocess.run(["sc", "delete", "docker"], check=False)
            except Exception as e:
                self.worker.log_message.emit(f"Warning: Failed to roll back Docker Engine: {str(e)}")
