import shutil
from app.core.docker.common.docker_operation import DockerOperation

class InstallationStepManager(DockerOperation):
    """Manages and tracks installation steps."""
    def __init__(self, worker):
        self.worker = worker
        self.steps = []
        self.completed_steps = []

    def add_step(self, step):
        """Add a step to the installation process."""
        self.steps.append(step)

    def execute_steps(self):
        """Execute all steps in sequence with rollback on failure."""
        try:
            total_steps = len(self.steps)
            for i, step in enumerate(self.steps):
                if self.worker.cancelled:
                    self.rollback_steps()
                    return False, "Installation cancelled by user"
                
                # Update progress and log step execution
                progress = int((i / total_steps) * 100)
                self.worker.progress_updated.emit(progress, f"Executing: {step.description}")
                self.worker.log_message.emit(f"Starting step: {step.description}")
                
                # Execute step and mark as completed
                step.execute()
                step.completed = True
                self.completed_steps.append(step)
                
            return True, "Installation completed successfully"
        except FileNotFoundError as e:
            self.worker.log_message.emit(f"ERROR: Missing file or dependency: {str(e)}")
            self.rollback_steps()
            return False, "Installation failed due to missing file or dependency."
        except subprocess.CalledProcessError as e:
            self.worker.log_message.emit(f"ERROR: Command execution failed: {str(e)}")
            self.rollback_steps()
            return False, "Installation failed due to a command execution error."
        except Exception as e:
            import traceback
            self.worker.log_message.emit(f"ERROR: {str(e)}")
            self.worker.log_message.emit(traceback.format_exc())
            self.rollback_steps()
            return False, f"Installation failed: {str(e)}"

    def rollback_steps(self):
        """Roll back all completed steps in reverse order with progress reporting."""
        if not self.completed_steps:
            return
        
        self.worker.progress_updated.emit(0, "Rolling back failed installation...")
        total_steps = len(self.completed_steps)
        
        for i, step in enumerate(reversed(self.completed_steps)):
            progress = int((i / total_steps) * 100)
            self.worker.progress_updated.emit(progress, f"Rolling back: {step.description}")
            try:
                self.worker.log_message.emit(f"Rolling back: {step.description}")
                step.rollback()
            except Exception as e:
                self.worker.log_message.emit(f"Warning: Error during rollback of {step.description}: {str(e)}")

        self.verify_system_state()

    def verify_system_state(self):
        """Verify the system state after rollback."""
        self.worker.log_message.emit("Verifying system state after rollback...")
        try:
            # Example: Check if Docker services are stopped
            if shutil.which("docker"):
                result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    self.worker.log_message.emit("Warning: Docker containers are still running after rollback.")
        except NameError as e:
            self.worker.log_message.emit(f"System verification failed: Missing module - {str(e)}")
        except Exception as e:
            self.worker.log_message.emit(f"Warning: System verification failed: {str(e)}")
