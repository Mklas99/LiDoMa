@echo off
echo Running Docker Installation Test Environment
echo This is a safe test that will NOT modify your system

cd ..
python -u tests\test_docker_installation.py 2> tests\docker_test_error.log

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Test crashed. See tests\docker_test_error.log for details.
    notepad tests\docker_test_error.log
)

pause
