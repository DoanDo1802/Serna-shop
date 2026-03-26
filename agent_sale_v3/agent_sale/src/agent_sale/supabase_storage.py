"""Supabase storage for persistent session management."""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from supabase import create_client, Client


class SupabaseStorage:
    """
    Persistent storage using Supabase (PostgreSQL).
    
    Tables:
    - sessions: Store session metadata
    - messages: Store conversation messages
    """
    
    def __init__(self):
        """Initialize Supabase client."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        
        self.client: Client = create_client(url, key)
        print("[SUPABASE] Connected successfully")
    
    def create_tables(self):
        """
        Create tables if they don't exist.
        
        Run this SQL in Supabase SQL Editor:
        
        -- Sessions table
        CREATE TABLE IF NOT EXISTS sessions (
            user_id TEXT PRIMARY KEY,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            last_activity TIMESTAMPTZ DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'::jsonb
        );
        
        -- Messages table
        CREATE TABLE IF NOT EXISTS messages (
            id BIGSERIAL PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES sessions(user_id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'::jsonb
        );
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
        CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
        CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity);
        """
        print("[SUPABASE] Tables should be created via SQL Editor")
        print("[SUPABASE] See create_tables() docstring for SQL commands")
    
    def get_or_create_session(self, user_id: str) -> Dict:
        """Get existing session or create new one."""
        # Try to get existing session
        response = self.client.table("sessions").select("*").eq("user_id", user_id).execute()
        
        if response.data:
            # Update last_activity
            self.client.table("sessions").update({
                "last_activity": datetime.utcnow().isoformat()
            }).eq("user_id", user_id).execute()
            
            return response.data[0]
        else:
            # Create new session
            new_session = {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "metadata": {}
            }
            response = self.client.table("sessions").insert(new_session).execute()
            print(f"[SUPABASE] Created new session for user: {user_id}")
            return response.data[0]
    
    def add_message(self, user_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to conversation history."""
        message = {
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.client.table("messages").insert(message).execute()
        
        # Update session last_activity
        self.client.table("sessions").update({
            "last_activity": datetime.utcnow().isoformat()
        }).eq("user_id", user_id).execute()
    
    def get_messages(self, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history for a user."""
        query = self.client.table("messages").select("*").eq("user_id", user_id).order("timestamp", desc=False)
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        return response.data
    
    def get_recent_messages(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get recent messages for a user."""
        return self.get_messages(user_id, limit=limit)
    
    def clear_messages(self, user_id: str):
        """Clear all messages for a user."""
        self.client.table("messages").delete().eq("user_id", user_id).execute()
        print(f"[SUPABASE] Cleared messages for user: {user_id}")
    
    def delete_session(self, user_id: str):
        """Delete a session and all its messages."""
        # Messages will be deleted automatically due to CASCADE
        self.client.table("sessions").delete().eq("user_id", user_id).execute()
        print(f"[SUPABASE] Deleted session for user: {user_id}")
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all active sessions."""
        response = self.client.table("sessions").select("*").execute()
        return response.data
    
    def get_session_stats(self) -> Dict:
        """Get statistics about sessions."""
        sessions = self.get_all_sessions()
        
        total_messages = 0
        for session in sessions:
            messages = self.get_messages(session["user_id"])
            total_messages += len(messages)
        
        return {
            "total_sessions": len(sessions),
            "total_messages": total_messages,
            "avg_messages_per_session": total_messages / len(sessions) if sessions else 0,
            "session_ids": [s["user_id"] for s in sessions]
        }
    
    def cleanup_old_sessions(self, hours: int = 24):
        """Delete sessions inactive for more than X hours."""
        from datetime import timedelta, timezone
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # This requires a custom SQL query or RPC function
        # For now, we'll fetch and delete manually
        sessions = self.get_all_sessions()
        deleted = 0
        
        for session in sessions:
            last_activity_str = session["last_activity"]
            # Parse timestamp with timezone
            if last_activity_str.endswith('Z'):
                last_activity_str = last_activity_str.replace('Z', '+00:00')
            
            try:
                last_activity = datetime.fromisoformat(last_activity_str)
                # Make timezone aware if needed
                if last_activity.tzinfo is None:
                    last_activity = last_activity.replace(tzinfo=timezone.utc)
                
                if last_activity < cutoff:
                    self.delete_session(session["user_id"])
                    deleted += 1
            except Exception as e:
                print(f"[SUPABASE] Error parsing timestamp for session {session['user_id']}: {e}")
                continue
        
        if deleted > 0:
            print(f"[SUPABASE] Cleaned up {deleted} old session(s)")
        return deleted


# Global instance
_supabase_storage: Optional[SupabaseStorage] = None


def get_supabase_storage() -> SupabaseStorage:
    """Get or create global Supabase storage instance."""
    global _supabase_storage
    
    if _supabase_storage is None:
        _supabase_storage = SupabaseStorage()
    
    return _supabase_storage
