import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
import concurrent.futures
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from .proxy_rotator import ProxyRotator
from .data_processor import DataProcessor

class Scraper:
    """Main scraper class for handling data extraction."""
    
    def __init__(self, proxy_rotator: Optional[ProxyRotator] = None, 
                 logger: Optional[logging.Logger] = None,
                 max_retries: int = 3,
                 retry_delay: int = 5,
                 timeout: int = 30):
        self.logger = logger or logging.getLogger(__name__)
        self.proxy_rotator = proxy_rotator
        self.data_processor = DataProcessor(logger)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        
        # Initialize session with retry strategy
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create and configure requests session with retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Configure session
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
        return session
        
    def _make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with proxy rotation and retry logic."""
        try:
            # Configure proxy if available
            if self.proxy_rotator:
                proxy = self.proxy_rotator.get_next_proxy()
                if proxy:
                    proxy_url = f"{proxy['protocol']}://"
                    if proxy['username'] and proxy['password']:
                        proxy_url += f"{proxy['username']}:{proxy['password']}@"
                    proxy_url += f"{proxy['host']}:{proxy['port']}"
                    kwargs['proxies'] = {'http': proxy_url, 'https': proxy_url}
            
            # Set timeout if not provided
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout
            
            # Make request
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Validate response
            self._validate_response(response)
            return response
            
        except HTTPError as e:
            self.logger.error(f"HTTP error occurred: {str(e)}")
            if self.proxy_rotator and 'proxies' in kwargs:
                self.proxy_rotator.mark_proxy_failed(proxy)
            return None
            
        except ConnectionError as e:
            self.logger.error(f"Connection error occurred: {str(e)}")
            if self.proxy_rotator and 'proxies' in kwargs:
                self.proxy_rotator.mark_proxy_failed(proxy)
            return None
            
        except Timeout as e:
            self.logger.error(f"Timeout error occurred: {str(e)}")
            if self.proxy_rotator and 'proxies' in kwargs:
                self.proxy_rotator.mark_proxy_failed(proxy)
            return None
            
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {str(e)}")
            return None
            
    def _validate_response(self, response: requests.Response) -> None:
        """Validate response content and format."""
        if not response.content:
            raise ValueError("Empty response content")
            
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            raise ValueError(f"Unexpected content type: {content_type}")
            
        if not response.text.strip():
            raise ValueError("Empty HTML content")
            
    def _extract_element(self, soup: BeautifulSoup, selector: str, 
                        attr: Optional[str] = None, default: Any = '') -> Any:
        """Extract element data with robust error handling."""
        try:
            element = soup.select_one(selector)
            if not element:
                return default
                
            if attr:
                return element.get(attr, default)
            return element.text.strip()
            
        except Exception as e:
            self.logger.warning(f"Error extracting element {selector}: {str(e)}")
            return default
            
    def _extract_number(self, soup: BeautifulSoup, selector: str) -> int:
        """Extract and convert number from element."""
        text = self._extract_element(soup, selector)
        try:
            # Remove non-numeric characters and convert
            number = ''.join(filter(str.isdigit, text))
            return int(number) if number else 0
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Error converting number {text}: {str(e)}")
            return 0
            
    def _extract_price(self, soup: BeautifulSoup, selector: str) -> float:
        """Extract and convert price from element."""
        text = self._extract_element(soup, selector)
        try:
            # Remove currency symbols and convert
            number = ''.join(filter(lambda x: x.isdigit() or x == '.', text))
            return float(number) if number else 0.0
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Error converting price {text}: {str(e)}")
            return 0.0
            
    def _extract_datetime(self, soup: BeautifulSoup, selector: str) -> str:
        """Extract datetime with fallback options."""
        element = soup.select_one(selector)
        if element:
            for attr in ['datetime', 'data-timestamp', 'data-time']:
                value = element.get(attr)
                if value:
                    return value
        return time.strftime('%Y-%m-%d %H:%M:%S')
        
    def scrape_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Scrape product data with improved error handling."""
        try:
            url = f"https://example.com/products/{product_id}"
            response = self._make_request(url)
            
            if not response:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            product_data = {
                'id': product_id,
                'name': self._extract_element(soup, '.product-name'),
                'price': self._extract_price(soup, '.product-price'),
                'rating': self._extract_price(soup, '.product-rating'),
                'description': self._extract_element(soup, '.product-description'),
                'seller': self._extract_element(soup, '.seller-name'),
                'url': url,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Validate required fields
            if not product_data['name']:
                raise ValueError(f"Failed to extract product name for {product_id}")
                
            return self.data_processor.process_product_data([product_data])
            
        except Exception as e:
            self.logger.error(f"Error scraping product {product_id}: {str(e)}")
            return None
            
    def scrape_creator(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Scrape creator data with improved validation."""
        try:
            url = f"https://example.com/creators/{creator_id}"
            response = self._make_request(url)
            
            if not response:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            creator_data = {
                'id': creator_id,
                'username': self._extract_element(soup, '.username'),
                'name': self._extract_element(soup, '.full-name'),
                'followers': self._extract_number(soup, '.follower-count'),
                'following': self._extract_number(soup, '.following-count'),
                'bio': self._extract_element(soup, '.bio'),
                'url': url,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Validate required fields
            if not creator_data['username']:
                raise ValueError(f"Failed to extract username for {creator_id}")
                
            return self.data_processor.process_creator_data(creator_data)
            
        except Exception as e:
            self.logger.error(f"Error scraping creator {creator_id}: {str(e)}")
            return None
            
    def scrape_videos(self, creator_id: str, max_videos: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Scrape video data with improved extraction."""
        try:
            url = f"https://example.com/creators/{creator_id}/videos"
            response = self._make_request(url)
            
            if not response:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            videos = []
            
            video_elements = soup.select('.video-item')[:max_videos]
            for video in video_elements:
                video_data = {
                    'id': video.get('data-video-id', ''),
                    'creator_id': creator_id,
                    'description': self._extract_element(video, '.video-description'),
                    'like_count': self._extract_number(video, '.like-count'),
                    'comment_count': self._extract_number(video, '.comment-count'),
                    'share_count': self._extract_number(video, '.share-count'),
                    'view_count': self._extract_number(video, '.view-count'),
                    'created_at': self._extract_datetime(video, '.created-at'),
                    'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Validate required fields
                if video_data['id']:
                    videos.append(video_data)
                else:
                    self.logger.warning(f"Skipping video with missing ID for creator {creator_id}")
                    
            return self.data_processor.process_video_data(videos) if videos else None
            
        except Exception as e:
            self.logger.error(f"Error scraping videos for creator {creator_id}: {str(e)}")
            return None
            
    def scrape_batch(self, items: List[str], item_type: str, max_workers: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Scrape multiple items concurrently with improved error handling."""
        results = []
        min_delay = 2
        max_delay = 5
        
        def scrape_with_delay(item: str) -> Optional[Dict[str, Any]]:
            try:
                # Add random delay between requests
                delay = random.uniform(min_delay, max_delay)
                time.sleep(delay)
                
                if item_type == 'product':
                    return self.scrape_product(item, **kwargs)
                elif item_type == 'creator':
                    return self.scrape_creator(item, **kwargs)
                elif item_type == 'videos':
                    return self.scrape_videos(item, **kwargs)
                else:
                    raise ValueError(f"Invalid item type: {item_type}")
                    
            except Exception as e:
                self.logger.error(f"Error in batch scraping {item_type} {item}: {str(e)}")
                return None
                
        # Use ThreadPoolExecutor for concurrent scraping
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {executor.submit(scrape_with_delay, item): item for item in items}
            
            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing result for {item}: {str(e)}")
                    
        return results 