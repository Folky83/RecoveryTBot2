#!/usr/bin/env python3
"""
Test script to verify what happens when Perplexity has no real sources
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_empty_results():
    """Test with a company unlikely to have recent news"""
    
    print("Testing Empty Results Handling")
    print("=" * 35)
    
    # Initialize the news reader
    news_reader = PerplexityNewsReader()
    
    # Test with a fictional company that shouldn't have any real news
    test_company = {
        'brand_name': 'Nonexistent Finance Corp',
        'legal_name': 'Nonexistent Finance Corporation',
        'ActivityCountry': 'Latvia',
        'RegCountry': 'Latvia'
    }
    
    print(f"Testing with company: {test_company['brand_name']}")
    print("This company doesn't exist, so no real news should be found")
    
    try:
        # Test the news search
        news_items = await news_reader.search_company_news_with_date_filter(test_company, days_back=7)
        
        print(f"Found {len(news_items)} news items")
        
        if news_items:
            print("\n⚠️  WARNING: Found news for non-existent company!")
            for i, item in enumerate(news_items):
                print(f"\nNews Item {i+1}:")
                print(f"  Title: {item.title}")
                print(f"  Date: {item.date}")
                print(f"  URL: {item.url}")
                print(f"  Content preview: {item.content[:200]}...")
        else:
            print("✅ Correctly found no news for non-existent company")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_empty_results())