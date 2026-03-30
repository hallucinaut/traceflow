"""
Traceflow - Intelligent Error Analysis

A revolutionary workflow tool that intercepts process output,
analyzes errors in real-time, and provides contextual fix suggestions.
"""

from .daemon import TraceflowDaemon, ErrorAnalyzer, ErrorPatternRegistry, ParsedError, FixSuggestion

__version__ = "0.1.0"
__all__ = ["TraceflowDaemon", "ErrorAnalyzer", "ErrorPatternRegistry", "ParsedError", "FixSuggestion"]
