#!/usr/bin/env python3
"""
Test script to verify news search with a larger, more established company
"""
import asyncio
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_with_established_company():
    """Test with companies more likely to have news"""
    
    print("Testing CSV-based Perplexity news with established companies")
    print("=" * 60)
    
    # Initialize the news reader
    news_reader = PerplexityNewsReader()
    
    if not news_reader.api_key:
        print("PERPLEXITY_API_KEY not found - cannot test actual search")
        return
    
    # Look for well-known companies in the CSV that are more likely to have news
    target_companies = ['DelfinGroup', 'mogo', 'ESTO', 'creditstar', 'Eleving']
    
    found_companies = []
    for company in news_reader.companies:
        company_name = company['company_name']
        if any(target in company_name for target in target_companies):
            found_companies.append(company)
    
    if not found_companies:
        # Use first few companies as fallback
        found_companies = news_reader.companies[:3]
    
    print(f"Testing with {len(found_companies)} companies:")
    
    for i, company in enumerate(found_companies, 1):
        print(f"\n{i}. Testing: {company['company_name']}")
        print(f"   Mintos URL: {company['mintos_url']}")
        
        # Test domain filter
        domain_filter = news_reader._get_search_domain_filter(company)
        print(f"   Domain filter: {domain_filter}")
        
        try:
            # Search for news from last 14 days (wider range)
            news_items = await news_reader.search_company_news_with_date_filter(company, 14)
            
            print(f"   Found {len(news_items)} news items")
            
            if news_items:
                for j, item in enumerate(news_items[:1]):  # Show first item
                    print(f"   Sample news: {item.title}")
                    print(f"   Source: {item.url}")
                    print(f"   Date: {item.date}")
                break  # Stop after first successful result
            else:
                print(f"   No news found for {company['company_name']}")
                
        except Exception as e:
            print(f"   Error: {e}")
        
        # Small delay between requests
        await asyncio.sleep(2)
    
    print(f"\nSystem verification:")
    print(f"- Total companies loaded: {len(news_reader.companies)}")
    print(f"- Data source: CSV file (company_pages.csv)")
    print(f"- Search method: URL-based with Mintos context")
    print(f"- Blacklisted domains: {news_reader.blacklisted_domains}")

async def main():
    await test_with_established_company()

if __name__ == "__main__":
    asyncio.run(main())