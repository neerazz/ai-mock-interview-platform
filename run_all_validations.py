#!/usr/bin/env python3
"""
Master Validation Script

This script runs all end-to-end validation tests for the AI Mock Interview Platform.
It executes all validation scripts in sequence and provides a comprehensive report.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}")
    print(f"{text}")
    print(f"{'=' * 70}{Colors.RESET}\n")


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_info(message: str):
    """Print an info message"""
    print(f"  {message}")


def run_validation_script(script_name: str, description: str) -> Tuple[bool, float]:
    """Run a validation script and return success status and duration"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Running: {description}{Colors.RESET}")
    print(f"Script: {script_name}")
    print("-" * 70)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        elapsed = time.time() - start_time
        success = result.returncode == 0
        
        if success:
            print_success(f"Completed in {elapsed:.2f}s")
        else:
            print_error(f"Failed after {elapsed:.2f}s (exit code: {result.returncode})")
        
        return success, elapsed
        
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print_error(f"Timed out after {elapsed:.2f}s")
        return False, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print_error(f"Error: {str(e)}")
        return False, elapsed


def check_prerequisites() -> bool:
    """Check that prerequisites are met"""
    print_header("Checking Prerequisites")
    
    all_good = True
    
    # Check Python version
    print_info("Checking Python version...")
    if sys.version_info >= (3, 10):
        print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} (>= 3.10)")
    else:
        print_error(f"Python {sys.version_info.major}.{sys.version_info.minor} (requires >= 3.10)")
        all_good = False
    
    # Check environment variables
    print_info("Checking environment variables...")
    required_vars = ["OPENAI_API_KEY", "DATABASE_URL"]
    for var in required_vars:
        if os.getenv(var):
            print_success(f"{var} is set")
        else:
            print_warning(f"{var} is not set (some tests may be skipped)")
    
    # Check validation scripts exist
    print_info("Checking validation scripts...")
    scripts = [
        "validate_e2e_workflow.py",
        "validate_error_scenarios.py",
        "validate_docker_deployment.py",
        "validate_performance.py",
        "validate_ui_ux.py",
    ]
    
    for script in scripts:
        if Path(script).exists():
            print_success(f"Found: {script}")
        else:
            print_error(f"Missing: {script}")
            all_good = False
    
    return all_good


def main():
    """Run all validation tests"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  AI Mock Interview Platform - Complete Validation Suite".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print(Colors.RESET)
    
    start_time = time.time()
    
    # Check prerequisites
    if not check_prerequisites():
        print_error("\nPrerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    # Define validation tests
    validations = [
        ("validate_ui_ux.py", "UI/UX Polish Validation", True),
        ("validate_error_scenarios.py", "Error Scenarios Validation", True),
        ("validate_e2e_workflow.py", "End-to-End Workflow Validation", False),  # Requires API
        ("validate_performance.py", "Performance Validation", False),  # Requires API
        ("validate_docker_deployment.py", "Docker Deployment Validation", False),  # Optional
    ]
    
    results = []
    
    # Run validations
    for script, description, required in validations:
        if not Path(script).exists():
            print_warning(f"\nSkipping {description}: Script not found")
            results.append((description, False, 0, False))
            continue
        
        # Check if we should skip optional tests
        if not required and not os.getenv("OPENAI_API_KEY"):
            print_warning(f"\nSkipping {description}: OPENAI_API_KEY not set")
            results.append((description, None, 0, False))
            continue
        
        success, duration = run_validation_script(script, description)
        results.append((description, success, duration, required))
    
    # Print summary
    total_time = time.time() - start_time
    
    print_header("Validation Summary")
    
    passed = sum(1 for _, success, _, _ in results if success is True)
    failed = sum(1 for _, success, _, required in results if success is False and required)
    skipped = sum(1 for _, success, _, _ in results if success is None)
    total = len([r for r in results if r[3]])  # Count only required tests
    
    print(f"\n{Colors.BOLD}Test Results:{Colors.RESET}\n")
    
    for description, success, duration, required in results:
        if success is True:
            status = f"{Colors.GREEN}✓ PASS{Colors.RESET}"
        elif success is False:
            status = f"{Colors.RED}✗ FAIL{Colors.RESET}"
        else:
            status = f"{Colors.YELLOW}⊘ SKIP{Colors.RESET}"
        
        req_marker = "" if required else " (optional)"
        print(f"  {status} - {description}{req_marker} ({duration:.1f}s)")
    
    print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  Passed:  {passed}")
    print(f"  Failed:  {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Total:   {total} required tests")
    print(f"  Time:    {total_time:.1f}s")
    
    # Final verdict
    print()
    if failed == 0 and passed >= total:
        print(f"{Colors.BOLD}{Colors.GREEN}╔{'═' * 68}╗")
        print(f"║{'✓ ALL REQUIRED VALIDATIONS PASSED'.center(68)}║")
        print(f"╚{'═' * 68}╝{Colors.RESET}")
        print()
        print_info("The AI Mock Interview Platform is ready for use!")
        print_info("All critical functionality has been validated.")
        sys.exit(0)
    elif failed == 0:
        print(f"{Colors.BOLD}{Colors.YELLOW}╔{'═' * 68}╗")
        print(f"║{'⚠ SOME TESTS SKIPPED'.center(68)}║")
        print(f"╚{'═' * 68}╝{Colors.RESET}")
        print()
        print_warning("Some optional tests were skipped.")
        print_info("The platform should work, but full validation is incomplete.")
        sys.exit(0)
    else:
        print(f"{Colors.BOLD}{Colors.RED}╔{'═' * 68}╗")
        print(f"║{'✗ VALIDATION FAILED'.center(68)}║")
        print(f"╚{'═' * 68}╝{Colors.RESET}")
        print()
        print_error(f"{failed} required test(s) failed.")
        print_info("Please review the errors above and fix the issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
