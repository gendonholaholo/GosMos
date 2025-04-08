from typing import List, Optional, Dict, Union
import random
import logging
import time
import requests
from urllib.parse import urlparse
from datetime import datetime, timedelta
import re

class ProxyRotator:
    """Manages proxy rotation and validation."""
    
    def __init__(self, proxies: List[Union[str, Dict[str, str]]], logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.proxies = self._validate_proxies(proxies)
        self.current_proxy = None
        self.last_used = {}
        self.cooldown = timedelta(minutes=5)
    
    def _validate_proxies(self, proxies: List[Union[str, Dict[str, str]]]) -> List[Dict[str, str]]:
        """Validate and convert proxies to standard format."""
        valid_proxies = []
        for proxy in proxies:
            try:
                if isinstance(proxy, str):
                    proxy_dict = self._parse_proxy_string(proxy)
                elif isinstance(proxy, dict):
                    proxy_dict = self._validate_proxy_dict(proxy)
                else:
                    raise ValueError(f"Invalid proxy format: {proxy}")
                    
                if self.validate_proxy(proxy_dict):
                    valid_proxies.append(proxy_dict)
                    
            except Exception as e:
                self.logger.warning(f"Invalid proxy {proxy}: {str(e)}")
                
        if not valid_proxies:
            raise ValueError("No valid proxies provided")
            
        return valid_proxies
        
    def _parse_proxy_string(self, proxy_str: str) -> Dict[str, str]:
        """Parse proxy string into dictionary format."""
        try:
            # Parse proxy string format: protocol://username:password@host:port
            pattern = r'^(?P<protocol>https?)?:?/?/?(?:(?P<username>[^:@]+)(?::(?P<password>[^@]+))?@)?(?P<host>[^:]+)(?::(?P<port>\d+))?$'
            match = re.match(pattern, proxy_str)
            
            if not match:
                raise ValueError(f"Invalid proxy string format: {proxy_str}")
                
            proxy_dict = match.groupdict()
            required_fields = ['host', 'port']
            
            if not all(proxy_dict.get(field) for field in required_fields):
                raise ValueError(f"Missing required proxy fields: {proxy_str}")
                
            # Set defaults
            proxy_dict['protocol'] = proxy_dict.get('protocol', 'http')
            proxy_dict['username'] = proxy_dict.get('username', '')
            proxy_dict['password'] = proxy_dict.get('password', '')
            
            return proxy_dict
            
        except Exception as e:
            raise ValueError(f"Failed to parse proxy string: {str(e)}")
            
    def _validate_proxy_dict(self, proxy: Dict[str, str]) -> Dict[str, str]:
        """Validate proxy dictionary format."""
        required_fields = ['host', 'port']
        if not all(field in proxy for field in required_fields):
            raise ValueError(f"Missing required proxy fields: {proxy}")
            
        # Ensure all fields are strings
        return {
            'protocol': str(proxy.get('protocol', 'http')),
            'host': str(proxy['host']),
            'port': str(proxy['port']),
            'username': str(proxy.get('username', '')),
            'password': str(proxy.get('password', ''))
        }
        
    def validate_proxy(self, proxy: Dict[str, str]) -> bool:
        """Validate if a proxy is working."""
        try:
            if not proxy or not isinstance(proxy, dict):
                raise ValueError("Invalid proxy format")
                
            test_url = "http://httpbin.org/ip"
            proxy_url = f"{proxy['protocol']}://"
            if proxy['username'] and proxy['password']:
                proxy_url += f"{proxy['username']}:{proxy['password']}@"
            proxy_url += f"{proxy['host']}:{proxy['port']}"
            
            response = requests.get(
                test_url,
                proxies={
                    'http': proxy_url,
                    'https': proxy_url
                },
                timeout=10
            )
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Error validating proxy: {str(e)}")
            return False
            
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get the next available proxy."""
        try:
            if not self.proxies:
                raise ValueError("No proxies available")
                
            # Filter out proxies that are in cooldown
            available_proxies = [
                p for p in self.proxies
                if p not in self.last_used or
                datetime.now() - self.last_used[p] > self.cooldown
            ]
            
            if not available_proxies:
                # If all proxies are in cooldown, use the one with oldest last_used
                proxy = min(self.proxies, key=lambda p: self.last_used.get(p, datetime.min))
            else:
                proxy = random.choice(available_proxies)
                
            # Validate the proxy
            if not self.validate_proxy(proxy):
                self.logger.warning(f"Proxy {proxy['host']} failed validation")
                self.proxies.remove(proxy)
                return self.get_next_proxy() if self.proxies else None
                
            self.current_proxy = proxy
            self.last_used[proxy] = datetime.now()
            return proxy
            
        except Exception as e:
            self.logger.error(f"Error getting next proxy: {str(e)}")
            return None
            
    def get_current_proxy(self) -> Optional[Dict[str, str]]:
        """Get the currently active proxy."""
        return self.current_proxy
        
    def mark_proxy_failed(self, proxy: Dict[str, str]) -> None:
        """Mark a proxy as failed and remove it from rotation."""
        try:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
                self.logger.warning(f"Removed failed proxy: {proxy['host']}")
                
            if proxy == self.current_proxy:
                self.current_proxy = None
                
        except Exception as e:
            self.logger.error(f"Error marking proxy as failed: {str(e)}")
            
    def add_proxy(self, proxy: Union[str, Dict[str, str]]) -> bool:
        """Add a new proxy to the rotation."""
        try:
            if isinstance(proxy, str):
                proxy_dict = self._parse_proxy_string(proxy)
            elif isinstance(proxy, dict):
                proxy_dict = self._validate_proxy_dict(proxy)
            else:
                raise ValueError("Invalid proxy format")
                
            if self.validate_proxy(proxy_dict):
                self.proxies.append(proxy_dict)
                self.logger.info(f"Added new proxy: {proxy_dict['host']}")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error adding proxy: {str(e)}")
            return False