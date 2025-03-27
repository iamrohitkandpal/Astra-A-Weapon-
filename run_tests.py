#!/usr/bin/env python3
"""
Test runner script for Astra
"""

import os
import sys
import unittest
import subprocess
import platform
import time
import re
from pathlib import Path

def run_unit_tests():
    """Run the unit tests"""
    print("Running unit tests...")
    test_loader = unittest.TestLoader()
    
    # Discover tests in the tests directory
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    if not os.path.exists(test_dir):
        print("Tests directory not found. Creating...")
        os.makedirs(test_dir)
        with open(os.path.join(test_dir, '__init__.py'), 'w') as f:
            f.write('"""Test package for Astra"""')
        
        print("No tests found. Please add test files to the 'tests' directory.")
        return True
    
    test_suite = test_loader.discover(test_dir)
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

def check_dependencies():
    """Check if all dependencies are installed"""
    print("Checking dependencies...")
    
    try:
        # Import the dependency manager
        sys.path.append(os.path.dirname(__file__))
        from utils.dependency_manager import DependencyManager
        
        dm = DependencyManager()
        missing = dm.check_missing_dependencies()
        
        if missing and not isinstance(missing, dict) or (isinstance(missing, dict) and 'error' in missing):
            print("Error checking dependencies")
            return False
        
        if missing:
            print(f"Missing or incompatible dependencies: {', '.join(missing.keys())}")
            
            # Ask if user wants to install missing dependencies
            if input("Install missing dependencies? (y/n): ").lower() == 'y':
                result = dm.install_requirements()
                if not result['success']:
                    print(f"Error installing dependencies: {result['message']}")
                    return False
                print("Dependencies installed successfully")
                return True
            return False
        
        print("All dependencies installed.")
        return True
    
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        return False

def check_code_quality():
    """Run code quality checks"""
    print("Checking code quality...")
    
    try:
        # Check if pylint is installed
        try:
            import pylint
        except ImportError:
            print("pylint not installed. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pylint"])
        
        # Run pylint on core modules
        score = 0
        core_dir = 'core'
        if os.path.exists(core_dir):
            print(f"Running pylint on {core_dir}...")
            result = subprocess.run(
                [sys.executable, "-m", "pylint", core_dir, "--disable=C0111", "--disable=C0103", "--exit-zero"],
                capture_output=True, text=True
            )
            
            # Extract score
            score_match = re.search(r'Your code has been rated at ([\d.]+)/10', result.stdout)
            if score_match:
                score = float(score_match.group(1))
                print(f"Pylint score: {score}/10")
        
        return score >= 7.0  # Require a score of at least 7.0
    
    except Exception as e:
        print(f"Error checking code quality: {e}")
        return False

def check_build_readiness():
    """Check if the project is ready to be built"""
    print("Checking build readiness...")
    
    # Check if all needed directories exist
    required_dirs = ['core', 'utils', 'ui', 'ui/pages', 'ui/assets']
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"Missing required directory: {dir_path}")
            return False
    
    # Check for main.py
    if not os.path.exists('main.py'):
        print("Missing main.py file")
        return False
    
    # Check for required files
    required_files = [
        'requirements.txt',
        'README.md',
        'setup.py',
        'build_exe.py'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"Missing required file: {file_path}")
            return False
    
    # Check for build_exe.py script
    if os.path.exists('build_exe.py'):
        print("Build script found.")
    else:
        print("Warning: build_exe.py not found. This is required for packaging.")
        return False
    
    print("All required files and directories present.")
    return True

def run_manual_test_app(wait_time=5):
    """Run the application in test mode for manual testing"""
    print(f"Starting Astra for a quick {wait_time}-second test...")
    
    try:
        # Run the app with a test flag
        process = subprocess.Popen([sys.executable, "main.py", "--test"])
        
        # Wait a few seconds
        time.sleep(wait_time)
        
        # Terminate the process
        process.terminate()
        process.wait()
        
        print("Test run completed.")
        return True
    
    except Exception as e:
        print(f"Error running manual tests: {e}")
        return False

def test_report_generation():
    """Test the report generation functionality"""
    print("Testing report generation...")
    
    # Create a sample report directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Import the report generator
    try:
        sys.path.append(os.path.dirname(__file__))
        from utils.report_generator import ReportGenerator
        
        # Create a sample report
        report_gen = ReportGenerator()
        
        # Create test data
        test_data = [
            ("Test Item 1", "Test Value 1"),
            ("Test Item 2", "Test Value 2"),
            ("Test Item 3", "Test Value 3")
        ]
        
        # Generate both report types
        try:
            pdf_path = report_gen.generate_pdf_report(
                "Test Report", 
                test_data, 
                "Test", 
                "test_target"
            )
            
            html_path = report_gen.generate_html_report(
                "Test Report", 
                test_data, 
                "Test", 
                "test_target"
            )
            
            if pdf_path and html_path:
                print(f"Report generation successful. PDF: {pdf_path}, HTML: {html_path}")
                return True
            else:
                print("Report generation failed.")
                return False
                
        except Exception as e:
            print(f"Error generating reports: {e}")
            return False
    
    except ImportError:
        print("Report generator module not found.")
        return False

def test_theme_system():
    """Test the theme system functionality"""
    print("Testing theme system...")
    
    try:
        # Try to import theme system components
        from utils.theme_manager import ThemeManager
        from ui.theme_editor import ThemeEditorDialog
        from ui.controllers.theme_controller import ThemeController
        
        # Create a theme manager and test basic functionality
        theme_manager = ThemeManager()
        
        # Check that default themes exist
        themes = theme_manager.get_available_themes()
        if not themes or "light" not in themes or "dark" not in themes:
            print("❌ Default themes not found")
            return False
        
        # Test theme loading
        success = theme_manager.load_theme("light")
        if not success:
            print("❌ Failed to load light theme")
            return False
        
        light_theme = theme_manager.get_current_theme()
        
        success = theme_manager.load_theme("dark")
        if not success:
            print("❌ Failed to load dark theme")
            return False
        
        dark_theme = theme_manager.get_current_theme()
        
        # Check that the themes are different
        if light_theme == dark_theme:
            print("❌ Light and dark themes are identical")
            return False
        
        # Test system theme detection
        system_theme = theme_manager.get_system_theme()
        if system_theme not in ["light", "dark"]:
            print(f"⚠️ System theme detection returned unexpected value: {system_theme}")
        
        # Test auto-detect mode
        theme_manager.enable_auto_detect(True)
        if not theme_manager.is_auto_detect_enabled():
            print("❌ Failed to enable auto-detect mode")
            return False
        
        # Disable auto-detect
        theme_manager.enable_auto_detect(False)
        if theme_manager.is_auto_detect_enabled():
            print("❌ Failed to disable auto-detect mode")
            return False
        
        print("✅ Theme system tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing theme system: {e}")
        return False

def main():
    """Main test function"""
    print("Running Astra Test Suite")
    print("=======================")
    
    # Results tracking
    results = {}
    
    # Check dependencies
    results['dependencies'] = check_dependencies()
    
    # Check build readiness
    results['build_readiness'] = check_build_readiness()
    
    # Test report generation
    results['report_generation'] = test_report_generation()
    
    # Test theme system
    results['theme_system'] = test_theme_system()
    
    # Run a quick manual test
    results['quick_app_test'] = run_manual_test_app(3)
    
    # Run unit tests if available
    results['unit_tests'] = run_unit_tests()
    
    # Check code quality if requested
    if len(sys.argv) > 1 and sys.argv[1] == '--quality':
        results['code_quality'] = check_code_quality()
    
    # Print summary
    print("\nTest Results:")
    print("=======================")
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test}: {status}")
    
    # Overall result
    overall = all(results.values())
    print("\nOverall Result:", "✅ PASS" if overall else "❌ FAIL")
    
    # If all tests passed, suggest building the executable
    if overall:
        print("\nAll tests passed! You can now build the executable:")
        print("python build_exe.py")
    
    return 0 if overall else 1

if __name__ == "__main__":
    sys.exit(main())
