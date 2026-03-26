"""Message batching system with debounce timer."""

import threading
import time
from typing import Callable, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """A single message from user."""
    content: str
    timestamp: float


class MessageBatcher:
    """
    Batches multiple messages within a time window and processes them together.
    
    Example:
        User sends: "bên e có bán máy sấy tóc ion âm ko"
        User sends: "giá bao nhiêu thế"
        User sends: "nếu giao thì bao giờ tới nơi"
        
        System waits 30s, then processes all 3 messages as one:
        "bên e có bán máy sấy tóc ion âm ko giá bao nhiêu thế nếu giao thì bao giờ tới nơi"
    """
    
    def __init__(
        self,
        process_callback: Callable[[str], str],
        debounce_seconds: float = 30.0,
        max_wait_seconds: float = 60.0,
    ):
        """
        Initialize message batcher.
        
        Args:
            process_callback: Function to call with batched messages
            debounce_seconds: Wait time after last message before processing
            max_wait_seconds: Maximum wait time from first message
        """
        self.process_callback = process_callback
        self.debounce_seconds = debounce_seconds
        self.max_wait_seconds = max_wait_seconds
        
        self.messages: List[Message] = []
        self.timer: threading.Timer | None = None
        self.first_message_time: float | None = None
        self.lock = threading.Lock()
        self.is_processing = False
    
    def add_message(self, content: str) -> None:
        """
        Add a message to the batch.
        
        This will:
        1. Add message to queue
        2. Cancel existing timer
        3. Start new timer for debounce_seconds
        4. If max_wait_seconds exceeded, process immediately
        """
        with self.lock:
            if self.is_processing:
                # If already processing, queue for next batch
                print(f"[BATCHER] Currently processing, message queued for next batch")
                return
            
            now = time.time()
            
            # Add message
            self.messages.append(Message(content=content, timestamp=now))
            print(f"[BATCHER] Message added. Queue size: {len(self.messages)}")
            
            # Track first message time
            if self.first_message_time is None:
                self.first_message_time = now
                print(f"[BATCHER] First message received. Starting timer...")
            
            # Check if max wait time exceeded
            time_since_first = now - self.first_message_time
            if time_since_first >= self.max_wait_seconds:
                print(f"[BATCHER] Max wait time ({self.max_wait_seconds}s) exceeded. Processing now...")
                self._cancel_timer()
                self._process_batch()
                return
            
            # Cancel existing timer and start new one
            self._cancel_timer()
            remaining_time = min(
                self.debounce_seconds,
                self.max_wait_seconds - time_since_first
            )
            print(f"[BATCHER] Starting {remaining_time:.1f}s timer...")
            self.timer = threading.Timer(remaining_time, self._process_batch)
            self.timer.daemon = True
            self.timer.start()
    
    def _cancel_timer(self) -> None:
        """Cancel the current timer if exists."""
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None
    
    def _process_batch(self) -> None:
        """Process all messages in the batch."""
        with self.lock:
            if not self.messages:
                return
            
            if self.is_processing:
                return
            
            self.is_processing = True
            messages_to_process = self.messages.copy()
            self.messages = []
            self.first_message_time = None
        
        try:
            # Combine all messages
            combined = " ".join([msg.content for msg in messages_to_process])
            print(f"\n[BATCHER] Processing {len(messages_to_process)} message(s):")
            print(f"[BATCHER] Combined: {combined[:100]}...")
            print()
            
            # Process
            result = self.process_callback(combined)
            
            print(f"\n[BATCHER] Processing complete")
            print(f"[BATCHER] Result: {result[:100]}...")
            print()
            
        except Exception as e:
            print(f"[BATCHER] Error processing batch: {e}")
        finally:
            with self.lock:
                self.is_processing = False
    
    def flush(self) -> None:
        """Force process any pending messages immediately."""
        with self.lock:
            if self.messages and not self.is_processing:
                self._cancel_timer()
                self._process_batch()
    
    def is_empty(self) -> bool:
        """Check if there are no pending messages."""
        with self.lock:
            return len(self.messages) == 0 and not self.is_processing
