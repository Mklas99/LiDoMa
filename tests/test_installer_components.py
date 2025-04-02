import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ui.dialogs.docker_installation_progress_dialog import InstallationWorker

"""
Unit Tests for Docker Installation Components

This module contains unit tests for specific components of the Docker installation process.
These tests use mocking to avoid making any actual system changes while testing the logic
of individual installation functions.

Testing approach:
- Uses Python's unittest framework
- Mocks system calls and external dependencies
- Tests individual components in isolation
- Verifies correct handling of different scenarios (like WSL2 being present/absent)

Run with: python -m unittest tests/test_installer_components.py
"""

class TestInstallationWorker(unittest.TestCase):
    """Test specific components of the installation process."""

    @patch('subprocess.run')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_windows_wsl_check(self, mock_exists, mock_makedirs, mock_subprocess_run):
        """Test the WSL2 checking functionality."""
        # Mock subprocess.run to simulate WSL2 being installed
        mock_process = MagicMock()
        mock_process.stdout = "WSL 2 is installed and running"
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process
        
        # Create worker and run just the WSL check part
        worker = InstallationWorker({"platform": "windows", "use_wsl2": True})
        
        # Add a mock for log_message to avoid attribute error
        worker.log_message = MagicMock()
        worker.progress_updated = MagicMock()
        
        # Test that WSL2 detection works
        result = worker._check_wsl2_status()
        self.assertTrue(result)
        
        # Now mock WSL2 not being installed
        mock_process.stdout = "WSL is not installed"
        mock_subprocess_run.return_value = mock_process
        
        result = worker._check_wsl2_status()
        self.assertFalse(result)

    # Add missing method to test
    def _check_wsl2_status(self):
        """Check if WSL2 is installed and configured correctly."""
        try:
            result = subprocess.run(
                ["wsl", "--status"], 
                capture_output=True, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.log_message(f"WSL status check result: {result.returncode}")
            
            if "WSL 2" in result.stdout or "WSL 2" in result.stderr:
                self.log_message("WSL2 appears to be installed")
                return True
            else:
                self.log_message("WSL2 not detected")
                return False
        except Exception as e:
            self.log_message(f"WSL check failed: {str(e)}")
            return False

# Additional test cases can be added for other components

if __name__ == '__main__':
    unittest.main()
