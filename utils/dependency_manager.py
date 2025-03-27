"""
Dependency management utility for Astra
"""

import sys
import subprocess
import pkg_resources
import os
from pathlib import Path
import platform

class DependencyManager:
    """Manage dependencies for the Astra application"""
    
    def __init__(self):
        """Initialize the dependency manager"""
        # Determine pip command based on virtual environment
        if self._is_in_virtualenv():
            self.pip_command = [sys.executable, "-m", "pip"]
        elif platform.system() == "Windows":
            self.pip_command = ["pip"]
        else:
            self.pip_command = ["pip3"]
    
    def _is_in_virtualenv(self):
        """Check if running in a virtual environment"""
        return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    def get_installed_packages(self):
        """Get list of installed packages and versions"""
        return {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    
    def check_missing_dependencies(self):
        """Check for missing dependencies based on requirements.txt"""
        requirements_file = Path("requirements.txt")
        if not requirements_file.exists():
            return {"error": "requirements.txt not found"}
        
        required_packages = {}
        missing_packages = {}
        
        # Parse requirements.txt
        with open(requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Handle lines with version specifiers
                    if '==' in line:
                        package, version = line.split('==', 1)
                        required_packages[package.lower()] = version
                    elif '>=' in line:
                        package, version = line.split('>=', 1)
                        required_packages[package.lower()] = f">={version}"
                    else:
                        required_packages[line.lower()] = "any"
        
        # Get installed packages
        installed_packages = self.get_installed_packages()
        
        # Check for missing or incorrect versions
        for package, required_version in required_packages.items():
            package_key = package.lower().replace('-', '_')
            
            if package_key not in installed_packages:
                missing_packages[package] = {"required": required_version, "installed": None}
            elif required_version != "any" and required_version.startswith(">="):
                # Check if installed version is greater or equal
                min_version = required_version[2:]
                if pkg_resources.parse_version(installed_packages[package_key]) < pkg_resources.parse_version(min_version):
                    missing_packages[package] = {
                        "required": required_version, 
                        "installed": installed_packages[package_key]
                    }
            elif required_version != "any" and installed_packages[package_key] != required_version:
                missing_packages[package] = {
                    "required": required_version, 
                    "installed": installed_packages[package_key]
                }
        
        return missing_packages
    
    def install_package(self, package, version=None):
        """Install a single package"""
        try:
            if version:
                package_spec = f"{package}=={version}"
            else:
                package_spec = package
                
            result = subprocess.run([*self.pip_command, "install", package_spec], 
                                   capture_output=True, text=True)
                
            if result.returncode != 0:
                return {"success": False, "message": result.stderr}
            return {"success": True, "message": f"Successfully installed {package_spec}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def install_requirements(self):
        """Install all packages from requirements.txt"""
        try:
            result = subprocess.run([*self.pip_command, "install", "-r", "requirements.txt"], 
                                   capture_output=True, text=True)
                
            if result.returncode != 0:
                return {"success": False, "message": result.stderr}
            return {"success": True, "message": "Successfully installed all requirements"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def update_package(self, package):
        """Update a package to the latest version"""
        try:
            result = subprocess.run([*self.pip_command, "install", "--upgrade", package], 
                                   capture_output=True, text=True)
                
            if result.returncode != 0:
                return {"success": False, "message": result.stderr}
            return {"success": True, "message": f"Successfully updated {package}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def check_optional_dependencies(self):
        """Check for optional dependencies"""
        optional_deps = {
            "amass": self._check_command_exists("amass"),
            "stem": "stem" in self.get_installed_packages(),
            "tor": self._check_command_exists("tor"),
            "nmap": self._check_command_exists("nmap"),
            "pyinstaller": "pyinstaller" in self.get_installed_packages()
        }
        
        return optional_deps
    
    def _check_command_exists(self, command):
        """Check if a command exists in the system PATH"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["where", command], 
                                       capture_output=True, text=True)
            else:
                result = subprocess.run(["which", command], 
                                       capture_output=True, text=True)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def generate_dependency_report(self):
        """Generate a comprehensive report on dependencies"""
        report = {
            "installed_packages": self.get_installed_packages(),
            "missing_dependencies": self.check_missing_dependencies(),
            "optional_dependencies": self.check_optional_dependencies(),
            "environment": {
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "in_virtualenv": self._is_in_virtualenv()
            }
        }
        
        return report
