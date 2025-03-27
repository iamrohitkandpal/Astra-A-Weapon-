"""
Memory optimization utilities for Astra
"""

import gc
import sys
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

def enable_garbage_collection():
    """
    Configure Python's garbage collector for better memory usage.
    This is particularly useful for applications that create and destroy
    many objects, like network scanning tools.
    """
    # Set garbage collection thresholds
    # Lower threshold means more frequent collection
    gc.set_threshold(700, 10, 5)
    
    # Enable automatic garbage collection
    gc.enable()
    
    # Initial collection to start clean
    gc.collect()
    
    # Set process priority higher on Windows
    try:
        if sys.platform == 'win32' and PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            process.nice(psutil.NORMAL_PRIORITY_CLASS)
    except Exception:
        pass  # Ignore if setting priority fails

def get_memory_usage():
    """
    Get current memory usage of the application.
    
    Returns:
        dict: Memory usage stats in MB
    """
    try:
        if PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            return {
                'rss': memory_info.rss / (1024 * 1024),  # Resident Set Size in MB
                'vms': memory_info.vms / (1024 * 1024),  # Virtual Memory Size in MB
            }
    except Exception:
        pass  # Ignore errors
        
    return {'rss': 0, 'vms': 0}  # Return zeros if psutil is not available

def cleanup_resources():
    """
    Clean up memory resources manually. Call this when large operations finish
    or when switching between tools.
    """
    # Force garbage collection
    gc.collect()
    
    # Attempt to release memory back to OS on supported platforms
    if sys.platform == 'linux':
        try:
            import ctypes
            libc = ctypes.CDLL('libc.so.6')
            libc.malloc_trim(0)
        except Exception:
            pass
