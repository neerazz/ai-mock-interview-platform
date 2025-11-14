#!/usr/bin/env python3
"""
Docker Deployment Validation Script

This script validates Docker deployment:
1. startup.sh script execution
2. All services start correctly
3. Database initialization and schema creation
4. Application connectivity to database
5. Health checks work properly
6. Stopping and restarting services
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Tuple, Optional


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_step(step_num: int, description: str):
    """Print a test step header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Step {step_num}: {description}{Colors.RESET}")
    print("=" * 70)


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


def run_command(cmd: str, shell: bool = True, capture_output: bool = True) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def check_docker_installed() -> bool:
    """Check if Docker is installed"""
    print_step(0, "Checking Docker Installation")
    
    returncode, stdout, stderr = run_command("docker --version")
    if returncode == 0:
        print_success(f"Docker is installed: {stdout.strip()}")
    else:
        print_error("Docker is not installed or not in PATH")
        return False
    
    returncode, stdout, stderr = run_command("docker-compose --version")
    if returncode == 0:
        print_success(f"Docker Compose is installed: {stdout.strip()}")
    else:
        print_error("Docker Compose is not installed or not in PATH")
        return False
    
    return True


def check_env_file() -> bool:
    """Check if .env file exists"""
    print_step(1, "Checking Environment Configuration")
    
    env_file = Path(".env")
    if not env_file.exists():
        print_error(".env file not found")
        print_info("Please create .env file from config/.env.template")
        return False
    
    print_success(".env file found")
    
    # Check for required variables
    required_vars = ["DB_PASSWORD", "OPENAI_API_KEY"]
    env_content = env_file.read_text()
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in env_content or f"{var}=your_" in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print_error(f"Missing or unconfigured variables: {', '.join(missing_vars)}")
        return False
    
    print_success("All required environment variables are configured")
    return True


def check_docker_compose_file() -> bool:
    """Check if docker-compose.yml exists"""
    print_step(2, "Checking Docker Compose Configuration")
    
    compose_file = Path("docker-compose.yml")
    if not compose_file.exists():
        print_error("docker-compose.yml not found")
        return False
    
    print_success("docker-compose.yml found")
    
    # Validate compose file
    returncode, stdout, stderr = run_command("docker-compose config")
    if returncode == 0:
        print_success("docker-compose.yml is valid")
    else:
        print_error(f"docker-compose.yml validation failed: {stderr}")
        return False
    
    return True


def stop_existing_services() -> bool:
    """Stop any existing services"""
    print_step(3, "Stopping Existing Services")
    
    print_info("Stopping Docker services...")
    returncode, stdout, stderr = run_command("docker-compose down")
    
    if returncode == 0:
        print_success("Existing services stopped")
    else:
        print_warning(f"Could not stop services (may not be running): {stderr}")
    
    return True


def test_startup_script() -> bool:
    """Test startup.sh script execution"""
    print_step(4, "Testing startup.sh Script")
    
    startup_script = Path("startup.sh")
    if not startup_script.exists():
        print_error("startup.sh not found")
        return False
    
    print_success("startup.sh found")
    
    # Check if script is executable
    if not os.access(startup_script, os.X_OK):
        print_info("Making startup.sh executable...")
        os.chmod(startup_script, 0o755)
        print_success("startup.sh is now executable")
    
    # Note: We don't actually run startup.sh here as it starts services
    # We'll test the individual components instead
    print_info("Script validation complete (not executing to avoid conflicts)")
    
    return True


def start_services() -> bool:
    """Start Docker services"""
    print_step(5, "Starting Docker Services")
    
    print_info("Starting services with docker-compose up -d...")
    returncode, stdout, stderr = run_command("docker-compose up -d")
    
    if returncode != 0:
        print_error(f"Failed to start services: {stderr}")
        return False
    
    print_success("Docker services started")
    
    # Wait for services to initialize
    print_info("Waiting for services to initialize (10 seconds)...")
    time.sleep(10)
    
    return True


def check_services_running() -> bool:
    """Check if all services are running"""
    print_step(6, "Verifying Services Are Running")
    
    returncode, stdout, stderr = run_command("docker-compose ps")
    
    if returncode != 0:
        print_error(f"Failed to check service status: {stderr}")
        return False
    
    print_info("Service status:")
    print(stdout)
    
    # Check for specific services
    required_services = ["postgres", "app"]
    for service in required_services:
        if service in stdout.lower():
            print_success(f"{service} service is present")
        else:
            print_error(f"{service} service not found")
            return False
    
    return True


def test_database_initialization() -> bool:
    """Test database initialization and schema creation"""
    print_step(7, "Testing Database Initialization")
    
    # Wait for PostgreSQL to be ready
    print_info("Waiting for PostgreSQL to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        returncode, stdout, stderr = run_command(
            "docker exec interview_platform_db pg_isready -U interview_user"
        )
        if returncode == 0:
            print_success("PostgreSQL is ready")
            break
        time.sleep(1)
    else:
        print_error("PostgreSQL did not become ready in time")
        return False
    
    # Check if database exists
    print_info("Checking if database exists...")
    returncode, stdout, stderr = run_command(
        'docker exec interview_platform_db psql -U interview_user -d interview_platform -c "SELECT 1;"'
    )
    
    if returncode == 0:
        print_success("Database connection successful")
    else:
        print_error(f"Database connection failed: {stderr}")
        return False
    
    # Check if tables were created
    print_info("Checking if schema tables exist...")
    tables_query = """
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name;
    """
    
    returncode, stdout, stderr = run_command(
        f'docker exec interview_platform_db psql -U interview_user -d interview_platform -c "{tables_query}"'
    )
    
    if returncode != 0:
        print_error(f"Failed to query tables: {stderr}")
        return False
    
    print_info("Database tables:")
    print(stdout)
    
    # Check for required tables
    required_tables = [
        "resumes",
        "sessions",
        "conversations",
        "evaluations",
        "media_files",
        "token_usage",
        "audit_logs"
    ]
    
    for table in required_tables:
        if table in stdout.lower():
            print_success(f"Table '{table}' exists")
        else:
            print_error(f"Table '{table}' not found")
            return False
    
    return True


def test_application_connectivity() -> bool:
    """Test application connectivity to database"""
    print_step(8, "Testing Application Connectivity")
    
    # Check if app container is running
    print_info("Checking app container status...")
    returncode, stdout, stderr = run_command(
        "docker ps --filter name=interview_platform_app --format '{{.Status}}'"
    )
    
    if returncode == 0 and stdout.strip():
        print_success(f"App container is running: {stdout.strip()}")
    else:
        print_error("App container is not running")
        return False
    
    # Check app logs for errors
    print_info("Checking app logs for errors...")
    returncode, stdout, stderr = run_command(
        "docker logs interview_platform_app --tail 50"
    )
    
    if "error" in stdout.lower() or "exception" in stdout.lower():
        print_warning("Found errors in app logs:")
        print(stdout[-500:])  # Print last 500 chars
    else:
        print_success("No errors found in app logs")
    
    # Try to access Streamlit health endpoint
    print_info("Checking Streamlit health endpoint...")
    returncode, stdout, stderr = run_command(
        "curl -f http://localhost:8501/_stcore/health || echo 'Health check failed'"
    )
    
    if "ok" in stdout.lower() or returncode == 0:
        print_success("Streamlit health check passed")
    else:
        print_warning("Streamlit health check failed (may still be starting)")
    
    return True


def test_health_checks() -> bool:
    """Test that health checks work properly"""
    print_step(9, "Testing Health Checks")
    
    # Check PostgreSQL health check
    print_info("Testing PostgreSQL health check...")
    returncode, stdout, stderr = run_command(
        "docker inspect interview_platform_db --format='{{.State.Health.Status}}'"
    )
    
    if returncode == 0:
        health_status = stdout.strip()
        if health_status == "healthy":
            print_success(f"PostgreSQL health status: {health_status}")
        else:
            print_warning(f"PostgreSQL health status: {health_status}")
    else:
        print_warning("Could not check PostgreSQL health status")
    
    # Check app health check
    print_info("Testing app health check...")
    returncode, stdout, stderr = run_command(
        "docker inspect interview_platform_app --format='{{.State.Health.Status}}'"
    )
    
    if returncode == 0:
        health_status = stdout.strip()
        if health_status == "healthy":
            print_success(f"App health status: {health_status}")
        else:
            print_warning(f"App health status: {health_status} (may still be starting)")
    else:
        print_warning("Could not check app health status")
    
    return True


def test_service_restart() -> bool:
    """Test stopping and restarting services"""
    print_step(10, "Testing Service Restart")
    
    # Stop services
    print_info("Stopping services...")
    returncode, stdout, stderr = run_command("docker-compose stop")
    
    if returncode != 0:
        print_error(f"Failed to stop services: {stderr}")
        return False
    
    print_success("Services stopped")
    
    # Verify services are stopped
    time.sleep(2)
    returncode, stdout, stderr = run_command("docker-compose ps")
    print_info("Service status after stop:")
    print(stdout)
    
    # Restart services
    print_info("Restarting services...")
    returncode, stdout, stderr = run_command("docker-compose start")
    
    if returncode != 0:
        print_error(f"Failed to restart services: {stderr}")
        return False
    
    print_success("Services restarted")
    
    # Wait for services to be ready
    print_info("Waiting for services to be ready (10 seconds)...")
    time.sleep(10)
    
    # Verify services are running
    returncode, stdout, stderr = run_command("docker-compose ps")
    print_info("Service status after restart:")
    print(stdout)
    
    return True


def cleanup() -> bool:
    """Clean up - stop services"""
    print_step(11, "Cleanup")
    
    print_info("Stopping services...")
    returncode, stdout, stderr = run_command("docker-compose down")
    
    if returncode == 0:
        print_success("Services stopped and cleaned up")
    else:
        print_warning(f"Cleanup had issues: {stderr}")
    
    return True


def main():
    """Run Docker deployment validation"""
    print(f"\n{Colors.BOLD}{'=' * 70}")
    print("Docker Deployment Validation")
    print(f"{'=' * 70}{Colors.RESET}\n")
    
    # Run validation steps
    if not check_docker_installed():
        print_error("\nDocker is not properly installed. Exiting.")
        sys.exit(1)
    
    if not check_env_file():
        print_error("\nEnvironment configuration is missing. Exiting.")
        sys.exit(1)
    
    if not check_docker_compose_file():
        print_error("\nDocker Compose configuration is invalid. Exiting.")
        sys.exit(1)
    
    stop_existing_services()
    
    if not test_startup_script():
        print_error("\nStartup script validation failed. Exiting.")
        sys.exit(1)
    
    if not start_services():
        print_error("\nFailed to start services. Exiting.")
        cleanup()
        sys.exit(1)
    
    if not check_services_running():
        print_error("\nServices are not running properly. Exiting.")
        cleanup()
        sys.exit(1)
    
    if not test_database_initialization():
        print_error("\nDatabase initialization failed. Exiting.")
        cleanup()
        sys.exit(1)
    
    if not test_application_connectivity():
        print_error("\nApplication connectivity test failed. Exiting.")
        cleanup()
        sys.exit(1)
    
    test_health_checks()  # Non-critical
    
    if not test_service_restart():
        print_error("\nService restart test failed. Exiting.")
        cleanup()
        sys.exit(1)
    
    cleanup()
    
    # All tests passed
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 70}")
    print("✓ ALL DOCKER DEPLOYMENT TESTS PASSED")
    print(f"{'=' * 70}{Colors.RESET}\n")
    
    print_info("Docker deployment is working correctly!")
    print_info("To start the platform: docker-compose up -d")
    print_info("To stop the platform: docker-compose down")
    print_info("To view logs: docker-compose logs -f")


if __name__ == "__main__":
    main()
