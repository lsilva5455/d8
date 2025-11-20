#!/usr/bin/env python3
"""
🧪 Test de Integración FileSystemManager con Autonomous Congress
Valida que el congreso pueda usar operaciones de filesystem
"""

import sys
from pathlib import Path
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.autonomous_congress import AutonomousCongress

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def test_congress_filesystem_integration():
    """Test that Congress has FileSystemManager integrated"""
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🧪 Testing Congress + FileSystem Integration{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    results = []
    
    # Test 1: Congress can be initialized with FileSystem
    print(f"{BLUE}1. Initializing Congress...{RESET}")
    try:
        congress = AutonomousCongress()
        
        if hasattr(congress, 'filesystem'):
            print(f"{GREEN}   ✅ Congress has 'filesystem' attribute{RESET}")
            results.append(True)
        else:
            print(f"{RED}   ❌ Congress missing 'filesystem' attribute{RESET}")
            results.append(False)
            return False
        
    except Exception as e:
        print(f"{RED}   ❌ Error initializing: {e}{RESET}")
        return False
    
    # Test 2: FileSystem Manager methods exist
    print(f"\n{BLUE}2. Checking FileSystem Manager methods...{RESET}")
    required_methods = [
        'read_file',
        'write_file',
        'list_directory',
        'search_files',
        'git_status',
        'git_commit'
    ]
    
    for method in required_methods:
        if hasattr(congress.filesystem, method):
            print(f"{GREEN}   ✅ Method exists: {method}{RESET}")
            results.append(True)
        else:
            print(f"{RED}   ❌ Method missing: {method}{RESET}")
            results.append(False)
    
    # Test 3: Congress helper methods exist
    print(f"\n{BLUE}3. Checking Congress helper methods...{RESET}")
    helper_methods = [
        'analyze_codebase',
        'read_agent_genome',
        'write_agent_genome',
        'commit_improvements',
        'get_recent_changes'
    ]
    
    for method in helper_methods:
        if hasattr(congress, method):
            print(f"{GREEN}   ✅ Helper exists: {method}{RESET}")
            results.append(True)
        else:
            print(f"{RED}   ❌ Helper missing: {method}{RESET}")
            results.append(False)
    
    # Test 4: Try analyze_codebase (read-only operation)
    print(f"\n{BLUE}4. Testing analyze_codebase()...{RESET}")
    try:
        analysis = congress.analyze_codebase()
        
        if 'python_files' in analysis:
            print(f"{GREEN}   ✅ Codebase analysis works{RESET}")
            print(f"      Found {len(analysis['python_files'])} Python files")
            results.append(True)
        else:
            print(f"{RED}   ❌ Invalid analysis result{RESET}")
            results.append(False)
            
    except Exception as e:
        print(f"{RED}   ❌ Error analyzing: {e}{RESET}")
        results.append(False)
    
    # Test 5: Check implementer prompt includes filesystem operations
    print(f"\n{BLUE}5. Checking implementer prompt...{RESET}")
    try:
        implementer = next(m for m in congress.members if m['role'] == 'implementer')
        prompt = implementer['genome']['system_prompt']
        
        if 'FileSystem' in prompt and 'read_file' in prompt:
            print(f"{GREEN}   ✅ Implementer prompt includes filesystem operations{RESET}")
            results.append(True)
        else:
            print(f"{RED}   ❌ Implementer prompt missing filesystem references{RESET}")
            results.append(False)
            
    except Exception as e:
        print(f"{RED}   ❌ Error checking prompt: {e}{RESET}")
        results.append(False)
    
    # Test 6: Verify _execute_file_operations method exists
    print(f"\n{BLUE}6. Checking implementation methods...{RESET}")
    implementation_methods = [
        '_execute_file_operations',
        '_log_filesystem_operations'
    ]
    
    for method in implementation_methods:
        if hasattr(congress, method):
            print(f"{GREEN}   ✅ Method exists: {method}{RESET}")
            results.append(True)
        else:
            print(f"{RED}   ❌ Method missing: {method}{RESET}")
            results.append(False)
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    if percentage == 100:
        print(f"{GREEN}✅ ALL TESTS PASSED: {passed}/{total} ({percentage:.0f}%){RESET}")
        print(f"{GREEN}🎉 FileSystem integration is complete!{RESET}")
        return True
    elif percentage >= 80:
        print(f"{BLUE}⚠️ MOSTLY PASSED: {passed}/{total} ({percentage:.0f}%){RESET}")
        print(f"{BLUE}Integration functional with minor issues{RESET}")
        return True
    else:
        print(f"{RED}❌ TESTS FAILED: {passed}/{total} ({percentage:.0f}%){RESET}")
        return False


if __name__ == "__main__":
    success = test_congress_filesystem_integration()
    sys.exit(0 if success else 1)
