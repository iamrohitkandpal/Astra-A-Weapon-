#!/usr/bin/env python3
"""
Setup script to initialize the Astra project structure
"""

import os
import subprocess
import sys

def create_directory_structure():
    """Create the project directory structure"""
    directories = [
        'core',
        'modules',
        'utils',
        'docs',
        'config',
        'ui',
        'ui/pages',
        'ui/assets',
        'reports',
        'logs'
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create __init__.py in Python package directories
        if directory not in ['docs', 'config', 'reports', 'logs', 'ui/assets']:
            init_file = os.path.join(directory, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write('"""\n{} package\n"""\n'.format(directory.replace('/', '.')))
    
    print("✅ Directory structure created successfully")

def setup_virtual_environment():
    """Set up a Python virtual environment"""
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("✅ Virtual environment created successfully")
    else:
        print("✅ Virtual environment already exists")

def install_dependencies():
    """Install project dependencies"""
    # Determine the pip command based on the OS
    if sys.platform == 'win32':
        pip_path = os.path.join('venv', 'Scripts', 'pip')
    else:
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    print("Installing dependencies...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])
    print("✅ Dependencies installed successfully")

def initialize_git():
    """Initialize git repository if not already initialized"""
    if not os.path.exists('.git'):
        print("Initializing Git repository...")
        subprocess.run(["git", "init"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Initial project setup"])
        print("✅ Git repository initialized successfully")
    else:
        print("✅ Git repository already initialized")

def main():
    """Main setup function"""
    print("Setting up Astra project structure...")
    create_directory_structure()
    setup_virtual_environment()
    install_dependencies()
    initialize_git()
    print("\nSetup complete! Run the following commands to activate the environment and start the application:")
    if sys.platform == 'win32':
        print("\nvenv\\Scripts\\activate")
    else:
        print("\nsource venv/bin/activate")
    print("python main.py")

if __name__ == "__main__":
    main()
