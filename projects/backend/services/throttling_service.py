"""
Enhanced Rate Limiting and Throttling Service

This service implements a hybrid approach:
1. Per-user cooldowns (anti-spam)
2. Global throttling (API compliance)
3. Per-model rate limiting (existing functionality)
"""

import os
import json
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
import tempfile

STATE_FILE = os.path.join(tempfile.gettempdir(), "throttle_state.json")


class ThrottlingService:
    """
    Hybrid rate limiting service that combines:
    - User-level cooldowns (prevents individual user spam)
    - Global throttling (ensures API compliance across all users)
    - Per-model limits (respects provider-specific quotas)
    """
    
    _instance = None
    
    # Configuration
    USER_COOLDOWN_SECONDS = 120  # 2 minutes between generations per user
    GLOBAL_THROTTLE_SECONDS = 30  # 30 seconds between ANY generation
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThrottlingService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize service state."""
        self.user_last_generation: Dict[str, float] = {}  # user_id -> timestamp
        self.global_last_generation: Optional[float] = None
        self._load_state()
    
    def _load_state(self):
        """Load throttle state from disk."""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    self.user_last_generation = data.get("user_last_generation", {})
                    self.global_last_generation = data.get("global_last_generation")
            except Exception as e:
                print(f"Warning: Failed to load throttle state: {e}")
    
    def _save_state(self):
        """Save throttle state to disk."""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump({
                    "user_last_generation": self.user_last_generation,
                    "global_last_generation": self.global_last_generation
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save throttle state: {e}")
    
    def check_user_cooldown(self, user_id: str) -> Optional[int]:
        """
        Check if user is on cooldown.
        
        Returns:
            None if allowed, or remaining cooldown seconds if blocked
        """
        if not user_id:
            return None  # Allow anonymous/system requests
        
        last_gen = self.user_last_generation.get(user_id)
        if not last_gen:
            return None  # First time, allow
        
        elapsed = time.time() - last_gen
        if elapsed < self.USER_COOLDOWN_SECONDS:
            remaining = int(self.USER_COOLDOWN_SECONDS - elapsed)
            return remaining
        
        return None  # Cooldown expired, allow
    
    def check_global_throttle(self) -> Optional[int]:
        """
        Check global throttle across all users.
        
        Returns:
            None if allowed, or remaining throttle seconds if blocked
        """
        if self.global_last_generation is None:
            return None  # First generation ever, allow
        
        elapsed = time.time() - self.global_last_generation
        if elapsed < self.GLOBAL_THROTTLE_SECONDS:
            remaining = int(self.GLOBAL_THROTTLE_SECONDS - elapsed)
            return remaining
        
        return None  # Throttle expired, allow
    
    def record_generation(self, user_id: str):
        """
        Record that a generation has started.
        Updates both user and global timestamps.
        """
        now = time.time()
        
        if user_id:
            self.user_last_generation[user_id] = now
        
        self.global_last_generation = now
        self._save_state()
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get statistics for a specific user."""
        last_gen = self.user_last_generation.get(user_id)
        
        if not last_gen:
            return {
                "can_generate": True,
                "seconds_until_ready": 0,
                "last_generation": None
            }
        
        elapsed = time.time() - last_gen
        remaining = max(0, int(self.USER_COOLDOWN_SECONDS - elapsed))
        
        return {
            "can_generate": remaining == 0,
            "seconds_until_ready": remaining,
            "last_generation": datetime.fromtimestamp(last_gen).isoformat()
        }
    
    def cleanup_old_entries(self, max_age_hours: int = 24):
        """Clean up user entries older than specified hours."""
        cutoff = time.time() - (max_age_hours * 3600)
        
        old_users = [
            user_id for user_id, timestamp in self.user_last_generation.items()
            if timestamp < cutoff
        ]
        
        for user_id in old_users:
            del self.user_last_generation[user_id]
        
        if old_users:
            self._save_state()
            print(f"Cleaned up {len(old_users)} old throttle entries")


# Singleton instance
throttling_service = ThrottlingService()
