#!/usr/bin/env python3
"""
Quick test to verify the new header formatting is working
"""
from datetime import datetime
from mintos_bot.perplexity_news import PerplexityNewsReader, PerplexityNewsItem

def test_header_format():
    """Test the new header format"""
    reader = PerplexityNewsReader()
    
    # Create a test news item
    test_item = PerplexityNewsItem(
        title="Test News",
        url="https://example.com",
        date=datetime.now().isoformat(),
        content="📈 Financial Relevance: This is a test financial relevance.\n📋 Summary: This is a test summary.",
        company_name="Test Company",
        search_terms="test"
    )
    
    # Format the message
    formatted_message = reader.format_news_message(test_item)
    
    print("Formatted message:")
    print(formatted_message)
    print("\n" + "="*50)
    
    # Check if it contains the expected format (accounting for HTML bold tags)
    if "📰 <b>Perplexity News Search</b>" in formatted_message and "🏢 <b>Test Company</b> - Financial Update" in formatted_message:
        print("✅ Header format is correct!")
        print("✅ Changes successfully implemented!")
    else:
        print("❌ Header format is incorrect")
        print("Expected: '📰 <b>Perplexity News Search</b>' and '🏢 <b>Test Company</b> - Financial Update'")

if __name__ == "__main__":
    test_header_format()