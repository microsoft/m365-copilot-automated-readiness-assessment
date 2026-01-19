"""
Console spinner animation for long-running operations.
Runs in a separate thread to work even when async operations block the event loop.
"""
import sys
import threading
import time
from datetime import datetime

# Global lock to prevent multiple threads from writing to stdout simultaneously
_stdout_lock = threading.Lock()

# Global message buffer for collecting messages during progress bar display
_message_buffer = []
_buffer_enabled = False

def enable_message_buffering():
    """Enable buffering of messages (for use during progress bar display)"""
    global _buffer_enabled, _message_buffer
    _buffer_enabled = True
    _message_buffer = []

def disable_message_buffering():
    """Disable buffering and return buffered messages"""
    global _buffer_enabled, _message_buffer
    _buffer_enabled = False
    messages = _message_buffer.copy()
    _message_buffer = []
    return messages

def buffered_print(message):
    """Print message or buffer it if buffering is enabled"""
    global _buffer_enabled, _message_buffer
    if _buffer_enabled:
        _message_buffer.append(message)
    else:
        with _stdout_lock:
            print(message)

def get_timestamp():
    """Get current timestamp in standard format"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def simple_spinner(stop_event, message, stdout_lock):
    """Simple spinner for module loading"""
    spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    idx = 0
    timestamp = get_timestamp()
    
    while not stop_event.is_set():
        with stdout_lock:
            sys.stdout.write(f'\r[{timestamp}] {spinner_chars[idx]}    {message}')
            sys.stdout.flush()
        idx = (idx + 1) % len(spinner_chars)
        time.sleep(0.08)
    
    # Move cursor to start of line so next print() overwrites the spinner
    with stdout_lock:
        sys.stdout.write('\r')
        sys.stdout.flush()

def _spinner_thread(stop_event, message):
    """Run spinner animation in separate thread"""
    spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    idx = 0
    timestamp = get_timestamp()
    
    while not stop_event.is_set():
        # Read current message (supports dynamic updates)
        current_msg = message[0] if isinstance(message, list) else message
        with _stdout_lock:
            sys.stdout.write(f'\r[{timestamp}] {spinner_chars[idx]}    {current_msg}')
            sys.stdout.flush()
        idx = (idx + 1) % len(spinner_chars)
        time.sleep(0.08)
    
    # Clear the spinner line completely with spaces, then carriage return
    with _stdout_lock:
        sys.stdout.write('\r' + ' ' * 120 + '\r')
        sys.stdout.flush()
