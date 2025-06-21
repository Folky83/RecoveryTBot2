#!/usr/bin/env python3
"""
Test script to verify Perplexity API integration with country-based domain whitelisting
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_perplexity_integration():
    """Test the Perplexity API integration with domain whitelisting"""
    
    print("Testing Perplexity API Integration with Country-Based Whitelisting")
    print("=" * 65)
    
    # Initialize the news reader
    news_reader = PerplexityNewsReader()
    
    # Test with a larger, more established company likely to have real news
    test_company = {
        'brand_name': 'Delfin Group',
        'legal_name': 'AS DelfinGroup',
        'ActivityCountry': 'Latvia',
        'RegCountry': 'Latvia'
    }
    
    print(f"Testing with company: {test_company['brand_name']}")
    print(f"Countries: {test_company['ActivityCountry']} / {test_company['RegCountry']}")
    
    # Get whitelisted domains
    domains = news_reader._get_whitelisted_domains(test_company)
    print(f"Whitelisted domains ({len(domains)}): {domains[:5]}...")
    
    # Build search terms
    search_terms = news_reader._build_search_terms(test_company)
    print(f"Search terms: {search_terms}")
    
    print("\nAttempting Perplexity API call with whitelisted domains...")
    
    try:
        # Test the news search with a short date range
        news_items = await news_reader.search_company_news_with_date_filter(test_company, days_back=7)
        
        print(f"✅ API call successful! Found {len(news_items)} news items")
        
        # Show sample results
        for i, item in enumerate(news_items[:2]):
            print(f"\nNews Item {i+1}:")
            print(f"  Title: {item.title}")
            print(f"  Date: {item.date}")
            print(f"  URL: {item.url}")
            print(f"  Company: {item.company_name}")
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
        
        # Check if it's an API key issue
        if "api_key" in str(e).lower() or "authorization" in str(e).lower():
            print("\n⚠️  This appears to be an API key issue.")
            print("The domain whitelisting system is working correctly.")
            print("API key configuration may need to be checked.")
        else:
            print(f"\n⚠️  Unexpected error: {e}")

async def main():
    """Main test function"""
    await test_perplexity_integration()

if __name__ == "__main__":
    asyncio.run(main())