#!/usr/bin/env python3
"""
Test script for Perplexity news caching functionality
"""
import asyncio
import os
from datetime import datetime, timedelta
from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_caching():
    """Test the caching functionality"""
    
    print("🧪 Testing Perplexity News Caching")
    print("=" * 40)
    
    news_reader = PerplexityNewsReader()
    
    # Test with 7 days
    days = 7
    print(f"🔍 Testing cache for {days} days range")
    
    # First call - should fetch from API and cache
    print("📥 First call (should fetch from API)...")
    start_time = datetime.now()
    news_items_1 = await news_reader.fetch_news_by_days(days, use_cache=True)
    first_call_time = (datetime.now() - start_time).total_seconds()
    print(f"  ⏱️ Time taken: {first_call_time:.2f} seconds")
    print(f"  📰 Items found: {len(news_items_1)}")
    
    # Second call - should load from cache
    print("\n💾 Second call (should load from cache)...")
    start_time = datetime.now()
    news_items_2 = await news_reader.fetch_news_by_days(days, use_cache=True)
    second_call_time = (datetime.now() - start_time).total_seconds()
    print(f"  ⏱️ Time taken: {second_call_time:.2f} seconds")
    print(f"  📰 Items found: {len(news_items_2)}")
    
    # Verify cache is faster
    if second_call_time < first_call_time:
        print(f"✅ Cache is working! {first_call_time/second_call_time:.1f}x faster")
    else:
        print("⚠️ Cache might not be working as expected")
    
    # Verify same results
    if len(news_items_1) == len(news_items_2):
        print("✅ Same number of items returned from cache")
    else:
        print("⚠️ Different number of items from cache")
    
    # Test cache directory
    cache_dir = "data/news_cache"
    if os.path.exists(cache_dir):
        cache_files = os.listdir(cache_dir)
        print(f"📁 Cache directory has {len(cache_files)} files")
        for file in cache_files:
            file_path = os.path.join(cache_dir, file)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"  📄 {file} (created: {mod_time.strftime('%H:%M:%S')})")
    else:
        print("❌ Cache directory not found")
    
    # Test bypassing cache
    print("\n🚫 Third call (bypassing cache)...")
    start_time = datetime.now()
    news_items_3 = await news_reader.fetch_news_by_days(days, use_cache=False)
    third_call_time = (datetime.now() - start_time).total_seconds()
    print(f"  ⏱️ Time taken: {third_call_time:.2f} seconds")
    print(f"  📰 Items found: {len(news_items_3)}")
    
    print(f"\n✅ Caching test completed!")
    print(f"📊 Performance comparison:")
    print(f"  • First call (API): {first_call_time:.2f}s")
    print(f"  • Second call (cache): {second_call_time:.2f}s") 
    print(f"  • Third call (no cache): {third_call_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_caching())