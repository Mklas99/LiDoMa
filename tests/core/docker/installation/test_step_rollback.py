import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import subprocess
import platform

from app.core.docker.installation.step_manager import InstallationStepManager
from app.core.docker.installation.steps.base import InstallationStep
from app.core.docker.installation.steps.windows_steps import WindowsWSL2Step
from app.core.docker.installation.steps.mac_steps import (
    HomebrewInstallStep, DockerCLIInstallStep, ColimaInstallStep,
    ColimaStartStep, DesktopDownloadStep, DesktopInstallStep
)

class MockWorker:
    """Mock worker for testing."""
    def __init__(self):
        self.cancelled = False
        self.progress_updated = MagicMock()
        self.log_message = MagicMock()
        self.installation_completed = MagicMock()

class TestStepRollback(unittest.TestCase):
    """Test rollback functionality of installation steps."""
    
    def setUp(self):
        """Set up test environment."""
        self.worker = MockWorker()
        self.step_manager = InstallationStepManager(self.worker)
    
    def test_step_manager_execution(self):
        """Test step manager executes steps in order."""
        # Create mock steps
        step1 = MagicMock(spec=InstallationStep)
        step1.description = "Step 1"
        step1.completed = False
        
        step2 = MagicMock(spec=InstallationStep)
        step2.description = "Step 2"
        step2.completed = False
        
        # Add steps to manager
        self.step_manager.add_step(step1)
        self.step_manager.add_step(step2)
        
        # Execute steps
        success, message = self.step_manager.execute_steps()
        
        # Verify steps were executed in order
        step1.execute.assert_called_once()
        step2.execute.assert_called_once()
        self.assertTrue(success)
        self.assertEqual(message, "Installation completed successfully")
    
    def test_rollback_on_failure(self):
        """Test rollback happens when a step fails."""
        # Create mock steps
        step1 = MagicMock(spec=InstallationStep)
        step1.description = "Step 1"
        step1.completed = False
        
        step2 = MagicMock(spec=InstallationStep)
        step2.description = "Step 2"
        step2.completed = False
        step2.execute.side_effect = Exception("Step failed")
        
        # Add steps to manager
        self.step_manager.add_step(step1)
        self.step_manager.add_step(step2)
        
        # Execute steps
        success, message = self.step_manager.execute_steps()
        
        # Verify step 1 was executed and rolled back
        step1.execute.assert_called_once()
        step1.rollback.assert_called_once()
        
        # Verify step 2 execution was attempted but rollback was not called
        step2.execute.assert_called_once()
        step2.rollback.assert_not_called()
        
        # Verify failure was reported
        self.assertFalse(success)
        self.assertTrue(message.startswith("Installation failed"))
    
    def test_early_termination_on_cancel(self):
        """Test that steps stop and roll back when cancelled."""
        # Create mock steps
        step1 = MagicMock(spec=InstallationStep)
        step1.description = "Step 1"
        step1.completed = False
        
        step2 = MagicMock(spec=InstallationStep)
        step2.description = "Step 2"
        step2.completed = False
        
        # Set worker to cancelled state after step 1
        def set_cancelled(*args, **kwargs):
            self.worker.cancelled = True
        
        step1.execute.side_effect = set_cancelled
        
        # Add steps to manager
        self.step_manager.add_step(step1)
        self.step_manager.add_step(step2)
        
        # Execute steps
        success, message = self.step_manager.execute_steps()
        
        # Verify first step executed and rolled back
        step1.execute.assert_called_once()
        step1.rollback.assert_called_once()
        
        # Verify second step never executed
        step2.execute.assert_not_called()
        
        # Verify cancellation was reported
        self.assertFalse(success)
        self.assertEqual(message, "Installation cancelled by user")

    @unittest.skipIf(platform.system().lower() != "windows", "Windows-specific test")
    @patch("subprocess.run")
    def test_windows_wsl2_step(self, mock_run):
        """Test Windows WSL2 step execution and rollback."""
        # Mock the subprocess.run to simulate WSL not being installed
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        
        # Create and execute the WSL2 step
        wsl_step = WindowsWSL2Step(self.worker)
        wsl_step.execute()
        
        # Verify commands were executed to enable WSL2
        self.assertEqual(mock_run.call_count, 4)  # Status check + 3 setup commands
        
        # Test rollback
        wsl_step.rollback()
        
        # Verify log message about not disabling WSL2
        self.worker.log_message.assert_called_with(
            "Note: Not disabling WSL2 as it may be needed by other applications"
        )

    @unittest.skipIf(platform.system().lower() != "darwin", "macOS-specific test")
    @patch("subprocess.run")
    def test_mac_steps_execution_and_rollback(self, mock_run):
        """Test macOS steps execution and rollback."""
        # Configure mock to simulate successful commands
        mock_run.return_value.returncode = 0
        
        # Test Homebrew installation
        homebrew_step = HomebrewInstallStep(self.worker)
        homebrew_step.homebrew_installed = True  # Simulate successful installation
        homebrew_step.rollback()
        
        # Verify homebrew uninstall was called
        uninstall_call = any(
            args[0][0] == "brew" and "uninstall" in args[0] 
            for args, _ in mock_run.call_args_list
        )
        self.assertTrue(uninstall_call)
        
        # Reset mock to test other steps
        mock_run.reset_mock()
        
        # Test Docker CLI step
        docker_cli_step = DockerCLIInstallStep(self.worker)
        docker_cli_step.execute()
        docker_cli_step.rollback()
        
        # Verify Docker CLI install and uninstall
        install_call = any(
            args[0][0:2] == ["brew", "install"] and "docker" in args[0]
            for args, _ in mock_run.call_args_list
        )
        uninstall_call = any(
            args[0][0:2] == ["brew", "uninstall"] and "docker" in args[0]
            for args, _ in mock_run.call_args_list
        )
        self.assertTrue(install_call)
        self.assertTrue(uninstall_call)

if __name__ == "__main__":
    unittest.main()
