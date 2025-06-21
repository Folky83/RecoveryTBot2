"""
Test the fixed news search with relaxed criteria
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_fixed_search():
    """Test news search with fixed criteria"""
    print("Testing fixed news search...")
    
    news_reader = PerplexityNewsReader()
    
    # Test with Eleving Group (known to have recent news)
    test_company = {
        'brand_name': 'Eleving Group',
        'legal_name': 'AS Mogo',
        'group_name': 'Eleving Group',
        'ActivityCountry': 'Latvia',
        'RegCountry': 'Latvia'
    }
    
    try:
        # Search with 14 days back (more reasonable timeframe)
        news_items = await news_reader.search_company_news_with_date_filter(test_company, 14)
        
        print(f"Results: Found {len(news_items)} news items")
        
        if news_items:
            for i, item in enumerate(news_items, 1):
                print(f"\n--- News Item {i} ---")
                print(f"Title: {item.title}")
                print(f"Date: {item.date}")
                print(f"URL: {item.url}")
                print("Success: News search now working!")
        else:
            print("Still no results - may need further adjustment")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_fixed_search())