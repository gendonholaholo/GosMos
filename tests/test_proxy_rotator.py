import pytest
from unittest.mock import patch
from core.scraper_engine import ProxyRotator

def test_proxy_rotator_initialization(mock_proxy_list):
    """Test ProxyRotator initialization with proxy list."""
    rotator = ProxyRotator(mock_proxy_list)
    assert rotator.proxy_list == mock_proxy_list
    assert rotator.current_index == 0

def test_get_next_proxy_rotation(mock_proxy_list):
    """Test proxy rotation functionality."""
    rotator = ProxyRotator(mock_proxy_list)
    
    # Test first rotation
    proxy1 = rotator.get_next_proxy()
    assert proxy1 == mock_proxy_list[0]
    assert rotator.current_index == 1
    
    # Test second rotation
    proxy2 = rotator.get_next_proxy()
    assert proxy2 == mock_proxy_list[1]
    assert rotator.current_index == 2
    
    # Test wrap-around
    proxy3 = rotator.get_next_proxy()
    proxy4 = rotator.get_next_proxy()
    assert proxy3 == mock_proxy_list[2]
    assert proxy4 == mock_proxy_list[0]

def test_empty_proxy_list():
    """Test ProxyRotator with empty proxy list."""
    rotator = ProxyRotator([])
    assert rotator.get_next_proxy() is None

def test_proxy_validation():
    """Test proxy validation functionality."""
    invalid_proxies = [
        "invalid_proxy",
        "http://",
        "https://proxy:invalid_port"
    ]
    
    with pytest.raises(ValueError):
        ProxyRotator(invalid_proxies)

def test_proxy_rotation_with_invalid_proxy(mock_proxy_list):
    """Test proxy rotation when some proxies are invalid."""
    mixed_proxies = mock_proxy_list + ["invalid_proxy"]
    
    with pytest.raises(ValueError):
        ProxyRotator(mixed_proxies)

@patch('requests.get')
def test_proxy_validation_with_requests(mock_get, mock_proxy_list):
    """Test proxy validation using mock requests."""
    mock_get.return_value.status_code = 200
    
    rotator = ProxyRotator(mock_proxy_list)
    assert rotator.validate_proxy(mock_proxy_list[0]) is True

@patch('requests.get')
def test_proxy_validation_failure(mock_get):
    """Test proxy validation failure."""
    mock_get.return_value.status_code = 403
    
    rotator = ProxyRotator(["http://test:8080"])
    assert rotator.validate_proxy("http://test:8080") is False 