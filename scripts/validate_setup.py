#!/usr/bin/env python3
"""
Startup Validation Script for AI Mock Interview Platform

This script validates that all dependencies and services are properly configured
before starting the application. It checks:
- Python version
- Required packages
- Environment variables
- Docker services
- Database connectivity
- API keys
"""

import sys
import os
import subprocess
from typing import List, Tuple, Optional
from pathlib import Path
import importlib.util


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(message: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"  {message}")


def check_python_version() -> bool:
    """Check if Python version is 3.10 or higher."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 10:
        print_success(f"Python version: {version_str}")
        return True
    else:
        print_error(f"Python version: {version_str}")
        print_info("Required: Python 3.10 or higher")
        print_info("Please upgrade Python: https://www.python.org/downloads/")
        return False


def check_required_packages() -> bool:
    """Check if all required packages are installed."""
    print_header("Checking Required Packages")
    
    required_packages = [
        "streamlit",
        "langchain",
        "openai",
        "anthropic",
        "psycopg2",
        "streamlit_webrtc",
        "streamlit_drawable_canvas",
        "pydantic",
        "python-dotenv",
        "tenacity"
    ]
    
    all_installed = True
    
    for package in required_packages:
        # Handle package name variations
        import_name = package.replace("-", "_")
        
        if importlib.util.find_spec(import_name) is not None:
            print_success(f"{package} is installed")
        else:
            print_error(f"{package} is NOT installed")
            all_installed = False
    
    if not all_installed:
        print_info("\nTo install missing packages, run:")
        print_info("  pip install -r requirements.txt")
    
    return all_installed


def check_environment_variables() -> bool:
    """Check if required environment variables are set."""
    print_header("Checking Environment Variables")
    
    # Load .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        print_success(".env file found")
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print_warning("python-dotenv not installed, skipping .env loading")
    else:
        print_error(".env file NOT found")
        print_info("Copy config/.env.template to .env and configure it:")
        print_info("  cp config/.env.template .env")
        return False
    
    required_vars = {
        "DB_PASSWORD": "Database password",
        "OPENAI_API_KEY": "OpenAI API key (required)"
    }
    
    optional_vars = {
        "ANTHROPIC_API_KEY": "Anthropic API key (optional)",
        "LOG_LEVEL": "Logging level (default: INFO)",
        "DATA_DIR": "Data directory (default: ./data)"
    }
    
    all_set = True
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f"your-{var.lower().replace('_', '-')}-here":
            # Mask sensitive values
            if "KEY" in var or "PASSWORD" in var:
                masked = value[:8] + "..." if len(value) > 8 else "***"
                print_success(f"{var} is set ({masked})")
            else:
                print_success(f"{var} is set")
        else:
            print_error(f"{var} is NOT set")
            print_info(f"  {description}")
            all_set = False
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and value != f"your-{var.lower().replace('_', '-')}-here":
            if "KEY" in var:
                masked = value[:8] + "..." if len(value) > 8 else "***"
                print_success(f"{var} is set ({masked})")
            else:
                print_success(f"{var} is set ({value})")
        else:
            print_warning(f"{var} is not set")
            print_info(f"  {description}")
    
    if not all_set:
        print_info("\nEdit .env file and set required variables")
    
    return all_set


def check_docker_installed() -> bool:
    """Check if Docker is installed and running."""
    print_header("Checking Docker")
    
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"Docker is installed: {version}")
        else:
            print_error("Docker is installed but not responding")
            return False
    except FileNotFoundError:
        print_error("Docker is NOT installed")
        print_info("Install Docker Desktop: https://www.docker.com/products/docker-desktop")
        return False
    except subprocess.TimeoutExpired:
        print_error("Docker command timed out")
        return False
    
    # Check if Docker daemon is running
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("Docker daemon is running")
            return True
        else:
            print_error("Docker daemon is NOT running")
            print_info("Start Docker Desktop and try again")
            return False
    except subprocess.TimeoutExpired:
        print_error("Docker daemon check timed out")
        return False


def check_docker_services() -> bool:
    """Check if Docker services are running."""
    print_header("Checking Docker Services")
    
    try:
        result = subprocess.run(
            ["docker-compose", "ps"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "interview_platform_db" in result.stdout:
            if "Up" in result.stdout:
                print_success("PostgreSQL container is running")
                return True
            else:
                print_warning("PostgreSQL container exists but is not running")
                print_info("Start services with: docker-compose up -d")
                return False
        else:
            print_warning("PostgreSQL container not found")
            print_info("Start services with: docker-compose up -d")
            return False
            
    except FileNotFoundError:
        print_error("docker-compose is NOT installed")
        print_info("Install Docker Compose: https://docs.docker.com/compose/install/")
        return False
    except subprocess.TimeoutExpired:
        print_error("docker-compose command timed out")
        return False


def check_database_connection() -> bool:
    """Check if database is accessible."""
    print_header("Checking Database Connection")
    
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        
        db_password = os.getenv("DB_PASSWORD")
        if not db_password:
            print_error("DB_PASSWORD not set in .env")
            return False
        
        # Try to connect to database
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="interview_platform",
                user="interview_user",
                password=db_password,
                connect_timeout=5
            )
            
            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            cursor.close()
            conn.close()
            
            print_success("Database connection successful")
            return True
            
        except psycopg2.OperationalError as e:
            print_error("Cannot connect to database")
            print_info(f"Error: {str(e)}")
            print_info("\nPossible solutions:")
            print_info("  1. Start Docker services: docker-compose up -d")
            print_info("  2. Wait 30 seconds for PostgreSQL to initialize")
            print_info("  3. Check DB_PASSWORD in .env matches docker-compose.yml")
            return False
            
    except ImportError:
        print_error("psycopg2 package not installed")
        print_info("Install with: pip install psycopg2-binary")
        return False


def check_api_keys() -> bool:
    """Validate API keys by making test requests."""
    print_header("Validating API Keys")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    all_valid = True
    
    # Check OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.startswith("sk-"):
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            
            # Make a minimal test request
            response = client.models.list()
            print_success("OpenAI API key is valid")
            
        except Exception as e:
            print_error("OpenAI API key is INVALID")
            print_info(f"Error: {str(e)}")
            print_info("Get a valid key at: https://platform.openai.com/api-keys")
            all_valid = False
    else:
        print_error("OpenAI API key is missing or invalid format")
        print_info("Key should start with 'sk-'")
        all_valid = False
    
    # Check Anthropic API key (optional)
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and anthropic_key.startswith("sk-ant-"):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            
            # Make a minimal test request
            # Note: This might incur a small cost
            print_warning("Anthropic API key format is valid (not tested to avoid costs)")
            
        except Exception as e:
            print_warning("Anthropic API key validation failed")
            print_info(f"Error: {str(e)}")
    else:
        print_warning("Anthropic API key not set (optional)")
    
    return all_valid


def check_directories() -> bool:
    """Check if required directories exist and are writable."""
    print_header("Checking Directories")
    
    required_dirs = [
        "data",
        "data/sessions",
        "logs"
    ]
    
    all_ok = True
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        
        if path.exists():
            if os.access(path, os.W_OK):
                print_success(f"{dir_path}/ exists and is writable")
            else:
                print_error(f"{dir_path}/ exists but is NOT writable")
                all_ok = False
        else:
            try:
                path.mkdir(parents=True, exist_ok=True)
                print_success(f"{dir_path}/ created")
            except Exception as e:
                print_error(f"Cannot create {dir_path}/")
                print_info(f"Error: {str(e)}")
                all_ok = False
    
    return all_ok


def print_summary(checks: List[Tuple[str, bool]]) -> None:
    """Print validation summary."""
    print_header("Validation Summary")
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for check_name, result in checks:
        if result:
            print_success(f"{check_name}: PASSED")
        else:
            print_error(f"{check_name}: FAILED")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} checks passed{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All checks passed! You're ready to start the platform.{Colors.END}\n")
        print_info("To start the platform, run:")
        print_info("  ./startup.sh")
        print_info("\nOr manually:")
        print_info("  docker-compose up -d")
        print_info("  streamlit run src/main.py")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some checks failed. Please fix the issues above.{Colors.END}\n")
        print_info("Common solutions:")
        print_info("  1. Install missing packages: pip install -r requirements.txt")
        print_info("  2. Configure .env file: cp config/.env.template .env")
        print_info("  3. Start Docker Desktop")
        print_info("  4. Start services: docker-compose up -d")
        return False


def main():
    """Run all validation checks."""
    print(f"\n{Colors.BOLD}AI Mock Interview Platform - Setup Validation{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}\n")
    
    checks = [
        ("Python Version", check_python_version()),
        ("Required Packages", check_required_packages()),
        ("Environment Variables", check_environment_variables()),
        ("Docker Installation", check_docker_installed()),
        ("Docker Services", check_docker_services()),
        ("Database Connection", check_database_connection()),
        ("API Keys", check_api_keys()),
        ("Directories", check_directories())
    ]
    
    success = print_summary(checks)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
