"""
Test FileSystem Manager
Validates file operations and git integration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.integrations.filesystem_manager import FileSystemManager
import os

def test_filesystem_manager():
    """Test filesystem manager operations"""
    
    print("🧪 Testing FileSystem Manager")
    print("=" * 60)
    
    # Initialize
    print("\n1. Initializing FileSystemManager...")
    fs = FileSystemManager()
    print(f"   ✅ Project root: {fs.project_root}")
    print(f"   ✅ Data root: {fs.data_root}")
    
    # Test list directory
    print("\n2. Testing list_directory('.')...")
    result = fs.list_directory(".")
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
    else:
        print(f"   ✅ Path: {result['path']}")
        print(f"   ✅ Files: {len(result['files'])}")
        print(f"   ✅ Directories: {len(result['directories'])}")
        print(f"   📁 Sample dirs: {result['directories'][:5]}")
    
    # Test read file
    print("\n3. Testing read_file('README.md')...")
    result = fs.read_file("README.md")
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
    else:
        print(f"   ✅ Size: {result['size']} bytes")
        print(f"   ✅ Lines: {result['lines']}")
        print(f"   ✅ First line: {result['content'].split(chr(10))[0]}")
    
    # Test search files
    print("\n4. Testing search_files('*.py', path='app')...")
    result = fs.search_files("*.py", path="app")
    print(f"   ✅ Found {len(result)} Python files")
    print(f"   📄 Sample: {result[:3]}")
    
    # Test git status
    print("\n5. Testing git_status()...")
    result = fs.git_status()
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
    else:
        print(f"   ✅ Branch: {result['branch']}")
        print(f"   ✅ Modified: {len(result['modified'])}")
        print(f"   ✅ Untracked: {len(result['untracked'])}")
        print(f"   ✅ Staged: {len(result['staged'])}")
    
    # Test write file (to data directory)
    print("\n6. Testing write_file (to ~/Documents/d8_data/test.txt)...")
    test_content = f"Test file created at {Path.home() / 'Documents' / 'd8_data'}\n"
    result = fs.write_file(
        "~/Documents/d8_data/test.txt",
        test_content,
        create_backup=False
    )
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
    else:
        print(f"   ✅ Wrote {result['bytes_written']} bytes")
        print(f"   ✅ Path: {result['path']}")
    
    # Verify write
    print("\n7. Verifying write...")
    result = fs.read_file("~/Documents/d8_data/test.txt")
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
    else:
        print(f"   ✅ Content: {result['content'].strip()}")
    
    # Test path validation (should fail for unauthorized path)
    print("\n8. Testing path validation (should reject C:/Windows)...")
    try:
        result = fs.list_directory("C:/Windows")
        if "error" in result:
            print(f"   ✅ Correctly rejected: {result['error']}")
        else:
            print(f"   ❌ SECURITY ISSUE: Allowed unauthorized path!")
    except ValueError as e:
        print(f"   ✅ Correctly rejected: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed")
    
    return True

if __name__ == "__main__":
    try:
        success = test_filesystem_manager()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
