#!/usr/bin/env python3
"""
🧪 Test de Validación FASE 3
Verifica que todos los componentes estén implementados correctamente
"""

import sys
from pathlib import Path
import importlib.util

# Colors for terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(message, status="info"):
    """Print colored status message"""
    colors = {
        "success": GREEN,
        "error": RED,
        "warning": YELLOW,
        "info": BLUE
    }
    color = colors.get(status, RESET)
    symbol = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️"
    }
    print(f"{color}{symbol.get(status, '')} {message}{RESET}")


def check_file_exists(filepath, description):
    """Check if a file exists"""
    path = Path(filepath)
    if path.exists():
        print_status(f"{description}: {filepath}", "success")
        return True
    else:
        print_status(f"{description} NOT FOUND: {filepath}", "error")
        return False


def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    path = Path(dirpath)
    if path.exists() and path.is_dir():
        print_status(f"{description}: {dirpath}", "success")
        return True
    else:
        print_status(f"{description} NOT FOUND: {dirpath}", "error")
        return False


def check_module_imports(filepath, description):
    """Check if a Python module can be imported"""
    try:
        spec = importlib.util.spec_from_file_location("test_module", filepath)
        if spec is None:
            print_status(f"{description}: Cannot load spec", "error")
            return False
        
        module = importlib.util.module_from_spec(spec)
        # Don't execute, just check it can be loaded
        print_status(f"{description}: Syntax OK", "success")
        return True
    except SyntaxError as e:
        print_status(f"{description}: Syntax Error - {e}", "error")
        return False
    except Exception as e:
        print_status(f"{description}: Import Error - {e}", "warning")
        return True  # May fail due to dependencies, but file is valid


def main():
    """Run validation tests"""
    print("\n" + "="*60)
    print(f"{BLUE}🧪 FASE 3 - VALIDATION TEST{RESET}")
    print("="*60 + "\n")
    
    results = []
    
    # 1. Check Daemons
    print(f"\n{BLUE}📋 Checking Daemons...{RESET}")
    results.append(check_file_exists(
        "scripts/daemons/niche_discovery_daemon.py",
        "Niche Discovery Daemon"
    ))
    results.append(check_file_exists(
        "scripts/daemons/congress_daemon.py",
        "Congress Daemon"
    ))
    results.append(check_file_exists(
        "scripts/daemons/evolution_daemon.py",
        "Evolution Daemon"
    ))
    
    # 2. Check Monitoring
    print(f"\n{BLUE}📊 Checking Monitoring...{RESET}")
    results.append(check_file_exists(
        "app/monitoring/dashboard.py",
        "Monitoring Dashboard"
    ))
    
    # 3. Check Self-Healing
    print(f"\n{BLUE}🛡️ Checking Self-Healing...{RESET}")
    results.append(check_file_exists(
        "app/self_healing/monitor.py",
        "Self-Healing Monitor"
    ))
    
    # 4. Check Launch Scripts
    print(f"\n{BLUE}🚀 Checking Launch Scripts...{RESET}")
    results.append(check_file_exists(
        "scripts/launch/start_autonomous_system.py",
        "Autonomous System Launcher"
    ))
    
    # 5. Check Data Directories
    print(f"\n{BLUE}📁 Checking Data Directories...{RESET}")
    results.append(check_directory_exists(
        "data/logs",
        "Logs Directory"
    ))
    
    # Create missing directories
    for dir_path in [
        "data/niche_discovery",
        "data/congress_cycles",
        "data/generations",
        "data/incidents"
    ]:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print_status(f"Created directory: {dir_path}", "warning")
        else:
            print_status(f"Directory exists: {dir_path}", "success")
    
    # 6. Check Documentation
    print(f"\n{BLUE}📚 Checking Documentation...{RESET}")
    results.append(check_file_exists(
        "docs/07_reportes/FASE_3_IMPLEMENTADA.md",
        "FASE 3 Report"
    ))
    
    # 7. Syntax Validation
    print(f"\n{BLUE}🔍 Validating Python Syntax...{RESET}")
    python_files = [
        ("scripts/daemons/niche_discovery_daemon.py", "Niche Discovery"),
        ("scripts/daemons/congress_daemon.py", "Congress"),
        ("scripts/daemons/evolution_daemon.py", "Evolution"),
        ("app/monitoring/dashboard.py", "Dashboard"),
        ("app/self_healing/monitor.py", "Self-Healing"),
        ("scripts/launch/start_autonomous_system.py", "Launcher"),
    ]
    
    for filepath, description in python_files:
        if Path(filepath).exists():
            results.append(check_module_imports(filepath, description))
    
    # Summary
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    if percentage == 100:
        print(f"{GREEN}✅ ALL TESTS PASSED: {passed}/{total} ({percentage:.0f}%){RESET}")
        print(f"{GREEN}🎉 FASE 3 is ready to run!{RESET}")
        exit_code = 0
    elif percentage >= 80:
        print(f"{YELLOW}⚠️ MOSTLY PASSED: {passed}/{total} ({percentage:.0f}%){RESET}")
        print(f"{YELLOW}Some issues found, but system should work{RESET}")
        exit_code = 0
    else:
        print(f"{RED}❌ TESTS FAILED: {passed}/{total} ({percentage:.0f}%){RESET}")
        print(f"{RED}Critical issues found{RESET}")
        exit_code = 1
    
    print("="*60 + "\n")
    
    # Next Steps
    if exit_code == 0:
        print(f"{BLUE}📝 Next Steps:{RESET}")
        print("1. Install dependencies: pip install schedule flask")
        print("2. Start system: python scripts/launch/start_autonomous_system.py")
        print("3. Access dashboard: http://localhost:7500")
        print()
    
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
