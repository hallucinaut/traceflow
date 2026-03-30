"""
Integration Test: Simulate Debugging Workflow

This script tests the production-ready Traceflow daemon with:
- Error pattern recognition
- Fix generation
- History tracking
- Multi-language support
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from traceflow import (
    TraceflowDaemon,
    ErrorPatternRegistry,
    ParsedError,
    FixSuggestion,
    ErrorHistory
)


def test_error_patterns():
    """Test that error patterns are recognized correctly."""
    
    print("🧪 Testing error patterns...")
    
    registry = ErrorPatternRegistry()
    
    test_cases = [
        {
            "name": "ImportError",
            "error": "ImportError: No module named 'nonexistent'",
            "language": "python",
            "expected": "ImportError"
        },
        {
            "name": "FileNotFoundError",
            "error": "FileNotFoundError: No such file or directory: 'missing.txt'",
            "language": "python",
            "expected": "FileNotFoundError"
        },
        {
            "name": "NameError",
            "error": "NameError: name 'undefined_var' is not defined",
            "language": "python",
            "expected": "NameError"
        },
        {
            "name": "AttributeError",
            "error": "AttributeError: 'str' object has no attribute 'nonexistent'",
            "language": "python",
            "expected": "AttributeError"
        },
        {
            "name": "KeyError",
            "error": "KeyError: 'missing_key'",
            "language": "python",
            "expected": "KeyError"
        },
        {
            "name": "ReferenceError (JS)",
            "error": "ReferenceError: undefined_var is not defined",
            "language": "javascript",
            "expected": "ReferenceError"
        }
    ]
    
    passed = 0
    for test in test_cases:
        pattern = registry.find_matching_pattern(test["error"], test["language"])
        
        if pattern and pattern.name == test["expected"]:
            print(f"   ✓ {test['name']}: Correctly identified")
            passed += 1
        else:
            print(f"   ✗ {test['name']}: Expected {test['expected']}, got {pattern.name if pattern else 'None'}")
    
    return passed == len(test_cases)


def test_fix_generation():
    """Test that fixes are generated correctly."""
    
    print("\n🧪 Testing fix generation...")
    
    daemon = TraceflowDaemon()
    
    test_cases = [
        {
            "name": "KeyError fix",
            "error": "KeyError: 'missing_key'",
            "expected_fixes": 1
        },
        {
            "name": "ImportError fix",
            "error": "ImportError: No module named 'xyz'",
            "expected_fixes": 1
        }
    ]
    
    passed = 0
    for test in test_cases:
        pattern, suggestions = daemon.analyze_error(test["error"])
        
        if len(suggestions) >= test["expected_fixes"]:
            print(f"   ✓ {test['name']}: Generated {len(suggestions)} suggestions")
            for s in suggestions[:2]:
                print(f"      - {s.description} ({s.confidence:.0%} confidence)")
            passed += 1
        else:
            print(f"   ✗ {test['name']}: Expected {test['expected_fixes']} fixes, got {len(suggestions)}")
    
    return passed == len(test_cases)


def test_fix_application():
    """Test that fixes can be applied to files."""
    
    print("\n🧪 Testing fix application...")
    
    import tempfile
    import shutil
    
    test_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create a test file with a dictionary access
        test_file = test_dir / "test.py"
        test_file.write_text("""
data = {"key": "value"}
result = data['key']
""")
        
        # Create a KeyError fix suggestion
        suggestion = FixSuggestion(
            description="Use .get() with default",
            before_pattern=r"data\['key'\]",
            after_replacement=r"data.get('key', None)",
            confidence=0.8
        )
        
        # Apply the fix
        success = suggestion.apply_to_file(str(test_file))
        
        if success:
            content = test_file.read_text()
            if "data.get('key', None)" in content:
                print(f"   ✓ Fix applied successfully")
                print(f"      Before: data['key']")
                print(f"      After: data.get('key', None)")
                return True
            else:
                print(f"   ✗ Fix not applied correctly")
                return False
        else:
            print(f"   ✗ Fix application failed")
            return False
            
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_error_history():
    """Test that errors are logged to history."""
    
    print("\n🧪 Testing error history...")
    
    # Use a test database
    test_db = Path("/tmp/traceflow_test.db")
    if test_db.exists():
        test_db.unlink()
    
    history = ErrorHistory(str(test_db))
    
    # Log some errors
    error1 = ParsedError(
        raw_output="ImportError: No module named 'xyz'",
        error_type="ImportError",
        message="No module named 'xyz'"
    )
    history.log_error(error1, "ImportError")
    
    error2 = ParsedError(
        raw_output="KeyError: 'missing'",
        error_type="KeyError",
        message="KeyError: 'missing'"
    )
    history.log_error(error2, "KeyError")
    
    # Log a fix
    history.log_fix(1, "Install package", "pip install xyz", applied=True)
    
    # Retrieve history
    results = history.get_similar_errors("ImportError", limit=5)
    
    if len(results) >= 1:
        print(f"   ✓ History contains {len(results)} similar errors")
        for r in results[:2]:
            print(f"      - {r['error_type']}: {r['message'][:40]}...")
        
        # Cleanup
        test_db.unlink()
        return True
    else:
        print(f"   ✗ History is empty")
        test_db.unlink()
        return False


def test_multilanguage():
    """Test multi-language error handling."""
    
    print("\n🧪 Testing multi-language support...")
    
    daemon = TraceflowDaemon()
    
    # Python error
    py_pattern, py_suggestions = daemon.analyze_error(
        "NameError: name 'x' is not defined",
        language="python"
    )
    
    # JavaScript error
    js_pattern, js_suggestions = daemon.analyze_error(
        "ReferenceError: x is not defined",
        language="javascript"
    )
    
    py_passed = py_pattern is not None and len(py_suggestions) > 0
    js_passed = js_pattern is not None and len(js_suggestions) > 0
    
    if py_passed:
        print(f"   ✓ Python: {py_pattern.name} - {len(py_suggestions)} fixes")
    else:
        print(f"   ✗ Python: Pattern={py_pattern}, Suggestions={len(py_suggestions)}")
    
    if js_passed:
        print(f"   ✓ JavaScript: {js_pattern.name} - {len(js_suggestions)} fixes")
    else:
        print(f"   ✗ JavaScript: Pattern={js_pattern}, Suggestions={len(js_suggestions)}")
    
    return py_passed and js_passed


def test_integration():
    """Test a complete debugging workflow."""
    
    print("\n🧪 Testing complete workflow...")
    
    daemon = TraceflowDaemon()
    
    # Simulate debugging a Python script
    errors = [
        "ImportError: No module named 'missing_module'",
        "NameError: name 'undefined' is not defined",
        "KeyError: 'config'"
    ]
    
    all_passed = True
    
    for error_text in errors:
        pattern, suggestions = daemon.analyze_error(error_text)
        
        if pattern and len(suggestions) > 0:
            print(f"   ✓ Analyzed: {pattern.name}")
            for s in suggestions[:1]:
                print(f"      → {s.description} ({s.confidence:.0%})")
        else:
            print(f"   ✗ Failed to analyze: {error_text[:40]}")
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    print("=" * 60)
    print("TRACEFLOW INTEGRATION TEST SUITE (Production Ready)")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Error Patterns", test_error_patterns()))
    results.append(("Fix Generation", test_fix_generation()))
    results.append(("Fix Application", test_fix_application()))
    results.append(("Error History", test_error_history()))
    results.append(("Multi-language", test_multilanguage()))
    results.append(("Integration", test_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Traceflow is production-ready.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Review the output above.")
        sys.exit(1)
