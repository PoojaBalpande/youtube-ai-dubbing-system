import sys
from config import settings as config

from app.pipeline.runner import run_pipeline
from app.utils.logger import get_logger


def _resolve_urls() -> list[str]:
    """Resolve URLs from CLI args, a urls.txt file, or an interactive prompt."""
    args = sys.argv[1:]

    if not args:
        url = input("Enter YouTube URL: ").strip()
        return [url]

    if len(args) == 1 and args[0].lower().endswith(".txt"):
        with open(args[0], "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]

    return args


def main() -> None:
    """
    Entry point of the application. Supports:
        python main.py                  (interactive prompt, single video)
        python main.py <url>            (single video)
        python main.py <url1> <url2>    (batch)
        python main.py urls.txt         (batch, one URL per line)
    """
    logger = get_logger(__name__)

    from app.utils.validator import validate_config
    validate_config()

    urls = _resolve_urls()

    if len(urls) == 1:
        try:
            run_pipeline(urls[0])
        except Exception as error:
            logger.exception(f"Application failed: {error}")
    else:
        from app.batch.batch_runner import BatchRunner
        BatchRunner().run(urls)


if __name__ == "__main__":
    main()