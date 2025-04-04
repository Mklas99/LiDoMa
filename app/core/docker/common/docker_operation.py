class DockerOperation:
    """Base class for Docker operations like installation or uninstallation."""
    
    def __init__(self, worker):
        self.worker = worker
        self.steps = []
        self.completed_steps = []
        self.resources = []  # Track all resources created
    
    def add_step(self, step):
        """Add an operation step."""
        self.steps.append(step)
        step.operation = self  # Give step access to operation
    
    def register_resource(self, resource_path):
        """Register a resource for cleanup."""
        self.resources.append(resource_path)
        
    def execute(self):
        """Execute all steps with rollback on failure and consistent cancellation checks."""
        try:
            for step in self.steps:
                if self.worker.cancelled:
                    self.worker.log_message.emit("Operation cancelled by user.")
                    self.rollback()
                    return False, "Operation cancelled by user"
                
                self.worker.log_message.emit(f"Executing step: {step.description}")
                step.execute()
                step.completed = True
                self.completed_steps.append(step)
            return True, "Operation completed successfully"
        except Exception as e:
            self.worker.log_message.emit(f"ERROR: {str(e)}")
            self.rollback()
            return False, f"Operation failed: {str(e)}"
        finally:
            self.cleanup()
    
    def rollback(self):
        """Roll back all completed steps in reverse order."""
        self.worker.log_message.emit("Rolling back operation...")
        for step in reversed(self.completed_steps):
            try:
                self.worker.log_message.emit(f"Rolling back step: {step.description}")
                step.rollback()
            except Exception as e:
                self.worker.log_message.emit(f"Warning: Error during rollback of {step.description}: {str(e)}")
        
        # Verify system state after rollback
        self.verify_system_state()

    def verify_system_state(self):
        """Verify the system state after rollback."""
        self.worker.log_message.emit("Verifying system state after rollback...")
        try:
            # Example: Check if Docker services are stopped
            if shutil.which("docker"):
                result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    self.worker.log_message.emit("Warning: Docker containers are still running after rollback")
        except Exception as e:
            self.worker.log_message.emit(f"Warning: System verification failed: {str(e)}")

    def cleanup(self):
        """Clean up all registered resources."""
        for resource in self.resources:
            if os.path.exists(resource):
                try:
                    if os.path.isfile(resource):
                        os.remove(resource)
                    else:
                        shutil.rmtree(resource)
                    self.worker.log_message.emit(f"Cleaned up resource: {resource}")
                except Exception as e:
                    self.worker.log_message.emit(f"Warning: Failed to clean up {resource}: {str(e)}")
