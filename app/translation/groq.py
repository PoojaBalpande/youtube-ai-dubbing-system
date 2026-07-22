"""
Groq API translator implementation.

Provides a translator strategy that uses the official Groq SDK
for translation. The Groq API key, model name, and prompt template
are configurable in config.py or via environment variables.
"""

import os
from groq import Groq

from config import settings as config
from app.translation.base import BaseTranslator
from app.translation.text_splitter import TextSplitter
from app.utils.logger import get_logger


logger = get_logger(__name__)


class GroqTranslator(BaseTranslator):
    """
    Translator strategy using the Groq API.

    To activate:
        1. Set ``config.GROQ_API_KEY`` or set the ``GROQ_API_KEY``
           environment variable.
        2. Configure the translation model in ``config.GROQ_MODEL``.
    """

    def __init__(self) -> None:
        """
        Initialize the Groq translator with API key, model name, and prompt template.
        """
        self.api_key: str = (
            getattr(config, "GROQ_API_KEY", "") or
            os.environ.get("GROQ_API_KEY", "")
        )
        self.model_name: str = (
            getattr(config, "GROQ_MODEL", "") or
            os.environ.get("GROQ_MODEL", "")
        )
        self.prompt_template: str = config.GROQ_TRANSLATION_PROMPT

        if not self.api_key:
            raise ValueError(
                "Groq API key is not configured. "
                "Set GROQ_API_KEY in config.py or in the environment variables."
            )

        if not self.model_name:
            raise ValueError(
                "Groq model name is not configured. "
                "Set GROQ_MODEL in config.py or in the environment variables."
            )

        logger.info(f"Initializing Groq translator...")
        logger.info(f"Groq model loaded: {self.model_name}")
        self.client = Groq(api_key=self.api_key)

    def _build_prompt(self, text: str) -> str:
        """
        Build the translation prompt by inserting source text and the
        resolved target-language name into the configured template.

        Args:
            text: The source text to embed in the prompt.

        Returns:
            The fully formatted prompt string.
        """
        target_language = getattr(config, "TARGET_LANGUAGE", "en")
        language_name = getattr(config, "LANGUAGE_NAMES", {}).get(target_language, "English")
        return self.prompt_template.format(text=text, target_language=language_name)

    def _call_groq_api(self, prompt: str) -> str:
        """
        Send a prompt to the Groq API and return the response.

        Args:
            prompt: The fully formatted prompt to send.

        Returns:
            The translated text from the Groq response.
        """
        logger.info(f"Sending request to Groq API ({self.model_name})...")
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.model_name,
            temperature=0.0,  # low temperature for accurate translation
        )

        response_text = chat_completion.choices[0].message.content
        if not response_text:
            raise RuntimeError("Groq API returned an empty or invalid response.")

        return response_text.strip()

    def translate(self, text: str) -> str:
        """
        Translate text using the Groq API.

        The input text is split into chunks if it is too long, each chunk is
        translated using the Groq API, and the results are concatenated.

        Args:
            text: The source text to translate.

        Returns:
            The fully translated text.

        Raises:
            ValueError: If the input text is empty.
            RuntimeError: If the Groq API returns an error.
        """
        if not text.strip():
            raise ValueError("Input text is empty.")

        logger.info("Starting Groq translation...")

        chunk_size = getattr(config, "GROQ_CHUNK_SIZE", 80)
        chunks: list[str] = TextSplitter.split_into_chunks(
            text,
            chunk_size=chunk_size,
        )

        logger.info(f"Total chunks to translate: {len(chunks)}")

        translated_chunks: list[str] = []

        for index, chunk in enumerate(chunks, start=1):
            logger.info(f"Translating chunk {index}/{len(chunks)} via Groq...")
            prompt: str = self._build_prompt(chunk)

            try:
                translated_text: str = self._call_groq_api(prompt)
                translated_chunks.append(translated_text)
            except Exception as error:
                logger.error(f"Groq API error on chunk {index}: {error}")
                raise RuntimeError(
                    f"Groq translation failed on chunk {index}: {error}"
                ) from error

        logger.info("Groq translation successful.")
        return " ".join(translated_chunks)
