"""
batch/batch_runner.py

Sequentially executes the dubbing pipeline across multiple YouTube URLs.
Existing modules write to fixed config paths (TRANSCRIPT_FILE,
TRANSLATION_OUTPUT_FILE, TRANSLATED_SEGMENTS_JSON, DUBBED_VIDEO_OUTPUT);
rather than modifying those modules to accept per-run paths, this runner
copies each run's outputs into a per-video results folder immediately
after that run completes, before the next run starts.
"""
import shutil
import time
from pathlib import Path

from config import settings as config
from app.pipeline.runner import run_pipeline
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BatchRunner:
    """Runs the dubbing pipeline for a batch of YouTube URLs, one at a time."""

    def __init__(self) -> None:
        self.results_dir = config.OUTPUT_DIR / "batch"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def _slugify(self, url: str, index: int) -> str:
        tail = url.rstrip("/").split("/")[-1].split("=")[-1]
        safe = "".join(c for c in tail if c.isalnum() or c in ("-", "_")) or f"video_{index}"
        return f"{index:03d}_{safe}"

    def _archive_outputs(self, slug: str) -> Path:
        """Copy this run's fixed-path outputs into a per-video folder."""
        target_dir = self.results_dir / slug
        target_dir.mkdir(parents=True, exist_ok=True)

        artifacts = [
            config.TRANSCRIPT_FILE,
            config.TRANSLATION_OUTPUT_FILE,
            config.TRANSLATED_SEGMENTS_JSON,
            config.DUBBED_VIDEO_OUTPUT,
        ]
        for artifact in artifacts:
            artifact = Path(artifact)
            if artifact.exists():
                shutil.copy2(artifact, target_dir / artifact.name)

        return target_dir

    def run(self, urls: list[str]) -> list[dict]:
        """
        Process each URL through the full pipeline, one at a time.

        Args:
            urls: List of YouTube URLs to process in order.

        Returns:
            A list of per-video result dictionaries with status and timing.
        """
        results = []
        total = len(urls)

        for index, url in enumerate(urls, start=1):
            slug = self._slugify(url, index)
            logger.info(f"[Batch {index}/{total}] Starting: {url}")
            start_time = time.time()

            try:
                run_pipeline(url)
                archive_dir = self._archive_outputs(slug)
                elapsed = time.time() - start_time
                logger.info(f"[Batch {index}/{total}] Completed in {elapsed:.1f}s. Outputs: {archive_dir}")
                results.append({
                    "url": url, "status": "success",
                    "elapsed_seconds": elapsed, "output_dir": str(archive_dir),
                })
            except Exception as error:
                elapsed = time.time() - start_time
                logger.exception(f"[Batch {index}/{total}] Failed after {elapsed:.1f}s: {error}")
                results.append({
                    "url": url, "status": "failed",
                    "elapsed_seconds": elapsed, "error": str(error),
                })

        succeeded = sum(1 for r in results if r["status"] == "success")
        logger.info(f"Batch complete: {succeeded}/{total} succeeded.")
        return results
