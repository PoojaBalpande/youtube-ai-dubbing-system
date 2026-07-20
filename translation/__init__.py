"""
Translation module for the YouTube AI Dubbing System.

Public API:
    - ``BaseTranslator``: Abstract base class for all translator strategies.
    - ``get_translator``: Factory function to obtain a translator instance.
    - ``Translator``: Backward-compatible wrapper (delegates to factory).
"""

from translation.base import BaseTranslator
from translation.translator import get_translator, Translator

__all__ = [
    "BaseTranslator",
    "get_translator",
    "Translator",
]
