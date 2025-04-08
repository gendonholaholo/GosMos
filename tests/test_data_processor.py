import pytest
import pandas as pd
from datetime import datetime
from core.scraper_engine import DataProcessor

def test_process_product_data(data_processor, mock_product_data):
    """Test processing of product data."""
    df = data_processor.process_product_data([mock_product_data])
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]['id'] == mock_product_data['id']
    assert df.iloc[0]['name'] == mock_product_data['name']
    assert 'scraped_at' in df.columns

def test_process_creator_data(data_processor, mock_creator_data):
    """Test processing of creator data."""
    processed_data = data_processor.process_creator_data(mock_creator_data)
    
    assert isinstance(processed_data, dict)
    assert processed_data['id'] == mock_creator_data['id']
    assert processed_data['username'] == mock_creator_data['username']
    assert 'scraped_at' in processed_data

def test_process_video_data(data_processor, mock_video_data):
    """Test processing of video data."""
    df = data_processor.process_video_data(mock_video_data)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(mock_video_data)
    assert df.iloc[0]['id'] == mock_video_data[0]['id']
    assert 'scraped_at' in df.columns

def test_save_to_csv(data_processor, mock_product_data, tmp_path):
    """Test saving data to CSV file."""
    df = data_processor.process_product_data([mock_product_data])
    output_path = tmp_path / "test_products.csv"
    
    data_processor.save_to_csv(df, str(output_path))
    assert output_path.exists()
    
    # Verify saved data
    saved_df = pd.read_csv(output_path)
    assert len(saved_df) == 1
    assert saved_df.iloc[0]['id'] == mock_product_data['id']

def test_save_to_json(data_processor, mock_creator_data, tmp_path):
    """Test saving data to JSON file."""
    output_path = tmp_path / "test_creator.json"
    
    data_processor.save_to_json(mock_creator_data, str(output_path))
    assert output_path.exists()

def test_merge_dataframes(data_processor, mock_product_data, mock_video_data):
    """Test merging multiple DataFrames."""
    product_df = data_processor.process_product_data([mock_product_data])
    video_df = data_processor.process_video_data(mock_video_data)
    
    merged_df = data_processor.merge_dataframes([product_df, video_df], on='id')
    assert isinstance(merged_df, pd.DataFrame)

def test_empty_data_processing(data_processor):
    """Test processing of empty data."""
    empty_product_df = data_processor.process_product_data([])
    assert isinstance(empty_product_df, pd.DataFrame)
    assert len(empty_product_df) == 0
    
    empty_video_df = data_processor.process_video_data([])
    assert isinstance(empty_video_df, pd.DataFrame)
    assert len(empty_video_df) == 0

def test_invalid_data_handling(data_processor):
    """Test handling of invalid data."""
    invalid_data = [{"invalid": "data"}]
    
    with pytest.raises(ValueError):
        data_processor.process_product_data(invalid_data)
    
    with pytest.raises(ValueError):
        data_processor.process_video_data(invalid_data) 