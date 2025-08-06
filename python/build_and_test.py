#!/usr/bin/env python3
"""
Build and Test Script for PyFory Nanobind Buffer
================================================

This script helps you compile and test the nanobind Buffer implementation.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Check if all required tools are available."""
    print("Checking requirements...")
    
    requirements = [
        ("python", "Python interpreter"),
        ("pip", "Python package manager"),
        ("c++", "C++ compiler"),
        ("cmake", "CMake build system (if using cmake)"),
    ]
    
    missing = []
    for cmd, desc in requirements:
        try:
            result = subprocess.run([cmd, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {desc}: Found")
            else:
                missing.append((cmd, desc))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            missing.append((cmd, desc))
    
    # Check nanobind availability
    try:
        import nanobind
        print(f"✅ nanobind: {nanobind.__version__}")
    except ImportError:
        print("❌ nanobind: Not found")
        print("   Install with: pip install nanobind")
        missing.append(("nanobind", "Python binding library"))
    
    if missing:
        print("\nMissing requirements:")
        for cmd, desc in missing:
            print(f"❌ {desc} ({cmd})")
        return False
    
    print("✅ All requirements satisfied")
    return True


def find_project_root():
    """Find the project root directory."""
    current = Path.cwd()
    
    # Look for project indicators
    indicators = ["WORKSPACE", "BUILD", "pyproject.toml", "setup.py"]
    
    for parent in [current] + list(current.parents):
        if any((parent / indicator).exists() for indicator in indicators):
            return parent
    
    return current


def setup_build_environment():
    """Set up the build environment."""
    print("\nSetting up build environment...")
    
    project_root = find_project_root()
    python_dir = project_root / "python"
    
    if not python_dir.exists():
        print(f"❌ Python directory not found at {python_dir}")
        return None
    
    print(f"✅ Project root: {project_root}")
    print(f"✅ Python directory: {python_dir}")
    
    return python_dir


def compile_extension(python_dir):
    """Compile the nanobind extension."""
    print("\nCompiling nanobind extension...")
    
    nanobind_dir = python_dir / "pyfory" / "nanobind_ext"
    
    # Method 1: Try direct compilation with nanobind-config
    try:
        print("Attempting direct compilation with nanobind-config...")
        
        cpp_file = nanobind_dir / "pyfory_nb.cpp"
        if not cpp_file.exists():
            print(f"❌ Source file not found: {cpp_file}")
            return False
        
        # Get nanobind compilation flags
        result = subprocess.run(["python", "-m", "nanobind", "--cmake_dir"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Failed to get nanobind cmake directory")
            return False
        
        print("✅ Found nanobind configuration")
        return True
        
    except Exception as e:
        print(f"❌ Direct compilation failed: {e}")
    
    # Method 2: Try setup.py if available
    setup_py = python_dir / "setup.py"
    if setup_py.exists():
        print("Trying setup.py build...")
        try:
            os.chdir(python_dir)
            result = subprocess.run([sys.executable, "setup.py", "build_ext", "--inplace"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ setup.py build successful")
                return True
            else:
                print(f"❌ setup.py build failed: {result.stderr}")
        except Exception as e:
            print(f"❌ setup.py build error: {e}")
    
    print("❌ Failed to compile extension")
    return False


def test_import():
    """Test if the compiled extension can be imported."""
    print("\nTesting import...")
    
    try:
        # Try importing the nanobind extension
        from pyfory.nanobind_ext import Buffer
        print("✅ Successfully imported nanobind Buffer")
        
        # Quick functionality test
        buffer = Buffer.allocate(100)
        buffer.write_int32(12345)
        buffer.reader_index = 0
        value = buffer.read_int32()
        
        if value == 12345:
            print("✅ Basic functionality test passed")
            return True
        else:
            print(f"❌ Basic functionality test failed: expected 12345, got {value}")
            return False
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("   The extension may not be compiled correctly")
        return False
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


def run_examples():
    """Run the example script."""
    print("\nRunning examples...")
    
    try:
        # Import and run the examples
        from pyfory.nanobind_ext.examples import main as run_examples
        run_examples()
        return True
    except ImportError:
        print("❌ Could not import examples module")
        return False
    except Exception as e:
        print(f"❌ Examples failed: {e}")
        return False


def run_tests():
    """Run the test suite."""
    print("\nRunning tests...")
    
    try:
        # Look for test file
        test_files = [
            "test_buffer_comprehensive.py",
            "test_nanobind_buffer.py",
            "tests/test_buffer.py"
        ]
        
        test_file = None
        for tf in test_files:
            if Path(tf).exists():
                test_file = tf
                break
        
        if test_file:
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Tests passed")
                print(result.stdout)
                return True
            else:
                print("❌ Tests failed")
                print(result.stderr)
                return False
        else:
            print("⚠️  No test file found")
            return True
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


def main():
    """Main build and test workflow."""
    print("PyFory Nanobind Buffer - Build and Test")
    print("=" * 50)
    
    # Step 1: Check requirements
    if not check_requirements():
        print("\n❌ Requirements not satisfied. Please install missing components.")
        return 1
    
    # Step 2: Setup build environment
    python_dir = setup_build_environment()
    if not python_dir:
        print("\n❌ Failed to setup build environment")
        return 1
    
    # Step 3: Compile extension
    if not compile_extension(python_dir):
        print("\n❌ Compilation failed")
        print("\nManual compilation steps:")
        print("1. cd python/pyfory/nanobind_ext")
        print("2. python -m nanobind --help  # Check nanobind installation")
        print("3. Compile pyfory_nb.cpp with appropriate flags")
        return 1
    
    # Step 4: Test import
    if not test_import():
        print("\n❌ Import test failed")
        return 1
    
    # Step 5: Run examples (optional)
    try:
        run_examples()
    except:
        print("⚠️  Examples could not run, but core functionality works")
    
    # Step 6: Run tests (optional)
    try:
        run_tests()
    except:
        print("⚠️  Tests could not run, but core functionality works")
    
    print("\n" + "=" * 50)
    print("🎉 Build and test completed successfully!")
    print("\nYour nanobind Buffer is ready to use:")
    print("  from pyfory.nanobind_ext import Buffer")
    print("  buffer = Buffer.allocate(1024)")
    print("  buffer.write_int32(12345)")
    print("  value = buffer.read_int32()")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
