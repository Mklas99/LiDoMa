import subprocess
from .base import InstallationStep

class HomebrewInstallStep(InstallationStep):
    """Installs Homebrew on macOS."""
    def __init__(self, worker):
        super().__init__("Installing Homebrew", worker)
        self.homebrew_installed = False

    def execute(self):
        try:
            brew_path = subprocess.run(["which", "brew"], capture_output=True, text=True, check=False)
            if brew_path.returncode == 0:
                self.worker.log_message.emit("Homebrew is already installed")
                return
            self.worker.log_message.emit("Installing Homebrew...")
            subprocess.run(
                '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
                shell=True, check=True
            )
            self.homebrew_installed = True
        except Exception as e:
            self.worker.log_message.emit(f"Error installing Homebrew: {str(e)}")
            raise

    def rollback(self):
        if not self.homebrew_installed:
            self.worker.log_message.emit("Skipping Homebrew rollback as it wasn't installed by us")
            return
        self.worker.log_message.emit("Rolling back Homebrew installation...")
        subprocess.run(["brew", "uninstall", "--force", "brew"], check=False)

class DockerCLIInstallStep(InstallationStep):
    """Installs Docker CLI on macOS."""
    def execute(self):
        self.worker.log_message.emit("Installing Docker CLI...")
        subprocess.run(["brew", "install", "docker"], check=True)

    def rollback(self):
        self.worker.log_message.emit("Rolling back Docker CLI installation...")
        subprocess.run(["brew", "uninstall", "docker"], check=False)

class ColimaInstallStep(InstallationStep):
    """Installs Colima on macOS."""
    def execute(self):
        self.worker.log_message.emit("Installing Colima...")
        subprocess.run(["brew", "install", "colima"], check=True)

    def rollback(self):
        self.worker.log_message.emit("Rolling back Colima installation...")
        subprocess.run(["brew", "uninstall", "colima"], check=False)

class ColimaStartStep(InstallationStep):
    """Starts Colima and configures auto-start."""
    def execute(self):
        self.worker.log_message.emit("Starting Colima...")
        subprocess.run(["colima", "start"], check=True)
        self.worker.log_message.emit("Configuring Colima auto-start...")
        subprocess.run(["colima", "autostart"], check=True)

    def rollback(self):
        self.worker.log_message.emit("Rolling back Colima start...")
        subprocess.run(["colima", "stop"], check=False)

class DesktopDownloadStep(InstallationStep):
    """Downloads Docker Desktop DMG."""
    def __init__(self, worker):
        super().__init__("Downloading Docker Desktop", worker)
        self.dmg_path = None

    def execute(self):
        self.dmg_path = "/tmp/Docker.dmg"
        self.worker.log_message.emit("Downloading Docker Desktop DMG...")
        subprocess.run(
            ["curl", "-L", "-o", self.dmg_path, "https://desktop.docker.com/mac/main/amd64/Docker.dmg"],
            check=True
        )

    def rollback(self):
        if self.dmg_path and os.path.exists(self.dmg_path):
            self.worker.log_message.emit("Removing downloaded Docker Desktop DMG...")
            os.remove(self.dmg_path)

class DesktopInstallStep(InstallationStep):
    """Installs Docker Desktop from DMG."""
    def execute(self):
        self.worker.log_message.emit("Mounting Docker Desktop DMG...")
        subprocess.run(["hdiutil", "attach", "/tmp/Docker.dmg"], check=True)
        self.worker.log_message.emit("Copying Docker Desktop to Applications folder...")
        subprocess.run(["cp", "-R", "/Volumes/Docker/Docker.app", "/Applications/"], check=True)
        self.worker.log_message.emit("Unmounting Docker Desktop DMG...")
        subprocess.run(["hdiutil", "detach", "/Volumes/Docker"], check=True)

    def rollback(self):
        self.worker.log_message.emit("Removing Docker Desktop from Applications folder...")
        subprocess.run(["rm", "-rf", "/Applications/Docker.app"], check=False)
