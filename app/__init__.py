"""
MultiTool Flask Application Package
Provides a comprehensive suite of file processing tools.
"""

__version__ = "1.0.0"
__author__ = "MultiTool Team"

# Make key components available at package level
from .config import Config

__all__ = ['Config']
