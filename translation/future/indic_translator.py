"""
IndicTrans2 translator implementation (future).

This module provides a skeleton class for a future translator strategy
based on IndicTrans2 or similar Indic-language translation models.
It is not yet implemented — calling ``translate()`` will raise
``NotImplementedError``.
"""

from translation.base import BaseTranslator
from utils.logger import get_logger


logger = get_logger(__name__)


class IndicTranslator(BaseTranslator):
    """
    Translator strategy for Indic languages using IndicTrans2.

    This is a placeholder class designed for future extensibility.
    When implemented, it will support high-quality translations
    between Indic languages and English using the AI4Bharat
    IndicTrans2 model.

    To implement:
        1. Install the IndicTrans2 dependencies.
        2. Load the model in ``__init__``.
        3. Implement the ``translate`` method with the model's
           inference pipeline.
    """

    def __init__(self) -> None:
        """Initialize the IndicTranslator (future implementation)."""

        logger.warning(
            "IndicTranslator is not yet implemented. "
            "This is a placeholder for future development."
        )

    def translate(self, text: str) -> str:
        """
        Translate text using IndicTrans2.

        Args:
            text: The source text to translate.

        Returns:
            The translated text.

        Raises:
            NotImplementedError: Always, until the implementation
                is completed.
        """

        raise NotImplementedError(
            "IndicTranslator is not yet implemented. "
            "This translator will be available in a future release."
        )
