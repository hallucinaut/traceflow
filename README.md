# Traceflow 🔍

> **Intelligent error analysis and fix suggestions for developers**

---

## The Old Way

Debugging is a **painful, time-consuming process**:

1. **Run code** → See cryptic error message
2. **Google the error** → Find Stack Overflow threads from 5 years ago
3. **Read unrelated answers** → Try solutions that don't apply
4. **Copy-paste fixes** → Hope it works
5. **Repeat** → 2-3 hours per week wasted

**The cost:** Developers spend **2-3 hours weekly** just reading and interpreting error messages. The context is lost, the fix is forgotten, and the same mistakes are repeated.

---

## The New Paradigm

**Traceflow is different.** It's an **intelligent error analyzer** that runs alongside your code, intercepting errors in real-time and providing contextual fix suggestions.

### How It Works

```bash
$ python3 app.py
[Traceflow] 🔍 Detected: ImportError
   Message: No module named 'nonexistent_module_xyz'
   Pattern: ImportError
   Suggestions:
     1. Install the required package: pip install <package> (confidence: 70%)
     2. Check if the package name is correct (confidence: 50%)
     3. Verify Python version compatibility (confidence: 50%)
```

**No Google. No Stack Overflow. Just fixes.**

---

## Under the Hood

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Traceflow Daemon                       │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Process      │  │  Error       │  │  Fix         │  │
│  │ Monitor      │─▶│ Analyzer     │─▶│ Suggestion   │  │
│  │ (subprocess) │  │ (pattern     │  │  Engine      │  │
│  └──────────────┘  │ matching)    │  └──────────────┘  │
│                     └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

### Key Technologies

- **regex** - Advanced pattern matching for error detection
- **rich** - Beautiful terminal output
- **asyncio** - Non-blocking process monitoring
- **anyio** - Cross-platform async primitives

### Error Pattern Matching

Traceflow uses a **registry of known error patterns** with pre-built fix suggestions:

- Python syntax errors
- Import errors
- File not found errors
- Database errors
- Network connection errors
- And 20+ more...

### Extensible Pattern System

Add your own error patterns:

```python
from traceflow import ErrorPatternRegistry

registry = ErrorPatternRegistry()
registry.patterns.append(ErrorPattern(
    name="CustomError",
    pattern=regex.compile(r"MyCustomError:\s*(.+)"),
    severity="error",
    description="My custom error",
    fix_suggestions=["Fix your custom logic"]
))
```

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
from traceflow import TraceflowDaemon

daemon = TraceflowDaemon(codebase_path="./src")

def on_error(error, pattern, suggestions):
    print(f"Error: {error.message}")
    for suggestion in suggestions:
        print(f"  → {suggestion.description}")

daemon.register_suggestion_callback(on_error)
daemon.run_command(["python3", "app.py"])
```

---

## Proof of Concept

See `simulate_debugger.py` for a complete integration test that simulates debugging scenarios.

```bash
python simulate_debugger.py
```

---

## Why This Matters

**Traceflow is not a debugger. It's a debugging assistant.**

- **Ambient Intelligence** - Analyzes errors as they happen
- **Context-Aware** - Understands your codebase structure
- **Learning System** - Builds knowledge of common errors
- **Fix-First** - Provides actionable solutions, not just descriptions

This is the first tool that **understands your errors** rather than just displaying them.

---

## License

MIT - Open source, free for personal and commercial use.

---

## The Future

This is just the beginning. Next iterations will add:

- AI-powered error analysis (LLM integration)
- Cross-language support (JavaScript, Go, Rust)
- IDE plugin integration (VSCode, JetBrains)
- Error history and trend analysis
- Automated fix application

**The goal:** Eliminate the pain of debugging entirely.
