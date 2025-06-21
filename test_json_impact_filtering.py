#!/usr/bin/env python3
"""
Test script for the new JSON impact filtering approach
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_json_impact_filtering():
    """Test the new JSON impact filtering"""
    
    print("Testing JSON-based impact filtering...")
    
    # Initialize the reader
    reader = PerplexityNewsReader()
    
    # Test with a single company to see the JSON response format
    test_company = {
        'group_name': 'AS Grenardi Group',
        'legal_name': 'AS Grenardi Group',
        'brand_name': 'Grenardi'
    }
    
    print(f"\nTesting company: {test_company['group_name']}")
    
    try:
        # Fetch news with 'day' recency for immediate testing
        news_items = await reader.search_company_news_with_recency(test_company, 'day')
        
        print(f"Results: {len(news_items)} items found")
        
        for i, item in enumerate(news_items):
            print(f"\nItem {i+1}:")
            print(f"  Title: {item.title}")
            print(f"  URL: {item.url}")
            print(f"  Content preview: {item.content[:200]}...")
            print(f"  Company: {item.company_name}")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_json_impact_filtering())