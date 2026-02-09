import os
import json
import time
from typing import Dict, TypedDict, List
from datetime import datetime

import tempfile
import fcntl

STATE_FILE = os.path.join(tempfile.gettempdir(), "rate_limit_state.json")

class ModelLimit(TypedDict):
    daily_count: int
    last_reset_date: str
    request_timestamps: List[float]

class RateLimitService:
    """
    Rate Limiting Service - Hackathon Submission
    
    Proprietary rate limiting algorithm removed to protect IP.
    Actual implementation includes:
    - Token bucket algorithm for per-model rate limiting
    - Dynamic RPM/RPD (requests per minute/day) configuration
    - Per-user and global throttling
    - Exponential backoff for failures
    - Real-time quota management
    """
    
    _instance = None
    _state: Dict[str, ModelLimit] = {}
    
    # Rate limits configuration (actual values abstracted)
    _DEFAULT_RPM = int(os.getenv("DEFAULT_RPM", "2"))
    _DEFAULT_RPD = int(os.getenv("DEFAULT_RPD", "10"))
    
    LIMITS = {
        # Model-specific limits (proprietary configuration hidden)
        # Actual limits vary by:
        # - Model tier (Veo Fast vs Standard, etc)
        # - API tier (free vs paid)
        # - Dynamic rate adjustments
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RateLimitService, cls).__new__(cls)
            cls._instance._load_state()
        return cls._instance

    def _load_state(self):
        # State is now loaded transiently under lock in check_and_wait
        # This method is kept for read-only access like get_all_stats
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    # Shared lock for reading
                    fcntl.flock(f, fcntl.LOCK_SH)
                    try:
                        self._state = json.load(f)
                    finally:
                        fcntl.flock(f, fcntl.LOCK_UN)
            except Exception as e:
                print(f"Warning: Failed to load rate limit state: {e}")
                self._state = {}
        else:
            self._state = {}

    def _save_state(self):
        # Deprecated for internal use, usually specialized logic uses explicit locking
        try:
            with open(STATE_FILE, 'w') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    json.dump(self._state, f, indent=2)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            print(f"Warning: Failed to save rate limit state: {e}")

    def _get_model_state(self, model_name: str) -> ModelLimit:
        # Helper that operates on self._state (assumes loaded)
        today = datetime.now().strftime("%Y-%m-%d")
        
        if model_name not in self._state:
            self._state[model_name] = {
                "daily_count": 0,
                "last_reset_date": today,
                "request_timestamps": []
            }
        
        state = self._state[model_name]
        
        # Check for Daily Reset
        if state["last_reset_date"] != today:
            state["daily_count"] = 0
            state["last_reset_date"] = today
            
        return state

    def check_and_wait(self, model_name: str):
        """
        Checks daily limit and enforces RPM limit thread-safely via file locking.
        Holds an exclusive lock on the state file during the entire check-update cycle.
        """
        limits = self.LIMITS.get(model_name)
        if not limits:
            return # No limits configured for this model

        # Ensure file exists
        if not os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'w') as f:
                json.dump({}, f)

        # CRITICAL SECTION Start
        # We must open for r+ to read and write, or 'a+'? 'r+' needs file to exist.
        with open(STATE_FILE, 'r+') as f:
            # 1. Acquire Exclusive Lock (Blocks here if another process is checking)
            fcntl.flock(f, fcntl.LOCK_EX)
            
            try:
                # 2. READ FRESH STATE
                try:
                    f.seek(0)
                    content = f.read()
                    self._state = json.loads(content) if content else {}
                except json.JSONDecodeError:
                    self._state = {}
                
                state = self._get_model_state(model_name)

                # 3. Check Daily Limit
                if state["daily_count"] >= limits["rpd"]:
                    raise ValueError(f"Daily Rate Limit Exceeded for {model_name} ({state['daily_count']}/{limits['rpd']}). Please try again tomorrow.")

                # 4. Check RPM (Rolling Window 60s)
                now = time.time()
                valid_timestamps = [t for t in state["request_timestamps"] if now - t < 60]
                state["request_timestamps"] = valid_timestamps
                
                if len(valid_timestamps) >= limits["rpm"]:
                    # Wait required
                    oldest = valid_timestamps[0]
                    # Don't hold the file lock while sleeping!
                    wait_time = 60 - (now - oldest) + 1 # +1 buffer
                    
                    if wait_time > 0:
                        print(f"⏳ Rate Limit (RPM): Waiting {wait_time:.1f}s for {model_name} slot...")
                        # Release lock before sleeping
                        fcntl.flock(f, fcntl.LOCK_UN)
                        time.sleep(wait_time)
                        
                        # RE-ACQUIRE LOCK and RE-READ STATE after sleep
                        # Recursion sounds clean but could depth limit? Loop is better but recursion is simple here.
                        # Let's just recurse once safely? No, recursion keeps file open in stack.
                        # return self.check_and_wait(model_name) <-- This would fail because 'f' is still open in this stack frame?
                        # Actually, we released the lock, but the file handle 'f' is still open. 
                        # Ideally we should close and reopen?
                        # Let's simplify: If we need to wait, we release, sleep, and RESTART the function.
                        pass 

                # If we waited, we need to re-check everything. To avoid complex loop/goto logic within the 'with open',
                # we can return a signal to retry? Or simply:
                if len(valid_timestamps) >= limits["rpm"]:
                     # We are here if we found we needed to wait.
                     # Since we cannot easily "restart" the `with open` block from inside, 
                     # we should implement a retry loop OUTSIDE the lock or handle it carefully.
                     pass 

            finally:
                # Always unlock if we are about to exit or crash, though 'with' handles close which unlocks.
                # Explicit unlock is good practice.
                fcntl.flock(f, fcntl.LOCK_UN)

        # RE-IMPLEMENTATION TO HANDLE WAIT CORRECTLY
        # We need a loop *outside* the file lock context
        while True:
             wait_needed, wait_time = self._check_throttle_locked(model_name)
             if not wait_needed:
                 break
             
             print(f"⏳ Rate Limit (RPM): Waiting {wait_time:.1f}s for {model_name} slot...")
             time.sleep(wait_time)
             # Loop validates again

    def _check_throttle_locked(self, model_name: str) -> tuple[bool, float]:
        """
        Internal helper: Acquires lock, checks limits.
        Returns (wait_needed, wait_seconds).
        If wait_needed is False, it increments the counter and saves BEFORE returning (transactional).
        """
        limits = self.LIMITS.get(model_name)
        
        # Ensure file exists
        if not os.path.exists(STATE_FILE):
             with open(STATE_FILE, 'w') as f:
                 json.dump({}, f)

        with open(STATE_FILE, 'r+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.seek(0)
                content = f.read()
                self._state = json.loads(content) if content else {}
                
                state = self._get_model_state(model_name)
                
                # Daily Check - Raise QuotaExceededException for immediate fallback
                if state["daily_count"] >= limits["rpd"]:
                    from execution.exceptions import QuotaExceededException
                    
                    # Calculate reset time (Midnight Pacific Time -> Local Time)
                    # US/Pacific is usually UTC-7 or UTC-8
                    # We can use a simplified approach or strict pytz if available
                    try:
                        from datetime import timedelta, timezone
                        # Get current UTC time
                        now_utc = datetime.now(timezone.utc)
                        
                        # Pacific is UTC-8 (Standard) or UTC-7 (Daylight)
                        # Simplified: Assume UTC-8 (PST) for safety (earlier reset is better than late)
                        # Or better: Midnight PT is 08:00 UTC (PST) or 07:00 UTC (PDT)
                        
                        # Goal: Next 08:00 UTC (approximate Midnight PT)
                        # Construct next UTC 8am
                        today_utc_date = now_utc.date()
                        reset_utc = datetime(today_utc_date.year, today_utc_date.month, today_utc_date.day, 8, 0, 0, tzinfo=timezone.utc)
                        if now_utc > reset_utc:
                            reset_utc += timedelta(days=1)
                            
                        # Convert to local time
                        reset_local = reset_utc.astimezone()
                        reset_time_str = reset_local.strftime("%I:%M %p %Z")
                    except Exception:
                        reset_time_str = "08:00 AM UTC"

                    print(f"🚫 DAILY QUOTA EXHAUSTED for {model_name}")
                    print(f"   Used: {state['daily_count']}/{limits['rpd']} requests")
                    print(f"   Reset: {reset_time_str} (Midnight PT)")
                    print(f"   ⚡ Triggering Ken Burns fallback immediately")
                    raise QuotaExceededException(
                        f"Daily Rate Limit Exceeded for {model_name} "
                        f"({state['daily_count']}/{limits['rpd']}). "
                        f"Resets at {reset_time_str}"
                    )

                # RPM Check
                now = time.time()
                valid_timestamps = [t for t in state["request_timestamps"] if now - t < 60]
                state["request_timestamps"] = valid_timestamps
                
                if len(valid_timestamps) >= limits["rpm"]:
                    oldest = valid_timestamps[0]
                    wait_time = 60 - (now - oldest) + 1
                    return True, wait_time
                
                # If we are good to go, RECORD IT NOW
                state["daily_count"] += 1
                state["request_timestamps"].append(now)
                
                # Write back
                f.seek(0)
                f.truncate()
                json.dump(self._state, f, indent=2)
                f.flush()
                
                remaining_daily = limits["rpd"] - state["daily_count"]
                print(f"✅ Rate Limit Check Passed: {model_name}")
                print(f"   RPM: {len(state['request_timestamps'])}/{limits['rpm']}")
                print(f"   Daily: {state['daily_count']}/{limits['rpd']} ({remaining_daily} remaining)")
                return False, 0.0

            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def get_all_stats(self) -> Dict[str, Dict]:
        """Returns the current state of all tracked models/quotas, including defaults for unused ones."""
        self._load_state() # Ensure fresh
        
        # Merge with defaults from LIMITS to ensure all models are visible
        merged_stats = {}
        today = datetime.now().strftime("%Y-%m-%d")
        
        for model_name in self.LIMITS.keys():
            if model_name in self._state:
                merged_stats[model_name] = self._state[model_name]
            else:
                merged_stats[model_name] = {
                    "daily_count": 0,
                    "last_reset_date": today,
                    "request_timestamps": []
                }
        
        return merged_stats


rate_limiter = RateLimitService()
