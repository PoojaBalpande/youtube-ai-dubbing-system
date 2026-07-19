"""
Translation module using MarianMT.
"""

from pathlib import Path

from utils.logger import get_logger

from transformers import (
    MarianMTModel,
    MarianTokenizer,
)

import config


logger = get_logger(__name__)


class Translator:
    """
    Translator class for translating text into English.
    """

    def __init__(self):
        """
        Initialize translation model and tokenizer.
        """

        logger.info("Loading translation model...")

        try:
            self.model_name = config.TRANSLATION_MODEL

            self.tokenizer = MarianTokenizer.from_pretrained(
                self.model_name
            )

            self.model = MarianMTModel.from_pretrained(
                self.model_name
            )

            logger.info(
                "Translation model loaded successfully."
            )

        except Exception as e:
            logger.exception(
                "Failed to load translation model."
            )
            raise e

    def translate(self, text: str) -> str:
        """
        Translate text into English.
        """

        if not text.strip():
            raise ValueError("Input text is empty.")

        logger.info("Starting translation...")

        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
            )

            translated_tokens = self.model.generate(
                **inputs
            )

            translated_text = self.tokenizer.decode(
                translated_tokens[0],
                skip_special_tokens=True,
            )

            logger.info("Translation completed.")

            return translated_text

        except Exception as e:
            logger.exception(
                "Translation failed."
            )
            raise e

    def save_translation(
        self,
        translated_text: str,
    ) -> Path:
        """
        Save translated text to file.
        """

        output_path = config.TRANSLATION_OUTPUT_FILE

        try:

            with open(
                output_path,
                "w",
                encoding="utf-8",
            ) as file:

                file.write(translated_text)

            logger.info(
                f"Translation saved to {output_path}"
            )

            return output_path

        except Exception as e:

            logger.exception(
                "Failed to save translation."
            )

            raise e