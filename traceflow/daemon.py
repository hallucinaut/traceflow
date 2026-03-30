"""
Traceflow Daemon - Intelligent Error Analysis

The revolutionary core: A background daemon that intercepts stderr/stdout
from running processes, parses error patterns in real-time, and provides
contextual fix suggestions by analyzing the entire codebase.
"""

import asyncio
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import regex


@dataclass
class ErrorPattern:
    """Represents a parsed error pattern with fix suggestions."""
    name: str
    pattern: regex.Pattern
    severity: str  # 'critical', 'error', 'warning', 'info'
    description: str
    fix_suggestions: List[str]
    related_files: List[str] = field(default_factory=list)


@dataclass
class ParsedError:
    """Represents a parsed error with context."""
    raw_output: str
    error_type: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    pattern_matched: Optional[ErrorPattern] = None
    timestamp: float = field(default_factory=time.time)
    process_info: Optional[Dict[str, Any]] = None


@dataclass
class FixSuggestion:
    """Represents a fix suggestion with confidence score."""
    description: str
    code_change: Optional[str] = None
    confidence: float = 0.5
    explanation: str = ""
    requires_review: bool = True


class ErrorPatternRegistry:
    """
    Registry of known error patterns with fix suggestions.
    Extensible for new error types.
    """
    
    def __init__(self):
        self.patterns: List[ErrorPattern] = []
        self._init_builtin_patterns()
    
    def _init_builtin_patterns(self):
        """Initialize built-in error patterns."""
        
        # Python syntax errors
        self.patterns.append(ErrorPattern(
            name="SyntaxError",
            pattern=regex.compile(r"SyntaxError:\s*(.+)", regex.IGNORECASE),
            severity="error",
            description="Python syntax error",
            fix_suggestions=[
                "Check for missing colons after statements",
                "Verify proper indentation",
                "Look for unmatched parentheses or brackets",
                "Check for missing quotes around strings"
            ]
        ))
        
        # NameError
        self.patterns.append(ErrorPattern(
            name="NameError",
            pattern=regex.compile(r"NameError:\s*name\s+'?(\w+)'?\s+is\s+not\s+defined", regex.IGNORECASE),
            severity="error",
            description="Undefined variable or function",
            fix_suggestions=[
                "Check if the variable is defined before use",
                "Verify the import statement for the module",
                "Check for typos in variable/function names",
                "Ensure the variable is in scope"
            ]
        ))
        
        # FileNotFoundError
        self.patterns.append(ErrorPattern(
            name="FileNotFoundError",
            pattern=regex.compile(r"FileNotFoundError.*[Nn]o\s+(such\s+)?[fF]ile.*[Oo][rR].*[dD]irectory", regex.IGNORECASE),
            severity="error",
            description="File or directory not found",
            fix_suggestions=[
                "Verify the file path is correct",
                "Check if the file exists in the expected location",
                "Ensure proper file permissions",
                "Use absolute paths if relative paths fail"
            ]
        ))
        
        # ImportError
        self.patterns.append(ErrorPattern(
            name="ImportError",
            pattern=regex.compile(r"ImportError:\s*(.+)", regex.IGNORECASE),
            severity="error",
            description="Module or package import error",
            fix_suggestions=[
                "Install the required package: pip install <package>",
                "Check if the package name is correct",
                "Verify Python version compatibility",
                "Check if the package is in the Python path"
            ]
        ))
        
        # AttributeError
        self.patterns.append(ErrorPattern(
            name="AttributeError",
            pattern=regex.compile(r"AttributeError:\s*'(\w+)' object has no attribute '(\w+)'", regex.IGNORECASE),
            severity="error",
            description="Attribute or method not found on object",
            fix_suggestions=[
                "Check if the attribute exists on the object",
                "Verify the object type",
                "Check for typos in attribute names",
                "Ensure the object is initialized before use"
            ]
        ))
        
        # KeyError
        self.patterns.append(ErrorPattern(
            name="KeyError",
            pattern=regex.compile(r"KeyError:\s*'(\w+)'", regex.IGNORECASE),
            severity="error",
            description="Dictionary key not found",
            fix_suggestions=[
                "Check if the key exists in the dictionary",
                "Use .get() method with a default value",
                "Verify the key type matches",
                "Check for typos in key names"
            ]
        ))
        
        # ValueError
        self.patterns.append(ErrorPattern(
            name="ValueError",
            pattern=regex.compile(r"ValueError:\s*(.+)", regex.IGNORECASE),
            severity="error",
            description="Invalid value passed to function",
            fix_suggestions=[
                "Check the function's expected input type",
                "Validate input data before calling the function",
                "Check for None or empty values",
                "Verify the value range if applicable"
            ]
        ))
        
        # IndexError
        self.patterns.append(ErrorPattern(
            name="IndexError",
            pattern=regex.compile(r"IndexError:\s*list\s+index\s+out\s+of\s+range", regex.IGNORECASE),
            severity="error",
            description="List index out of range",
            fix_suggestions=[
                "Check the list length before accessing",
                "Use try/except for safe access",
                "Verify the index is within bounds",
                "Consider using enumerate() for iteration"
            ]
        ))
        
        # TypeError
        self.patterns.append(ErrorPattern(
            name="TypeError",
            pattern=regex.compile(r"TypeError:\s*(.+)", regex.IGNORECASE),
            severity="error",
            description="Invalid type operation",
            fix_suggestions=[
                "Check the types of operands",
                "Convert types if necessary",
                "Verify function argument types",
                "Check for None values"
            ]
        ))
        
        # Connection errors
        self.patterns.append(ErrorPattern(
            name="ConnectionError",
            pattern=regex.compile(r"(ConnectionRefused|ConnectionReset|ConnectionAborted)Error", regex.IGNORECASE),
            severity="critical",
            description="Network connection error",
            fix_suggestions=[
                "Check if the server is running",
                "Verify the host and port are correct",
                "Check firewall settings",
                "Ensure network connectivity"
            ]
        ))
        
        # Database errors
        self.patterns.append(ErrorPattern(
            name="DatabaseError",
            pattern=regex.compile(r"(OperationalError|ProgrammingError|DatabaseError)", regex.IGNORECASE),
            severity="critical",
            description="Database operation error",
            fix_suggestions=[
                "Check database connection",
                "Verify SQL syntax",
                "Check if tables exist",
                "Review database permissions"
            ]
        ))
    
    def find_matching_pattern(self, error_message: str) -> Optional[ErrorPattern]:
        """Find the best matching error pattern."""
        for pattern in self.patterns:
            if pattern.pattern.search(error_message):
                return pattern
        return None


class ProcessMonitor:
    """
    Monitors running processes and captures their stdout/stderr.
    """
    
    def __init__(self, callback: Callable[[ParsedError], None]):
        self.callback = callback
        self.running_processes: Dict[int, subprocess.Popen] = {}
        self.process_metadata: Dict[int, Dict[str, Any]] = {}
    
    def start_monitoring(self, command: List[str], cwd: Optional[str] = None):
        """Start monitoring a process."""
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=cwd,
            bufsize=1
        )
        
        pid = proc.pid
        self.running_processes[pid] = proc
        self.process_metadata[pid] = {
            'command': ' '.join(command),
            'cwd': cwd or os.getcwd(),
            'start_time': time.time()
        }
        
        asyncio.create_task(self._read_output(pid, proc))
    
    async def _read_output(self, pid: int, proc: subprocess.Popen):
        """Read and analyze process output."""
        while proc.poll() is None:
            try:
                output = proc.stderr.read(4096)
                if output:
                    await self.callback(ParsedError(
                        raw_output=output,
                        error_type="unknown",
                        message=output.strip(),
                        process_info=self.process_metadata.get(pid)
                    ))
                await asyncio.sleep(0.1)
            except ValueError:
                break
        
        # Read remaining output
        remaining = proc.stderr.read()
        if remaining:
            await self.callback(ParsedError(
                raw_output=remaining,
                error_type="unknown",
                message=remaining.strip(),
                process_info=self.process_metadata.get(pid)
            ))
    
    def stop_monitoring(self, pid: int):
        """Stop monitoring a process."""
        if pid in self.running_processes:
            proc = self.running_processes[pid]
            proc.terminate()
            proc.wait()
            del self.running_processes[pid]


class ErrorAnalyzer:
    """
    Analyzes error messages and provides fix suggestions.
    """
    
    def __init__(self, codebase_path: Optional[str] = None):
        self.registry = ErrorPatternRegistry()
        self.codebase_path = codebase_path
        self.error_history: List[ParsedError] = []
        self.fix_suggestions_cache: Dict[str, List[FixSuggestion]] = {}
    
    def analyze(self, error: ParsedError) -> Tuple[ErrorPattern, List[FixSuggestion]]:
        """Analyze an error and return pattern + suggestions."""
        # Find matching pattern
        pattern = self.registry.find_matching_pattern(error.raw_output)
        
        # Generate fix suggestions
        suggestions = self._generate_suggestions(error, pattern)
        
        # Cache for future use
        cache_key = error.message[:100]
        self.fix_suggestions_cache[cache_key] = suggestions
        
        return pattern, suggestions
    
    def _generate_suggestions(self, error: ParsedError, pattern: Optional[ErrorPattern]) -> List[FixSuggestion]:
        """Generate fix suggestions based on error analysis."""
        suggestions = []
        
        if pattern:
            # Use pattern-based suggestions
            for i, suggestion in enumerate(pattern.fix_suggestions):
                suggestions.append(FixSuggestion(
                    description=suggestion,
                    confidence=0.7 if i == 0 else 0.5,
                    explanation=f"Pattern: {pattern.name}",
                    requires_review=True
                ))
        
        # Add context-aware suggestions if codebase path is available
        if self.codebase_path and error.file_path:
            context_suggestions = self._get_context_suggestions(error)
            suggestions.extend(context_suggestions)
        
        return suggestions
    
    def _get_context_suggestions(self, error: ParsedError) -> List[FixSuggestion]:
        """Get suggestions based on codebase context."""
        suggestions = []
        
        # Check if the error file exists
        if error.file_path and os.path.exists(error.file_path):
            suggestions.append(FixSuggestion(
                description=f"Review {os.path.basename(error.file_path)} for the error",
                confidence=0.6,
                explanation="File exists in codebase",
                requires_review=False
            ))
        
        return suggestions
    
    def get_similar_errors(self, error: ParsedError, limit: int = 5) -> List[ParsedError]:
        """Find similar errors from history."""
        similar = []
        for hist_error in self.error_history:
            if hist_error.message == error.message:
                similar.append(hist_error)
            elif self._similarity_score(hist_error.message, error.message) > 0.8:
                similar.append(hist_error)
        
        return similar[:limit]
    
    def _similarity_score(self, s1: str, s2: str) -> float:
        """Calculate similarity between two error messages."""
        # Simple token-based similarity
        tokens1 = set(s1.lower().split())
        tokens2 = set(s2.lower().split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        
        return len(intersection) / len(union) if union else 0.0


class TraceflowDaemon:
    """
    The main daemon that orchestrates error monitoring and analysis.
    """
    
    def __init__(self, codebase_path: Optional[str] = None):
        self.codebase_path = codebase_path
        self.error_analyzer = ErrorAnalyzer(codebase_path)
        self.process_monitor = ProcessMonitor(self._handle_error)
        self.running = False
        self.suggestion_callbacks: List[Callable] = []
    
    def _handle_error(self, error: ParsedError):
        """Handle a parsed error from a monitored process."""
        pattern, suggestions = self.error_analyzer.analyze(error)
        
        # Log error
        self.error_analyzer.error_history.append(error)
        
        # Notify callbacks
        for callback in self.suggestion_callbacks:
            try:
                callback(error, pattern, suggestions)
            except Exception as e:
                print(f"[Traceflow] Callback error: {e}", file=sys.stderr)
    
    def register_suggestion_callback(self, callback: Callable):
        """Register a callback to receive error suggestions."""
        self.suggestion_callbacks.append(callback)
    
    def run_command(self, command: List[str], cwd: Optional[str] = None):
        """Run a command and monitor for errors."""
        self.running = True
        self.process_monitor.start_monitoring(command, cwd)
        
        # Wait for process to complete
        while self.running:
            time.sleep(0.5)
            if not self.process_monitor.running_processes:
                break
    
    def stop(self):
        """Stop the daemon."""
        self.running = False
        for pid in list(self.process_monitor.running_processes.keys()):
            self.process_monitor.stop_monitoring(pid)
        print("[Traceflow] Daemon stopped.")
    
    def analyze_error(self, error_text: str) -> Tuple[ErrorPattern, List[FixSuggestion]]:
        """Analyze an error message without running a process."""
        error = ParsedError(
            raw_output=error_text,
            error_type="unknown",
            message=error_text.strip()
        )
        return self.error_analyzer.analyze(error)


def main():
    """Entry point for the traceflow CLI."""
    daemon = TraceflowDaemon()
    
    # Demo callback
    async def show_suggestions(error, pattern, suggestions):
        print(f"\n🔍 Traceflow detected: {error.error_type}")
        print(f"   Message: {error.message[:100]}")
        if pattern:
            print(f"   Pattern: {pattern.name}")
        print(f"   Suggestions:")
        for i, s in enumerate(suggestions[:3], 1):
            print(f"     {i}. {s.description} (confidence: {s.confidence:.0%})")
    
    daemon.register_suggestion_callback(show_suggestions)
    
    try:
        # Demo: Run a command that produces an error
        print("[Traceflow] Starting error monitoring...")
        print("[Traceflow] Running demo command that will produce an error...\n")
        
        daemon.run_command(["python3", "-c", "import nonexistent_module_xyz"])
        
    except KeyboardInterrupt:
        daemon.stop()


if __name__ == "__main__":
    main()
