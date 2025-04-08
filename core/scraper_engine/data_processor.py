import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import pandas as pd

class DataProcessor:
    """Handles data processing and storage for scraped data."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        
    def process_product_data(self, products: List[Dict]) -> pd.DataFrame:
        """Process product data into a structured DataFrame."""
        try:
            if not products:
                return pd.DataFrame()
                
            processed_data = []
            for product in products:
                if not isinstance(product, dict):
                    raise ValueError(f"Invalid product data format: {product}")
                    
                processed_data.append({
                    'id': str(product.get('id', '')),
                    'name': str(product.get('name', '')),
                    'price': str(product.get('price', '0.0')),
                    'rating': str(product.get('rating', '0.0')),
                    'description': str(product.get('description', '')),
                    'seller': str(product.get('seller', '')),
                    'url': str(product.get('url', '')),
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
            return pd.DataFrame(processed_data)
            
        except Exception as e:
            self.logger.error(f"Error processing product data: {str(e)}")
            raise ValueError(f"Failed to process product data: {str(e)}")
        
    def process_creator_data(self, creator: Dict) -> Dict:
        """Process creator data into a structured format."""
        try:
            if not creator or not isinstance(creator, dict):
                raise ValueError("Invalid creator data format")
                
            return {
                'id': str(creator.get('id', '')),
                'username': str(creator.get('username', '')),
                'name': str(creator.get('name', '')),
                'followers': str(creator.get('followers', '0')),
                'following': str(creator.get('following', '0')),
                'bio': str(creator.get('bio', '')),
                'url': str(creator.get('url', '')),
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.logger.error(f"Error processing creator data: {str(e)}")
            raise ValueError(f"Failed to process creator data: {str(e)}")
            
    def process_video_data(self, videos: List[Dict]) -> pd.DataFrame:
        """Process video data into a structured DataFrame."""
        try:
            if not videos:
                return pd.DataFrame()
                
            processed_data = []
            for video in videos:
                if not isinstance(video, dict):
                    raise ValueError(f"Invalid video data format: {video}")
                    
                processed_data.append({
                    'id': str(video.get('id', '')),
                    'creator_id': str(video.get('creator_id', '')),
                    'description': str(video.get('description', '')),
                    'like_count': str(video.get('like_count', '0')),
                    'comment_count': str(video.get('comment_count', '0')),
                    'share_count': str(video.get('share_count', '0')),
                    'view_count': str(video.get('view_count', '0')),
                    'created_at': str(video.get('created_at', '')),
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
            return pd.DataFrame(processed_data)
            
        except Exception as e:
            self.logger.error(f"Error processing video data: {str(e)}")
            raise ValueError(f"Failed to process video data: {str(e)}")
        
    def save_to_csv(self, df: pd.DataFrame, filepath: str) -> bool:
        """Save DataFrame to CSV file."""
        try:
            if df.empty:
                raise ValueError("Empty DataFrame, nothing to save")
                
            df.to_csv(filepath, index=False)
            self.logger.info(f"Data saved to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {str(e)}")
            raise ValueError(f"Failed to save to CSV: {str(e)}")
            
    def save_to_json(self, data: Union[Dict, pd.DataFrame], filepath: str) -> bool:
        """Save data to JSON file."""
        try:
            if isinstance(data, pd.DataFrame):
                if data.empty:
                    raise ValueError("Empty DataFrame, nothing to save")
                data = data.to_dict('records')
            elif not data:
                raise ValueError("Empty data, nothing to save")
                
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Data saved to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {str(e)}")
            raise ValueError(f"Failed to save to JSON: {str(e)}")
            
    def merge_dataframes(self, dfs: List[pd.DataFrame], on: str) -> pd.DataFrame:
        """Merge multiple DataFrames on a common column."""
        try:
            if not dfs:
                raise ValueError("No DataFrames provided")
                
            if len(dfs) == 1:
                return dfs[0]
                
            # Check if all DataFrames have the merge column
            for df in dfs:
                if on not in df.columns:
                    raise ValueError(f"Column '{on}' not found in DataFrame")
                    
            merged_df = dfs[0]
            for df in dfs[1:]:
                merged_df = pd.merge(merged_df, df, on=on, how='outer')
                
            return merged_df
            
        except Exception as e:
            self.logger.error(f"Error merging DataFrames: {str(e)}")
            raise ValueError(f"Failed to merge DataFrames: {str(e)}") 