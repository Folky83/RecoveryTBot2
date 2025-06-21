#!/usr/bin/env python3
"""
Script to check the structure of company_perplexity.xlsx
"""
import pandas as pd

def main():
    try:
        # Read the Excel file
        df = pd.read_excel('company_perplexity.xlsx')
        
        print("Column names:")
        for col in df.columns:
            print(f"  - {col}")
        
        print(f"\nTotal rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        
        # Show first few rows
        print("\nFirst 5 rows:")
        print(df.head().to_string())
        
        # Check if country column exists
        if 'country' in df.columns:
            print(f"\nCountry column found!")
            print("Unique countries:")
            countries = df['country'].value_counts()
            for country, count in countries.items():
                print(f"  - {country}: {count} companies")
        else:
            # Check for other possible country column names
            possible_country_cols = [col for col in df.columns if 'country' in col.lower()]
            if possible_country_cols:
                print(f"\nPossible country columns found: {possible_country_cols}")
            else:
                print("\nNo country column found")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == "__main__":
    main()