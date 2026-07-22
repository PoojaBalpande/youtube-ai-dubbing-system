"""
Abstract base class for all translator implementations.

Defines the common interface that every translator strategy must implement,
following the Strategy Pattern. This ensures that any translator can be
swapped in without modifying client code.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from config import settings as config
from app.utils.logger import get_logger
from app.models.segment import TranscriptSegment


logger = get_logger(__name__)


class BaseTranslator(ABC):
    """
    Abstract base class for translation strategies.

    Every concrete translator (MarianTranslator, GeminiTranslator, etc.)
    must inherit from this class and implement the ``translate`` method.

    The ``save_translation`` method is provided as a concrete implementation
    shared by all translators, since the save logic is translator-agnostic.
    """

    @abstractmethod
    def translate(self, text: str) -> str:
        """
        Translate the given text to the target language.

        Args:
            text: The source text to translate.

        Returns:
            The translated text.

        Raises:
            ValueError: If the input text is empty or invalid.
            RuntimeError: If translation fails due to model/API errors.
        """

    def save_translation(self, translated_text: str) -> Path:
        """
        Save translated text to the configured output file.

        This method is shared across all translator implementations
        because the persistence logic is independent of the translation
        strategy used.

        Args:
            translated_text: The translated text to persist.

        Returns:
            The path to the saved translation file.
        """

        output_path: Path = config.TRANSLATION_OUTPUT_FILE

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(translated_text)

        logger.info(f"Translation saved to {output_path}")

        return output_path

    def translate_segments(self, segments: list[TranscriptSegment]) -> list[TranscriptSegment]:
        """
        Translate a list of TranscriptSegment objects using context preservation windows.

        Neighboring segments are merged together into larger text blocks, translated,
        and then redistributed back into the original segments proportionally.

        Args:
            segments: A list of TranscriptSegment objects.

        Returns:
            The list of segments with translated_text attributes updated.
        """
        from app.translation.context_builder import ContextBuilder

        logger.info(f"Starting context-preserving segment translation for {len(segments)} segments...")

        # Build context windows
        windows = ContextBuilder.build_windows(segments)

        for index, (window_segs, window_text) in enumerate(windows, start=1):
            if not window_text.strip():
                for seg in window_segs:
                    seg.translated_text = ""
                continue

            logger.info(f"Translating window {index}/{len(windows)} (total original words: {len(window_text.split())})...")
            
            # Translate the entire merged window text
            translated_window = self.translate(window_text)

            # Redistribute translated text back to constituent segments
            ContextBuilder.redistribute(window_segs, translated_window)

        logger.info("Segment translation and redistribution completed.")
        return segments
