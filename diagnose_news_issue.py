"""
Diagnostic script to identify why no news is being found
"""
import asyncio
import sys
import os
import aiohttp
import json

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_basic_api_call():
    """Test basic Perplexity API call without restrictive filters"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("No API key found")
        return
    
    # Test with a simple, less restrictive prompt
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "user",
                "content": "Find recent news about Eleving Group or AS Mogo from Latvia. Return any financial or business news."
            }
        ],
        "temperature": 0.2,
        "max_tokens": 1000
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("Testing basic API call...")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.perplexity.ai/chat/completions",
            json=payload,
            headers=headers
        ) as response:
            if response.status != 200:
                print(f"API Error: {response.status} - {await response.text()}")
                return
            
            data = await response.json()
            print(f"Status: {response.status}")
            print(f"Citations found: {len(data.get('citations', []))}")
            print(f"Content length: {len(data.get('choices', [{}])[0].get('message', {}).get('content', ''))}")
            
            if data.get('citations'):
                print("Citations:")
                for i, citation in enumerate(data.get('citations', [])[:3]):
                    print(f"  {i+1}. {citation}")
            
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            if content:
                print("\nContent preview:")
                print(content[:500] + "..." if len(content) > 500 else content)

async def test_with_date_filter():
    """Test with date filter to see if that's the issue"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    from datetime import datetime, timedelta
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%m/%d/%Y')
    
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "user",
                "content": "Find news about Eleving Group Latvia. Any business or financial news."
            }
        ],
        "search_after_date_filter": cutoff_date,
        "temperature": 0.2,
        "max_tokens": 1000
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\nTesting with 30-day date filter (after {cutoff_date})...")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.perplexity.ai/chat/completions",
            json=payload,
            headers=headers
        ) as response:
            data = await response.json()
            print(f"Status: {response.status}")
            print(f"Citations found: {len(data.get('citations', []))}")
            print(f"Content length: {len(data.get('choices', [{}])[0].get('message', {}).get('content', ''))}")

async def main():
    """Run diagnostic tests"""
    print("=== Perplexity News Diagnostic ===")
    await test_basic_api_call()
    await test_with_date_filter()

if __name__ == "__main__":
    asyncio.run(main())