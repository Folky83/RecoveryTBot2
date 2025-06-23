"""
Simple configuration loader that supports multiple ways to set API keys
Makes it easy for users to configure the bot with config files.
"""
import os
import logging

def load_config_value(key_name):
    """
    Load configuration value from multiple sources in order of preference:
    1. Environment variable
    2. config.txt file in current directory
    3. config.txt file in user's home directory
    """
    logger = logging.getLogger(__name__)
    
    # Method 1: Environment variable
    value = os.getenv(key_name)
    if value:
        logger.info(f"{key_name} loaded from environment variable")
        return value
    
    # Method 2: config.txt in current directory
    config_files = ['config.txt', 'bot_config.txt', '.env']
    
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith(f'{key_name}='):
                            value = line.split('=', 1)[1].strip()
                            if value:
                                logger.info(f"{key_name} loaded from {config_file}")
                                return value
            except Exception as e:
                logger.warning(f"Could not read {config_file}: {e}")
    
    # Method 3: config.txt in home directory
    home_config = os.path.expanduser('~/mintos_bot_config.txt')
    if os.path.exists(home_config):
        try:
            with open(home_config, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f'{key_name}='):
                        value = line.split('=', 1)[1].strip()
                        if value:
                            logger.info(f"{key_name} loaded from {home_config}")
                            return value
        except Exception as e:
            logger.warning(f"Could not read {home_config}: {e}")
    
    return None

def load_telegram_token():
    """Load Telegram bot token from config sources"""
    token = load_config_value('TELEGRAM_BOT_TOKEN')
    if not token:
        logger = logging.getLogger(__name__)
        logger.error("No Telegram bot token found!")
        logger.error("Please set your token using one of these methods:")
        logger.error("1. Set environment variable: set TELEGRAM_BOT_TOKEN=your_token_here")
        logger.error("2. Create config.txt file with: TELEGRAM_BOT_TOKEN=your_token_here")
        logger.error("3. Create ~/.mintos_bot_config.txt with: TELEGRAM_BOT_TOKEN=your_token_here")
    return token

def load_openai_key():
    """Load OpenAI API key from config sources"""
    return load_config_value('OPENAI_API_KEY')

def create_sample_config():
    """Create a sample config file for users"""
    sample_config = """# Mintos Telegram Bot Configuration
# Replace the placeholder values with your actual API keys

# Telegram Bot Token (required)
# To get a bot token:
# 1. Open Telegram and search for @BotFather
# 2. Send /newbot command
# 3. Follow the instructions to create your bot
# 4. Copy the token and paste it below
TELEGRAM_BOT_TOKEN=your_bot_token_here

# OpenAI API Key (required for news analysis)
# To get an OpenAI API key:
# 1. Go to https://platform.openai.com/api-keys
# 2. Create an account or log in
# 3. Generate a new API key
# 4. Copy the key and paste it below
OPENAI_API_KEY=your_openai_api_key_here

# Brave Search API Key (optional - for enhanced news search)
BRAVE_API_KEY=your_brave_api_key_here
"""
    
    try:
        with open('config.txt', 'w', encoding='utf-8') as f:
            f.write(sample_config)
        print("Created sample config.txt file")
        print("Please edit config.txt and add your Telegram bot token")
        return True
    except Exception as e:
        print(f"Could not create config.txt: {e}")
        return False