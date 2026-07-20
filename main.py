import config

from audio.extractor import AudioExtractor
from downloader.youtube import YouTubeDownloader
from transcription.whisper_engine import WhisperEngine
from translation.translator import Translator
from utils.logger import get_logger
from audio.merger import AudioMerger


def main() -> None:
    """
    Entry point of the application.
    """

    logger = get_logger(__name__)

    # Centralized Configuration & Dependency Validation
    from utils.validator import validate_config
    validate_config()

    url = input("Enter YouTube URL: ").strip()

    downloader = YouTubeDownloader()
    extractor = AudioExtractor()
    transcriber = WhisperEngine()
    merger = AudioMerger()
    
    try:
        # Download video
        video_path = downloader.download(url)
        logger.info(f"Video saved to: {video_path}")

        # Extract audio
        audio_path = extractor.extract(video_path)
        logger.info(f"Audio saved to: {audio_path}")

        # Transcribe audio to segments
        segments = transcriber.transcribe_segments(audio_path)

        # Save transcript text for debugging/inspection (optional output)
        original_text = " ".join([seg.original_text for seg in segments])
        transcript_path = transcriber.save_transcript(original_text)
        logger.info(f"Transcript saved at: {transcript_path}")

        # Create translator only when needed to avoid unnecessary resource usage
        translator = Translator()

        # Translate segments
        translated_segments = translator.translate_segments(segments)

        # Run segment-wise TTS and timing engine analysis
        from tts.tts_engine import SegmentTTS
        segment_tts = SegmentTTS()
        
        logger.info("Starting segment-wise Text-to-Speech generation and timing analysis...")
        for index, segment in enumerate(translated_segments, start=1):
            segment.audio = segment_tts.generate_segment(segment, index)

        # Save translated segments with audio metadata to JSON
        from models.segment import save_segments
        segments_path = save_segments(translated_segments, config.TRANSLATED_SEGMENTS_JSON)
        logger.info(f"Translated segments saved at: {segments_path}")

        # Join translated segments to get full translated text for TTS compatibility
        translated_text = " ".join([seg.translated_text for seg in translated_segments if seg.translated_text])

        translation_path = translator.save_translation(
            translated_text
        )
        
        # Stitch individual segment audios into a single synchronized final WAV audio track
        from timing.audio_stitcher import AudioStitcher
        stitcher = AudioStitcher()
        stitched_wav_path = config.OUTPUT_DIR / "dubbed_audio.wav"
        dubbed_audio_path = stitcher.stitch(translated_segments, stitched_wav_path)

        logger.info(
            f"Translated transcript saved at: {translation_path}"
        )
        
        # Merge stitched synchronized audio WAV with original video
        dubbed_video = merger.merge_audio(
            video_path=video_path,
            audio_path=dubbed_audio_path,
            output_path=config.DUBBED_VIDEO_OUTPUT, 
        )
        
        logger.debug(f"Loaded config module path: {config.__file__}")

        logger.info("Pipeline completed successfully.")
        
        logger.info("AI dubbing completed successfully!")
        logger.info(f"Final video: {dubbed_video}")

    except Exception as error:
        logger.exception(f"Application failed: {error}")


if __name__ == "__main__":
    main()