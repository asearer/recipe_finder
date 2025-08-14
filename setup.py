#!/usr/bin/env python3
"""
Setup script for AI Recipe Finder Portfolio Project
This script sets up the virtual environment and installs dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"Command: {command}")
        print(f"Exit code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def main():
    """Main setup function."""
    print("🚀 Setting up AI Recipe Finder Portfolio Project")
    print("=" * 50)

    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)

    # Check if virtual environment exists
    venv_path = project_root / ".venv"

    if not venv_path.exists():
        print("📦 Virtual environment not found. Creating new virtual environment...")
        run_command(f"python3 -m venv {venv_path}", "Creating virtual environment")
    else:
        print("✅ Virtual environment already exists")

    # Determine the correct python and pip paths
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        python_path = venv_path / "bin" / "python"
        pip_path = venv_path / "bin" / "pip"

    # Upgrade pip
    run_command(f"{python_path} -m pip install --upgrade pip", "Upgrading pip")

    # Install requirements
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        run_command(f"{pip_path} install -r requirements.txt", "Installing Python dependencies")
    else:
        print("⚠️ requirements.txt not found. Installing basic FastAPI dependencies...")
        run_command(f"{pip_path} install fastapi uvicorn sqlalchemy pydantic python-jose passlib python-multipart", "Installing basic dependencies")

    # Create database tables
    print("🗄️ Setting up database...")
    run_command(f"{python_path} -c \"from backend.database import engine, Base; from backend import models; Base.metadata.create_all(bind=engine); print('Database tables created successfully')\"", "Creating database tables")

    # Seed initial data if seed script exists
    seed_script = project_root / "backend" / "seed_data.py"
    if seed_script.exists():
        try:
            run_command(f"{python_path} -m backend.seed_data", "Seeding initial data")
        except:
            print("ℹ️ Seed data script found but failed to run (this is optional)")

    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. To start the backend server:")
    print(f"   {python_path} -m uvicorn backend.main:app --reload --port 8000")
    print("\n2. To serve the frontend, use a simple HTTP server:")
    print("   cd frontend && python3 -m http.server 3000")
    print("\n3. Open your browser and go to:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API docs: http://localhost:8000/docs")
    print("\n4. Or use the run script:")
    print("   python3 run.py")

if __name__ == "__main__":
    main()
