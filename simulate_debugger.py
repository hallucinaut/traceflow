"""
Integration Test: Simulate Debugging Workflow

This script simulates a developer debugging errors and verifies
that Traceflow successfully analyzes them and provides fix suggestions.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from traceflow import TraceflowDaemon, ErrorAnalyzer, ParsedError


def test_error_analysis():
    """Test that Traceflow can analyze various error types."""
    
    print("🧪 Testing error analysis...")
    
    analyzer = ErrorAnalyzer()
    
    test_cases = [
        {
            "name": "ImportError",
            "error": "ImportError: No module named 'nonexistent_module'",
            "expected_pattern": "ImportError"
        },
        {
            "name": "FileNotFoundError",
            "error": "FileNotFoundError: No such file or directory: 'missing.txt'",
            "expected_pattern": "FileNotFoundError"
        },
        {
            "name": "NameError",
            "error": "NameError: name 'undefined_var' is not defined",
            "expected_pattern": "NameError"
        },
        {
            "name": "AttributeError",
            "error": "AttributeError: 'str' object has no attribute 'nonexistent'",
            "expected_pattern": "AttributeError"
        },
        {
            "name": "KeyError",
            "error": "KeyError: 'missing_key'",
            "expected_pattern": "KeyError"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        error = ParsedError(
            raw_output=test["error"],
            error_type="unknown",
            message=test["error"]
        )
        
        pattern, suggestions = analyzer.analyze(error)
        
        if pattern and pattern.name == test["expected_pattern"]:
            print(f"   ✓ {test['name']}: Correctly identified")
            print(f"      Suggestions: {len(suggestions)} fix ideas")
            passed += 1
        else:
            print(f"   ✗ {test['name']}: Expected {test['expected_pattern']}, got {pattern.name if pattern else 'None'}")
            failed += 1
    
    return passed == len(test_cases)


def test_suggestion_quality():
    """Test that generated suggestions are relevant."""
    
    print("\n🧪 Testing suggestion quality...")
    
    analyzer = ErrorAnalyzer()
    
    error = ParsedError(
        raw_output="FileNotFoundError: [Errno 2] No such file or directory: 'data/config.json'",
        error_type="unknown",
        message="FileNotFoundError: [Errno 2] No such file or directory: 'data/config.json'"
    )
    
    pattern, suggestions = analyzer.analyze(error)
    
    if not pattern:
        print("   ✗ No pattern matched")
        return False
    
    # Check that we got suggestions
    if len(suggestions) == 0:
        print("   ✗ No suggestions generated")
        return False
    
    # Check that suggestions are reasonable
    has_path_suggestion = any("path" in s.description.lower() for s in suggestions)
    has_file_suggestion = any("file" in s.description.lower() for s in suggestions)
    
    if has_path_suggestion or has_file_suggestion:
        print(f"   ✓ Generated {len(suggestions)} relevant suggestions")
        for i, s in enumerate(suggestions[:3], 1):
            print(f"      {i}. {s.description} ({s.confidence:.0%} confidence)")
        return True
    else:
        print("   ✗ Suggestions not relevant to FileNotFoundError")
        return False


def test_error_registry():
    """Test that the error pattern registry is complete."""
    
    print("\n🧪 Testing error registry...")
    
    from traceflow import ErrorPatternRegistry
    
    registry = ErrorPatternRegistry()
    
    # Check that we have built-in patterns
    if len(registry.patterns) >= 10:
        print(f"   ✓ Registry contains {len(registry.patterns)} error patterns")
        
        # List some patterns
        pattern_names = [p.name for p in registry.patterns[:5]]
        print(f"      Examples: {', '.join(pattern_names)}")
        
        return True
    else:
        print(f"   ✗ Registry only has {len(registry.patterns)} patterns (expected >= 10)")
        return False


def test_simulated_debugging():
    """Test a complete debugging scenario."""
    
    print("\n🧪 Testing simulated debugging scenario...")
    
    daemon = TraceflowDaemon()
    
    errors_detected = []
    suggestions_provided = []
    
    def on_error(error, pattern, suggestions):
        errors_detected.append(error)
        suggestions_provided.extend(suggestions)
    
    daemon.register_suggestion_callback(on_error)
    
    # Simulate running a command that produces an error
    print("   Simulating: python3 -c \"import nonexistent_xyz\"")
    
    # Direct analysis (we can't actually run this without creating the module)
    error_text = "ImportError: No module named 'nonexistent_xyz'"
    pattern, suggestions = daemon.analyze_error(error_text)
    
    if pattern:
        print(f"   ✓ Detected: {pattern.name}")
        print(f"   ✓ Provided {len(suggestions)} suggestions")
        return True
    else:
        print("   ✗ Failed to detect error")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("TRACEFLOW INTEGRATION TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Error Analysis", test_error_analysis()))
    results.append(("Suggestion Quality", test_suggestion_quality()))
    results.append(("Error Registry", test_error_registry()))
    results.append(("Simulated Debugging", test_simulated_debugging()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Traceflow is ready for production.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Review the output above.")
        sys.exit(1)
