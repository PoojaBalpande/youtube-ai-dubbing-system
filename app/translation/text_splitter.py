"""
Utility for splitting long transcripts into manageable chunks.
"""


class TextSplitter:
    """
    Splits text into chunks based on word count.
    """

    @staticmethod
    def split_into_chunks(
        text: str,
        chunk_size: int = 80,
    ) -> list[str]:
        """
        Split transcript into chunks of approximately chunk_size words.
        """

        words = text.split()

        if not words:
            return []

        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks