#!/usr/bin/env python3
"""
Chores.ai Desktop POC - Main Entry Point

This is the main entry point for the Chores.ai desktop application.
It initializes and runs the main application window.

To run the application:
    python main.py

Or simply:
    python main.py
"""

import sys
import os

# Add the current directory to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from chore_ui import ChoresAIApp
    print("Starting Chores.ai Desktop POC...")
    print("=" * 50)
    
    # Create and run the application
    app = ChoresAIApp()
    app.run()
    
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure all required files are in the same directory:")
    print("- chore_model.py")
    print("- chore_manager.py") 
    print("- chore_ui.py")
    sys.exit(1)
    
except Exception as e:
    print(f"Error starting application: {e}")
    print("Please check the error message above and try again.")
    sys.exit(1) 