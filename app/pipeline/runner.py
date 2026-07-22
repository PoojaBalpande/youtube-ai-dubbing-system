"""
pipeline/runner.py

Single-video dubbing pipeline, extracted verbatim from the previous
main.py body so single-run and batch-run (Milestone 2) callers share
one orchestration path. Diarization (Milestone 4) is added as an
optional, config-gated step between transcription and translation;
all other modules and call order are unchanged.
"""
from pathlib import Path

from config import settings as config
from app.audio.extractor import AudioExtractor
from app.downloader.youtube import YouTubeDownloader
from app.transcription.whisper_engine import WhisperEngine
from app.translation.translator import Translator
from app.utils.logger import get_logger
from app.audio.merger import AudioMerger

logger = get_logger(__name__)


def run_pipeline(url: str) -> Path:
    """
    Run the full dubbing pipeline for a single YouTube URL.

    Args:
        url: The YouTube video URL to process.

    Returns:
        Path to the final dubbed video.
    """
    downloader = YouTubeDownloader()
    extractor = AudioExtractor()
    transcriber = WhisperEngine()
    merger = AudioMerger()

    video_path = downloader.download(url)
    logger.info(f"Video saved to: {video_path}")

    audio_path = extractor.extract(video_path)
    logger.info(f"Audio saved to: {audio_path}")

    segments = transcriber.transcribe_segments(audio_path)

    original_text = " ".join([seg.original_text for seg in segments])
    transcript_path = transcriber.save_transcript(original_text)
    logger.info(f"Transcript saved at: {transcript_path}")

    # --- Milestone 4: optional speaker diarization ---
    if getattr(config, "ENABLE_DIARIZATION", False) or getattr(config, "ENABLE_VOICE_CLONING", False) or getattr(config, "VOICE_PROVIDER", "edge") == "xtts":
        from app.diarization.speaker_detector import SpeakerDetector
        detector = SpeakerDetector()
        speaker_segments = detector.detect(audio_path)
        detector.assign_speakers_to_segments(segments, speaker_segments)
        logger.info("Speaker diarization applied to transcript segments.")

        if getattr(config, "ENABLE_VOICE_CLONING", False) or getattr(config, "VOICE_PROVIDER", "edge") == "xtts":
            from app.voice_cloning.reference_extractor import ReferenceExtractor
            extractor = ReferenceExtractor()
            speaker_refs = extractor.extract_speakers_references(audio_path, speaker_segments)
            for seg in segments:
                speaker_id = seg.metadata.get("speaker", "SPEAKER_00")
                if speaker_id in speaker_refs:
                    seg.metadata["reference_audio"] = str(speaker_refs[speaker_id])
            logger.info("Speaker reference audio clips extracted and assigned to segments.")

    translator = Translator()
    translated_segments = translator.translate_segments(segments)

    from app.tts.tts_engine import SegmentTTS
    segment_tts = SegmentTTS()

    logger.info("Starting segment-wise Text-to-Speech generation and timing analysis...")
    for index, segment in enumerate(translated_segments, start=1):
        segment.audio = segment_tts.generate_segment(segment, index)

    from app.models.segment import save_segments
    segments_path = save_segments(translated_segments, config.TRANSLATED_SEGMENTS_JSON)
    logger.info(f"Translated segments saved at: {segments_path}")

    translated_text = " ".join(
        [seg.translated_text for seg in translated_segments if seg.translated_text]
    )
    translation_path = translator.save_translation(translated_text)

    from app.timing.audio_stitcher import AudioStitcher
    stitcher = AudioStitcher()
    stitched_wav_path = config.OUTPUT_DIR / "dubbed_audio.wav"
    dubbed_audio_path = stitcher.stitch(translated_segments, stitched_wav_path)

    logger.info(f"Translated transcript saved at: {translation_path}")

    dubbed_video = merger.merge_audio(
        video_path=video_path,
        audio_path=dubbed_audio_path,
        output_path=config.DUBBED_VIDEO_OUTPUT,
    )

    logger.info("Pipeline completed successfully.")
    logger.info(f"Final video: {dubbed_video}")

    return dubbed_video
