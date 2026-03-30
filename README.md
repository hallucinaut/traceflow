# Traceflow 🔍

> **Intelligent error analysis and fix generation for developers**

---

## What This Is

Traceflow is a **background daemon** that monitors process output, analyzes errors in real-time, and generates code fix suggestions. It works by:

1. **Pattern matching** - Recognizes common error types (SyntaxError, NameError, etc.)
2. **Fix generation** - Creates regex-based code changes to fix the error
3. **History tracking** - Learns from your past errors and fixes
4. **Multi-language** - Supports Python and JavaScript/TypeScript

---

## What This Is NOT

- ❌ **Not AI-powered** - No LLM or machine learning
- ❌ **Not magic** - Fixes are template-based, not context-aware
- ❌ **Not perfect** - Generated fixes require review
- ❌ **Not a debugger** - Doesn't step through code or set breakpoints

---

## Installation

```bash
pip install traceflow
```

### Development Setup

```bash
git clone https://github.com/hallucinaut/traceflow
cd traceflow
pip install -e ".[dev]"
```

---

## Usage

### As a Daemon

```bash
traceflow
```

Monitors the current directory and analyzes errors from running commands.

### As a Library

```python
from traceflow import TraceflowDaemon, FixSuggestion

daemon = TraceflowDaemon()

# Analyze an error
pattern, suggestions = daemon.analyze_error("NameError: name 'undefined' is not defined")

for suggestion in suggestions:
    print(f"Suggestion: {suggestion.description}")
    print(f"Confidence: {suggestion.confidence}")
    
    # Apply the fix (if you trust it)
    if suggestion.confidence > 0.7:
        success = suggestion.apply_to_file("app.py")
        print(f"Applied: {success}")
```

### Monitoring a Process

```python
daemon = TraceflowDaemon()

def on_error(error, suggestions):
    print(f"Error: {error.message}")
    for s in suggestions:
        print(f"  → {s.description}")

daemon.register_suggestion_callback(on_error)

# Run a command and monitor for errors
daemon.run_command(["python3", "app.py"], language="python")
```

---

## API Reference

### TraceflowDaemon

```python
from traceflow import TraceflowDaemon

daemon = TraceflowDaemon()

# Analyze an error message
pattern, suggestions = daemon.analyze_error("FileNotFoundError: [Errno 2]...", language="python")

# Suggest fixes for a parsed error
from traceflow import ParsedError
error = ParsedError(
    raw_output="NameError: name 'x' is not defined",
    error_type="NameError",
    message="name 'x' is not defined",
    file_path="app.py"
)
suggestions = daemon.suggest_fix(error)

# Run and monitor a command
daemon.run_command(["python3", "app.py"], language="python")

# Get error history
history = daemon.get_error_history(limit=20)
```

### FixSuggestion

```python
from traceflow import FixSuggestion

suggestion = FixSuggestion(
    description="Add missing import",
    code_change="import missing_module",
    before_pattern=r"^import",
    after_replacement=r"import missing_module\nimport",
    confidence=0.8,
    explanation="Pattern: ImportError",
    requires_review=True
)

# Apply the fix to a file
success = suggestion.apply_to_file("app.py")
```

### ErrorPatternRegistry

```python
from traceflow import ErrorPatternRegistry

registry = ErrorPatternRegistry()

# Find matching pattern
pattern = registry.find_matching_pattern("SyntaxError: invalid syntax", "python")

# Get all patterns
for p in registry.patterns:
    print(f"{p.name}: {p.description}")
```

---

## Supported Error Patterns

### Python

- SyntaxError (missing colons, indentation issues)
- NameError (undefined variables)
- FileNotFoundError (missing files)
- ImportError (missing modules)
- AttributeError (missing attributes)
- KeyError (missing dictionary keys)
- IndexError (list index out of range)
- TypeError (invalid type operations)
- ConnectionError (network issues)
- DatabaseError (SQL errors)

### JavaScript/TypeScript

- ReferenceError (undefined variables)
- TypeError (type operations)
- SyntaxError (syntax issues)

---

## How It Works

### Pattern Matching

Traceflow uses regex patterns to recognize errors:

```python
# Example: NameError pattern
pattern = regex.compile(
    r"NameError:\s*name\s+'?(\w+)'?\s+is\s+not\s+defined",
    regex.IGNORECASE
)
```

### Fix Generation

Fixes are regex-based code transformations:

```python
fix = {
    "description": "Use .get() with default",
    "before_pattern": r"(\w+)\['(\w+)'\]",
    "after_replacement": r"\1.get('\2', None)"
}
```

### History Tracking

Errors and fixes are stored in SQLite at `~/.config/traceflow/traceflow.db`:

```sql
CREATE TABLE errors (
    id INTEGER PRIMARY KEY,
    raw_output TEXT,
    error_type TEXT,
    message TEXT,
    pattern_matched TEXT,
    timestamp REAL
);

CREATE TABLE fixes (
    id INTEGER PRIMARY KEY,
    error_id INTEGER,
    fix_description TEXT,
    code_change TEXT,
    applied BOOLEAN,
    timestamp REAL
);
```

---

## Limitations

### What Works Well

- ✅ Pattern-based error recognition
- ✅ Fast regex-based fix generation
- ✅ Persistent error history
- ✅ Multi-language support (Python, JS/TS)
- ✅ Confidence scoring for fixes

### What Doesn't Work

- ❌ **No semantic understanding** - Can't understand code intent
- ❌ **No project context** - Doesn't know your codebase structure
- ❌ **Template-based fixes** - May not work for complex cases
- ❌ **No IDE integration** - Terminal only
- ❌ **No learning** - Doesn't improve over time

---

## Proof of Concept

Run the integration test:

```bash
python simulate_debugger.py
```

This tests:
- Error pattern recognition
- Fix suggestion generation
- Error history tracking
- Multi-language support

---

## Honest Assessment

This tool is **functional but limited**:

1. **Pattern matching works** - It recognizes the 11+ built-in error patterns
2. **Fix generation works** - It creates regex replacements
3. **But...** - The fixes are generic templates, not context-aware

**Example:**

```python
# Error: KeyError: 'missing_key'
# Traceflow suggests: dict.get('missing_key', None)
# This works for simple cases, but not if you need special logic
```

**The fixes require review.** Don't blindly apply them.

---

## Future Possibilities

If you want to extend this:

1. **Add more patterns** - Support more error types
2. **Add project context** - Know your codebase structure
3. **Add AI** - Use an LLM for smarter fixes
4. **Add IDE plugin** - VSCode extension
5. **Add user feedback** - Learn which fixes work

---

## License

MIT - Open source, free for personal and commercial use.
