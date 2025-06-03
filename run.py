#!/usr/bin/env python3
"""
Simple runner script for the Real-Time AI Audio Assistant
"""

import sys
import os
import subprocess

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if virtual environment exists
    if not os.path.exists('.venv'):
        print("❌ Virtual environment not found!")
        print("Please run the installation script first:")
        print("  chmod +x install.sh && ./install.sh")
        return False
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please copy .env.example to .env and configure your API keys:")
        print("  cp .env.example .env")
        return False
    
    return True

def run_application():
    """Run the application"""
    if not check_requirements():
        sys.exit(1)
    
    print("🚀 Starting Real-Time AI Audio Assistant...")
    print("📝 Make sure you have configured your API keys in the .env file!")
    print("🎤 Grant microphone permissions when prompted by your browser")
    print("🌐 The application will be available at http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Activate virtual environment and run the application
    if os.name == 'nt':  # Windows
        python_path = os.path.join('.venv', 'Scripts', 'python.exe')
    else:  # Unix/Linux/macOS
        python_path = os.path.join('.venv', 'bin', 'python')
    
    try:
        subprocess.run([python_path, 'main.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Application failed to start: {e}")
        print("Try running the installation script again:")
        print("  chmod +x install.sh && ./install.sh")
    except FileNotFoundError:
        print("❌ Python not found in virtual environment")
        print("Please run the installation script:")
        print("  chmod +x install.sh && ./install.sh")

if __name__ == "__main__":
    run_application()