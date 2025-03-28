import pytest
from app.core.services.service_locator import ServiceLocator

def test_service_locator_initialization():
    """Test that ServiceLocator initializes all services correctly."""
    locator = ServiceLocator()
    
    # Test retrieval of services
    assert locator.get_docker_service() is not None
    assert locator.get_container_service() is not None
    assert locator.get_image_service() is not None
    assert locator.get_volume_service() is not None
    assert locator.get_network_service() is not None
    assert locator.get_context_service() is not None
    assert locator.get_compose_service() is not None
    
    # Test singleton pattern
    locator2 = ServiceLocator()
    assert locator is locator2, "ServiceLocator should be a singleton"
