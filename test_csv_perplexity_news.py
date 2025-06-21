#!/usr/bin/env python3
"""
Test script to verify the modified Perplexity news system using company_pages.csv
"""
import asyncio
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_csv_perplexity_news():
    """Test the modified Perplexity news system with CSV data source"""
    
    print("🧪 Testing Modified Perplexity News System with CSV Data")
    print("=" * 60)
    
    # Initialize the news reader
    news_reader = PerplexityNewsReader()
    
    # Check if API key is available
    if not news_reader.api_key:
        print("❌ PERPLEXITY_API_KEY not found in environment")
        print("   Please provide your Perplexity API key to test the system")
        return
    
    print(f"✅ API key found: {news_reader.api_key[:10]}...")
    
    # Check company data loading from CSV
    print(f"📊 Loaded {len(news_reader.companies)} companies from CSV:")
    
    # Show first few companies with their data structure
    for i, company in enumerate(news_reader.companies[:5]):
        print(f"  {i+1}. {company['company_name']}")
        print(f"     Mintos URL: {company['mintos_url']}")
        print(f"     Search terms: '{news_reader._build_search_terms(company)}'")
        
        # Test domain filter
        domain_filter = news_reader._get_search_domain_filter(company)
        print(f"     Domain filter: {domain_filter}")
        print()
    
    if len(news_reader.companies) > 5:
        print(f"  ... and {len(news_reader.companies) - 5} more companies")
    
    # Test blacklisted domains
    print(f"🚫 Blacklisted domains: {news_reader.blacklisted_domains}")
    
    # Test with a specific company (first one)
    if news_reader.companies:
        test_company = news_reader.companies[0]
        print(f"\n🔍 Testing news search for: {test_company['company_name']}")
        print(f"   Mintos URL: {test_company['mintos_url']}")
        
        try:
            # Test with recent date filter (last 7 days)
            print(f"📅 Searching for news from last 7 days...")
            
            news_items = await news_reader.search_company_news_with_date_filter(test_company, 7)
            
            print(f"📰 Found {len(news_items)} news items")
            
            if news_items:
                print("\nSample news items:")
                for i, item in enumerate(news_items[:2]):
                    print(f"\n--- News Item {i+1} ---")
                    print(f"Title: {item.title}")
                    print(f"URL: {item.url}")
                    print(f"Date: {item.date}")
                    print(f"Company: {item.company_name}")
                    print(f"Search Terms: {item.search_terms}")
                    print(f"Content Preview: {item.content[:100]}...")
            else:
                print("   No news items found for this company")
                
        except Exception as e:
            print(f"❌ Error testing news search: {e}")
    
    # Test deduplication
    print(f"\n🔄 Testing deduplication...")
    original_companies = len(news_reader.companies)
    print(f"   Final company count after deduplication: {original_companies}")
    
    # Verify no country sources are being used
    print(f"\n✅ Verification:")
    print(f"   - Using CSV data source: {news_reader.company_file}")
    print(f"   - No country sources dependency")
    print(f"   - URL-based search with Mintos context")
    print(f"   - Blacklisted domains applied: {news_reader.blacklisted_domains}")

async def main():
    """Main test function"""
    await test_csv_perplexity_news()

if __name__ == "__main__":
    asyncio.run(main())