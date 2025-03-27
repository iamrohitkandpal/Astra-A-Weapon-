"""
Configuration loading utility for Astra
"""

import os
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "theme": "dark",
    "save_reports_path": "reports",
    "advanced_tools_enabled": False,
    "log_level": "info",
    "proxy": {
        "type": "direct"
    },
    "advanced": {
        "memory_optimization": "normal",
        "max_threads": 20,
        "timeout": 5
    }
}

def load_config():
    """Load configuration from file or use defaults"""
    config_dir = Path("config")
    config_file = config_dir / "settings.json"
    
    # Create config directory if it doesn't exist
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
    
    # If config file doesn't exist, create it with default settings
    if not config_file.exists():
        with open(config_file, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    
    # Load existing config file
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        # Merge with defaults for any missing keys
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
            elif isinstance(value, dict) and key in config:
                # Handle nested dicts
                for sub_key, sub_value in value.items():
                    if sub_key not in config[key]:
                        config[key][sub_key] = sub_value
                
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to file"""
    config_file = Path("config") / "settings.json"
    
    try:
        # Ensure config directory exists
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False
