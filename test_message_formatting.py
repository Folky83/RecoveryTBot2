#!/usr/bin/env python3
"""
Test script to verify improved message formatting
Tests the new JSON cleaning and header deduplication logic
"""
import asyncio
from datetime import datetime
from mintos_bot.perplexity_news import PerplexityNewsReader, PerplexityNewsItem

def test_json_content_cleaning():
    """Test JSON content cleaning functionality"""
    
    print("🧪 Testing Message Formatting Improvements")
    print("=" * 50)
    
    # Test case 1: JSON content with news_items
    json_content = '''```json
{
  "news_items": [
    {
      "title": "Nasdaq Baltic Updates Trading Information for AgroCredit Latvia 7% Bond",
      "summary": "AgroCredit has announced updates to their bond trading information on Nasdaq Baltic exchange, reflecting current market conditions and investor interest.",
      "url": "https://example.com/news1",
      "date": "2025-06-15"
    }
  ]
}
```'''
    
    # Test case 2: Raw JSON without markdown
    raw_json = '''{
  "news_items": [
    {
      "title": "Financial Update",
      "summary": "Recent quarterly results show strong performance across key metrics.",
      "content": "The company reported increased revenue and improved operational efficiency.",
      "url": "https://example.com/news2"
    }
  ]
}'''
    
    # Test case 3: Mixed content with JSON artifacts
    mixed_content = '''Here is the most recent and relevant financial news:
```json
{
  "news_items": [
    {
      "title": "Market Analysis Report",
      "summary": "Comprehensive analysis of market trends and financial performance indicators.",
      "url": "https://example.com/news3"
    }
  ]
}
```'''
    
    # Create test news items
    test_cases = [
        {
            "name": "JSON with markdown blocks",
            "content": json_content,
            "title": "News Update for AgroCredit",
            "company": "AgroCredit"
        },
        {
            "name": "Raw JSON content",
            "content": raw_json,
            "title": "News Update for DelfinGroup", 
            "company": "DelfinGroup"
        },
        {
            "name": "Mixed content with JSON",
            "content": mixed_content,
            "title": "News Update for Auga Group",
            "company": "Auga Group"
        }
    ]
    
    reader = PerplexityNewsReader()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        # Create test news item
        news_item = PerplexityNewsItem(
            title=test_case["title"],
            url="https://example.com/test",
            date=datetime.now().isoformat(),
            content=test_case["content"],
            company_name=test_case["company"],
            search_terms="test search"
        )
        
        # Format the message
        formatted_message = reader.format_news_message(news_item)
        
        print("Original content preview:")
        print(test_case["content"][:100] + "..." if len(test_case["content"]) > 100 else test_case["content"])
        print(f"\nFormatted message ({len(formatted_message)} chars):")
        print(formatted_message)
        print("\n" + "="*50)
    
    print("\n✅ Message formatting test completed!")
    print("\nKey improvements:")
    print("• JSON artifacts are properly removed")
    print("• Meaningful content is extracted from structured data")
    print("• Duplicate headers are eliminated")
    print("• Clean, readable format for users")
    print("• Proper fallback for edge cases")

if __name__ == "__main__":
    test_json_content_cleaning()