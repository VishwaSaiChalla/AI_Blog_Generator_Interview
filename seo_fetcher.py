import random
from typing import Dict

def get_seo_data(keyword: str) -> Dict[str, float]:
    """
    Get SEO metrics for a given keyword.
    This is a mock implementation that returns random data.
    In a real implementation, this would call an SEO API.
    
    Args:
        keyword (str): The keyword to get SEO data for
        
    Returns:
        Dict[str, float]: Dictionary containing SEO metrics
    """
    # Mock data ranges
    search_volume_range = (1000, 100000)
    difficulty_range = (0, 100)
    cpc_range = (0.5, 10.0)
    
    # Generate random data within ranges
    seo_data = {
        "search_volume": random.randint(*search_volume_range),
        "keyword_difficulty": random.randint(*difficulty_range),
        "avg_cpc": round(random.uniform(*cpc_range), 2)
    }
    
    return seo_data