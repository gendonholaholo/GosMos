import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime
import json
import logging
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page
import undetected_chromedriver as uc
from .proxy_rotator import ProxyRotator

class TikTokScraper:
    def __init__(
        self,
        headless: bool = True,
        proxy_list: Optional[List[str]] = None,
        timeout: int = 30,
        retry_attempts: int = 3
    ):
        self.headless = headless
        self.proxy_rotator = ProxyRotator(proxy_list or [])
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.browser: Optional[Browser] = None
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        playwright = await async_playwright().start()
        proxy = self.proxy_rotator.get_next_proxy()
        
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            proxy=proxy
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
            
    async def _get_page(self) -> Page:
        """Create a new browser page with proper headers."""
        if not self.browser:
            raise RuntimeError("Browser not initialized")
            
        context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        return await context.new_page()
        
    async def scrape_products(
        self,
        query: str,
        limit: int = 100,
        output_file: Optional[Path] = None
    ) -> List[Dict]:
        """Scrape product data from TikTok Shop search results."""
        products = []
        page = await self._get_page()
        
        try:
            # Navigate to TikTok Shop search page
            await page.goto(f"https://www.tiktok.com/search?q={query}&t=shop")
            await page.wait_for_selector(".product-card", timeout=self.timeout * 1000)
            
            # Scroll and collect products
            for _ in range(limit):
                product_cards = await page.query_selector_all(".product-card")
                for card in product_cards:
                    try:
                        product = {
                            "id": await card.get_attribute("data-product-id"),
                            "title": await card.query_selector(".product-title").inner_text(),
                            "price": await card.query_selector(".product-price").inner_text(),
                            "rating": await card.query_selector(".product-rating").inner_text(),
                            "sales": await card.query_selector(".product-sales").inner_text(),
                            "url": await card.query_selector("a").get_attribute("href"),
                            "scraped_at": datetime.now().isoformat()
                        }
                        products.append(product)
                        
                        if len(products) >= limit:
                            break
                            
                    except Exception as e:
                        self.logger.error(f"Error scraping product: {e}")
                        continue
                        
                if len(products) >= limit:
                    break
                    
                # Scroll to load more products
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error during product scraping: {e}")
            
        finally:
            await page.close()
            
        # Save results if output file specified
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
                
        return products
        
    async def scrape_creator(
        self,
        creator_id: str,
        output_file: Optional[Path] = None
    ) -> Dict:
        """Scrape creator profile data."""
        creator_data = {}
        page = await self._get_page()
        
        try:
            # Navigate to creator profile
            await page.goto(f"https://www.tiktok.com/@{creator_id}")
            await page.wait_for_selector(".creator-profile", timeout=self.timeout * 1000)
            
            # Extract creator information
            creator_data = {
                "id": creator_id,
                "name": await page.query_selector(".creator-name").inner_text(),
                "followers": await page.query_selector(".follower-count").inner_text(),
                "products": await page.query_selector(".product-count").inner_text(),
                "rating": await page.query_selector(".creator-rating").inner_text(),
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error scraping creator profile: {e}")
            
        finally:
            await page.close()
            
        # Save results if output file specified
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(creator_data, f, indent=2, ensure_ascii=False)
                
        return creator_data
        
    async def scrape_videos(
        self,
        creator_id: str,
        limit: int = 100,
        output_file: Optional[Path] = None
    ) -> List[Dict]:
        """Scrape video data from a creator's profile."""
        videos = []
        page = await self._get_page()
        
        try:
            # Navigate to creator's videos
            await page.goto(f"https://www.tiktok.com/@{creator_id}/videos")
            await page.wait_for_selector(".video-card", timeout=self.timeout * 1000)
            
            # Scroll and collect videos
            for _ in range(limit):
                video_cards = await page.query_selector_all(".video-card")
                for card in video_cards:
                    try:
                        video = {
                            "id": await card.get_attribute("data-video-id"),
                            "title": await card.query_selector(".video-title").inner_text(),
                            "views": await card.query_selector(".view-count").inner_text(),
                            "likes": await card.query_selector(".like-count").inner_text(),
                            "comments": await card.query_selector(".comment-count").inner_text(),
                            "shares": await card.query_selector(".share-count").inner_text(),
                            "url": await card.query_selector("a").get_attribute("href"),
                            "scraped_at": datetime.now().isoformat()
                        }
                        videos.append(video)
                        
                        if len(videos) >= limit:
                            break
                            
                    except Exception as e:
                        self.logger.error(f"Error scraping video: {e}")
                        continue
                        
                if len(videos) >= limit:
                    break
                    
                # Scroll to load more videos
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error during video scraping: {e}")
            
        finally:
            await page.close()
            
        # Save results if output file specified
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(videos, f, indent=2, ensure_ascii=False)
                
        return videos 