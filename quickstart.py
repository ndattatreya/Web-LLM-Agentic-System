#!/usr/bin/env python
"""
Quick Start Script for Web-LLM Agentic System
Starts both backend and frontend servers
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def run_backend():
    """Start the FastAPI backend server"""
    print("🎯 Starting Backend (FastAPI)...")
    print("   Backend will run on http://localhost:8000")
    print("   API docs at http://localhost:8000/docs\n")
    
    backend_path = Path(__file__).parent / "backend" / "app" / "main.py"
    
    try:
        subprocess.Popen(
            [sys.executable, str(backend_path)],
            cwd=str(Path(__file__).parent)
        )
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False
    
    return True

def run_frontend():
    """Start the React development server"""
    print("🎨 Starting Frontend (React)...")
    print("   Frontend will run on http://localhost:5173\n")
    
    frontend_path = Path(__file__).parent / "frontend"
    
    try:
        subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(frontend_path)
        )
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return False
    
    return True

def main():
    print("""
    ╔════════════════════════════════════════════════╗
    ║   Web-LLM Agentic System - Full Stack Setup   ║
    ╚════════════════════════════════════════════════╝
    """)
    
    print("📋 Quick Start Guide:")
    print("   1. Backend will start on port 8000")
    print("   2. Frontend will start on port 5173")
    print("   3. Browser will open automatically\n")
    
    # Start services
    backend_ok = run_backend()
    time.sleep(5)  # Give backend time to start
    
    frontend_ok = run_frontend()
    time.sleep(5)  # Give frontend time to start
    
    if backend_ok and frontend_ok:
        print("✅ Both services started successfully!")
        print("\n📱 Opening browser...")
        time.sleep(2)
        webbrowser.open("http://localhost:5173")
        
        print("""
        ═══════════════════════════════════════════════════════════
        ✅ Setup Complete! The application is ready to use.
        
        📊 Access Points:
           - Frontend: http://localhost:5173
           - Backend API: http://localhost:8000
           - API Docs: http://localhost:8000/docs
           - OpenAPI Schema: http://localhost:8000/openapi.json
        
        ⌨️  Controls:
           - Press Ctrl+C to stop all services
           - Check terminal output for any errors
        
        📚 First Steps:
           1. Go to "Process Document" tab
           2. Enter a URL or upload a PDF
           3. View the results in "View Results" tab
           4. Check "Data Analysis" for statistics
        ═══════════════════════════════════════════════════════════
        """)
    else:
        print("❌ Failed to start all services")
        print("Please check the error messages above")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down services...")
        sys.exit(0)
