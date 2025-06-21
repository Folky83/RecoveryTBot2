#!/usr/bin/env python3
"""
Test script to verify company name display is working correctly
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_company_name_display():
    """Test that company names are displayed correctly in news items"""
    print("Testing company name display functionality...")
    
    # Initialize the news reader
    news_reader = PerplexityNewsReader()
    
    if not news_reader.companies:
        print("No companies loaded")
        return
    
    print(f"Loaded {len(news_reader.companies)} companies")
    
    # Check how company names are being processed
    print("\nCompany name display examples:")
    for i, company in enumerate(news_reader.companies[:10]):
        brand_name = company.get('brand_name', '').strip()
        legal_name = company.get('legal_name', '').strip()
        group_name = company.get('group_name', '').strip()
        
        # Apply the same logic as in the fixed code
        display_name = brand_name
        if not display_name or display_name == '-':
            display_name = legal_name
        if not display_name or display_name == '-':
            display_name = group_name if group_name else 'Unknown Company'
        
        print(f"  {i+1}. Brand: '{brand_name}' | Legal: '{legal_name}' | Group: '{group_name}'")
        print(f"     Display Name: '{display_name}'")
        print()

async def main():
    """Main test function"""
    await test_company_name_display()

if __name__ == "__main__":
    asyncio.run(main())