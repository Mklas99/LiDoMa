class DockerStep:
    """Base class for Docker steps with execute and rollback functionality."""
    def __init__(self, description, worker):
        self.description = description
        self.worker = worker
        self.completed = False

    def execute(self):
        """Execute the step."""
        raise NotImplementedError("Subclasses must implement execute()")

    def rollback(self):
        """Roll back the step."""
        raise NotImplementedError("Subclasses must implement rollback()")

class InstallationStep(DockerStep):
    """Base class for installation steps that can be executed and rolled back."""
    def __init__(self, description, worker):
        super().__init__(description, worker)
        self.prerequisites = []

    def execute(self):
        """Execute the installation step."""
        raise NotImplementedError("Subclasses must implement execute()")

    def rollback(self):
        """Roll back the installation step if it was completed."""
        raise NotImplementedError("Subclasses must implement rollback()")
