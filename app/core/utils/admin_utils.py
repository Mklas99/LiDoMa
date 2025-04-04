"""
Utility functions for admin privilege operations.
"""
import ctypes
import sys
import platform

def is_admin():
    """Check if the process has admin privileges."""
    try:
        if platform.system().lower() == "windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # For Unix systems, 0 uid is root
            import os
            return os.geteuid() == 0
    except:
        return False

def request_admin_privileges():
    """
    Restart the program with admin privileges.
    
    Returns:
        bool: True if already running with admin privileges, 
              False if the program was restarted with elevated privileges
    """
    if is_admin():
        return True
        
    if platform.system().lower() == "windows":
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, 
            " ".join(sys.argv), None, 1
        )
        return False
    else:
        # For Unix systems, we would typically use sudo
        # But this is more complex and platform-specific
        return False
