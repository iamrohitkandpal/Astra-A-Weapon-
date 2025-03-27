#!/usr/bin/env python3
"""
Build script to package Astra as an executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
import platform

def clean_build_dir():
    """Clean up build directory before starting"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    spec_file = 'astra.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)

def build_executable():
    """Build the executable using PyInstaller"""
    # Create directory for assets
    os.makedirs('dist/assets', exist_ok=True)
    
    # Determine icon path based on platform
    icon_param = ""
    if platform.system() == 'Windows':
        icon_param = "--icon=ui/assets/astra_icon.ico"
    elif platform.system() == 'Darwin':  # macOS
        icon_param = "--icon=ui/assets/astra_icon.icns"
        
    # Define PyInstaller command
    command = [
        "pyinstaller",
        "--name=Astra",
        "--onedir",
        "--windowed",
        f"{icon_param}",
        "--add-data=ui/assets;ui/assets",
        "--add-data=config;config",
        "--add-data=LICENSE;.",
        "--add-data=README.md;.",
        "--hidden-import=dns.resolver",
        "--hidden-import=socks",
        "--hidden-import=stem",
        "--hidden-import=reportlab",
        "--hidden-import=dominate",
        "--hidden-import=psutil",
        "main.py"
    ]
    
    # Run PyInstaller
    subprocess.run(" ".join(command), shell=True)
    
    # Copy additional assets to dist
    copy_assets()

def copy_assets():
    """Copy additional assets to the distribution folder"""
    # Create necessary directories
    os.makedirs('dist/Astra/reports', exist_ok=True)
    os.makedirs('dist/Astra/logs', exist_ok=True)
    
    # Copy default wordlists
    os.makedirs('dist/Astra/wordlists', exist_ok=True)
    if os.path.exists('wordlists'):
        for wordlist in os.listdir('wordlists'):
            if wordlist.endswith('.txt'):
                shutil.copy(
                    os.path.join('wordlists', wordlist),
                    os.path.join('dist/Astra/wordlists', wordlist)
                )

def main():
    """Main build function"""
    print("Building Astra Executable...")
    
    # Clean up previous build artifacts
    clean_build_dir()
    
    # Create the executable
    build_executable()
    
    print("\nBuild complete! Executable can be found in the 'dist/Astra' directory.")

if __name__ == "__main__":
    main()
