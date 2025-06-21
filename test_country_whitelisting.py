#!/usr/bin/env python3
"""
Test script to verify the country-based domain whitelisting functionality
Ensures exactly 10 domains maximum per company search
"""
import asyncio
import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mintos_bot.perplexity_news import PerplexityNewsReader

async def test_country_whitelisting():
    """Test the country-based domain whitelisting functionality"""
    
    print("Testing Country-Based Domain Whitelisting")
    print("=" * 50)
    
    # Initialize the news reader
    news_reader = PerplexityNewsReader()
    
    # Test loading country sources
    print(f"Loaded country sources for {len(news_reader.country_sources)} countries")
    
    # Show sample countries and their domain counts
    print("\nSample country sources:")
    for country, domains in list(news_reader.country_sources.items())[:5]:
        print(f"  {country}: {len(domains)} domains - {domains[:3]}{'...' if len(domains) > 3 else ''}")
    
    # Test with sample companies that have different country configurations
    test_companies = [
        {
            'brand_name': 'AvaFin',
            'legal_name': 'SIA AvaFin',
            'ActivityCountry': 'Latvia',
            'RegCountry': 'Latvia'
        },
        {
            'brand_name': 'Adapundi',
            'legal_name': 'PT Adapundi Investama',
            'ActivityCountry': 'Indonesia', 
            'RegCountry': 'Singapore'
        },
        {
            'brand_name': 'TestCompany',
            'legal_name': 'Test Company Ltd',
            'ActivityCountry': 'Mexico',
            'RegCountry': 'Estonia'
        },
        {
            'brand_name': 'NoCountryCompany',
            'legal_name': 'No Country Company',
            'ActivityCountry': '',
            'RegCountry': ''
        }
    ]
    
    print("\nTesting domain whitelisting for different companies:")
    print("-" * 60)
    
    for company in test_companies:
        print(f"\nCompany: {company['brand_name']}")
        print(f"Activity Country: {company['ActivityCountry']}")
        print(f"Registration Country: {company['RegCountry']}")
        
        # Get whitelisted domains
        domains = news_reader._get_whitelisted_domains(company)
        
        print(f"Whitelisted domains: {len(domains)} (max 10)")
        
        # Verify API limit compliance
        if len(domains) > 10:
            print(f"❌ ERROR: Too many domains ({len(domains)}), API limit is 10!")
        elif len(domains) == 0:
            print("⚠️  WARNING: No whitelisted domains found")
        else:
            print(f"✅ OK: {len(domains)} domains within API limit")
        
        # Show the domains
        if domains:
            print(f"Domains: {', '.join(domains)}")
        
        print("-" * 40)
    
    # Test with actual company data
    print("\nTesting with actual company data:")
    print("-" * 40)
    
    if news_reader.companies:
        # Test first 3 companies from actual data
        for company in news_reader.companies[:3]:
            name = company.get('brand_name', company.get('legal_name', 'Unknown'))
            activity_country = company.get('ActivityCountry', 'N/A')
            reg_country = company.get('RegCountry', 'N/A')
            
            domains = news_reader._get_whitelisted_domains(company)
            
            print(f"\nCompany: {name}")
            print(f"Countries: {activity_country} / {reg_country}")
            print(f"Domains: {len(domains)} (limit: 10)")
            
            if len(domains) > 10:
                print(f"❌ VIOLATION: {len(domains)} domains exceed API limit!")
            else:
                print("✅ Compliant with API limit")

async def main():
    """Main test function"""
    await test_country_whitelisting()

if __name__ == "__main__":
    asyncio.run(main())