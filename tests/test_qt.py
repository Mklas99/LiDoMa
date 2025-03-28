import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

def main():
    """Test if PyQt is working correctly"""
    print("Starting PyQt test...")
    app = QApplication(sys.argv)
    
    # Create a simple window
    window = QMainWindow()
    window.setWindowTitle("PyQt Test")
    window.setGeometry(100, 100, 400, 200)
    
    # Add a label
    label = QLabel("If you can see this, PyQt is working correctly!", window)
    label.setGeometry(50, 50, 300, 100)
    
    # Show the window
    window.show()
    print("Window should now be visible.")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
