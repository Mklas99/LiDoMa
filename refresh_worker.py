from PyQt5.QtCore import QThread, pyqtSignal

class RefreshWorker(QThread):
    """Worker thread to retrieve Docker data asynchronously."""
    # Signal to deliver the list of containers, images, volumes, networks and any error messages.
    results_ready = pyqtSignal(list, list, list, list, str)

    def __init__(self, docker_service):
        super().__init__()
        self.docker_service = docker_service

    def run(self):
        all_containers = []
        all_images = []
        all_volumes = []
        all_networks = []
        errors = ""
        
        # Get contexts
        contexts, ctx_err = self.docker_service.get_docker_contexts()
        if ctx_err:
            errors += f"Error retrieving contexts: {ctx_err}\n"
            
        # Always include the default context
        if "default" not in contexts:
            contexts.append("default")
            
        for context in contexts:
            # Get containers
            try:
                containers = self.docker_service.list_containers(all_containers=True, context=context)
                all_containers.extend(containers)
            except Exception as e:
                errors += f"Error fetching containers for context '{context}': {e}\n"
            
            # Get images
            try:
                images = self.docker_service.list_images(context=context)
                all_images.extend(images)
            except Exception as e:
                errors += f"Error fetching images for context '{context}': {e}\n"
            
            # Get volumes
            try:
                volumes = self.docker_service.list_volumes(context=context)
                all_volumes.extend(volumes)
            except Exception as e:
                errors += f"Error fetching volumes for context '{context}': {e}\n"
            
            # Get networks
            try:
                networks = self.docker_service.list_networks(context=context)
                all_networks.extend(networks)
            except Exception as e:
                errors += f"Error fetching networks for context '{context}': {e}\n"
            
        self.results_ready.emit(all_containers, all_images, all_volumes, all_networks, errors)
