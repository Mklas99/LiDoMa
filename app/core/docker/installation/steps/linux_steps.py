import os
import subprocess
import tempfile
from .base import InstallationStep

class DetectDistroStep(InstallationStep):
    """Detects Linux distribution."""
    def __init__(self, worker):
        super().__init__("Detecting Linux Distribution", worker)
        self.distro = None
    
    def execute(self):
        """Detect the Linux distribution."""
        self.worker.log_message.emit("Detecting Linux distribution...")
        self.distro = self._get_linux_distro()
        if not self.distro or self.distro == "unknown":
            self.worker.log_message.emit("ERROR: Could not determine Linux distribution")
            raise Exception("Could not determine Linux distribution")
        self.worker.log_message.emit(f"Detected Linux distribution: {self.distro}")
        return self.distro
    
    def rollback(self):
        """Nothing to roll back for detection."""
        pass
    
    def _get_linux_distro(self):
        """Helper method to detect the Linux distribution."""
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("ID="):
                            return line.split("=")[1].strip().strip('"')
            
            # Fallbacks
            if os.path.exists("/etc/debian_version"):
                return "debian"
            elif os.path.exists("/etc/fedora-release"):
                return "fedora"
            elif os.path.exists("/etc/centos-release"):
                return "centos"
            elif os.path.exists("/etc/redhat-release"):
                return "rhel"
                
            return "unknown"
        except:
            return "unknown"

class DockerPackageStep(InstallationStep):
    """Installs Docker packages on Linux."""
    def __init__(self, worker, distro, add_user=True, auto_start=True):
        super().__init__("Installing Docker Packages", worker)
        self.distro = distro
        self.add_user = add_user
        self.auto_start = auto_start
        self.installation_script = None
        self.installation_successful = False
    
    def execute(self):
        """Install Docker packages based on the distribution."""
        self.worker.log_message.emit("Preparing Docker installation...")
        
        # Create installation script
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".sh") as script_file:
            self.installation_script = script_file.name
            
            script_file.write("#!/bin/bash\n")
            script_file.write("set -e\n\n")
            script_file.write("echo 'Starting Docker installation...'\n\n")
            
            if self.distro in ["ubuntu", "debian"]:
                # Ubuntu/Debian installation
                self._write_debian_script(script_file)
            elif self.distro in ["fedora", "centos", "rhel"]:
                # Fedora/CentOS/RHEL installation
                self._write_fedora_script(script_file)
            else:
                # Generic Linux installation
                self._write_generic_script(script_file)
                
            script_file.write("\necho 'Docker installation completed successfully'\n")
        
        # Make script executable
        os.chmod(self.installation_script, 0o755)
        
        # Run script with sudo
        self.worker.log_message.emit("Installing Docker (requires sudo)...")
        
        try:
            with subprocess.Popen(
                ["sudo", self.installation_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            ) as process:
                
                for line in process.stdout:
                    self.worker.log_message.emit(line.strip())
                    if self.worker.cancelled:
                        process.terminate()
                        raise Exception("Installation cancelled by user")
                
                # Wait for process to complete and check return code
                process.wait()
                if process.returncode != 0:
                    error_output = process.stderr.read()
                    self.worker.log_message.emit(f"ERROR: Installation failed: {error_output}")
                    raise Exception(f"Installation failed with code {process.returncode}")
                
                self.installation_successful = True
        finally:
            # Clean up script
            if os.path.exists(self.installation_script):
                os.unlink(self.installation_script)
    
    def rollback(self):
        """Roll back the Docker installation."""
        if not self.installation_successful:
            self.worker.log_message.emit("Skipping Docker uninstallation as installation didn't complete")
            return
        
        self.worker.log_message.emit("Rolling back Docker installation...")
        
        # Create uninstallation script
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".sh") as script_file:
            uninstall_script = script_file.name
            
            script_file.write("#!/bin/bash\n")
            script_file.write("set -e\n\n")
            script_file.write("echo 'Uninstalling Docker...'\n\n")
            
            if self.distro in ["ubuntu", "debian"]:
                script_file.write("apt-get remove -y docker-ce docker-ce-cli containerd.io\n")
                script_file.write("apt-get purge -y docker-ce docker-ce-cli containerd.io\n")
                script_file.write("apt-get autoremove -y\n")
            elif self.distro in ["fedora", "centos", "rhel"]:
                script_file.write("dnf remove -y docker-ce docker-ce-cli containerd.io\n")
            else:
                script_file.write("# Generic uninstall\n")
                script_file.write("if command -v docker > /dev/null; then\n")
                script_file.write("    systemctl stop docker 2>/dev/null || true\n")
                script_file.write("    which docker-compose && rm -f $(which docker-compose) || true\n")
                script_file.write("    which docker && rm -f $(which docker) || true\n")
                script_file.write("fi\n")
            
            script_file.write("\necho 'Docker uninstallation completed'\n")
        
        # Make script executable
        os.chmod(uninstall_script, 0o755)
        
        try:
            # Run uninstallation script with sudo
            with subprocess.Popen(
                ["sudo", uninstall_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            ) as process:
                for line in process.stdout:
                    self.worker.log_message.emit(line.strip())
                process.wait()
        except Exception as e:
            self.worker.log_message.emit(f"Warning: Error during Docker uninstallation: {str(e)}")
        finally:
            # Clean up uninstallation script
            if os.path.exists(uninstall_script):
                os.unlink(uninstall_script)
    
    def _write_debian_script(self, script_file):
        """Write Debian/Ubuntu-specific installation script."""
        script_file.write("""
# Remove old versions if any
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Update apt repos
apt-get update

# Install dependencies
apt-get install -y \\
    apt-transport-https \\
    ca-certificates \\
    curl \\
    gnupg \\
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \\
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Configure Docker to start on boot
systemctl enable docker
""")
        
        # Add user to docker group if needed
        if self.add_user:
            script_file.write("""
# Add current user to docker group
usermod -aG docker $SUDO_USER
""")
        
        # Start Docker if needed
        if self.auto_start:
            script_file.write("""
# Start Docker service
systemctl start docker
""")
    
    def _write_fedora_script(self, script_file):
        """Write Fedora/CentOS/RHEL-specific installation script."""
        script_file.write("""
# Remove old versions if any
dnf remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine podman 2>/dev/null || true

# Install required packages
dnf -y install dnf-plugins-core

# Add Docker repo
dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

# Install Docker
dnf install -y docker-ce docker-ce-cli containerd.io

# Configure Docker to start on boot
systemctl enable docker
""")
        
        # Add user to docker group if needed
        if self.add_user:
            script_file.write("""
# Add current user to docker group
usermod -aG docker $SUDO_USER
""")
        
        # Start Docker if needed
        if self.auto_start:
            script_file.write("""
# Start Docker service
systemctl start docker
""")
    
    def _write_generic_script(self, script_file):
        """Write generic Linux installation script."""
        script_file.write("""
# Using convenience script for other distributions
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Configure Docker to start on boot
systemctl enable docker 2>/dev/null || true
""")
        
        # Add user to docker group if needed
        if self.add_user:
            script_file.write("""
# Add current user to docker group
usermod -aG docker $SUDO_USER 2>/dev/null || usermod -aG docker $USER
""")
        
        # Start Docker if needed
        if self.auto_start:
            script_file.write("""
# Start Docker service
systemctl start docker 2>/dev/null || service docker start
""")

class DockerVerificationStep(InstallationStep):
    """Verifies Docker installation on Linux."""
    def __init__(self, worker, add_user=True):
        super().__init__("Verifying Docker Installation", worker)
        self.add_user = add_user
    
    def execute(self):
        """Verify Docker installation."""
        self.worker.log_message.emit("Verifying Docker installation...")
        
        try:
            if self.add_user:
                self.worker.log_message.emit("Docker was installed successfully, but you may need to log out and log back in to use it without sudo")
            else:
                # Try to verify with sudo
                result = subprocess.run(
                    ["sudo", "docker", "--version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.worker.log_message.emit(f"Docker verified: {result.stdout.strip()}")
        except Exception as e:
            self.worker.log_message.emit(f"WARNING: Docker installation verification failed: {str(e)}")
            self.worker.log_message.emit("You might need to restart your system to complete the installation.")
    
    def rollback(self):
        """Roll back verification by stopping Docker services if needed."""
        self.worker.log_message.emit("Rolling back Docker verification...")
        try:
            subprocess.run(["sudo", "systemctl", "stop", "docker"], check=False)
            self.worker.log_message.emit("Docker service stopped during rollback.")
        except Exception as e:
            self.worker.log_message.emit(f"Warning: Failed to stop Docker service during rollback: {str(e)}")
