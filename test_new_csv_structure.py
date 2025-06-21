#!/usr/bin/env python3
"""
Test script to verify the new CSV structure with enhanced company descriptions is working
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_new_csv_structure():
    """Test the new CSV structure with enhanced company descriptions"""
    print("Testing new CSV structure with enhanced company descriptions...")
    
    # Initialize the news reader
    news_reader = PerplexityNewsReader()
    
    # Load company data to verify the new structure
    companies = news_reader._load_company_data()
    print(f"Loaded {len(companies)} companies from new CSV structure")
    
    # Display first few companies to verify data structure
    print("\nFirst 5 companies with descriptions:")
    for i, company in enumerate(companies[:5]):
        company_name = company.get('company_name', 'N/A')
        brief_description = company.get('brief_description', 'N/A')
        print(f"{i+1}. {company_name}")
        print(f"   Description: {brief_description}")
        
        # Test search terms building
        search_terms = news_reader._build_search_terms(company)
        print(f"   Search terms: {search_terms}")
        print()
    
    # Test with a specific company to see enhanced search context
    print("Testing enhanced search with a specific company...")
    if companies:
        test_company = companies[0]  # Use first company
        company_name = test_company.get('company_name', '')
        brief_description = test_company.get('brief_description', '')
        
        print(f"Testing company: {company_name}")
        print(f"Description: {brief_description}")
        
        # Test search terms generation
        search_terms = news_reader._build_search_terms(test_company)
        print(f"Enhanced search terms: {search_terms}")
        
        # Verify the search terms include both name and description context
        expected_format = f"{company_name} ({brief_description})"
        if search_terms == expected_format:
            print("✓ Search terms format is correct")
        else:
            print("✗ Search terms format is incorrect")
            print(f"Expected: {expected_format}")
            print(f"Got: {search_terms}")

async def main():
    """Main test function"""
    await test_new_csv_structure()

if __name__ == "__main__":
    asyncio.run(main())