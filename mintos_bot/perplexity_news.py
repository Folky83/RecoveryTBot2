"""
Perplexity News Reader for Company Updates
Handles fetching news for companies using Perplexity AI's sonar model
"""
import asyncio
import aiohttp
import json
import os
# import pandas as pd  # Temporarily disabled due to system library issues
import hashlib
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from .logger import setup_logger
from .base_manager import BaseManager

logger = setup_logger(__name__)

# Cache configuration
CACHE_DIR = "data/news_cache"
CACHE_DURATION_HOURS = 6

class PerplexityNewsItem:
    """Represents a single news item from Perplexity"""
    
    def __init__(self, title: str, url: str, date: str, content: str, company_name: str, search_terms: str):
        self.title = title
        self.url = url
        self.date = date  # Date from the news source
        self.content = content
        self.company_name = company_name
        self.search_terms = search_terms
        self.guid = self._generate_guid()
        self.published_dt = self._parse_date(date)
    
    def _generate_guid(self) -> str:
        """Generate a unique identifier for this news item"""
        import hashlib
        unique_string = f"{self.title}_{self.url}_{self.company_name}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats to datetime object"""
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Try standard date format
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Could not parse date: {date_str}")
                return datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'title': self.title,
            'url': self.url,
            'date': self.date,
            'content': self.content,
            'company_name': self.company_name,
            'search_terms': self.search_terms,
            'guid': self.guid,
            'timestamp': self.published_dt.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerplexityNewsItem':
        """Create from dictionary"""
        return cls(
            title=data['title'],
            url=data['url'],
            date=data['date'],
            content=data['content'],
            company_name=data['company_name'],
            search_terms=data['search_terms']
        )

class PerplexityNewsReader(BaseManager):
    """Perplexity News Reader for company updates"""
    
    def __init__(self):
        super().__init__('data/perplexity_news_cache.json')
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.company_file = 'data/mintos_companies_prompt_input.csv'
        self.sent_items_file = 'data/perplexity_sent_items.json'
        self.user_preferences_file = 'data/perplexity_user_preferences.json'
        
        # Blacklisted domains to exclude from searches
        self.blacklisted_domains = ['-nasdaqbaltic.com', '-nasdaq.com']
        
        # Load company data
        self.companies = self._load_company_data()
        
        # Load user preferences
        self.user_preferences = self._load_user_preferences()
        
        # Load sent items
        self.sent_items = self._load_sent_items()
        
        # Initialize cache
        self._ensure_cache_dir()
    
    def _load_company_data(self) -> List[Dict[str, str]]:
        """Load company data from CSV file"""
        try:
            df = pd.read_csv(self.company_file)
            companies = []
            seen_companies = set()  # Track duplicates
            
            for _, row in df.iterrows():
                company_name = str(row['Company Name']).strip()
                brief_description = str(row['Brief Description']).strip()
                
                # Skip empty rows or duplicates
                if not company_name or company_name in seen_companies:
                    if company_name:
                        logger.debug(f"Skipping duplicate company: {company_name}")
                    continue
                
                seen_companies.add(company_name)
                
                company_data = {
                    'company_name': company_name,
                    'brief_description': brief_description,
                    'investment_type': 'Bond'  # Default for Mintos companies
                }
                
                companies.append(company_data)
            
            logger.info(f"Loaded {len(companies)} unique companies from {self.company_file} (deduplicated)")
            return companies
        except Exception as e:
            logger.error(f"Error loading company data: {e}")
            return []
    

    
    def _load_user_preferences(self) -> Dict[str, bool]:
        """Load user preferences for Perplexity news"""
        try:
            if os.path.exists(self.user_preferences_file):
                with open(self.user_preferences_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
        return {}
    
    def _save_user_preferences(self) -> None:
        """Save user preferences"""
        try:
            os.makedirs(os.path.dirname(self.user_preferences_file), exist_ok=True)
            with open(self.user_preferences_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving user preferences: {e}")
    
    def _load_sent_items(self) -> Dict[str, List[str]]:
        """Load sent items tracking"""
        try:
            if os.path.exists(self.sent_items_file):
                with open(self.sent_items_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading sent items: {e}")
        return {}
    
    def _save_sent_items(self) -> None:
        """Save sent items tracking"""
        try:
            os.makedirs(os.path.dirname(self.sent_items_file), exist_ok=True)
            with open(self.sent_items_file, 'w') as f:
                json.dump(self.sent_items, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving sent items: {e}")
    
    def set_user_preference(self, chat_id: str, enabled: bool) -> None:
        """Set Perplexity news preference for a user"""
        self.user_preferences[str(chat_id)] = enabled
        self._save_user_preferences()
        logger.info(f"Perplexity news {'enabled' if enabled else 'disabled'} for user {chat_id}")
    
    def get_user_preference(self, chat_id: str) -> bool:
        """Get Perplexity news preference for a user (default: False)"""
        return self.user_preferences.get(str(chat_id), False)
    
    def get_users_with_news_enabled(self) -> List[str]:
        """Get list of users who have Perplexity news enabled"""
        return [chat_id for chat_id, enabled in self.user_preferences.items() if enabled]
    
    def is_item_sent(self, chat_id: str, item_url: str) -> bool:
        """Check if an item has been sent to a specific user based on URL"""
        return item_url in self.sent_items.get(str(chat_id), [])
    
    def mark_item_sent(self, chat_id: str, item_url: str) -> None:
        """Mark an item as sent to a specific user based on URL"""
        if str(chat_id) not in self.sent_items:
            self.sent_items[str(chat_id)] = []
        if item_url not in self.sent_items[str(chat_id)]:
            self.sent_items[str(chat_id)].append(item_url)
            self._save_sent_items()
    
    def reset_sent_items(self, chat_id: str | None = None) -> int:
        """Reset sent items tracking for a specific user or all users"""
        if chat_id:
            # Reset for specific user
            count = len(self.sent_items.get(str(chat_id), []))
            self.sent_items[str(chat_id)] = []
        else:
            # Reset for all users
            count = sum(len(items) for items in self.sent_items.values())
            self.sent_items.clear()
        
        self._save_sent_items()
        return count
    

    

    
    async def fetch_all_company_news_with_date_filter(self, days_back: int) -> List[PerplexityNewsItem]:
        """Fetch news for all companies using exact date filtering"""
        all_news = []
        
        logger.info(f"Fetching news for {len(self.companies)} companies for last {days_back} days")
        
        for company in self.companies:
            try:
                news_items = await self.search_company_news_with_date_filter(company, days_back)
                all_news.extend(news_items)
                company_name = company.get('company_name', 'Unknown Company')
                logger.info(f"Found {len(news_items)} news items for {company_name}")
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                company_name = company.get('company_name', 'Unknown Company')
                logger.error(f"Error fetching news for {company_name}: {e}")
        
        logger.info(f"Total news items fetched: {len(all_news)}")
        return all_news
    
    def format_news_message(self, item: PerplexityNewsItem) -> str:
        """Format a news item for Telegram message"""
        # Parse date for display
        try:
            date_obj = datetime.fromisoformat(item.date.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%d %b %Y')
        except:
            formatted_date = item.date
        
        # Clean up content - extract meaningful text from JSON or raw content
        content = item.content.strip() if item.content else ""
        clean_content = ""
        
        # Check if content is already properly formatted (contains title and source)
        if content and '📰' in content and '🔗 Source:' in content:
            # Content is already properly formatted, use as-is
            clean_content = content
        # Remove JSON artifacts and extract meaningful content
        elif content:
            try:
                import json
                import re
                
                # Remove markdown code blocks
                content = re.sub(r'```json\s*', '', content)
                content = re.sub(r'```\s*$', '', content)
                
                # Try to parse as JSON
                if content.startswith('{') and '"news_items"' in content:
                    try:
                        json_data = json.loads(content)
                        if 'news_items' in json_data and json_data['news_items']:
                            # Extract the first meaningful news item
                            for news_item in json_data['news_items']:
                                if isinstance(news_item, dict):
                                    # Get summary or description
                                    summary = news_item.get('summary', '') or news_item.get('description', '') or news_item.get('content', '')
                                    if summary and len(summary.strip()) > 20:  # Only use substantial content
                                        clean_content = summary.strip()
                                        break
                                    # Fallback to title if no good summary
                                    title = news_item.get('title', '')
                                    if title and not clean_content:
                                        clean_content = title.strip()
                    except json.JSONDecodeError:
                        pass
                
                # If JSON parsing failed or didn't yield good content, clean the raw text
                if not clean_content:
                    # Remove JSON-like structures and extract readable text
                    text_lines = []
                    for line in content.split('\n'):
                        line = line.strip()
                        # Skip JSON syntax lines
                        if line in ['{', '}', '[', ']'] or line.startswith('"') or line.endswith(',') or line.endswith(':'):
                            continue
                        # Extract quoted strings that look like meaningful content
                        if '"' in line:
                            matches = re.findall(r'"([^"]*)"', line)
                            for match in matches:
                                if len(match.strip()) > 10 and not match.lower().startswith(('title', 'url', 'date')):
                                    text_lines.append(match.strip())
                        elif len(line) > 10:
                            text_lines.append(line)
                    
                    if text_lines:
                        clean_content = ' '.join(text_lines[:2])  # Use first 2 meaningful lines
                
                # Final fallback - if still no content, provide a generic message
                if not clean_content or len(clean_content.strip()) < 10:
                    clean_content = "Recent financial news and business developments for this company."
                
            except Exception as e:
                logger.debug(f"Error cleaning content: {e}")
                clean_content = "Recent financial news and business developments."
        
        # Create clean, professional message layout
        message = f"📰 <b>Perplexity News Search</b>\n"
        message += f"🏢 <b>{item.company_name}</b> - Financial Update\n\n"
        
        # Extract URLs from content if stored as dict string
        source_url = None
        perplexity_url = None
        title_content = clean_content
        
        try:
            import ast
            if clean_content and clean_content.startswith('{'):
                content_dict = ast.literal_eval(clean_content)
                title_content = content_dict.get('title', clean_content)
                source_url = content_dict.get('source_url')
                perplexity_url = content_dict.get('perplexity_url')
        except:
            # Fallback to original content if parsing fails
            title_content = clean_content
        
        if title_content:
            message += f"{title_content}\n\n"
        
        message += f"📅 {formatted_date}\n"
        
        # Add source URL under "Read more" if available
        if source_url:
            message += f"🔗 <a href='{source_url}'>Read more</a>\n"
        
        # Add Perplexity search link
        if perplexity_url:
            message += f"🔍 <a href='{perplexity_url}'>Search Perplexity</a>"
        else:
            # Fallback perplexity search if not stored
            search_query = f"{item.company_name.replace(' ', '+')}+financial+news"
            message += f"🔍 <a href='https://www.perplexity.ai/search?q={search_query}'>Search Perplexity</a>"
        
        return message
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        os.makedirs(CACHE_DIR, exist_ok=True)
    
    def _get_cache_key(self, companies: List[Dict], days: int) -> str:
        """Generate cache key for news results"""
        company_names = sorted([c['company_name'] for c in companies])
        key_data = f"{'_'.join(company_names)}_{days}days"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path"""
        return os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cache is still valid"""
        if not os.path.exists(cache_path):
            return False
        
        try:
            mod_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
            expiry_time = mod_time + timedelta(hours=CACHE_DURATION_HOURS)
            return datetime.now() < expiry_time
        except:
            return False
    
    def _load_cached_results(self, cache_key: str) -> Optional[List[PerplexityNewsItem]]:
        """Load cached news results"""
        cache_path = self._get_cache_path(cache_key)
        
        if not self._is_cache_valid(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            items = []
            for item_data in data:
                items.append(PerplexityNewsItem.from_dict(item_data))
            
            logger.info(f"Loaded {len(items)} items from cache")
            return items
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return None
    
    def _build_search_terms(self, company: Dict[str, str]) -> str:
        """Build search terms for a company using company name and brief description"""
        company_name = company.get('company_name', '').strip()
        brief_description = company.get('brief_description', '').strip()
        
        # Combine company name with descriptive context
        if brief_description:
            return f"{company_name} ({brief_description})"
        else:
            return company_name
    
    def _get_search_domain_filter(self, company: Dict[str, str]) -> List[str]:
        """Get domain filter using only blacklisted domains"""
        domains = []
        
        # Only add blacklisted domains (with - prefix for denial)
        domains.extend(self.blacklisted_domains)
        
        company_name = company.get('company_name', 'Unknown')
        logger.debug(f"Company {company_name}: Using domain filter: {domains}")
        
        return domains
    
    def _is_valid_news_result(self, result: Dict, company: Dict[str, str], cutoff_date: datetime) -> bool:
        """Check if search result is valid news within date range"""
        title = result.get('title', '').lower()
        company_name = company.get('company_name', '').lower()
        
        # Check date filter
        result_date_str = result.get('date', '')
        if result_date_str:
            try:
                result_date = self._parse_date(result_date_str)
                if result_date < cutoff_date:
                    return False
            except Exception:
                pass  # Include if date parsing fails
        
        # Skip promotional content
        promotional_keywords = [
            'unlock fast cash', 'loan app', 'download', 'install',
            'get loan', 'apply now', 'quick cash', 'instant loan',
            'best app', 'top app', 'review app'
        ]
        
        if any(keyword in title for keyword in promotional_keywords):
            return False
        
        # Require company mention or business relevance
        business_keywords = [
            'earnings', 'revenue', 'profit', 'acquisition', 'merger',
            'regulatory', 'approval', 'license', 'partnership', 'expansion',
            'financial', 'investment', 'funding', 'ipo', 'listing'
        ]
        
        has_company_mention = company_name in title
        has_business_relevance = any(keyword in title for keyword in business_keywords)
        
        return has_company_mention or has_business_relevance
    
    def _create_news_item_from_result(self, result: Dict, company: Dict[str, str], search_terms: str) -> Optional[PerplexityNewsItem]:
        """Create news item from search result"""
        try:
            import urllib.parse
            
            title = result.get('title', 'News Update')
            source_url = result.get('url', '')
            result_date = result.get('date', datetime.now().strftime('%Y-%m-%d'))
            
            # Create Perplexity search URL
            company_name = company.get('company_name', '').strip()
            search_query = f"{company_name} {title}"
            encoded_query = urllib.parse.quote(search_query)
            perplexity_url = f"https://www.perplexity.ai/search?q={encoded_query}"
            
            # Store URLs for message formatting
            content_with_urls = {
                'title': title,
                'source_url': source_url,
                'perplexity_url': perplexity_url
            }
            
            return PerplexityNewsItem(
                title=title,
                url=source_url if source_url else perplexity_url,
                date=result_date,
                content=str(content_with_urls),
                company_name=company_name,
                search_terms=search_terms
            )
        except Exception as e:
            logger.error(f"Error creating news item: {e}")
            return None

    async def search_company_news_with_date_filter(self, company: Dict[str, str], days_back: int) -> List[PerplexityNewsItem]:
        """Simplified search using Perplexity's native search_results"""
        if not self.api_key:
            logger.error("Perplexity API key not configured")
            return []
        
        try:
            search_terms = self._build_search_terms(company)
            company_name = company.get('company_name', 'Unknown Company')
            
            # Create date filter for API request
            cutoff_date_str = (datetime.now() - timedelta(days=days_back)).strftime('%m/%d/%Y')
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Simple, direct query without complex JSON formatting
            user_query = f"Recent financial and business news about {search_terms}"
            
            payload = {
                "model": "sonar",
                "messages": [
                    {"role": "user", "content": user_query}
                ],
                "max_tokens": 800,
                "temperature": 0.1,
                "search_after_date_filter": cutoff_date_str,
                "web_search_options": {
                    "search_context_size": "medium"
                }
            }
            
            # Add domain filter if configured
            domain_filter = self._get_search_domain_filter(company)
            if domain_filter:
                payload["search_domain_filter"] = domain_filter
                logger.debug(f"Using domain filter for {search_terms}: {domain_filter}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Searching for '{search_terms}' with date filter: after {cutoff_date_str}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.perplexity.ai/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        logger.error(f"API request failed: {response.status} - {await response.text()}")
                        return []
                    
                    data = await response.json()
                    search_results = data.get('search_results', [])
                    citations = data.get('citations', [])
                    
                    # Verify we have authentic sources
                    if not search_results and not citations:
                        logger.warning(f"No search results or citations found for {company_name}")
                        return []
                    
                    logger.debug(f"Found {len(search_results)} search results for {company_name}")
                    
                    # Process search results directly
                    news_items = []
                    for result in search_results[:5]:  # Limit to top 5 results
                        if self._is_valid_news_result(result, company, cutoff_date):
                            news_item = self._create_news_item_from_result(result, company, search_terms)
                            if news_item:
                                news_items.append(news_item)
                    
                    logger.info(f"Created {len(news_items)} news items for {company_name}")
                    return news_items
                    
        except Exception as e:
            company_name = company.get('company_name', 'Unknown Company')
            logger.error(f"Error searching news for {company_name}: {e}")
            return []
    
    def _save_cached_results(self, cache_key: str, items: List[PerplexityNewsItem]):
        """Save news results to cache"""
        cache_path = self._get_cache_path(cache_key)
        
        try:
            data = [item.to_dict() for item in items]
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(items)} items to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    async def fetch_news_by_days(self, days: int, use_cache: bool = False) -> List[PerplexityNewsItem]:
        """Fetch news for all companies within specified days"""
        # Always perform fresh search - caching disabled
        logger.info(f"Performing fresh news search (caching disabled)")
        
        # Determine recency filter for API
        if days <= 1:
            recency_filter = "day"
        elif days <= 14:  # Extended week range for better precision
            recency_filter = "week"  
        elif days <= 30:
            recency_filter = "month"
        else:
            recency_filter = "year"
        
        # Fetch fresh data with proper API filtering
        logger.info(f"Fetching news for last {days} days using exact date filtering")
        all_news = await self.fetch_all_company_news_with_date_filter(days)
        
        # Apply client-side filtering for precise day range if needed
        target_date = datetime.now() - timedelta(days=days)
        cutoff_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        filtered_news = self._filter_news_by_date(all_news, cutoff_date)
        
        # Caching disabled - skip saving results
        
        logger.info(f"API returned {len(all_news)} items, filtered to {len(filtered_news)} items within last {days} days")
        return filtered_news
    
    def _filter_news_by_date(self, news_items: List[PerplexityNewsItem], cutoff_date: datetime) -> List[PerplexityNewsItem]:
        """Filter news items to only include those after the cutoff date"""
        filtered_items = []
        skipped_count = 0
        invalid_date_count = 0
        
        logger.debug(f"Starting date filtering with cutoff: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        for item in news_items:
            try:
                # Parse the item's date
                item_date = self._parse_date(item.date)
                
                # Convert to comparable format (remove time component for day-level comparison)
                item_date_day = item_date.replace(hour=0, minute=0, second=0, microsecond=0)
                cutoff_date_day = cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Only include items from after or on the cutoff date
                if item_date_day >= cutoff_date_day:
                    filtered_items.append(item)
                    logger.debug(f"Included item from {item_date.strftime('%Y-%m-%d')} for {item.company_name}")
                else:
                    skipped_count += 1
                    logger.debug(f"Filtered out item from {item_date.strftime('%Y-%m-%d')} (before {cutoff_date.strftime('%Y-%m-%d')}) for {item.company_name}")
                    
            except Exception as e:
                invalid_date_count += 1
                logger.warning(f"Could not parse date '{item.date}' for {item.company_name}: {e}")
                # For items with invalid dates, only include if they're from today (fallback date)
                if item.date == datetime.now().strftime('%Y-%m-%d'):
                    filtered_items.append(item)
                    logger.debug(f"Included item with fallback date for {item.company_name}")
        
        logger.info(f"Date filtering completed: {len(filtered_items)} included, {skipped_count} filtered out, {invalid_date_count} invalid dates")
        return filtered_items
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats to datetime object"""
        if not date_str or not isinstance(date_str, str):
            raise ValueError(f"Invalid date string: {date_str}")
        
        date_str = date_str.strip()
        
        # Common date formats to try
        date_formats = [
            "%Y-%m-%d",           # 2025-06-17
            "%Y-%m-%dT%H:%M:%S",  # 2025-06-17T10:30:00
            "%Y-%m-%dT%H:%M:%SZ", # 2025-06-17T10:30:00Z
            "%m/%d/%Y",           # 06/17/2025
            "%d/%m/%Y",           # 17/06/2025
            "%d.%m.%Y",           # 17.06.2025
            "%B %d, %Y",          # June 17, 2025
            "%b %d, %Y",          # Jun 17, 2025
            "%d %B %Y",           # 17 June 2025
            "%d %b %Y",           # 17 Jun 2025
        ]
        
        # Try ISO format first (with timezone handling)
        try:
            if 'T' in date_str:
                parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                # Convert to naive datetime for consistent comparison
                if parsed_date.tzinfo is not None:
                    parsed_date = parsed_date.replace(tzinfo=None)
                return parsed_date
        except ValueError:
            pass
        
        # Try each format
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If all parsing fails, raise an exception
        raise ValueError(f"Could not parse date format: {date_str}")

    def _validate_date_format(self, date_str: str) -> bool:
        """Validate if date string is in YYYY-MM-DD format"""
        try:
            datetime.strptime(date_str.strip(), '%Y-%m-%d')
            return True
        except (ValueError, AttributeError):
            return False