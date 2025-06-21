import json
import os
from .logger import setup_logger
from .config import USERS_FILE, DATA_DIR

logger = setup_logger(__name__)

class UserManager:
    def __init__(self):
        self.users = {}  # Changed from set to dict to store username with chat_id
        self.rss_preferences_file = os.path.join(DATA_DIR, 'rss_user_preferences.json')
        self.notification_preferences_file = os.path.join(DATA_DIR, 'notification_preferences.json')
        self.user_states_file = os.path.join(DATA_DIR, 'user_states.json')
        self.rss_preferences = {}  # Store RSS notification preferences
        self.notification_preferences = {}  # Store other notification preferences
        self.user_states = {}  # Store user states for interactive commands
        self._ensure_data_directory()
        self.load_users()
        self._load_rss_preferences()
        self._load_notification_preferences()
        self._load_user_states()

    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(USERS_FILE):
            self.save_users()  # Create an empty users file if it doesn't exist
        logger.info(f"Data directory checked: {DATA_DIR}")

    def load_users(self):
        try:
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, 'r') as f:
                    data = json.load(f)
                    # Handle both old format (list of chat_ids) and new format (dict with usernames)
                    if isinstance(data, list):
                        # Convert old format to new format
                        self.users = {chat_id: None for chat_id in data}
                        logger.info(f"Converted {len(data)} users from old format to new format")
                    else:
                        self.users = data
                logger.info(f"Loaded {len(self.users)} users")
            else:
                self.users = {}
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            self.users = {}  # Reset to empty dict on error

    def save_users(self):
        try:
            with open(USERS_FILE, 'w') as f:
                json.dump(self.users, f)
            logger.info(f"Users saved successfully: {self.users}")
            
            # Verify the file was written correctly
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, 'r') as f:
                    saved_data = f.read().strip()
                    logger.info(f"Verification - users.json contains: {saved_data}")
            else:
                logger.error(f"Verification failed - {USERS_FILE} does not exist after save")
        except Exception as e:
            logger.error(f"Error saving users: {e}", exc_info=True)

    def add_user(self, chat_id, username=None):
        """Add or update a user with optional username"""
        chat_id = str(chat_id)
        self.users[chat_id] = username
        self.save_users()
        if username:
            logger.info(f"Added/updated user: {chat_id} (username: {username})")
        else:
            logger.info(f"Added/updated user: {chat_id}")

    def remove_user(self, chat_id):
        """Remove a user from the saved users list"""
        chat_id = str(chat_id)
        if chat_id in self.users:
            username = self.users.pop(chat_id)
            self.save_users()
            if username:
                logger.info(f"Removed user: {chat_id} (username: {username})")
            else:
                logger.info(f"Removed user: {chat_id}")

    def get_all_users(self):
        """Get list of all user chat IDs"""
        return list(self.users.keys())
    
    def get_user_info(self, chat_id):
        """Get username for a given chat_id"""
        chat_id = str(chat_id)
        return self.users.get(chat_id)

    def has_user(self, chat_id):
        """Check if a user exists in the saved users list"""
        return str(chat_id) in self.users

    def _load_rss_preferences(self):
        """Load RSS notification preferences"""
        try:
            if os.path.exists(self.rss_preferences_file):
                with open(self.rss_preferences_file, 'r') as f:
                    self.rss_preferences = json.load(f)
                logger.info(f"Loaded RSS preferences for {len(self.rss_preferences)} users")
            else:
                self.rss_preferences = {}
        except Exception as e:
            logger.error(f"Error loading RSS preferences: {e}")
            self.rss_preferences = {}

    def _save_rss_preferences(self):
        """Save RSS notification preferences"""
        try:
            with open(self.rss_preferences_file, 'w') as f:
                json.dump(self.rss_preferences, f, indent=2)
            logger.info(f"Saved RSS preferences for {len(self.rss_preferences)} users")
        except Exception as e:
            logger.error(f"Error saving RSS preferences: {e}")

    def set_rss_preference(self, chat_id, enabled):
        """Set RSS notifications preference for a user (legacy method for backward compatibility)"""
        chat_id = str(chat_id)
        # Convert legacy boolean to new format with all feeds enabled/disabled
        if chat_id not in self.rss_preferences:
            self.rss_preferences[chat_id] = {}
        
        feeds = ['nasdaq', 'mintos', 'ffnews']
        for feed in feeds:
            self.rss_preferences[chat_id][feed] = enabled
        
        self._save_rss_preferences()
        logger.info(f"RSS notifications {'enabled' if enabled else 'disabled'} for all feeds for user {chat_id}")

    def set_feed_preference(self, chat_id, feed_source, enabled):
        """Set RSS notifications preference for a specific feed"""
        chat_id = str(chat_id)
        
        # Initialize or handle legacy format
        if chat_id not in self.rss_preferences:
            self.rss_preferences[chat_id] = {}
        elif isinstance(self.rss_preferences[chat_id], bool):
            # Convert legacy boolean format to dictionary
            legacy_value = self.rss_preferences[chat_id]
            feeds = ['nasdaq', 'mintos', 'ffnews']
            self.rss_preferences[chat_id] = {feed: legacy_value for feed in feeds}
        
        # Ensure it's a dictionary before setting
        if not isinstance(self.rss_preferences[chat_id], dict):
            self.rss_preferences[chat_id] = {}
        
        self.rss_preferences[chat_id][feed_source] = enabled
        self._save_rss_preferences()
        logger.info(f"{feed_source} RSS notifications {'enabled' if enabled else 'disabled'} for user {chat_id}")

    def get_rss_preference(self, chat_id):
        """Get RSS notifications preference for a user (legacy method - returns True if any feed is enabled)"""
        chat_id = str(chat_id)
        user_prefs = self.rss_preferences.get(chat_id, {})
        # Handle legacy format (boolean) and new format (dict)
        if isinstance(user_prefs, bool):
            return user_prefs
        elif isinstance(user_prefs, dict):
            return any(user_prefs.values()) if user_prefs else False
        return False

    def get_feed_preference(self, chat_id, feed_source):
        """Get RSS notifications preference for a specific feed"""
        chat_id = str(chat_id)
        user_prefs = self.rss_preferences.get(chat_id, {})
        # Handle legacy format
        if isinstance(user_prefs, bool):
            return user_prefs  # Legacy users get all feeds if they enabled RSS
        elif isinstance(user_prefs, dict):
            return user_prefs.get(feed_source, False)
        return False

    def get_user_feed_preferences(self, chat_id):
        """Get all feed preferences for a user"""
        chat_id = str(chat_id)
        user_prefs = self.rss_preferences.get(chat_id, {})
        # Handle legacy format
        if isinstance(user_prefs, bool):
            feeds = ['nasdaq', 'mintos', 'ffnews']
            return {feed: user_prefs for feed in feeds}
        elif isinstance(user_prefs, dict):
            return user_prefs
        return {}

    def get_users_with_rss_enabled(self):
        """Get list of users who have RSS notifications enabled for any feed"""
        enabled_users = []
        for chat_id, prefs in self.rss_preferences.items():
            if isinstance(prefs, bool) and prefs:
                enabled_users.append(chat_id)
            elif isinstance(prefs, dict) and any(prefs.values()):
                enabled_users.append(chat_id)
        return enabled_users

    def get_users_with_feed_enabled(self, feed_source):
        """Get list of users who have notifications enabled for a specific feed"""
        enabled_users = []
        for chat_id, prefs in self.rss_preferences.items():
            if isinstance(prefs, bool) and prefs:
                enabled_users.append(chat_id)  # Legacy users get all feeds
            elif isinstance(prefs, dict) and prefs.get(feed_source, False):
                enabled_users.append(chat_id)
        return enabled_users

    def _load_notification_preferences(self):
        """Load notification preferences from file"""
        try:
            if os.path.exists(self.notification_preferences_file):
                with open(self.notification_preferences_file, 'r') as f:
                    self.notification_preferences = json.load(f)
                logger.info(f"Loaded notification preferences for {len(self.notification_preferences)} users")
            else:
                self.notification_preferences = {}
        except Exception as e:
            logger.error(f"Error loading notification preferences: {e}")
            self.notification_preferences = {}

    def _save_notification_preferences(self):
        """Save notification preferences to file"""
        try:
            os.makedirs(os.path.dirname(self.notification_preferences_file), exist_ok=True)
            with open(self.notification_preferences_file, 'w') as f:
                json.dump(self.notification_preferences, f, indent=2)
            logger.info(f"Saved notification preferences for {len(self.notification_preferences)} users")
        except Exception as e:
            logger.error(f"Error saving notification preferences: {e}")

    def set_notification_preference(self, chat_id, notification_type, enabled):
        """Set notification preference for a specific type (campaigns, recovery_updates, documents)"""
        chat_id = str(chat_id)
        if chat_id not in self.notification_preferences:
            self.notification_preferences[chat_id] = {
                'campaigns': True,  # Default enabled
                'recovery_updates': True,  # Default enabled 
                'documents': True   # Default enabled
            }
        
        self.notification_preferences[chat_id][notification_type] = enabled
        self._save_notification_preferences()
        logger.info(f"{notification_type} notifications {'enabled' if enabled else 'disabled'} for user {chat_id}")

    def get_notification_preference(self, chat_id, notification_type):
        """Get notification preference for a specific type"""
        chat_id = str(chat_id)
        return self.notification_preferences.get(chat_id, {}).get(notification_type, True)  # Default enabled

    def get_user_notification_preferences(self, chat_id):
        """Get all notification preferences for a user"""
        chat_id = str(chat_id)
        default_prefs = {'campaigns': True, 'recovery_updates': True, 'documents': True}
        return self.notification_preferences.get(chat_id, default_prefs)

    def get_users_with_notification_enabled(self, notification_type):
        """Get list of users who have a specific notification type enabled"""
        enabled_users = []
        for chat_id, prefs in self.notification_preferences.items():
            if prefs.get(notification_type, True):  # Default enabled
                enabled_users.append(chat_id)
        
        # Also include users not in the file (they get defaults)
        for chat_id in self.users.keys():
            if str(chat_id) not in self.notification_preferences:
                enabled_users.append(str(chat_id))
        
        return list(set(enabled_users))  # Remove duplicates

    def _load_user_states(self):
        """Load user states from file"""
        try:
            if os.path.exists(self.user_states_file):
                with open(self.user_states_file, 'r') as f:
                    self.user_states = json.load(f)
                logger.info(f"Loaded user states for {len(self.user_states)} users")
            else:
                self.user_states = {}
        except Exception as e:
            logger.error(f"Error loading user states: {e}")
            self.user_states = {}

    def _save_user_states(self):
        """Save user states to file"""
        try:
            os.makedirs(os.path.dirname(self.user_states_file), exist_ok=True)
            with open(self.user_states_file, 'w') as f:
                json.dump(self.user_states, f, indent=2)
            logger.info(f"Saved user states for {len(self.user_states)} users")
        except Exception as e:
            logger.error(f"Error saving user states: {e}")

    def set_user_state(self, chat_id, state):
        """Set user state for interactive commands"""
        chat_id = str(chat_id)
        self.user_states[chat_id] = state
        self._save_user_states()
        logger.info(f"Set user state for {chat_id}: {state}")

    def get_user_state(self, chat_id):
        """Get user state"""
        chat_id = str(chat_id)
        return self.user_states.get(chat_id)

    def clear_user_state(self, chat_id):
        """Clear user state"""
        chat_id = str(chat_id)
        if chat_id in self.user_states:
            del self.user_states[chat_id]
            self._save_user_states()
            logger.info(f"Cleared user state for {chat_id}")

    def has_user_state(self, chat_id, state=None):
        """Check if user has a specific state or any state"""
        chat_id = str(chat_id)
        user_state = self.user_states.get(chat_id)
        if state is None:
            return user_state is not None
        return user_state == state

    def set_user_context(self, chat_id, key, value):
        """Set user context data"""
        chat_id = str(chat_id)
        if chat_id not in self.user_states:
            self.user_states[chat_id] = {}
        
        # Store context data with 'context_' prefix to avoid conflicts
        context_key = f"context_{key}"
        if not isinstance(self.user_states[chat_id], dict):
            self.user_states[chat_id] = {}
        
        self.user_states[chat_id][context_key] = value
        self._save_user_states()
        logger.info(f"Set user context for {chat_id}: {key} = {value}")

    def get_user_context(self, chat_id, key):
        """Get user context data"""
        chat_id = str(chat_id)
        user_data = self.user_states.get(chat_id)
        
        if not isinstance(user_data, dict):
            return None
        
        context_key = f"context_{key}"
        return user_data.get(context_key)

    def clear_user_context(self, chat_id, key):
        """Clear specific user context data"""
        chat_id = str(chat_id)
        user_data = self.user_states.get(chat_id)
        
        if isinstance(user_data, dict):
            context_key = f"context_{key}"
            if context_key in user_data:
                del user_data[context_key]
                self._save_user_states()
                logger.info(f"Cleared user context for {chat_id}: {key}")