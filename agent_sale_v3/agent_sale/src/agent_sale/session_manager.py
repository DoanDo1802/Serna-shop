"""Session management for multi-user support with Supabase persistence."""

import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from agent_sale.supabase_storage import get_supabase_storage


@dataclass
class UserSession:
    """Session data for a single user."""
    user_id: str
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)
    
    # Cache for conversation history (loaded from Supabase)
    _conversation_history: Optional[List[Dict[str, str]]] = None
    
    def __post_init__(self):
        """Initialize Supabase storage."""
        self.storage = get_supabase_storage()
        
        # Ensure session exists in Supabase
        self.storage.get_or_create_session(self.user_id)
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history (saves to Supabase)."""
        # Save to Supabase
        self.storage.add_message(self.user_id, role, content)
        
        # Invalidate cache
        self._conversation_history = None
        
        self.last_activity = time.time()
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history (loads from Supabase)."""
        # Use cache if available
        if self._conversation_history is not None:
            return self._conversation_history
        
        # Load from Supabase
        messages = self.storage.get_messages(self.user_id)
        
        # Convert to expected format
        self._conversation_history = [
            {
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg.get("timestamp")
            }
            for msg in messages
        ]
        
        return self._conversation_history
    
    def clear_history(self):
        """Clear conversation history (deletes from Supabase)."""
        self.storage.clear_messages(self.user_id)
        self._conversation_history = None
    
    def is_expired(self, timeout_seconds: float) -> bool:
        """Check if session has expired."""
        return (time.time() - self.last_activity) > timeout_seconds
    
    def get_age(self) -> float:
        """Get session age in seconds."""
        return time.time() - self.created_at
    
    def get_idle_time(self) -> float:
        """Get idle time in seconds."""
        return time.time() - self.last_activity


class SessionManager:
    """
    Manages user sessions for multi-user chat system with Supabase persistence.
    
    Features:
    - Isolated conversation history per user
    - Automatic session cleanup
    - Thread-safe operations
    - Session expiration
    - Persistent storage in Supabase
    """
    
    def __init__(
        self,
        session_timeout: float = 3600.0,  # 1 hour
        cleanup_interval: float = 300.0,  # 5 minutes
    ):
        """
        Initialize session manager.
        
        Args:
            session_timeout: Session expires after this many seconds of inactivity
            cleanup_interval: Run cleanup every this many seconds
        """
        self.session_timeout = session_timeout
        self.cleanup_interval = cleanup_interval
        
        # In-memory cache of active sessions
        self.sessions: Dict[str, UserSession] = {}
        self.lock = threading.Lock()
        
        # Supabase storage
        self.storage = get_supabase_storage()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True,
        )
        self.cleanup_thread.start()
        
        print("[SESSION] SessionManager initialized with Supabase persistence")
    
    def get_or_create_session(self, user_id: str) -> UserSession:
        """
        Get existing session or create new one.
        
        Args:
            user_id: Unique identifier for the user
        
        Returns:
            UserSession for this user
        """
        with self.lock:
            if user_id not in self.sessions:
                self.sessions[user_id] = UserSession(user_id=user_id)
                print(f"[SESSION] Created new session for user: {user_id}")
            else:
                # Update last activity
                self.sessions[user_id].last_activity = time.time()
            
            return self.sessions[user_id]
    
    def get_session(self, user_id: str) -> Optional[UserSession]:
        """
        Get existing session without creating new one.
        
        Args:
            user_id: Unique identifier for the user
        
        Returns:
            UserSession if exists, None otherwise
        """
        with self.lock:
            return self.sessions.get(user_id)
    
    def delete_session(self, user_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            user_id: Unique identifier for the user
        
        Returns:
            True if session was deleted, False if not found
        """
        with self.lock:
            if user_id in self.sessions:
                del self.sessions[user_id]
                print(f"[SESSION] Deleted session for user: {user_id}")
                return True
            return False
    
    def clear_session_history(self, user_id: str) -> bool:
        """
        Clear conversation history for a session.
        
        Args:
            user_id: Unique identifier for the user
        
        Returns:
            True if history was cleared, False if session not found
        """
        with self.lock:
            if user_id in self.sessions:
                self.sessions[user_id].clear_history()
                print(f"[SESSION] Cleared history for user: {user_id}")
                return True
            return False
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        with self.lock:
            return list(self.sessions.keys())
    
    def get_session_count(self) -> int:
        """Get number of active sessions."""
        with self.lock:
            return len(self.sessions)
    
    def get_session_stats(self) -> Dict:
        """Get statistics about sessions (from Supabase)."""
        return self.storage.get_session_stats()
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions from memory cache."""
        with self.lock:
            expired = [
                user_id
                for user_id, session in self.sessions.items()
                if session.is_expired(self.session_timeout)
            ]
            
            for user_id in expired:
                idle_time = self.sessions[user_id].get_idle_time()
                del self.sessions[user_id]
                print(f"[SESSION] Cleaned up expired session from cache: {user_id} (idle: {idle_time:.0f}s)")
            
            if expired:
                print(f"[SESSION] Cleaned up {len(expired)} expired session(s) from cache")
        
        # Also cleanup old sessions from Supabase (24 hours)
        try:
            deleted = self.storage.cleanup_old_sessions(hours=24)
            if deleted > 0:
                print(f"[SESSION] Cleaned up {deleted} old session(s) from Supabase")
        except Exception as e:
            print(f"[SESSION] Error cleaning up Supabase sessions: {e}")
    
    def _cleanup_loop(self):
        """Background thread that periodically cleans up expired sessions."""
        while True:
            time.sleep(self.cleanup_interval)
            self._cleanup_expired_sessions()


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager(
    session_timeout: float = 3600.0,
    cleanup_interval: float = 300.0,
) -> SessionManager:
    """
    Get or create global session manager instance.
    
    Args:
        session_timeout: Session expires after this many seconds of inactivity
        cleanup_interval: Run cleanup every this many seconds
    
    Returns:
        Global SessionManager instance
    """
    global _session_manager
    
    if _session_manager is None:
        _session_manager = SessionManager(
            session_timeout=session_timeout,
            cleanup_interval=cleanup_interval,
        )
    
    return _session_manager
