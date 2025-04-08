import pytest
from unittest.mock import patch, MagicMock
from core.scraper_engine import Scraper, ProxyRotator, DataProcessor

@pytest.fixture
def proxy_rotator():
    return ProxyRotator([])

@pytest.fixture
def data_processor():
    return DataProcessor()

@patch('requests.Session')
def test_scraper_initialization(mock_session, proxy_rotator):
    """Test Scraper initialization."""
    scraper = Scraper(proxy_rotator=proxy_rotator)
    assert scraper.proxy_rotator == proxy_rotator
    assert isinstance(scraper.data_processor, DataProcessor)

@patch('requests.Session')
def test_make_request_success(mock_session, proxy_rotator):
    """Test successful request making."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>Test content</html>"
    mock_response.headers = {'Content-Type': 'text/html'}
    mock_session.return_value.request.return_value = mock_response

    scraper = Scraper(proxy_rotator=proxy_rotator)
    response = scraper._make_request("http://test.com")
    
    assert response == mock_response
    mock_session.return_value.request.assert_called_once()

@patch('requests.Session')
def test_make_request_retry(mock_session, proxy_rotator):
    """Test request retry mechanism."""
    mock_response_fail = MagicMock()
    mock_response_fail.status_code = 500
    mock_response_fail.raise_for_status.side_effect = Exception("Server Error")

    mock_response_success = MagicMock()
    mock_response_success.status_code = 200
    mock_response_success.text = "<html>Success</html>"
    mock_response_success.headers = {'Content-Type': 'text/html'}

    mock_session.return_value.request.side_effect = [
        mock_response_fail,
        mock_response_fail,
        mock_response_success
    ]

    scraper = Scraper(proxy_rotator=proxy_rotator)
    response = scraper._make_request("http://test.com")
    
    assert response == mock_response_success
    assert mock_session.return_value.request.call_count == 3

@patch('requests.Session')
def test_scrape_product(mock_session, proxy_rotator, mock_product_data):
    """Test product scraping functionality."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>Product page</html>"
    mock_response.headers = {'Content-Type': 'text/html'}
    mock_session.return_value.request.return_value = mock_response

    scraper = Scraper(proxy_rotator=proxy_rotator)
    result = scraper.scrape_product("123")
    
    assert result is not None
    mock_session.return_value.request.assert_called_once()

@patch('requests.Session')
def test_scrape_creator(mock_session, proxy_rotator, mock_creator_data):
    """Test creator scraping functionality."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>Creator page</html>"
    mock_response.headers = {'Content-Type': 'text/html'}
    mock_session.return_value.request.return_value = mock_response

    scraper = Scraper(proxy_rotator=proxy_rotator)
    result = scraper.scrape_creator("creator123")
    
    assert result is not None
    mock_session.return_value.request.assert_called_once()

@patch('requests.Session')
def test_scrape_videos(mock_session, proxy_rotator, mock_video_data):
    """Test video scraping functionality."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>Videos page</html>"
    mock_response.headers = {'Content-Type': 'text/html'}
    mock_session.return_value.request.return_value = mock_response

    scraper = Scraper(proxy_rotator=proxy_rotator)
    result = scraper.scrape_videos("creator123")
    
    assert result is not None
    mock_session.return_value.request.assert_called_once()

@patch('requests.Session')
def test_scrape_batch(mock_session, proxy_rotator):
    """Test batch scraping functionality."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>Test page</html>"
    mock_response.headers = {'Content-Type': 'text/html'}
    mock_session.return_value.request.return_value = mock_response

    scraper = Scraper(proxy_rotator=proxy_rotator)
    items = ["item1", "item2"]
    results = scraper.scrape_batch(items, "product")
    
    assert isinstance(results, list)
    assert mock_session.return_value.request.call_count == len(items)

@patch('requests.Session')
def test_error_handling(mock_session, proxy_rotator):
    """Test error handling in scraper."""
    mock_session.return_value.request.side_effect = Exception("Test error")

    scraper = Scraper(proxy_rotator=proxy_rotator)
    result = scraper._make_request("http://test.com")
    
    assert result is None
    assert mock_session.return_value.request.call_count == 3  # Max retries 