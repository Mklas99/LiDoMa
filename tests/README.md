# Docker Installation Tests

This directory contains various tests for the Docker installation functionality in LiDoMa. The tests are designed to validate the installation process without making any actual changes to your system.

## Test Components

### 1. Safe UI Testing
- **test_docker_installation.py**: A complete GUI test environment that simulates the Docker installation process without making any actual system changes. It provides visual feedback on what would happen during a real installation.
- **run_docker_install_test.bat**: Batch file to easily run the UI test environment.

### 2. System Compatibility Tests
- Inside the UI test is a "Run System Compatibility Check" feature that safely scans your system for Docker prerequisites.
- This test checks for WSL2 availability, disk space, permissions, and other requirements without making any changes.

### 3. Unit Testing
- **test_installer_components.py**: Contains unit tests for specific components of the Docker installation process, using mocks to avoid making system changes.

### 4. Container-based Testing
- **docker/Dockerfile.test_env**: Creates a Docker container for testing the installation code in an isolated environment.
- **run_test_in_container.py**: The test script that runs inside the Docker container.
- **run_container_test.bat**: Batch file to build the container and run the tests.

## Running the Tests

### UI Test
1. Execute `run_docker_install_test.bat` from the tests directory
2. In the UI, select a platform to test (Windows, macOS, Linux)
3. Choose between "Automatic" and "Custom" installation modes
4. Click the "Test XX Installation" button to run a full simulation
5. Alternatively, click "Run System Compatibility Check" to check your current system

### Unit Tests
```
python -m unittest tests/test_installer_components.py
```

### Container Tests
1. Ensure Docker is running on your system
2. Execute `run_container_test.bat` from the tests directory

## Safety Information

All tests in this directory are designed to be **safe to run** and will not modify your system or install Docker. The container test runs in an isolated Docker container, and the UI and unit tests use mock implementations that only simulate the installation process.

To run actual Docker installation, use the main application UI rather than these test tools.
