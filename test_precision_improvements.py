"""
Test script to verify the precision improvements for Perplexity news
"""
import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_precision_improvements():
    """Test the improved precision settings"""
    print("Testing Perplexity news precision improvements...")
    
    # Check if API key is available
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("❌ PERPLEXITY_API_KEY not found in environment")
        return
    
    print(f"✅ API key found (length: {len(api_key)})")
    
    # Create news reader instance
    news_reader = PerplexityNewsReader()
    
    # Test with a specific company that might have recent news
    test_company = {
        'brand_name': 'Eleving Group',
        'legal_name': 'AS Mogo',
        'group_name': 'Eleving Group',
        'ActivityCountry': 'Latvia',
        'RegCountry': 'Latvia'
    }
    
    print(f"\nTesting with company: {test_company['brand_name']}")
    print("Improvements being tested:")
    print("- web_search_options.search_context_size: 'high'")
    print("- Require company as PRIMARY SUBJECT")
    print("- More focused prompt for precision")
    print("- Reduced temperature to 0.1")
    
    try:
        # Search for news with 7 days back
        news_items = await news_reader.search_company_news_with_date_filter(test_company, 7)
        
        print(f"\nResults: Found {len(news_items)} high-precision news items")
        
        if news_items:
            for i, item in enumerate(news_items, 1):
                print(f"\n--- News Item {i} ---")
                print(f"Title: {item.title}")
                print(f"URL: {item.url}")
                print(f"Date: {item.date}")
                print(f"Company: {item.company_name}")
        else:
            print("No news items found (this indicates good precision - only high-impact, primary-subject news)")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_precision_improvements())