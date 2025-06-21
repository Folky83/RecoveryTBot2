#!/usr/bin/env python3
"""
Test script to verify the country-enhanced Perplexity search functionality
"""
import asyncio
import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_country_enhanced_search():
    """Test the country-enhanced search functionality"""
    print("Testing country-enhanced Perplexity search...")
    
    # Initialize the news reader
    news_reader = PerplexityNewsReader()
    
    # Check if companies loaded correctly
    if not news_reader.companies:
        print("❌ No companies loaded")
        return
    
    print(f"✅ Loaded {len(news_reader.companies)} companies")
    
    # Show a few examples of how search terms are built
    print("\nSearch term examples:")
    for i, company in enumerate(news_reader.companies[:5]):
        search_terms = news_reader._build_search_terms(company)
        print(f"  {i+1}. {company.get('brand_name', company.get('group_name', 'Unknown'))}")
        print(f"     Search terms: '{search_terms}'")
        print(f"     Reg Country: {company.get('RegCountry', 'N/A')}")
        print(f"     Activity Country: {company.get('ActivityCountry', 'N/A')}")
        print()
    
    # Test search for one company (if API key is available)
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("⚠️  PERPLEXITY_API_KEY not set - cannot test actual search")
        return
    
    # Test with a specific company
    test_company = news_reader.companies[0]
    company_name = test_company.get('brand_name', test_company.get('group_name', 'Unknown'))
    
    print(f"Testing search for: {company_name}")
    print(f"Search terms: '{news_reader._build_search_terms(test_company)}'")
    
    try:
        results = await news_reader.search_company_news_with_date_filter(test_company, 4)
        print(f"✅ Search completed - found {len(results)} news items")
        
        for item in results:
            print(f"  - {item.title[:80]}...")
            print(f"    Date: {item.date}")
            print(f"    URL: {item.url}")
            print()
            
    except Exception as e:
        print(f"❌ Search failed: {e}")

async def main():
    """Main test function"""
    await test_country_enhanced_search()

if __name__ == "__main__":
    asyncio.run(main())