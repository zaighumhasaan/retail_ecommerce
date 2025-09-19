#!/usr/bin/env python
"""
Test runner script for Retail DevOps application.
Runs different types of tests with appropriate configurations.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_devops.settings')

import django
django.setup()


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def run_unit_tests():
    """Run unit tests."""
    command = [
        'python', '-m', 'pytest',
        'core/tests.py',
        'core/test_views.py',
        '-v',
        '--tb=short',
        '--disable-warnings'
    ]
    return run_command(command, "Unit Tests")


def run_integration_tests():
    """Run integration tests."""
    command = [
        'python', '-m', 'pytest',
        'core/test_integration.py',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '-m', 'integration'
    ]
    return run_command(command, "Integration Tests")


def run_e2e_tests():
    """Run end-to-end tests."""
    try:
        # Check if playwright is installed
        subprocess.run(['python', '-c', 'import playwright'], 
                      check=True, capture_output=True)
        
        # Install playwright browsers if not already installed
        install_command = ['python', '-m', 'playwright', 'install', 'chromium']
        print("Installing Playwright browsers...")
        subprocess.run(install_command, check=False)
        
        command = [
            'python', '-m', 'pytest',
            'tests/test_e2e_basic.py',
            '-v',
            '--tb=short',
            '--disable-warnings',
            '-m', 'e2e'
        ]
        return run_command(command, "End-to-End Tests")
    except subprocess.CalledProcessError:
        print("⚠️  Skipping E2E Tests - Playwright not installed")
        return True


def run_all_tests():
    """Run all tests."""
    command = [
        'python', '-m', 'pytest',
        'core/',
        'tests/',
        '-v',
        '--tb=short',
        '--disable-warnings'
    ]
    return run_command(command, "All Tests")


def run_coverage():
    """Run tests with coverage report."""
    command = [
        'python', '-m', 'pytest',
        'core/',
        'tests/',
        '--cov=core',
        '--cov-report=html',
        '--cov-report=term-missing',
        '--cov-fail-under=80',
        '-v'
    ]
    return run_command(command, "Tests with Coverage")


def run_linting():
    """Run code linting."""
    commands = [
        (['python', '-m', 'black', '--check', 'core/', 'tests/'], "Black Code Formatting Check"),
        (['python', '-m', 'flake8', 'core/', 'tests/'], "Flake8 Linting"),
    ]
    
    all_passed = True
    for command, description in commands:
        try:
            # Check if the module exists before running
            module_name = command[2]  # Get the module name (black, flake8)
            subprocess.run(['python', '-c', f'import {module_name}'], 
                         check=True, capture_output=True)
            if not run_command(command, description):
                all_passed = False
        except subprocess.CalledProcessError:
            print(f"⚠️  Skipping {description} - {command[2]} not installed")
            continue
    
    return all_passed


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run Retail DevOps tests')
    parser.add_argument(
        '--type',
        choices=['unit', 'integration', 'e2e', 'all', 'coverage', 'lint'],
        default='all',
        help='Type of tests to run'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    print("Retail DevOps Test Runner")
    print("=" * 50)
    
    success = True
    
    if args.type == 'unit':
        success = run_unit_tests()
    elif args.type == 'integration':
        success = run_integration_tests()
    elif args.type == 'e2e':
        success = run_e2e_tests()
    elif args.type == 'coverage':
        success = run_coverage()
    elif args.type == 'lint':
        success = run_linting()
    else:  # all
        print("Running all test types...")
        success = (
            run_linting() and
            run_unit_tests() and
            run_integration_tests() and
            run_e2e_tests()
        )
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
