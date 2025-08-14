#!/usr/bin/env python3
"""
Run script for AI Recipe Finder Portfolio Project
This script starts both the backend and frontend servers.
"""

import subprocess
import sys
import os
import signal
import time
from pathlib import Path
import threading

def run_backend():
    """Run the FastAPI backend server."""
    project_root = Path(__file__).parent.absolute()
    venv_path = project_root / ".venv"

    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"

    os.chdir(project_root)

    print("🚀 Starting backend server on http://localhost:8000")
    try:
        subprocess.run([
            str(python_path), "-m", "uvicorn",
            "backend.main:app", "--reload", "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting backend server: {e}")

def run_frontend():
    """Run the frontend server."""
    project_root = Path(__file__).parent.absolute()
    frontend_path = project_root / "frontend"

    if not frontend_path.exists():
        print("❌ Frontend directory not found!")
        return

    os.chdir(frontend_path)

    print("🌐 Starting frontend server on http://localhost:3000")
    print("📂 Serving from frontend directory")

    try:
        subprocess.run([
            sys.executable, "-m", "http.server", "3000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend server: {e}")

def run_both():
    """Run both servers in separate threads."""
    print("🚀 AI Recipe Finder - Starting both servers")
    print("=" * 50)

    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    # Give backend time to start
    time.sleep(3)

    # Start frontend in main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "backend":
            run_backend()
        elif sys.argv[1] == "frontend":
            run_frontend()
        elif sys.argv[1] == "help" or sys.argv[1] == "-h":
            print("Usage:")
            print("  python3 run.py           # Start both servers")
            print("  python3 run.py backend   # Start only backend server")
            print("  python3 run.py frontend  # Start only frontend server")
            print("  python3 run.py help      # Show this help message")
        else:
            print(f"❌ Unknown command: {sys.argv[1]}")
            print("Use 'python3 run.py help' for usage information")
    else:
        run_both()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
