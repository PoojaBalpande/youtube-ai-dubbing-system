"""
Timing engine package for audio duration calculation and sync analysis.
"""

from timing.duration import calculate_expected_duration, calculate_actual_duration
from timing.sync import analyze_timing

__all__ = [
    "calculate_expected_duration",
    "calculate_actual_duration",
    "analyze_timing",
]
