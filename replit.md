# Mintos Telegram Bot

## Overview

The Mintos Telegram Bot is a sophisticated monitoring and notification system for the Mintos peer-to-peer lending platform. It provides real-time tracking of recovery updates, campaigns, document changes, and financial news for lending companies, delivering notifications through Telegram and a web dashboard.

## System Architecture

### Backend Architecture
- **Language**: Python 3.11+
- **Framework**: Asynchronous Python with asyncio
- **Communication**: Telegram Bot API integration
- **Web Interface**: Streamlit dashboard on port 5000
- **Deployment**: Cloud Run with webhook support

### Frontend Architecture
- **Dashboard**: Streamlit-based web interface
- **User Interface**: Telegram bot with inline keyboards
- **Responsive Design**: Mobile-friendly Telegram interface

## Key Components

### Core Services
1. **Telegram Bot (`telegram_bot.py`)**: Main bot interface handling user commands and notifications
2. **Mintos Client (`mintos_client.py`)**: API client for Mintos platform data retrieval
3. **Data Manager (`data_manager.py`)**: Centralized data persistence and caching layer
4. **Document Scraper (`document_scraper.py`)**: Automated PDF document monitoring system

### News Integration
1. **OpenAI News Reader (`openai_news.py`)**: Primary news search using GPT-4o model
2. **Brave Search Integration (`brave_news.py`)**: Alternative news source via Brave API
3. **RSS Reader (`rss_reader.py`)**: Multi-source RSS feed monitoring (NASDAQ Baltic, Mintos, FFNews)

### Data Sources
- **Company Data**: CSV-based company information with rich descriptions
- **Recovery Updates**: JSON-cached Mintos API responses
- **Document Tracking**: Automated PDF discovery and change detection
- **Financial News**: AI-powered search with contextual company information

## Data Flow

### Update Monitoring
1. Periodic polling of Mintos API for recovery updates and campaigns
2. Data comparison against cached versions to identify new items
3. User notification via Telegram with formatted messages
4. Web dashboard synchronization for browser access

### News Processing
1. Company-specific search term generation using rich descriptions
2. OpenAI GPT-4o model queries for relevant financial news
3. Domain filtering to exclude irrelevant sources
4. User notification with formatted news summaries

### Document Monitoring
1. Web scraping of company pages for document links
2. Change detection through content hashing
3. PDF categorization (Presentation, Financials, Loan Agreement)
4. Automated notification of new document availability

## External Dependencies

### APIs and Services
- **Telegram Bot API**: Core messaging and user interaction
- **OpenAI API**: GPT-4o model for news analysis and search
- **Brave Search API**: Alternative news source (optional)
- **Mintos Platform API**: Recovery data and company information

### Python Packages
- `python-telegram-bot`: Telegram integration
- `aiohttp`: Async HTTP client
- `beautifulsoup4`: HTML parsing for document scraping
- `streamlit`: Web dashboard framework
- `pandas`: Data manipulation (temporarily disabled)
- `openai`: OpenAI API integration

## Deployment Strategy

### Replit Environment
- **Runtime**: Python 3.11 with Nix package management
- **Port Configuration**: External port 80 → Internal port 5000
- **Process Management**: Single process handling both bot and dashboard
- **Persistence**: File-based data storage in `/data` directory

### Configuration Management
- **Environment Variables**: `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`
- **Config Files**: Support for `config.txt` with key-value pairs
- **Fallback System**: Multiple configuration source priority

### Process Lifecycle
1. **Startup**: Token validation and service initialization
2. **Lock Management**: Single instance enforcement via file locking
3. **Webhook Setup**: Automatic Telegram webhook configuration
4. **Graceful Shutdown**: Cleanup of resources and temporary files

## Recent Changes
- June 30, 2025: Fixed Brave API key configuration loading - updated brave_news module to use centralized config loader system instead of only checking environment variables
- June 24, 2025: Fixed Windows logging permission errors by implementing platform-specific logging approach
- June 24, 2025: Bot successfully deployed and running on Replit with dashboard on port 5000
- June 24, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.