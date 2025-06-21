"""
Test script to verify the simplified news format with just title and source URL
"""
import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader, PerplexityNewsItem

async def test_simplified_format():
    """Test the new simplified news format"""
    print("Testing simplified news format...")
    
    # Create a test news item with the new format
    test_item = PerplexityNewsItem(
        title="Test Company Announces Major Financial Restructuring",
        url="https://example.com/news/test-article",
        date="2025-06-16",
        content="📰 Test Company Announces Major Financial Restructuring\n🔗 Source: https://example.com/news/test-article",
        company_name="Test Company",
        search_terms="Test Company financial news"
    )
    
    # Create news reader instance
    news_reader = PerplexityNewsReader()
    
    # Format the message
    formatted_message = news_reader.format_news_message(test_item)
    
    print("\nFormatted message:")
    print("="*50)
    print(formatted_message)
    print("="*50)
    
    # Verify the new format is being used
    if "📰" in formatted_message and "🔗 Source:" in formatted_message:
        print("\n✅ SUCCESS: New simplified format is working!")
        print("- Shows news title with 📰 icon")
        print("- Shows source URL with 🔗 icon")
    else:
        print("\n❌ ISSUE: Format not as expected")
    
    # Check that old format elements are not present
    if "📋 Summary:" not in formatted_message and "📈 Financial Relevance:" not in formatted_message:
        print("✅ SUCCESS: Old detailed format removed")
    else:
        print("❌ ISSUE: Old format elements still present")

if __name__ == "__main__":
    asyncio.run(test_simplified_format())