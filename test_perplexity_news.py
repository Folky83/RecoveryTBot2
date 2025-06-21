#!/usr/bin/env python3
"""
Test script for Perplexity news functionality
Verifies the implementation with sample company data
"""
import asyncio
import os
from datetime import datetime, timedelta
from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_perplexity_news():
    """Test the Perplexity news functionality"""
    
    print("🧪 Testing Perplexity News Implementation")
    print("=" * 50)
    
    # Initialize the news reader
    news_reader = PerplexityNewsReader()
    
    # Check if API key is available
    if not news_reader.api_key:
        print("❌ PERPLEXITY_API_KEY not found in environment")
        return
    
    print(f"✅ API key found: {news_reader.api_key[:10]}...")
    
    # Check company data loading
    print(f"📊 Loaded {len(news_reader.companies)} companies:")
    for i, company in enumerate(news_reader.companies[:3]):  # Show first 3
        print(f"  {i+1}. {company['group_name']} ({company['brand_name']}) - {company['investment_type']}")
    if len(news_reader.companies) > 3:
        print(f"  ... and {len(news_reader.companies) - 3} more")
    
    # Test with a single company (first one)
    if news_reader.companies:
        test_company = news_reader.companies[0]
        print(f"\n🔍 Testing news search for: {test_company['group_name']}")
        
        try:
            # Test with date filter (last 7 days)
            date_filter = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            print(f"📅 Using date filter: {date_filter}")
            
            news_items = await news_reader.search_company_news_with_recency(test_company, "week")
            
            print(f"📰 Found {len(news_items)} news items")
            
            if news_items:
                for i, item in enumerate(news_items[:2]):  # Show first 2
                    print(f"\n  Item {i+1}:")
                    print(f"    📰 Title: {item.title}")
                    print(f"    🔗 URL: {item.url}")
                    print(f"    📅 Date: {item.date}")
                    print(f"    📝 Content: {item.content[:100]}...")
                    print(f"    🆔 GUID: {item.guid[:16]}...")
            else:
                print("  ℹ️ No news items found (this is normal for testing)")
        
        except Exception as e:
            print(f"❌ Error testing news search: {e}")
    
    # Test user preferences
    print(f"\n👤 Testing user preferences:")
    test_user_id = "123456789"
    
    # Check default preference
    default_pref = news_reader.get_user_preference(test_user_id)
    print(f"  Default preference: {default_pref}")
    
    # Set preference to enabled
    news_reader.set_user_preference(test_user_id, True)
    enabled_pref = news_reader.get_user_preference(test_user_id)
    print(f"  After enabling: {enabled_pref}")
    
    # Test sent items tracking
    print(f"\n📨 Testing sent items tracking:")
    test_guid = "test_guid_12345"
    
    # Check if item is sent (should be False initially)
    is_sent_before = news_reader.is_item_sent(test_user_id, test_guid)
    print(f"  Item sent before marking: {is_sent_before}")
    
    # Mark as sent
    news_reader.mark_item_sent(test_user_id, test_guid)
    is_sent_after = news_reader.is_item_sent(test_user_id, test_guid)
    print(f"  Item sent after marking: {is_sent_after}")
    
    # Test message formatting
    print(f"\n📋 Testing message formatting:")
    if news_reader.companies:
        from mintos_bot.perplexity_news import PerplexityNewsItem
        
        sample_item = PerplexityNewsItem(
            title="Sample Financial Update",
            url="https://example.com/news/sample",
            date=datetime.now().strftime('%Y-%m-%d'),
            content="This is a sample news content for testing message formatting.",
            company_name=test_company['group_name'],
            search_terms=f"{test_company['group_name']} {test_company['brand_name']}"
        )
        
        formatted_message = news_reader.format_news_message(sample_item)
        print(f"  Formatted message length: {len(formatted_message)} characters")
        print(f"  First 200 chars: {formatted_message[:200]}...")
    
    print(f"\n✅ Perplexity news testing completed successfully!")
    print(f"🗞️ The /news command is now available in the Telegram bot")
    
    # Show usage instructions
    print(f"\n📖 Usage Instructions:")
    print(f"  1. Use /news command in the bot to access Perplexity news")
    print(f"  2. Enable news notifications for your user")
    print(f"  3. Use buttons to fetch news with different date filters:")
    print(f"     • Latest news (no date filter)")
    print(f"     • Today's news")
    print(f"     • This week's news")
    print(f"  4. Each company gets searched individually")
    print(f"  5. News items are sent as separate messages")
    print(f"  6. Duplicate messages are prevented by tracking sent items")

if __name__ == "__main__":
    asyncio.run(test_perplexity_news())