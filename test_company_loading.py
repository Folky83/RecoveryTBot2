#!/usr/bin/env python3
"""
Test script to debug company loading issue
"""

import os
import csv
import sys

def test_company_loading():
    """Test the company loading logic"""
    print("Testing company loading...")
    
    # Try multiple locations for the CSV file
    possible_paths = [
        'data/mintos_companies_prompt_input.csv',
        'mintos_bot/data/mintos_companies_prompt_input.csv',
        os.path.join(os.path.dirname(__file__), 'data', 'mintos_companies_prompt_input.csv')
    ]
    
    print(f"Current working directory: {os.getcwd()}")
    
    csv_path = None
    for path in possible_paths:
        print(f"Checking path: {path} - exists: {os.path.exists(path)}")
        if os.path.exists(path):
            csv_path = path
            break
    
    if not csv_path:
        print("ERROR: No CSV file found!")
        return []
    
    print(f"Using CSV file: {csv_path}")
    
    try:
        companies_dict = {}
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            print(f"CSV headers: {reader.fieldnames}")
            
            for i, row in enumerate(reader):
                if i < 3:  # Show first 3 rows for debugging
                    print(f"Row {i}: {row}")
                
                company_name = str(row.get('Company Name', '')).strip()
                if company_name and company_name not in companies_dict:
                    companies_dict[company_name] = {
                        'company_name': company_name,
                        'brief_description': str(row.get('Brief Description', '')).strip(),
                        'mintos_url': f"https://www.mintos.com/en/lending-companies/{company_name.replace(' ', '')}",
                        'country': str(row.get('Country', 'US')).strip()
                    }
        
        companies = list(companies_dict.values())
        print(f"Successfully loaded {len(companies)} companies")
        if companies:
            print(f"First company: {companies[0]}")
        
        return companies
        
    except Exception as e:
        print(f"Error loading companies: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    companies = test_company_loading()
    print(f"Final result: {len(companies)} companies loaded")