import pytest
from core.scraper_engine import ProxyRotator, DataProcessor

@pytest.fixture
def mock_proxy_list():
    """Fixture providing a list of mock proxies for testing."""
    return [
        "http://proxy1:8080",
        "http://proxy2:8080",
        "http://proxy3:8080"
    ]

@pytest.fixture
def proxy_rotator(mock_proxy_list):
    """Fixture providing a ProxyRotator instance."""
    return ProxyRotator(mock_proxy_list)

@pytest.fixture
def data_processor():
    """Fixture providing a DataProcessor instance."""
    return DataProcessor()

@pytest.fixture
def mock_product_data():
    """Fixture providing mock product data for testing."""
    return {
        "id": "123",
        "name": "Test Product",
        "price": "100.00",
        "rating": "4.5",
        "seller": "Test Seller",
        "url": "https://tiktok.com/product/123"
    }

@pytest.fixture
def mock_creator_data():
    """Fixture providing mock creator data for testing."""
    return {
        "id": "creator123",
        "username": "testcreator",
        "name": "Test Creator",
        "followers": "1000",
        "following": "500",
        "bio": "Test bio",
        "url": "https://tiktok.com/@testcreator"
    }

@pytest.fixture
def mock_video_data():
    """Fixture providing mock video data for testing."""
    return [
        {
            "id": "video1",
            "creator_id": "creator123",
            "description": "Test video 1",
            "likes": "1000",
            "comments": "100",
            "shares": "50",
            "url": "https://tiktok.com/video/1"
        },
        {
            "id": "video2",
            "creator_id": "creator123",
            "description": "Test video 2",
            "likes": "2000",
            "comments": "200",
            "shares": "100",
            "url": "https://tiktok.com/video/2"
        }
    ] 