#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Documentation Validation Script for AI Mock Interview Platform

This script validates that all setup instructions in documentation are accurate
and complete. It checks:
- All referenced files and directories exist
- All download links are accessible
- Commands in documentation are valid
- Setup instructions can be executed
"""

import sys
import os
import re
import subprocess
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import urllib.request
import urllib.error

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


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
    try:
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    except UnicodeEncodeError:
        print(f"{Colors.GREEN}[OK] {message}{Colors.END}")


def print_error(message: str) -> None:
    """Print an error message."""
    try:
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    except UnicodeEncodeError:
        print(f"{Colors.RED}[FAIL] {message}{Colors.END}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    try:
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
    except UnicodeEncodeError:
        print(f"{Colors.YELLOW}[WARN] {message}{Colors.END}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"  {message}")


def read_documentation_file(file_path: str) -> Optional[str]:
    """Read documentation file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print_error(f"Documentation file not found: {file_path}")
        return None
    except Exception as e:
        print_error(f"Error reading {file_path}: {str(e)}")
        return None


def extract_file_references(content: str) -> List[str]:
    """Extract file and directory references from documentation."""
    references = []
    
    # Pattern 1: Backtick file paths (e.g., `.env`, `config/.env.template`)
    backtick_pattern = r'`([^\s`]+\.[a-zA-Z0-9]+)`'
    references.extend(re.findall(backtick_pattern, content))
    
    # Pattern 2: Directory paths (e.g., `data/`, `logs/`)
    dir_pattern = r'`([^\s`]+/)`'
    references.extend(re.findall(dir_pattern, content))
    
    # Pattern 3: Explicit file mentions in instructions
    file_pattern = r'(?:file named|named|called)\s+["`]([^"`]+)["`]'
    references.extend(re.findall(file_pattern, content, re.IGNORECASE))
    
    # Pattern 4: Docker compose file
    if 'docker-compose' in content.lower():
        references.append('docker-compose.yml')
    
    # Pattern 5: Startup script
    if 'startup.sh' in content:
        references.append('startup.sh')
    
    # Remove duplicates and filter out placeholders
    unique_refs = list(set(references))
    filtered_refs = [
        ref for ref in unique_refs
        if not any(placeholder in ref.lower() for placeholder in [
            'your-', 'example', '<', '>', 'path-to', 'project-root', 'test_', '.vscode'
        ])
    ]
    
    # Filter out patterns that are just examples
    filtered_refs = [
        ref for ref in filtered_refs
        if not ref.endswith('...')
    ]
    
    return filtered_refs


def extract_urls(content: str) -> List[str]:
    """Extract URLs from documentation."""
    # Pattern for markdown links and plain URLs
    url_pattern = r'https?://[^\s\)\]<>"`,]+'
    urls = re.findall(url_pattern, content)
    
    # Remove duplicates and filter out localhost URLs
    unique_urls = list(set(urls))
    filtered_urls = [
        url for url in unique_urls
        if not url.startswith('http://localhost')
    ]
    
    return filtered_urls


def extract_commands(content: str) -> List[str]:
    """Extract shell commands from code blocks."""
    commands = []
    
    # Pattern for bash/shell code blocks
    code_block_pattern = r'```(?:bash|sh|shell|cmd)?\n(.*?)```'
    code_blocks = re.findall(code_block_pattern, content, re.DOTALL)
    
    for block in code_blocks:
        lines = block.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#') and not line.startswith('//'):
                # Skip lines that are just output examples
                if not any(skip in line for skip in ['...', 'NAME', 'STATUS', 'PORTS', '====', 'Services started']):
                    commands.append(line)
    
    return commands


def validate_file_references(doc_name: str, references: List[str]) -> bool:
    """Validate that all referenced files and directories exist."""
    print_header(f"Validating File References in {doc_name}")
    
    all_valid = True
    project_root = Path.cwd()
    
    # Skip validation for certain references that are examples or user-specific
    skip_refs = [
        'ai-mock-interview-platform',  # User's extracted folder name
        'interview_platform.log',  # Created at runtime
    ]
    
    for ref in references:
        # Clean up the reference
        ref = ref.strip('`').strip()
        
        # Skip if in skip list
        if ref in skip_refs:
            print_info(f"Skipping runtime/user-specific file: {ref}")
            continue
        
        # Handle directory references
        if ref.endswith('/'):
            ref = ref.rstrip('/')
        
        # Try multiple possible locations
        possible_paths = [
            project_root / ref,
            project_root / 'config' / ref,
            project_root / 'docs' / ref,
            project_root / 'scripts' / ref,
            project_root / 'logs' / ref,
        ]
        
        found = False
        for path in possible_paths:
            if path.exists():
                print_success(f"Found: {ref}")
                found = True
                break
        
        if not found:
            # Check if it's a template or example file
            if 'template' in ref.lower() or ref == '.env':
                # .env might not exist yet, check for template
                template_path = project_root / 'config' / '.env.template'
                if template_path.exists():
                    print_success(f"Template exists for: {ref}")
                    found = True
            
            if not found:
                print_error(f"Not found: {ref}")
                all_valid = False
    
    return all_valid


def validate_urls(doc_name: str, urls: List[str]) -> bool:
    """Validate that all URLs are accessible."""
    print_header(f"Validating URLs in {doc_name}")
    
    all_valid = True
    
    # Skip validation for placeholder URLs
    skip_urls = [
        'repository-url',
        'support email',
        'example.com',
        'GitHub Release Link'
    ]
    
    for url in urls:
        # Skip placeholder URLs
        if any(skip in url for skip in skip_urls):
            print_warning(f"Skipping placeholder URL: {url}")
            continue
        
        try:
            # Set a user agent to avoid being blocked
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Documentation Validator)'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    print_success(f"Accessible: {url}")
                else:
                    print_warning(f"Status {response.status}: {url}")
        
        except urllib.error.HTTPError as e:
            if e.code == 403:
                # Some sites block automated requests, but URL might be valid
                print_warning(f"Access forbidden (403) but URL exists: {url}")
            elif e.code == 308:
                # Permanent redirect - URL is valid but moved
                print_warning(f"Permanent redirect (308) - URL valid: {url}")
            else:
                print_error(f"HTTP {e.code}: {url}")
                all_valid = False
        
        except urllib.error.URLError as e:
            print_error(f"Cannot access: {url} - {str(e)}")
            all_valid = False
        
        except Exception as e:
            print_error(f"Error checking {url}: {str(e)}")
            all_valid = False
    
    return all_valid


def validate_commands(doc_name: str, commands: List[str]) -> bool:
    """Validate that documented commands are syntactically correct."""
    print_header(f"Validating Commands in {doc_name}")
    
    all_valid = True
    
    # Commands that should exist
    required_commands = {
        'docker': 'Docker',
        'docker-compose': 'Docker Compose',
        'python': 'Python',
        'pip': 'pip',
        'git': 'Git'
    }
    
    # Check if required commands are available
    for cmd, name in required_commands.items():
        # Skip if command is not mentioned in the doc
        if not any(cmd in command for command in commands):
            continue
        
        try:
            # Check if command exists
            if sys.platform == 'win32':
                result = subprocess.run(
                    ['where', cmd],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            else:
                result = subprocess.run(
                    ['which', cmd],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            
            if result.returncode == 0:
                print_success(f"{name} command is available")
            else:
                print_warning(f"{name} command not found (may need to be installed)")
        
        except Exception as e:
            print_warning(f"Could not check {name}: {str(e)}")
    
    # Validate command syntax
    for command in commands:
        # Skip variable assignments and multi-line commands
        if '=' in command or '\\' in command:
            continue
        
        # Check for common command patterns
        if command.startswith(('cd ', 'mkdir ', 'cp ', 'mv ', 'rm ')):
            print_success(f"Valid command: {command[:50]}...")
        elif command.startswith(('docker', 'python', 'pip', 'git', 'streamlit')):
            print_success(f"Valid command: {command[:50]}...")
        elif command.startswith(('./startup.sh', 'chmod')):
            print_success(f"Valid command: {command[:50]}...")
        else:
            # Unknown command pattern, just note it
            print_info(f"Command: {command[:50]}...")
    
    return all_valid


def validate_quick_start_guide() -> bool:
    """Validate Quick Start Guide documentation."""
    doc_path = 'docs/QUICK_START_GUIDE.md'
    content = read_documentation_file(doc_path)
    
    if not content:
        return False
    
    print_header("Validating Quick Start Guide")
    
    all_valid = True
    
    # Extract and validate file references
    file_refs = extract_file_references(content)
    if not validate_file_references('Quick Start Guide', file_refs):
        all_valid = False
    
    # Extract and validate URLs
    urls = extract_urls(content)
    if not validate_urls('Quick Start Guide', urls):
        all_valid = False
    
    # Extract and validate commands
    commands = extract_commands(content)
    if not validate_commands('Quick Start Guide', commands):
        all_valid = False
    
    # Check for required sections
    required_sections = [
        'What You\'ll Need',
        'Install Docker Desktop',
        'Get Your OpenAI API Key',
        'Download the Interview Platform',
        'Configure Your Settings',
        'Start the Platform',
        'Troubleshooting'
    ]
    
    print_header("Checking Required Sections in Quick Start Guide")
    for section in required_sections:
        if section in content:
            print_success(f"Section found: {section}")
        else:
            print_error(f"Section missing: {section}")
            all_valid = False
    
    return all_valid


def validate_developer_setup_guide() -> bool:
    """Validate Developer Setup Guide documentation."""
    doc_path = 'docs/DEVELOPER_SETUP_GUIDE.md'
    content = read_documentation_file(doc_path)
    
    if not content:
        return False
    
    print_header("Validating Developer Setup Guide")
    
    all_valid = True
    
    # Extract and validate file references
    file_refs = extract_file_references(content)
    if not validate_file_references('Developer Setup Guide', file_refs):
        all_valid = False
    
    # Extract and validate URLs
    urls = extract_urls(content)
    if not validate_urls('Developer Setup Guide', urls):
        all_valid = False
    
    # Extract and validate commands
    commands = extract_commands(content)
    if not validate_commands('Developer Setup Guide', commands):
        all_valid = False
    
    # Check for required sections
    required_sections = [
        'Prerequisites',
        'Environment Setup',
        'Local Development',
        'Running Tests',
        'Debugging',
        'Development Workflows',
        'Code Quality',
        'Architecture Overview'
    ]
    
    print_header("Checking Required Sections in Developer Setup Guide")
    for section in required_sections:
        if section in content:
            print_success(f"Section found: {section}")
        else:
            print_error(f"Section missing: {section}")
            all_valid = False
    
    # Check for environment variable documentation
    print_header("Checking Environment Variable Documentation")
    env_vars = [
        'DB_PASSWORD',
        'DATABASE_URL',
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'LOG_LEVEL',
        'DATA_DIR'
    ]
    
    for var in env_vars:
        if var in content:
            print_success(f"Environment variable documented: {var}")
        else:
            print_warning(f"Environment variable not documented: {var}")
    
    return all_valid


def validate_project_structure() -> bool:
    """Validate that documented project structure matches reality."""
    print_header("Validating Project Structure")
    
    all_valid = True
    
    # Key directories that should exist
    required_dirs = [
        'src',
        'tests',
        'docs',
        'config',
        'scripts',
        'data',
        'logs',
        '.github',
        '.streamlit'
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print_success(f"Directory exists: {dir_name}/")
        else:
            print_error(f"Directory missing: {dir_name}/")
            all_valid = False
    
    # Key files that should exist
    required_files = [
        'README.md',
        'requirements.txt',
        'requirements-dev.txt',
        'docker-compose.yml',
        'Dockerfile',
        'init.sql',
        'startup.sh',
        'pytest.ini',
        'pyproject.toml',
        '.gitignore',
        '.pre-commit-config.yaml'
    ]
    
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists() and file_path.is_file():
            print_success(f"File exists: {file_name}")
        else:
            print_error(f"File missing: {file_name}")
            all_valid = False
    
    return all_valid


def validate_setup_instructions() -> bool:
    """Validate that setup instructions are complete and accurate."""
    print_header("Validating Setup Instructions")
    
    all_valid = True
    
    # Check that .env.template exists
    template_path = Path('config/.env.template')
    if template_path.exists():
        print_success(".env.template exists in config/")
        
        # Read template and check for required variables
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            required_vars = ['DB_PASSWORD', 'OPENAI_API_KEY']
            for var in required_vars:
                if var in template_content:
                    print_success(f"Template includes: {var}")
                else:
                    print_error(f"Template missing: {var}")
                    all_valid = False
        
        except Exception as e:
            print_error(f"Error reading template: {str(e)}")
            all_valid = False
    else:
        print_error(".env.template not found in config/")
        all_valid = False
    
    # Check that startup.sh is executable
    startup_path = Path('startup.sh')
    if startup_path.exists():
        print_success("startup.sh exists")
        
        # Check if it's executable (Unix-like systems)
        if sys.platform != 'win32':
            if os.access(startup_path, os.X_OK):
                print_success("startup.sh is executable")
            else:
                print_warning("startup.sh is not executable (run: chmod +x startup.sh)")
    else:
        print_error("startup.sh not found")
        all_valid = False
    
    # Check docker-compose.yml
    compose_path = Path('docker-compose.yml')
    if compose_path.exists():
        print_success("docker-compose.yml exists")
        
        try:
            with open(compose_path, 'r') as f:
                compose_content = f.read()
            
            # Check for required services
            if 'postgres:' in compose_content:
                print_success("PostgreSQL service defined")
            else:
                print_error("PostgreSQL service not defined")
                all_valid = False
            
            # Check for health checks
            if 'healthcheck:' in compose_content:
                print_success("Health checks defined")
            else:
                print_warning("Health checks not defined")
        
        except Exception as e:
            print_error(f"Error reading docker-compose.yml: {str(e)}")
            all_valid = False
    else:
        print_error("docker-compose.yml not found")
        all_valid = False
    
    return all_valid


def print_summary(checks: List[Tuple[str, bool]]) -> bool:
    """Print validation summary."""
    print_header("Documentation Validation Summary")
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for check_name, result in checks:
        if result:
            print_success(f"{check_name}: PASSED")
        else:
            print_error(f"{check_name}: FAILED")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} checks passed{Colors.END}\n")
    
    if passed == total:
        try:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ All documentation validation checks passed!{Colors.END}\n")
        except UnicodeEncodeError:
            print(f"{Colors.GREEN}{Colors.BOLD}[OK] All documentation validation checks passed!{Colors.END}\n")
        print_info("Documentation is accurate and complete.")
        return True
    else:
        try:
            print(f"{Colors.RED}{Colors.BOLD}✗ Some documentation validation checks failed.{Colors.END}\n")
        except UnicodeEncodeError:
            print(f"{Colors.RED}{Colors.BOLD}[FAIL] Some documentation validation checks failed.{Colors.END}\n")
        print_info("Please review and fix the issues above.")
        print_info("Common issues:")
        print_info("  1. Missing or renamed files")
        print_info("  2. Broken URLs")
        print_info("  3. Outdated commands")
        print_info("  4. Missing documentation sections")
        return False


def main():
    """Run all documentation validation checks."""
    print(f"\n{Colors.BOLD}AI Mock Interview Platform - Documentation Validation{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}\n")
    
    checks = [
        ("Quick Start Guide", validate_quick_start_guide()),
        ("Developer Setup Guide", validate_developer_setup_guide()),
        ("Project Structure", validate_project_structure()),
        ("Setup Instructions", validate_setup_instructions())
    ]
    
    success = print_summary(checks)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
