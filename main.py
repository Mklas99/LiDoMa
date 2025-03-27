import sys
import os
from PyQt5.QtWidgets import QApplication
from ui import DockerManagerApp

def main():
    """Main entry point for the Docker Manager application."""
    app = QApplication(sys.argv)
    
    # Load style from QSS file
    style_path = os.path.join(os.path.dirname(__file__), "ui", "style.qss")
    try:
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Error loading style: {e}")
    
    window = DockerManagerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
