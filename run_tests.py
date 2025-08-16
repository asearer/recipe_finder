#!/usr/bin/env python3
"""
Test runner script for the Recipe Finder project.
Provides easy commands to run different types of tests and generate coverage reports.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Command not found. Make sure pytest is installed.")
        return False


def install_dependencies():
    """Install test dependencies."""
    print("Installing test dependencies...")
    command = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    return run_command(command, "Installing dependencies")


def run_unit_tests():
    """Run unit tests only."""
    command = [sys.executable, "-m", "pytest", "tests/", "-v", "-k", "not integration"]
    return run_command(command, "Unit tests")


def run_integration_tests():
    """Run integration tests only."""
    command = [sys.executable, "-m", "pytest", "tests/", "-v", "-k", "integration"]
    return run_command(command, "Integration tests")


def run_all_tests():
    """Run all tests."""
    command = [sys.executable, "-m", "pytest", "tests/", "-v"]
    return run_command(command, "All tests")


def run_tests_with_coverage():
    """Run tests with coverage report."""
    command = [sys.executable, "-m", "pytest", "tests/", "-v", "--cov=backend", "--cov-report=term-missing", "--cov-report=html"]
    return run_command(command, "Tests with coverage")


def run_specific_test_file(test_file):
    """Run a specific test file."""
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found!")
        return False
    
    command = [sys.executable, "-m", "pytest", test_file, "-v"]
    return run_command(command, f"Specific test file: {test_file}")


def run_specific_test_class(test_file, test_class):
    """Run a specific test class."""
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found!")
        return False
    
    command = [sys.executable, "-m", "pytest", f"{test_file}::{test_class}", "-v"]
    return run_command(command, f"Test class: {test_class}")


def run_specific_test_method(test_file, test_class, test_method):
    """Run a specific test method."""
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found!")
        return False
    
    command = [sys.executable, "-m", "pytest", f"{test_file}::{test_class}::{test_method}", "-v"]
    return run_command(command, f"Test method: {test_method}")


def show_coverage_report():
    """Show the coverage report."""
    coverage_file = Path("htmlcov/index.html")
    if coverage_file.exists():
        print(f"\n📊 Coverage report generated at: {coverage_file.absolute()}")
        print("Open this file in your browser to view the detailed coverage report.")
    else:
        print("\n❌ No coverage report found. Run tests with coverage first.")


def show_help():
    """Show help information."""
    help_text = """
Recipe Finder Test Runner

Usage: python run_tests.py [command]

Commands:
    install          Install test dependencies
    unit            Run unit tests only
    integration     Run integration tests only
    all             Run all tests
    coverage        Run tests with coverage report
    help            Show this help message

Examples:
    python run_tests.py install          # Install dependencies
    python run_tests.py unit            # Run unit tests
    python run_tests.py coverage        # Run tests with coverage
    python run_tests.py all             # Run all tests

For more specific testing:
    python -m pytest tests/test_models.py -v                    # Run specific test file
    python -m pytest tests/test_models.py::TestUserModel -v     # Run specific test class
    python -m pytest tests/test_models.py::TestUserModel::test_create_user -v  # Run specific test method

Coverage reports:
    - Terminal coverage: python -m pytest --cov=backend --cov-report=term-missing
    - HTML coverage: python -m pytest --cov=backend --cov-report=html
    - XML coverage: python -m pytest --cov=backend --cov-report=xml
"""
    print(help_text)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        install_dependencies()
    elif command == "unit":
        run_unit_tests()
    elif command == "integration":
        run_integration_tests()
    elif command == "all":
        run_all_tests()
    elif command == "coverage":
        run_tests_with_coverage()
        show_coverage_report()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()
