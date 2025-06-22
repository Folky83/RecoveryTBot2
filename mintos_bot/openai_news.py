"""
OpenAI News Reader - Integrated with Brave API
Uses Brave API for search, then OpenAI for selecting most authoritative source
"""

import asyncio
import aiohttp
import json
import urllib.parse
import os
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
# import pandas as pd  # Temporarily disabled due to system library issues

from .logger import setup_logger
from .brave_news import BraveNewsReader, BraveNewsResult

logger = setup_logger(__name__)

@dataclass
class OpenAINewsItem:
    """Represents a news item found by OpenAI"""
    title: str
    url: str
    date: str
    content: str
    company_name: str
    search_terms: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OpenAINewsItem':
        """Create from dictionary"""
        return cls(**data)

class OpenAINewsReader:
    """OpenAI-based news reader integrated with Brave API search"""

    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.brave_reader = BraveNewsReader()
        self.companies = self.brave_reader.companies
        self.csv_log_file = 'data/brave_openai_responses.tsv'
        self.rejected_urls_file = 'data/openai_rejected_urls.json'
        self._ensure_csv_headers()
        self._load_rejected_urls()

    async def _select_best_result_with_openai(self, quoted_results: List[BraveNewsResult], unquoted_results: List[BraveNewsResult], company: Dict[str, str]):
        """Use OpenAI to analyze both quoted and unquoted Brave results and select the most authoritative/relevant one"""
        all_results = quoted_results + unquoted_results
        if not self.openai_api_key or not all_results:
            return None
            
        try:
            company_name = company.get('company_name', 'Unknown')
            brief_description = company.get('brief_description', '')
            
            # Add certainty tags to results for OpenAI analysis
            tagged_results = []
            for result in quoted_results:
                result.certainty = 'high'
                tagged_results.append(result)
            for result in unquoted_results:
                result.certainty = 'low'
                tagged_results.append(result)
            
            # Prepare results summary for OpenAI analysis
            results_summary = []
            for i, result in enumerate(tagged_results, 1):
                certainty_tag = "[HIGH CERTAINTY]" if getattr(result, 'certainty', 'low') == 'high' else "[LOWER CERTAINTY]"
                results_summary.append(f"""
Result {i} {certainty_tag}:
Title: {result.title}
URL: {result.url}
Description: {result.description}
Published: {result.age}
Source Domain: {result.meta_url.get('hostname', 'Unknown')}
""")
            
            # Create prompt for OpenAI to select best result
            prompt = f"""
You are analyzing news search results for the financial company "{company_name}" ({brief_description}).

Please review these search results and select the SINGLE most authoritative and relevant news article:

{chr(10).join(results_summary)}

CRITICAL COMPANY RELEVANCE CRITERIA:
The article MUST specifically mention "{company_name}" by name in the title OR description.

REJECT articles that only contain:
- General industry trends without mentioning {company_name} specifically
- Competitor news (other companies in the same sector)
- General market analysis or sector reports
- Job postings or career-related content
- Regional economic news without company-specific information
- Regulatory changes affecting the industry broadly

ACCEPT articles that discuss:
- {company_name}'s financial results, earnings, or revenue
- {company_name}'s business announcements, press releases, or corporate news
- {company_name}'s acquisitions, mergers, partnerships, or strategic initiatives
- {company_name}'s new products, services, or market expansions
- {company_name}'s executive appointments or leadership changes
- {company_name}'s regulatory issues or legal matters
- Direct quotes from {company_name} representatives or executives

Selection criteria (in order of priority):
1. MUST explicitly mention {company_name} by name
2. Comes from credible financial/business news sources
3. Contains specific information about {company_name}'s business operations or financial performance
4. Has recent and accurate information
5. When results have similar quality, prioritize [HIGH CERTAINTY] results over [LOWER CERTAINTY] ones

Respond ONLY with a JSON object in this exact format:
{{
    "selected_index": <1-based index of chosen result>,
    "reasoning": "<brief explanation focusing on how the article specifically mentions {company_name}>",
    "title": "<exact title from chosen result>",
    "content_summary": "<create a clear 1-2 sentence summary focusing on what this means for {company_name}>",
    "translation_needed": <true/false - whether the content appears to be in a non-English language>,
    "translated_summary": "<if translation_needed is true, provide English translation of the summary>",
    "is_relevant": true/false
}}

For content_summary: Extract key business information specifically about {company_name} from the article's description.
For translation: If the content contains non-English text (Spanish, Russian, German, etc.), set translation_needed to true and provide an English translation.

If NO results specifically mention "{company_name}" by name, set "is_relevant": false.
"""

            payload = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are a financial news analyst that selects the most credible and relevant news sources."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 300
            }
            
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI API request failed: {response.status} - {error_text}")
                        return None
                    
                    data = await response.json()
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    if not content:
                        logger.warning(f"No content in OpenAI response for {company_name}")
                        return None
                    
                    # Parse OpenAI response
                    analysis = None
                    try:
                        import re
                        json_match = re.search(r'\{.*\}', content, re.DOTALL)
                        if json_match:
                            analysis = json.loads(json_match.group())
                            
                            if not analysis.get('is_relevant', False):
                                logger.info(f"OpenAI determined no relevant results for {company_name}")
                                return analysis  # Return analysis for logging
                            
                            selected_index = analysis.get('selected_index', 1) - 1  # Convert to 0-based
                            if 0 <= selected_index < len(all_results):
                                selected_result = all_results[selected_index]
                                
                                # Use OpenAI's content analysis and translation
                                final_content = analysis.get('content_summary', selected_result.description)
                                if analysis.get('translation_needed', False) and analysis.get('translated_summary'):
                                    final_content = analysis.get('translated_summary')
                                
                                # Create OpenAI news item from selected Brave result
                                selected_item = OpenAINewsItem(
                                    title=analysis.get('title', selected_result.title),
                                    url=selected_result.url,
                                    date=self._parse_brave_date(selected_result.page_age),
                                    content=final_content,
                                    company_name=company_name,
                                    search_terms=f'"{company_name}",{brief_description}'
                                )
                                return (analysis, selected_item)
                            
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.error(f"Error parsing OpenAI analysis response: {e}")
                        return None
                    
                    return analysis  # Return analysis even if no item selected
                        
        except Exception as e:
            company_name = company.get('company_name', 'Unknown')
            logger.error(f"Error in OpenAI analysis for {company_name}: {e}")
            return None
        
        return None
    
    def _ensure_csv_headers(self):
        """Ensure CSV file exists with proper headers"""
        try:
            if not os.path.exists(self.csv_log_file):
                os.makedirs(os.path.dirname(self.csv_log_file), exist_ok=True)
                with open(self.csv_log_file, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile, delimiter='\t')
                    writer.writerow([
                        'timestamp', 'company_name', 'company_description', 'quoted_query', 'unquoted_query',
                        'date_range', 'quoted_results_count', 'unquoted_results_count', 'total_results_count',
                        'all_results_json', 'openai_analysis', 'selected_result_index', 'selected_title',
                        'selected_url', 'is_relevant'
                    ])
        except Exception as e:
            logger.warning(f"Could not create CSV log file: {e}")

    def _load_rejected_urls(self):
        """Load previously rejected URLs from file"""
        self.rejected_urls = set()
        try:
            if os.path.exists(self.rejected_urls_file):
                with open(self.rejected_urls_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.rejected_urls = set(data.get('rejected_urls', []))
                    logger.info(f"Loaded {len(self.rejected_urls)} previously rejected URLs")
            else:
                # Create empty file
                os.makedirs(os.path.dirname(self.rejected_urls_file), exist_ok=True)
                self._save_rejected_urls()
        except Exception as e:
            logger.warning(f"Could not load rejected URLs: {e}")
            self.rejected_urls = set()

    def _save_rejected_urls(self):
        """Save rejected URLs to file"""
        try:
            with open(self.rejected_urls_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'rejected_urls': list(self.rejected_urls),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save rejected URLs: {e}")

    def _filter_rejected_urls(self, results: List[BraveNewsResult]) -> List[BraveNewsResult]:
        """Filter out URLs that have been previously rejected by OpenAI"""
        if not self.rejected_urls:
            return results
        
        filtered_results = []
        rejected_count = 0
        
        for result in results:
            if result.url not in self.rejected_urls:
                filtered_results.append(result)
            else:
                rejected_count += 1
        
        if rejected_count > 0:
            logger.info(f"Filtered out {rejected_count} previously rejected URLs from results")
        
        return filtered_results
    
    def _log_to_csv(self, company: Dict[str, str], quoted_results: List[BraveNewsResult],
                    unquoted_results: List[BraveNewsResult], openai_analysis: Optional[Dict], 
                    selected_item: Optional[OpenAINewsItem], days_back: int):
        """Log the search session to CSV"""
        try:
            # Prepare data for CSV
            timestamp = datetime.now().isoformat()
            company_name = company.get('company_name', '')
            company_description = company.get('brief_description', '')
            quoted_query = f'"{company_name}",{company_description}'
            unquoted_query = f'{company_name},{company_description}'
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            date_range = f"{start_date.strftime('%Y-%m-%d')}to{end_date.strftime('%Y-%m-%d')}"
            
            # Add certainty flag to results
            quoted_results_with_certainty = []
            for result in quoted_results:
                result_dict = result.to_dict()
                result_dict['certainty'] = 'high'
                quoted_results_with_certainty.append(result_dict)
            
            unquoted_results_with_certainty = []
            for result in unquoted_results:
                result_dict = result.to_dict()
                result_dict['certainty'] = 'low'
                unquoted_results_with_certainty.append(result_dict)
            
            all_results = quoted_results_with_certainty + unquoted_results_with_certainty
            all_results_json = json.dumps(all_results)
            
            openai_analysis_json = json.dumps(openai_analysis) if openai_analysis else ""
            selected_index = openai_analysis.get('selected_index', '') if openai_analysis else ''
            selected_title = selected_item.title if selected_item else ''
            selected_url = selected_item.url if selected_item else ''
            is_relevant = openai_analysis.get('is_relevant', False) if openai_analysis else False
            
            # Write to TSV (tab-separated values)
            with open(self.csv_log_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter='\t')
                writer.writerow([
                    timestamp, company_name, company_description, quoted_query, unquoted_query,
                    date_range, len(quoted_results), len(unquoted_results), len(all_results),
                    all_results_json, openai_analysis_json, selected_index, selected_title,
                    selected_url, is_relevant
                ])
                
            logger.debug(f"Logged search session to CSV: {company_name}, {len(quoted_results)} quoted + {len(unquoted_results)} unquoted results, relevant: {is_relevant}")
            
        except Exception as e:
            logger.warning(f"Could not log to CSV: {e}")
    
    def _parse_brave_date(self, page_age: str) -> str:
        """Parse Brave API page_age to standard date format"""
        try:
            if 'T' in page_age:
                # ISO format: 2025-03-17T07:59:58
                date_part = page_age.split('T')[0]
                # Validate and format for display
                date_obj = datetime.strptime(date_part, '%Y-%m-%d')
                return date_obj.strftime('%d %b %Y')  # Format as "17 Mar 2025"
            else:
                # Try other formats or fallback
                return datetime.now().strftime('%d %b %Y')
        except Exception:
            return datetime.now().strftime('%d %b %Y')







    async def search_company_news_with_date_filter(self, company: Dict[str, str], days_back: int) -> List[OpenAINewsItem]:
        """Search for company news using Brave API + OpenAI analysis"""
        if not self.openai_api_key:
            logger.error("OpenAI API key not configured")
            return []
        
        try:
            company_name = company.get('company_name', 'Unknown Company')
            
            # Step 1: Search Brave API with quoted company name (high certainty)
            logger.info(f"Searching Brave API for {company_name} (quoted)")
            quoted_results_raw = await self.brave_reader.search_company_news(company, days_back)
            quoted_results = self._filter_rejected_urls(quoted_results_raw)
            
            # Step 2: Rate limiting between queries (Brave API: 1 request per second)
            await asyncio.sleep(1.1)
            
            # Step 3: Search Brave API without quotes (lower certainty)
            logger.info(f"Searching Brave API for {company_name} (unquoted)")
            # Create unquoted version of company data
            unquoted_company = company.copy()
            unquoted_company['use_quotes'] = 'false'
            unquoted_results_raw = await self.brave_reader.search_company_news(unquoted_company, days_back)
            unquoted_results = self._filter_rejected_urls(unquoted_results_raw)
            
            total_results = len(quoted_results) + len(unquoted_results)
            logger.info(f"Found {len(quoted_results)} quoted + {len(unquoted_results)} unquoted = {total_results} total results for {company_name}")
            
            if total_results == 0:
                logger.info(f"No Brave results found for {company_name}")
                # Still log the empty search
                self._log_to_csv(company, [], [], None, None, days_back)
                return []
            
            # Step 4: Use OpenAI to analyze both sets of results
            openai_result = await self._select_best_result_with_openai(quoted_results, unquoted_results, company)
            
            analysis = None
            selected_item = None
            
            if isinstance(openai_result, tuple):
                # Got both analysis and selected item
                analysis, selected_item = openai_result
            elif isinstance(openai_result, dict):
                # Got only analysis (no relevant results)
                analysis = openai_result
            
            # Track rejected URLs if OpenAI marked results as not relevant
            if analysis and not analysis.get('is_relevant', False):
                self._track_rejected_urls(quoted_results + unquoted_results)
            
            # Log to CSV regardless of outcome
            self._log_to_csv(company, quoted_results, unquoted_results, analysis, selected_item, days_back)
            
            if selected_item:
                logger.info(f"OpenAI selected best result for {company_name}: {selected_item.title}")
                return [selected_item]
            else:
                logger.info(f"OpenAI found no suitable results for {company_name}")
                return []
                    
        except Exception as e:
            company_name = company.get('company_name', 'Unknown Company')
            logger.error(f"Error searching news for {company_name}: {e}")
            return []



    async def fetch_news_by_days(self, days: int, use_cache: bool = False) -> List[OpenAINewsItem]:
        """Fetch news for all companies within specified days using Brave + OpenAI"""
        all_news = []
        
        for company in self.companies:
            try:
                company_news = await self.search_company_news_with_date_filter(company, days)
                all_news.extend(company_news)
                
                # Rate limiting for company iterations (dual queries + OpenAI analysis)
                await asyncio.sleep(2.5)  # Allow for dual Brave queries + OpenAI processing
                
            except Exception as e:
                company_name = company.get('company_name', 'Unknown')
                logger.error(f"Error fetching news for {company_name}: {e}")
                continue
        
        logger.info(f"Fetched total of {len(all_news)} news items from {len(self.companies)} companies")
        return all_news

    def get_user_preference(self, user_id: str) -> bool:
        """OpenAI news is always enabled - no user preferences needed"""
        return True

    def set_user_preference(self, user_id: str, enabled: bool) -> None:
        """OpenAI news is always enabled - no user preferences needed"""
        pass

    def is_item_sent(self, user_id: str, item_url: str) -> bool:
        """Simple sent tracking - always return False for now"""
        return False

    def mark_item_sent(self, user_id: str, item_url: str) -> None:
        """Simple sent tracking - no-op for now"""
        pass

    def reset_sent_items(self, user_id: str) -> int:
        """Reset sent items for user - return count of reset items"""
        return 0

    def _track_rejected_urls(self, results: List[BraveNewsResult]):
        """Track URLs that were rejected by OpenAI as not relevant"""
        if not results:
            return
        
        new_rejected_count = 0
        for result in results:
            if result.url not in self.rejected_urls:
                self.rejected_urls.add(result.url)
                new_rejected_count += 1
        
        if new_rejected_count > 0:
            logger.info(f"Added {new_rejected_count} URLs to rejected list")
            self._save_rejected_urls()

    def get_rejected_urls_count(self) -> int:
        """Get count of rejected URLs for monitoring"""
        return len(self.rejected_urls)

    def clear_rejected_urls(self) -> int:
        """Clear all rejected URLs (admin function)"""
        count = len(self.rejected_urls)
        self.rejected_urls.clear()
        self._save_rejected_urls()
        logger.info(f"Cleared {count} rejected URLs")
        return count



    def format_news_message(self, item: 'OpenAINewsItem') -> str:
        """Format a news item for Telegram message"""
        try:
            import html
            
            # Get company info for Perplexity search
            company_info = None
            for company in self.companies:
                if company.get('company_name') == item.company_name:
                    company_info = company
                    break
            
            company_description = company_info.get('brief_description', '') if company_info else ''
            
            # Create Perplexity search URL
            perplexity_query = f"{item.company_name}"
            if company_description:
                perplexity_query += f" {company_description}"
            perplexity_query += " latest news"
            encoded_perplexity_query = urllib.parse.quote(perplexity_query)
            perplexity_url = f"https://www.perplexity.ai/search?q={encoded_perplexity_query}"
            
            # Format message with new structure
            message = "🔍 <b>Brave + OpenAI Search</b>\n\n"
            message += f"<b>{html.escape(item.company_name)}</b>\n\n"
            
            # Use content (summary) instead of title
            content_to_display = item.content or item.title
            if content_to_display:
                # Note: Translation would need to be done during news processing, not here
                # as this is a sync function but translation is async
                message += f"{html.escape(content_to_display)}\n\n"
            
            # Use date from item (should be parsed from page_age)
            message += f"📅 {item.date}\n\n"
            
            # Add "Read more" link (source URL)
            if item.url and item.url.startswith('http'):
                message += f"🔗 <a href='{item.url}'>Read more</a>\n"
            
            # Add Perplexity search link
            message += f"🔍 <a href='{perplexity_url}'>Search Perplexity</a>"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting news message: {e}")
            import html
            # Fallback formatting
            return (f"🔍 <b>Brave + OpenAI Search</b>\n\n"
                   f"<b>{html.escape(item.company_name)}</b>\n"
                   f"{html.escape(item.content or item.title)}\n"
                   f"📅 {item.date}\n"
                   f"🔗 <a href='{item.url}'>Read more</a>")