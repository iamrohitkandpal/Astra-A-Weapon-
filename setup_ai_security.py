#!/usr/bin/env python3
"""
Setup script to install AI Security Analysis dependencies for Astra
"""

import subprocess
import sys
import os
import platform
import time

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    return True

def install_dependencies(include_tensorflow=False):
    """Install the required dependencies"""
    print("Installing required packages...")
    
    # Basic ML dependencies
    basic_deps = [
        "scikit-learn",
        "numpy",
        "selenium",
        "webdriver-manager",
        "fpdf",
        "beautifulsoup4", 
        "lxml",
        "jinja2",
        "matplotlib"
    ]
    
    # Optional TensorFlow for advanced models
    if include_tensorflow:
        basic_deps.append("tensorflow")
        print("Including TensorFlow (this may take some time)...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        for package in basic_deps:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def setup_data_directories():
    """Set up the necessary data directories"""
    print("Setting up data directories...")
    
    dirs = [
        "data",
        "models",
        "reports"
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create empty mitigation templates file if it doesn't exist
    templates_path = os.path.join("data", "mitigation_templates.json")
    if not os.path.exists(templates_path):
        with open(templates_path, 'w') as f:
            f.write("{}")
        print(f"Created empty mitigation templates file: {templates_path}")
        
    return True

def main():
    """Main setup function"""
    print("Astra AI Security Analysis Setup")
    print("=" * 35)
    
    if not check_python_version():
        return 1
    
    # Ask if user wants to include TensorFlow
    include_tf = input("Install TensorFlow for advanced deep learning models? (y/n): ").lower() == 'y'
    
    # Install dependencies
    if not install_dependencies(include_tensorflow=include_tf):
        return 1
    
    # Set up directories
    if not setup_data_directories():
        return 1
    
    print("\nSetup complete!")
    print("""
To use AI-powered security scanning, you can:
1. Run a web vulnerability scan with AI analysis enabled
2. Generate enhanced reports with vulnerability scores and mitigations
3. Use dynamic scanning for JavaScript-based vulnerabilities
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
