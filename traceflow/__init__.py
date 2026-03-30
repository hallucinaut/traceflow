"""
Traceflow - Intelligent Error Analysis & Fix Generation

Production-ready implementation with:
- Real code fix generation
- Multi-language support (Python, JavaScript)
- Context-aware fixes
- Persistent error history
"""

from .daemon import (
    TraceflowDaemon,
    ErrorPatternRegistry,
    ParsedError,
    FixSuggestion,
    ErrorHistory,
    CodeAnalyzer
)

__version__ = "1.0.0"
__all__ = ["TraceflowDaemon", "ErrorPatternRegistry", "ParsedError", 
           "FixSuggestion", "ErrorHistory", "CodeAnalyzer"]
