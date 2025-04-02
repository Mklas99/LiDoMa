@echo off
echo Building test container...
docker build -t docker-installer-test -f tests/docker/Dockerfile.test_env .

echo Running installation tests in container...
docker run --rm -v "%cd%:/app" docker-installer-test

echo Test completed.
pause
