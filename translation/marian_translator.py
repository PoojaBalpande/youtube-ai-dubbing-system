"""
MarianMT translator implementation.

Encapsulates the existing Helsinki-NLP/MarianMT translation logic
into a strategy class that conforms to the BaseTranslator interface.
This is a direct migration of the original Translator class — no
behavioral changes were made.
"""

from transformers import MarianMTModel, MarianTokenizer

import config
from translation.base import BaseTranslator
from translation.text_splitter import TextSplitter
from utils.logger import get_logger


logger = get_logger(__name__)


class MarianTranslator(BaseTranslator):
    """
    Translator strategy using Helsinki-NLP MarianMT models.

    Uses the Hugging Face ``transformers`` library to load a pre-trained
    MarianMT model for sequence-to-sequence translation. Text is split
    into chunks via ``TextSplitter`` to respect model token limits.
    """

    def __init__(self) -> None:
        """
        Initialize the MarianMT model and tokenizer.

        The model name is read from ``config.TRANSLATION_MODEL``.
        """

        logger.info("Loading MarianMT translation model...")

        self.model_name: str = config.TRANSLATION_MODEL

        self.tokenizer = MarianTokenizer.from_pretrained(
            self.model_name
        )

        self.model = MarianMTModel.from_pretrained(
            self.model_name
        )

        logger.info("MarianMT translation model loaded successfully.")

    def translate(self, text: str) -> str:
        """
        Translate a long transcript chunk by chunk using MarianMT.

        The input text is split into manageable chunks using
        ``TextSplitter``, each chunk is translated independently,
        and the results are joined back together.

        Args:
            text: The source text to translate.

        Returns:
            The fully translated text.

        Raises:
            ValueError: If the input text is empty or whitespace-only.
        """

        if not text.strip():
            raise ValueError("Input text is empty.")

        logger.info("Splitting transcript into chunks...")

        chunks: list[str] = TextSplitter.split_into_chunks(
            text,
            chunk_size=80,
        )

        logger.info(f"Total chunks: {len(chunks)}")

        translated_chunks: list[str] = []

        for index, chunk in enumerate(chunks, start=1):

            logger.info(
                f"Translating chunk {index}/{len(chunks)}..."
            )

            inputs = self.tokenizer(
                chunk,
                return_tensors="pt",
                padding=True,
                truncation=True,
            )

            translated = self.model.generate(**inputs)

            translated_text: str = self.tokenizer.decode(
                translated[0],
                skip_special_tokens=True,
            )

            translated_chunks.append(translated_text)

        logger.info("MarianMT translation completed.")

        return " ".join(translated_chunks)
