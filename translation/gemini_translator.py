"""
Google Gemini translator implementation.

Provides a translator strategy that uses the official Google Gemini SDK
for translation. The Gemini API key and prompt template are configurable in config.py
or via environment variables.
"""

import os
import google.generativeai as genai

import config
from translation.base import BaseTranslator
from translation.text_splitter import TextSplitter
from utils.logger import get_logger


logger = get_logger(__name__)


class GeminiTranslator(BaseTranslator):
    """
    Translator strategy using the Google Gemini API.

    To activate:
        1. Set ``config.GEMINI_API_KEY`` or set the ``GEMINI_API_KEY``
           environment variable.
        2. Configure the translation instructions in ``config.GEMINI_TRANSLATION_PROMPT``.
    """

    def __init__(self) -> None:
        """
        Initialize the Gemini translator with API key and prompt template.

        Reads the API key from config.py or fallback to environmental variables.
        """
        # Read from config first, fallback to environment variable
        self.api_key: str = (
            getattr(config, "GEMINI_API_KEY", "") or 
            os.environ.get("GEMINI_API_KEY", "")
        )
        self.prompt_template: str = config.GEMINI_TRANSLATION_PROMPT
        self.model_name: str = getattr(config, "GEMINI_MODEL", "gemini-1.5-flash")

        if not self.api_key:
            raise ValueError(
                "Gemini API key is not configured. "
                "Set GEMINI_API_KEY in config.py or in the environment variables."
            )

        logger.info(f"GeminiTranslator initialized using model: {self.model_name}")

    def _build_prompt(self, text: str) -> str:
        """
        Build the translation prompt by inserting source text
        into the configured template.

        Args:
            text: The source text to embed in the prompt.

        Returns:
            The fully formatted prompt string.
        """
        return self.prompt_template.format(text=text)

    def _call_gemini_api(self, prompt: str) -> str:
        """
        Send a prompt to the Gemini API and return the response.

        Args:
            prompt: The fully formatted prompt to send.

        Returns:
            The translated text from the Gemini response.
        """
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model_name)
        
        logger.info(f"Sending prompt to Gemini API ({self.model_name})...")
        response = model.generate_content(prompt)
        
        if not response.text:
            raise RuntimeError("Gemini API returned an empty or invalid response.")
            
        return response.text.strip()

    def translate(self, text: str) -> str:
        """
        Translate text using the Google Gemini API.

        The input text is split into chunks if it is too long, each chunk is
        translated using the Gemini API, and the results are concatenated.

        Args:
            text: The source text to translate.

        Returns:
            The fully translated text.

        Raises:
            ValueError: If the input text is empty.
            RuntimeError: If the Gemini API returns an error.
        """
        if not text.strip():
            raise ValueError("Input text is empty.")

        logger.info("Starting Gemini translation...")

        chunks: list[str] = TextSplitter.split_into_chunks(
            text,
            chunk_size=80,
        )

        logger.info(f"Total chunks to translate: {len(chunks)}")

        translated_chunks: list[str] = []

        for index, chunk in enumerate(chunks, start=1):
            logger.info(f"Translating chunk {index}/{len(chunks)} via Gemini...")
            prompt: str = self._build_prompt(chunk)

            try:
                translated_text: str = self._call_gemini_api(prompt)
                translated_chunks.append(translated_text)
            except Exception as error:
                logger.error(f"Gemini API error on chunk {index}: {error}")
                raise RuntimeError(
                    f"Gemini translation failed on chunk {index}: {error}"
                ) from error

        logger.info("Gemini translation completed.")
        return " ".join(translated_chunks)
