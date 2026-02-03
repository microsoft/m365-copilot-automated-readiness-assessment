"""
Module loading progress bar for recommendation modules
"""
import sys
from .spinner import _stdout_lock
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ModuleLoadingProgress:
    def __init__(self):
        self.total_services = 0
        self.loaded_services = 0
        self.total_modules = 0
        self.service_names = []
        self.started = False
        
    def start(self, total_services):
        """Start progress bar with expected number of services"""
        self.total_services = total_services
        self.started = True
        with _stdout_lock:
            sys.stdout.write(f'[{get_timestamp()}]   Loading Modules         [░░░░░░░░░░░░░░░░░░░░]   0%')
            sys.stdout.flush()
        
    def update(self, service_name, module_count):
        """Update progress when a service finishes loading modules"""
        with _stdout_lock:
            self.loaded_services += 1
            self.total_modules += module_count
            self.service_names.append(service_name)
            
            # Calculate progress
            progress = self.loaded_services / self.total_services
            bar_length = 20
            filled = int(bar_length * progress)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            # Clear line and show progress
            if self.loaded_services >= self.total_services:
                # Completion - add checkmark
                sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Loading Modules         [{bar}] {int(progress * 100):3d}%\n')
            else:
                # In progress
                sys.stdout.write(f'\r[{get_timestamp()}]   Loading Modules         [{bar}] {int(progress * 100):3d}%')
            sys.stdout.flush()

# Global instance
_module_progress = None

def get_progress_tracker():
    """Get or create the global progress tracker"""
    global _module_progress
    if _module_progress is None:
        _module_progress = ModuleLoadingProgress()
    return _module_progress

def start_module_loading(total_services):
    """Initialize and show the progress bar with the expected number of services"""
    global _module_progress
    _module_progress = ModuleLoadingProgress()
    _module_progress.start(total_services)
