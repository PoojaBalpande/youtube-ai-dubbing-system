"""
Audio synchronization strategy engine.

Responsible for comparing expected vs. actual audio duration and determining
appropriate synchronization actions (none, pad, speed) based on configuration.
"""

from config import settings as config
from app.utils.logger import get_logger


logger = get_logger(__name__)


def analyze_timing(expected: float, actual: float) -> dict:
    """
    Compare expected vs. actual duration and make synchronization decisions.

    Rules:
        - Level 1: If absolute difference < SYNC_TOLERANCE_MS, do nothing.
        - Level 2: If actual < expected (shorter), mark for silence padding.
        - Level 3: If actual > expected (longer), mark for speed rate change,
          limiting adjustment to MAX_TTS_RATE_CHANGE.

    Args:
        expected: The expected segment duration in seconds.
        actual: The actual generated audio duration in seconds.

    Returns:
        A dictionary containing:
        - "action": The decision ("none", "pad", "speed").
        - "value": The magnitude of adjustment (padding duration in seconds,
          or speed adjustment percentage).
        - "difference": The float duration difference (actual - expected).
    """
    difference = actual - expected
    difference_ms = difference * 1000

    # Load configurations
    tolerance_ms = getattr(config, "SYNC_TOLERANCE_MS", 100)
    max_rate_change = getattr(config, "MAX_TTS_RATE_CHANGE", 15)
    enable_rate = getattr(config, "ENABLE_RATE_ADJUSTMENT", True)
    enable_pad = getattr(config, "ENABLE_SILENCE_PADDING", True)

    # Level 1: Under tolerance threshold
    if abs(difference_ms) < tolerance_ms:
        logger.debug(f"Timing difference {difference_ms:+.2f} ms is within tolerance limit ({tolerance_ms} ms).")
        return {
            "action": "none",
            "value": 0.0,
            "difference": difference
        }

    # Level 2: Actual is shorter than expected (shorter) -> Silence padding later
    if difference < 0:
        if enable_pad:
            padding_seconds = abs(difference)
            logger.info(f"Audio is shorter by {abs(difference_ms):.1f} ms. Action: pad silence ({padding_seconds:.2f}s).")
            return {
                "action": "pad",
                "value": padding_seconds,
                "difference": difference
            }
        else:
            logger.info("Audio is shorter, but silence padding is disabled. Action: none.")
            return {
                "action": "none",
                "value": 0.0,
                "difference": difference
            }

    # Level 3: Actual is longer than expected (longer) -> Speed rate change
    if difference > 0:
        if enable_rate:
            if expected <= 0:
                logger.warning("Expected duration is zero. Cannot adjust rate. Action: none.")
                return {
                    "action": "none",
                    "value": 0.0,
                    "difference": difference
                }

            # Rate change speedup ratio. E.g. actual=1.2s, expected=1.0s -> speedup by 20% (+20% in Edge-TTS)
            rate_needed = ((actual / expected) - 1.0) * 100
            
            # Cap speedup rate to limit distortion
            capped_rate = min(rate_needed, max_rate_change)
            logger.info(
                f"Audio is longer by {difference_ms:+.1f} ms (requires +{rate_needed:.1f}% speedup). "
                f"Action: speed rate change (+{capped_rate:.1f}% capped at +{max_rate_change}%)."
            )
            return {
                "action": "speed",
                "value": capped_rate,
                "difference": difference
            }
        else:
            logger.info("Audio is longer, but rate adjustment is disabled. Action: none.")
            return {
                "action": "none",
                "value": 0.0,
                "difference": difference
            }
