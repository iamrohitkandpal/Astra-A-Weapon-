#!/usr/bin/env python3
"""
Script to prepare a new release of Astra
"""

import os
import sys
import subprocess
import re
import shutil
import platform
from datetime import datetime
from pathlib import Path

def get_current_version():
    """Get the current version from the main window file"""
    with open('ui/main_window.py', 'r') as f:
        content = f.read()
        match = re.search(r'version_label = QLabel\("v([0-9.]+)"\)', content)
        if match:
            return match.group(1)
    return "0.1.0"  # Default version

def update_version(version):
    """Update the version in the main window file"""
    with open('ui/main_window.py', 'r') as f:
        content = f.read()
    
    # Replace version in main_window.py
    updated_content = re.sub(
        r'version_label = QLabel\("v[0-9.]+"\)', 
        f'version_label = QLabel("v{version}")', 
        content
    )
    
    with open('ui/main_window.py', 'w') as f:
        f.write(updated_content)
    
    print(f"✅ Updated version to {version} in ui/main_window.py")

def update_readme(version):
    """Update the version in the README.md file"""
    if os.path.exists('README.md'):
        with open('README.md', 'r') as f:
            content = f.read()
        
        # Update version in README if it exists
        if re.search(r'## Version [0-9.]+', content):
            updated_content = re.sub(
                r'## Version [0-9.]+', 
                f'## Version {version}', 
                content
            )
            
            with open('README.md', 'w') as f:
                f.write(updated_content)
            
            print(f"✅ Updated version to {version} in README.md")

def create_release_zip(version):
    """Create a ZIP file for the release (without building the exe)"""
    release_dir = Path('release')
    release_dir.mkdir(exist_ok=True)
    
    filename = f"astra-{version}-source.zip"
    zip_path = release_dir / filename
    
    # Files and directories to include
    include_paths = [
        'core', 'ui', 'utils', 'modules', 'config', 'docs',
        'main.py', 'requirements.txt', 'README.md', 'setup.py',
        'build_exe.py', 'LICENSE'
    ]
    
    # Files and directories to exclude
    exclude_paths = [
        '__pycache__', '.git', '.gitignore', '.DS_Store', 
        '*.pyc', '*.pyo', '*.pyd', '.pytest_cache', 
        'build', 'dist', '*.spec'
    ]
    
    # Create a filtered zip file
    if platform.system() == "Windows":
        powershell_command = [
            "powershell", 
            "-Command", 
            f"Compress-Archive -Path {','.join(include_paths)} -DestinationPath {zip_path} -Force"
        ]
        subprocess.run(powershell_command)
    else:
        # For Unix systems, use zip command
        exclude_args = ' '.join([f"--exclude='{ex}'" for ex in exclude_paths])
        subprocess.run(f"zip -r {zip_path} {' '.join(include_paths)} {exclude_args}", shell=True)
    
    print(f"✅ Release source ZIP created at {zip_path}")
    return zip_path

def build_executable():
    """Build the executable using the build_exe.py script"""
    print("Building executable...")
    
    # Run the build script
    if platform.system() == "Windows":
        subprocess.run([sys.executable, "build_exe.py"])
    else:
        subprocess.run([sys.executable, "build_exe.py"])
    
    print("✅ Build completed")
    
    # Create a ZIP of the dist directory
    version = get_current_version()
    release_dir = Path('release')
    release_dir.mkdir(exist_ok=True)
    
    filename = f"astra-{version}-{platform.system().lower()}.zip"
    zip_path = release_dir / filename
    
    # Zip the dist/Astra directory
    if os.path.exists('dist/Astra'):
        if platform.system() == "Windows":
            powershell_command = [
                "powershell", 
                "-Command", 
                f"Compress-Archive -Path dist/Astra -DestinationPath {zip_path} -Force"
            ]
            subprocess.run(powershell_command)
        else:
            subprocess.run(f"cd dist && zip -r ../{zip_path} Astra", shell=True)
        
        print(f"✅ Release executable ZIP created at {zip_path}")
        return zip_path
    else:
        print("❌ Build directory not found")
        return None

def create_release_notes(version):
    """Create release notes file"""
    notes_dir = Path('release_notes')
    notes_dir.mkdir(exist_ok=True)
    
    release_date = datetime.now().strftime("%Y-%m-%d")
    notes_file = notes_dir / f"v{version}_{release_date}.md"
    
    with open(notes_file, 'w') as f:
        f.write(f"# Release Notes - Version {version}\n\n")
        f.write(f"Release Date: {release_date}\n\n")
        f.write("## Changes\n\n")
        f.write("- Add your changes here\n")
        f.write("- Feature: \n")
        f.write("- Fix: \n")
        f.write("- Improvement: \n\n")
        f.write("## Known Issues\n\n")
        f.write("- None\n")
    
    print(f"✅ Created release notes template at {notes_file}")
    return notes_file

def commit_and_tag(version):
    """Commit changes and create a tag for the release"""
    # Add all modified files
    subprocess.run(["git", "add", "."])
    
    # Commit changes
    subprocess.run(["git", "commit", "-m", f"Release version {version}"])
    
    # Create tag
    subprocess.run(["git", "tag", "-a", f"v{version}", "-m", f"Version {version}"])
    
    print(f"✅ Committed and tagged version {version}")

def main():
    """Main release function"""
    print("Preparing new Astra release...")
    
    # Get current version
    current_version = get_current_version()
    
    # Calculate new version (increment patch number)
    version_parts = current_version.split('.')
    version_parts[-1] = str(int(version_parts[-1]) + 1)
    new_version = '.'.join(version_parts)
    
    # Prompt for confirmation
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    
    confirm = input("Do you want to proceed with this version? (y/n): ")
    if confirm.lower() != 'y':
        print("Release process canceled.")
        return
    
    # Update version in files
    update_version(new_version)
    update_readme(new_version)
    
    # Create release notes
    notes_file = create_release_notes(new_version)
    
    # Prompt user to edit release notes
    print(f"\nPlease edit the release notes at {notes_file}")
    input("Press Enter when you've finished editing the release notes...")
    
    # Create release source ZIP
    create_release_zip(new_version)
    
    # Ask if user wants to build the executable
    build_confirm = input("Do you want to build the executable? (y/n): ")
    if build_confirm.lower() == 'y':
        build_executable()
    
    # Commit and tag release
    git_confirm = input("Do you want to commit and tag this release? (y/n): ")
    if git_confirm.lower() == 'y':
        commit_and_tag(new_version)
        
        # Push to remote if requested
        push_confirm = input("Push to remote repository? (y/n): ")
        if push_confirm.lower() == 'y':
            subprocess.run(["git", "push", "origin", "master"])
            subprocess.run(["git", "push", "origin", "--tags"])
            print("✅ Pushed to remote repository")
    
    print(f"\n🎉 Release {new_version} prepared successfully!")
    print("The release files can be found in the 'release' directory.")

if __name__ == "__main__":
    main()
