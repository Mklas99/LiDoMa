"""
Main entry point for the Docker Manager application.
"""
import sys
import os
from pathlib import Path

# Ensure the project root is in the Python path
# This helps Python find the 'app' package
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from app.ui.viewmodels import MainViewModel
from app.core.services.service_locator import ServiceLocator
from app.ui.main_window import DockerManagerApp
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    
    try:
        # Initialize services
        service_locator = ServiceLocator()
        docker_service = service_locator.get_docker_service()
        
        # Create main view model with the docker service
        main_vm = MainViewModel(docker_service)
        
        # Create and show main window with main_vm
        window = DockerManagerApp(main_vm)
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        from PyQt5.QtWidgets import QMessageBox
        error_msg = f"Error starting application: {str(e)}"
        print(error_msg)
        QMessageBox.critical(None, "Application Error", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
