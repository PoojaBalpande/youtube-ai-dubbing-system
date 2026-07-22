"""
Translator factory and backward-compatible wrapper.

This module is the single entry point for obtaining a translator instance.
It provides:

- ``get_translator()``: Factory function that reads
  ``config.TRANSLATOR_PROVIDER`` and returns the appropriate
  ``BaseTranslator`` implementation.

- ``Translator``: A thin backward-compatible wrapper class that
  delegates to ``get_translator()``. This preserves the existing
  import and usage pattern used by ``main.py`` and other modules,
  so that no downstream code needs to change.
"""

from app.translation.base import BaseTranslator
from config import settings as config
from app.utils.logger import get_logger
from app.models.segment import TranscriptSegment


logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Registry of supported translator providers.
#
# Each key maps to a tuple of (module_path, class_name). Imports are
# deferred (lazy) so that heavy dependencies like MarianMT or Groq SDK
# are only loaded when the corresponding provider is actually selected.
# ---------------------------------------------------------------------------

_TRANSLATOR_REGISTRY: dict[str, tuple[str, str]] = {
    "marian": (
        "app.translation.marian_translator",
        "MarianTranslator",
    ),
    "groq": (
        "app.translation.groq",
        "GroqTranslator",
    ),
}


def get_translator(provider: str | None = None) -> BaseTranslator:
    """
    Factory function that creates and returns a translator instance
    based on the configured or specified provider.

    The provider is resolved in the following order:
        1. The ``provider`` argument (if given).
        2. ``config.TRANSLATOR_PROVIDER`` (default).

    Args:
        provider: Optional override for the translator provider name.
            If ``None``, the value from ``config.TRANSLATOR_PROVIDER``
            is used.

    Returns:
        An instance of the appropriate ``BaseTranslator`` subclass.

    Raises:
        ValueError: If the provider name is not recognized.
        ImportError: If the translator module cannot be imported.

    Example::

        translator = get_translator()           # uses config default
        translator = get_translator("groq")     # explicit override
        translated = translator.translate("नमस्ते दोस्तों")
    """

    selected_provider: str = (
        provider if provider is not None
        else config.TRANSLATOR_PROVIDER
    ).lower().strip()

    if selected_provider not in _TRANSLATOR_REGISTRY:
        supported = ", ".join(sorted(_TRANSLATOR_REGISTRY.keys()))
        raise ValueError(
            f"Unknown translator provider: '{selected_provider}'. "
            f"Supported providers: {supported}"
        )

    module_path, class_name = _TRANSLATOR_REGISTRY[selected_provider]

    logger.info(
        f"Creating translator: provider='{selected_provider}', "
        f"class='{class_name}'"
    )

    # Lazy import — only load the module when the provider is selected.
    import importlib

    module = importlib.import_module(module_path)
    translator_class = getattr(module, class_name)

    return translator_class()


# ---------------------------------------------------------------------------
# Backward-compatible wrapper
# ---------------------------------------------------------------------------


class Translator:
    """
    Backward-compatible wrapper around the translator factory.

    This class preserves the original import and usage pattern::

        from app.translation.translator import Translator

        translator = Translator()
        translated = translator.translate(text)
        translator.save_translation(translated)

    Internally, it delegates to ``get_translator()`` which returns
    the appropriate ``BaseTranslator`` subclass based on
    ``config.TRANSLATOR_PROVIDER``.

    This ensures that ``main.py``, ``test_translation.py``, and any
    other existing code that imports ``Translator`` continues to work
    without modification.
    """

    def __init__(self) -> None:
        """
        Initialize by delegating to the factory.

        The underlying translator strategy is determined by
        ``config.TRANSLATOR_PROVIDER``.
        """
        try:
            self._strategy: BaseTranslator = get_translator()
        except Exception as error:
            fallback_enabled = getattr(config, "ENABLE_TRANSLATION_FALLBACK", False)
            if fallback_enabled:
                fallback_provider = getattr(config, "FALLBACK_TRANSLATOR", "marian")
                logger.warning(
                    f"Initialization of primary translator failed: {error}. "
                    f"Falling back to '{fallback_provider}'..."
                )
                try:
                    self._strategy = get_translator(fallback_provider)
                except Exception as fallback_error:
                    logger.error(f"Fallback translator initialization failed: {fallback_error}")
                    raise fallback_error from error
            else:
                logger.error(f"Translator initialization failed and fallback is disabled: {error}")
                raise error

        logger.info(
            f"Translator wrapper initialized with strategy: "
            f"{type(self._strategy).__name__}"
        )

    def translate(self, text: str) -> str:
        """
        Translate text using the selected strategy, with optional fallback support.

        Args:
            text: The source text to translate.

        Returns:
            The translated text.
        """
        try:
            return self._strategy.translate(text)
        except Exception as error:
            fallback_enabled = getattr(config, "ENABLE_TRANSLATION_FALLBACK", False)
            if fallback_enabled:
                fallback_provider = getattr(config, "FALLBACK_TRANSLATOR", "marian")
                logger.warning(
                    f"Primary translator {type(self._strategy).__name__} failed: {error}. "
                    f"Attempting fallback to '{fallback_provider}'..."
                )
                try:
                    fallback_strategy = get_translator(fallback_provider)
                    return fallback_strategy.translate(text)
                except Exception as fallback_error:
                    logger.error(f"Fallback translator failed: {fallback_error}")
                    raise fallback_error from error
            else:
                logger.error(f"Translation failed and fallback is disabled: {error}")
                raise error

    def save_translation(self, translated_text: str):
        """
        Save translated text using the selected strategy.

        Args:
            translated_text: The translated text to persist.

        Returns:
            The path to the saved translation file.
        """
        return self._strategy.save_translation(translated_text)

    def translate_segments(self, segments: list[TranscriptSegment]) -> list[TranscriptSegment]:
        """
        Translate a list of TranscriptSegment objects using the selected strategy,
        with optional fallback support.

        Args:
            segments: A list of TranscriptSegment objects.

        Returns:
            The list of segments with translated_text attributes updated.
        """
        try:
            return self._strategy.translate_segments(segments)
        except Exception as error:
            fallback_enabled = getattr(config, "ENABLE_TRANSLATION_FALLBACK", False)
            if fallback_enabled:
                fallback_provider = getattr(config, "FALLBACK_TRANSLATOR", "marian")
                logger.warning(
                    f"Primary translator {type(self._strategy).__name__} failed during segment translation: {error}. "
                    f"Attempting fallback to '{fallback_provider}'..."
                )
                try:
                    fallback_strategy = get_translator(fallback_provider)
                    return fallback_strategy.translate_segments(segments)
                except Exception as fallback_error:
                    logger.error(f"Fallback segment translation failed: {fallback_error}")
                    raise fallback_error from error
            else:
                logger.error(f"Segment translation failed and fallback is disabled: {error}")
                raise error