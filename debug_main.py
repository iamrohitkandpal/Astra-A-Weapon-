#!/usr/bin/env python3
"""
Astra - An Ethical Hacking Desktop Application
Main entry point
"""

import sys
import os
import gc 
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.config_loader import load_config
from utils.memory_optimizer import enable_garbage_collection

def main():
    """Main application entry point"""
    # Enable aggressive garbage collection for better memory management
    enable_garbage_collection()
    
    # Load configuration
    config = load_config()
    
    # Add these lines right before QApplication is created:
    print("Setting up application...")
    print(f"Python version: {sys.version}")
    print(f"PyQt6 version: {PyQt6.__version__}")
    print("Creating application instance...")
    
    # Start application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
