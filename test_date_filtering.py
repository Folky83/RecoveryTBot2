#!/usr/bin/env python3
"""
Quick test script to verify date filtering works correctly
"""
import asyncio
from datetime import datetime, timedelta
from mintos_bot.perplexity_news import PerplexityNewsReader, PerplexityNewsItem

def test_date_filtering():
    """Test the date filtering functionality"""
    
    print("Testing date filtering logic...")
    
    reader = PerplexityNewsReader()
    
    # Create test news items with different dates
    now = datetime.now()
    cutoff_date = now - timedelta(days=7)
    
    test_items = [
        PerplexityNewsItem(
            title="Recent News",
            url="https://example.com/1",
            date=(now - timedelta(days=2)).isoformat(),
            content="Recent content",
            company_name="TestCompany1",
            search_terms="test"
        ),
        PerplexityNewsItem(
            title="Old News",
            url="https://example.com/2", 
            date=(now - timedelta(days=30)).isoformat(),
            content="Old content",
            company_name="TestCompany2",
            search_terms="test"
        ),
        PerplexityNewsItem(
            title="Today's News",
            url="https://example.com/3",
            date=now.isoformat(),
            content="Today's content",
            company_name="TestCompany3",
            search_terms="test"
        )
    ]
    
    print(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}")
    print(f"Test items before filtering: {len(test_items)}")
    
    # Test the filtering
    filtered_items = reader._filter_news_by_date(test_items, cutoff_date)
    
    print(f"Items after filtering: {len(filtered_items)}")
    
    for item in filtered_items:
        item_date = reader._parse_date(item.date)
        print(f"- {item.title}: {item_date.strftime('%Y-%m-%d')} (within range)")
    
    print("Date filtering test completed!")
    return len(filtered_items) == 2  # Should keep 2 items (recent and today's)

if __name__ == "__main__":
    success = test_date_filtering()
    print(f"Test {'PASSED' if success else 'FAILED'}")