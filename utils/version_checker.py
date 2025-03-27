"""
Version checking utility for Astra
"""

import os
import json
import requests
import re
import platform
from datetime import datetime

def get_current_version():
    """Get the current version of the application"""
    # Read from the config file if it exists
    try:
        config_path = os.path.join("config", "settings.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                if 'version' in config:
                    return config['version']
        
        # If not in config, try to parse from main window
        with open('ui/main_window.py', 'r') as f:
            content = f.read()
            match = re.search(r'version_label = QLabel\("v([0-9.]+)"\)', content)
            if match:
                return match.group(1)
    except Exception:
        pass
    
    return "0.1.0"  # Default version

def parse_version(version_str):
    """Parse a version string into components"""
    try:
        return [int(x) for x in version_str.split('.')]
    except ValueError:
        return [0, 0, 0]  # Default to 0.0.0 if parsing fails

def compare_versions(version1, version2):
    """
    Compare two version strings
    
    Returns:
        -1 if version1 < version2
        0 if version1 == version2
        1 if version1 > version2
    """
    v1_parts = parse_version(version1)
    v2_parts = parse_version(version2)
    
    # Pad shorter version with zeros
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_len - len(v1_parts)))
    v2_parts.extend([0] * (max_len - len(v2_parts)))
    
    # Compare component by component
    for i in range(max_len):
        if v1_parts[i] < v2_parts[i]:
            return -1
        elif v1_parts[i] > v2_parts[i]:
            return 1
    
    return 0  # Versions are equal

def check_for_updates(current_version=None, repo_url="https://api.github.com/repos/yourusername/astra/releases"):
    """
    Check for updates by comparing the current version with the latest release on GitHub
    
    Args:
        current_version: The current version (if None, it will be detected automatically)
        repo_url: The GitHub API URL for releases
        
    Returns:
        dict: Information about updates with keys:
            'update_available': True if an update is available
            'current_version': The current version
            'latest_version': The latest version available
            'release_url': URL to the latest release
            'release_notes': Release notes for the latest version
            'last_check': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    """
    if current_version is None:
        current_version = get_current_version()
    
    result = {
        'update_available': False,
        'current_version': current_version,
        'latest_version': current_version,
        'release_url': '',
        'release_notes': '',
        'last_check': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        # Use a session with timeout to prevent hanging
        session = requests.Session()
        response = session.get(repo_url, timeout=5)
        
        if response.status_code == 200:
            releases = response.json()
            
            if releases and len(releases) > 0:
                # Get the latest release
                latest_release = releases[0]
                latest_version_tag = latest_release['tag_name']
                
                # Remove 'v' prefix if present
                if latest_version_tag.startswith('v'):
                    latest_version = latest_version_tag[1:]
                else:
                    latest_version = latest_version_tag
                
                # Compare versions
                if compare_versions(current_version, latest_version) < 0:
                    result['update_available'] = True
                    result['latest_version'] = latest_version
                    result['release_url'] = latest_release['html_url']
                    result['release_notes'] = latest_release.get('body', '')
    
    except Exception:
        # Just return the default result on any error
        pass
    
    # Save the check result to config
    try:
        config_path = os.path.join("config", "settings.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            config['last_update_check'] = result
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
    except Exception:
        pass
    
    return result

def get_update_message(update_info):
    """
    Format an update message based on update info
    
    Args:
        update_info: The result from check_for_updates()
        
    Returns:
        str: A formatted message about updates
    """
    if update_info['update_available']:
        return (
            f"Update Available!\n\n"
            f"Your version: {update_info['current_version']}\n"
            f"Latest version: {update_info['latest_version']}\n\n"
            f"Visit {update_info['release_url']} to download the update."
        )
    else:
        return "You are using the latest version."

def main():
    """Run update check from command line"""
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    print("Checking for updates...")
    update_info = check_for_updates(current_version)
    
    print(get_update_message(update_info))
    
    return 0

if __name__ == "__main__":
    main()
