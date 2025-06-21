"""
Brave API News Search Integration
Uses Brave Search API to find news articles, then processes them with OpenAI
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
# import pandas as pd  # Temporarily disabled due to system library issues

from .logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class BraveNewsResult:
    """Represents a news result from Brave API"""
    title: str
    url: str
    description: str
    age: str
    page_age: str
    meta_url: Dict[str, Any]
    thumbnail: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BraveNewsResult':
        """Create from dictionary"""
        return cls(**data)

class BraveNewsReader:
    """Brave API-based news reader for financial companies"""

    def __init__(self):
        self.api_key = os.getenv('BRAVE_API_KEY')
        self.base_url = "https://api.search.brave.com/res/v1/news/search"
        self.companies = []
        # Mapping for unsupported country codes to closest supported alternatives
        self.country_mapping = {
            'LV': 'RU',  # Latvia -> Russia (closest geographically)
            'EE': 'RU',  # Estonia -> Russia (closest geographically)
            'BG': 'RU',  # Bulgaria -> Russia (closest supported)
            'KZ': 'RU',  # Kazakhstan -> Russia (closest supported)
            'MD': 'RU',  # Moldova -> Russia (closest supported) 
            'KE': 'ZA',  # Kenya -> South Africa (closest supported in Africa)
            'MN': 'CN',  # Mongolia -> China (closest supported)
            'LT': 'RU',  # Lithuania -> Russia (closest supported)
            'RO': 'RU',  # Romania -> Russia (closest supported)
            'HR': 'DE',  # Croatia -> Germany (closest supported in Europe)
            'SI': 'AT',  # Slovenia -> Austria (closest supported)
            'SK': 'AT',  # Slovakia -> Austria (closest supported)
            'CZ': 'AT',  # Czech Republic -> Austria (closest supported)
            'HU': 'AT',  # Hungary -> Austria (closest supported)
            'RS': 'RU',  # Serbia -> Russia (closest supported)
            'BA': 'RU',  # Bosnia -> Russia (closest supported)
            'MK': 'RU',  # North Macedonia -> Russia (closest supported)
            'AL': 'IT',  # Albania -> Italy (closest supported)
            'GE': 'RU',  # Georgia -> Russia (closest supported)
            'AM': 'RU',  # Armenia -> Russia (closest supported)
            'AZ': 'RU',  # Azerbaijan -> Russia (closest supported)
            'UZ': 'RU',  # Uzbekistan -> Russia (closest supported)
            'KG': 'RU',  # Kyrgyzstan -> Russia (closest supported)
            'TJ': 'RU',  # Tajikistan -> Russia (closest supported)
            'TM': 'RU',  # Turkmenistan -> Russia (closest supported)
            'BY': 'RU',  # Belarus -> Russia (closest supported)
            'UA': 'RU',  # Ukraine -> Russia (closest supported)
        }
        self._load_companies()

    def _load_companies(self):
        """Load companies from CSV file"""
        try:
            csv_path = 'data/mintos_companies_prompt_input.csv'
            if os.path.exists(csv_path):
                # Read CSV manually without pandas
                import csv
                companies_dict = {}
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        company_name = str(row.get('Company Name', '')).strip()
                        if company_name and company_name not in companies_dict:
                            companies_dict[company_name] = {
                                'company_name': company_name,
                                'brief_description': str(row.get('Brief Description', '')).strip(),
                                'mintos_url': f"https://www.mintos.com/en/lending-companies/{company_name.replace(' ', '')}",
                                'country': str(row.get('Country', 'US')).strip()  # Default to US if no country specified
                            }
                
                self.companies = list(companies_dict.values())
                logger.info(f"Loaded {len(self.companies)} unique companies from {csv_path}")
            else:
                logger.warning(f"Companies CSV file not found: {csv_path}")
        except Exception as e:
            logger.error(f"Error loading companies: {e}")

    def _build_search_query(self, company: Dict[str, str]) -> str:
        """Build search query with quoted company name and description"""
        company_name = company.get('company_name', '').strip()
        brief_description = company.get('brief_description', '').strip()
        use_quotes = company.get('use_quotes', 'true') != 'false'
        
        # Quote the company name for exact matching if enabled
        if use_quotes:
            formatted_name = f'"{company_name}"'
        else:
            formatted_name = company_name
        
        if brief_description:
            return f'{formatted_name},{brief_description}'
        return formatted_name

    def _format_freshness_date(self, days_back: int) -> str:
        """Format date range for Brave API freshness parameter"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        return f"{start_str}to{end_str}"

    def _get_supported_country_code(self, country_code: str) -> str:
        """Convert country code to Brave API supported country code"""
        # List of supported country codes by Brave API
        supported_countries = {
            'AR', 'AU', 'AT', 'BE', 'BR', 'CA', 'CL', 'DK', 'FI', 'FR', 'DE', 'HK', 
            'IN', 'ID', 'IT', 'JP', 'KR', 'MY', 'MX', 'NL', 'NZ', 'NO', 'CN', 'PL', 
            'PT', 'PH', 'RU', 'SA', 'ZA', 'ES', 'SE', 'CH', 'TW', 'TR', 'GB', 'US'
        }
        
        # If country code is already supported, return it
        if country_code in supported_countries:
            return country_code
        
        # If not supported, use mapping to closest alternative
        mapped_country = self.country_mapping.get(country_code, 'US')  # Default to US
        logger.debug(f"Mapping unsupported country {country_code} to {mapped_country}")
        return mapped_country

    async def search_company_news(self, company: Dict[str, str], days_back: int) -> List[BraveNewsResult]:
        """Search for company news using Brave API"""
        if not self.api_key:
            logger.error("Brave API key not configured")
            return []

        try:
            search_query = self._build_search_query(company)
            freshness = self._format_freshness_date(days_back)
            company_name = company.get('company_name', 'Unknown')
            original_country = company.get('country', 'US')
            company_country = self._get_supported_country_code(original_country)
            
            params = {
                "q": search_query,
                "country": company_country,
                "count": "10",
                "spellcheck": "false",
                "freshness": freshness
            }

            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "x-subscription-token": self.api_key
            }
            
            if original_country != company_country:
                logger.info(f"Searching Brave API for '{search_query}' (country: {original_country} -> {company_country}, freshness: {freshness})")
            else:
                logger.info(f"Searching Brave API for '{search_query}' (country: {company_country}, freshness: {freshness})")
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(
                    self.base_url,
                    params=params,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Brave API request failed: {response.status} - {error_text}")
                        return []
                    
                    data = await response.json()
                    
                    # Extract results from Brave API response
                    results = data.get('results', [])
                    brave_results = []
                    
                    for item in results:
                        if item.get('type') == 'news_result':
                            try:
                                brave_result = BraveNewsResult(
                                    title=item.get('title', ''),
                                    url=item.get('url', ''),
                                    description=item.get('description', ''),
                                    age=item.get('age', ''),
                                    page_age=item.get('page_age', ''),
                                    meta_url=item.get('meta_url', {}),
                                    thumbnail=item.get('thumbnail')
                                )
                                brave_results.append(brave_result)
                            except Exception as e:
                                logger.warning(f"Error parsing Brave result: {e}")
                                continue
                    
                    logger.info(f"Found {len(brave_results)} news results for {company_name}")
                    return brave_results
                    
        except Exception as e:
            logger.error(f"Error searching Brave API for {company.get('company_name', 'Unknown')}: {e}")
            return []

    async def fetch_news_by_days(self, days: int) -> Dict[str, List[BraveNewsResult]]:
        """Fetch news for all companies within specified days"""
        all_results = {}
        
        for company in self.companies:
            try:
                company_name = company.get('company_name', 'Unknown')
                company_results = await self.search_company_news(company, days)
                if company_results:
                    all_results[company_name] = company_results
                
                # Rate limiting for Brave API
                await asyncio.sleep(0.5)
                
            except Exception as e:
                company_name = company.get('company_name', 'Unknown')
                logger.error(f"Error fetching news for {company_name}: {e}")
                continue
        
        total_results = sum(len(results) for results in all_results.values())
        logger.info(f"Fetched total of {total_results} news results from {len(all_results)} companies")
        return all_results