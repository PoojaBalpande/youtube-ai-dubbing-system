"""
Context builder module for the translation pipeline.

Provides utility functions to merge neighboring TranscriptSegment objects into
larger context-preserving translation windows, and to redistribute the translated
text back into the original segments proportionally. Contains no translation logic.
"""

import config
from models.segment import TranscriptSegment
from utils.logger import get_logger


logger = get_logger(__name__)


class ContextBuilder:
    """
    Groups and merges segments into context windows, mapping translated text
    back to original segments proportionally based on original word count.
    """

    @staticmethod
    def build_windows(
        segments: list[TranscriptSegment],
        window_size: int | None = None
    ) -> list[tuple[list[TranscriptSegment], str]]:
        """
        Groups consecutive segments into translation windows.

        Args:
            segments: A list of TranscriptSegment objects.
            window_size: Number of segments per window. If None, read from config.

        Returns:
            A list of tuples, each containing:
            - The original list of TranscriptSegment objects in the window.
            - A concatenated string of original text from those segments.
        """
        if window_size is None:
            window_size = getattr(config, "CONTEXT_WINDOW", 3)

        logger.info(f"Grouping {len(segments)} segments into windows (size={window_size})...")

        windows = []
        for i in range(0, len(segments), window_size):
            window_segs = segments[i:i + window_size]
            # Join segment text with spaces, filtering out empty entries
            window_text = " ".join(
                [seg.original_text.strip() for seg in window_segs if seg.original_text.strip()]
            )
            windows.append((window_segs, window_text))

        logger.info(f"Created {len(windows)} translation windows.")
        return windows

    @staticmethod
    def redistribute(
        window_segments: list[TranscriptSegment],
        translated_text: str
    ) -> None:
        """
        Redistributes the translated window text back into individual segments
        using a word-level proportional allocation strategy.

        Assumptions & Logic:
        - Words in the target language correspond sequentially/proportionally to
          the length of the source segments.
        - Spacing at word boundaries is sufficient for division.
        - Handled safely when translated_text is shorter or longer than expected.
        """
        translated_words = translated_text.split()

        if not translated_words:
            for seg in window_segments:
                seg.translated_text = ""
            return

        orig_word_counts = [len(seg.original_text.split()) for seg in window_segments]
        total_orig_words = sum(orig_word_counts)

        if total_orig_words == 0:
            # If all segments were empty, divide words equally among segments
            num_segs = len(window_segments)
            words_per_seg = len(translated_words) // num_segs
            for i, seg in enumerate(window_segments):
                start_idx = i * words_per_seg
                end_idx = (i + 1) * words_per_seg if i < num_segs - 1 else len(translated_words)
                seg.translated_text = " ".join(translated_words[start_idx:end_idx])
            return

        current_idx = 0
        for i, seg in enumerate(window_segments):
            orig_count = orig_word_counts[i]
            share = orig_count / total_orig_words
            num_words_to_assign = int(round(share * len(translated_words)))

            # If it's the last segment, assign all remaining words
            if i == len(window_segments) - 1:
                assigned = translated_words[current_idx:]
            else:
                # Ensure at least 1 word gets assigned if original had words and we have remaining words
                if num_words_to_assign == 0 and orig_count > 0 and current_idx < len(translated_words):
                    num_words_to_assign = 1
                assigned = translated_words[current_idx:current_idx + num_words_to_assign]
                current_idx += len(assigned)

            seg.translated_text = " ".join(assigned)
