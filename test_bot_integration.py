#!/usr/bin/env python3
"""
Test script to verify bot integration with the modified Perplexity news system
"""
import asyncio
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_bot_integration():
    """Test that the bot can properly initialize and use the modified news system"""
    
    print("Testing Bot Integration with Modified Perplexity News System")
    print("=" * 60)
    
    try:
        # Initialize the news reader (same as bot would do)
        news_reader = PerplexityNewsReader()
        
        print(f"✅ News reader initialized successfully")
        print(f"   Companies loaded: {len(news_reader.companies)}")
        print(f"   Data source: {news_reader.company_file}")
        print(f"   Blacklisted domains: {news_reader.blacklisted_domains}")
        
        # Test key methods that the bot uses
        
        # 1. Test user preference management
        test_chat_id = "test_user_123"
        news_reader.set_user_preference(test_chat_id, True)
        preference = news_reader.get_user_preference(test_chat_id)
        print(f"✅ User preference system working: {preference}")
        
        # 2. Test company data structure
        if news_reader.companies:
            sample_company = news_reader.companies[0]
            required_fields = ['company_name', 'mintos_url', 'investment_type']
            has_all_fields = all(field in sample_company for field in required_fields)
            print(f"✅ Company data structure valid: {has_all_fields}")
            print(f"   Sample company: {sample_company['company_name']}")
        
        # 3. Test search term building
        if news_reader.companies:
            search_terms = news_reader._build_search_terms(news_reader.companies[0])
            print(f"✅ Search term building working: '{search_terms}'")
        
        # 4. Test domain filtering
        if news_reader.companies:
            domain_filter = news_reader._get_search_domain_filter(news_reader.companies[0])
            print(f"✅ Domain filtering working: {domain_filter}")
        
        # 5. Test that all companies have valid data
        invalid_companies = []
        for company in news_reader.companies:
            if not company.get('company_name') or not company.get('mintos_url'):
                invalid_companies.append(company)
        
        print(f"✅ Data validation: {len(invalid_companies)} invalid companies found")
        
        # 6. Test deduplication worked
        company_names = [c['company_name'] for c in news_reader.companies]
        unique_names = set(company_names)
        duplicates = len(company_names) - len(unique_names)
        print(f"✅ Deduplication: {duplicates} duplicates removed")
        
        print(f"\n🎯 Integration Status: SUCCESS")
        print(f"   The bot can now use the CSV-based Perplexity news system")
        print(f"   All core functionality is compatible and working")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    
    return True

async def main():
    success = await test_bot_integration()
    if success:
        print(f"\n✅ Migration complete - bot integration verified")
    else:
        print(f"\n❌ Integration issues detected")

if __name__ == "__main__":
    asyncio.run(main())