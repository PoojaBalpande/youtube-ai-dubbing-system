"""
voice_cloning/voice_cloning_factory.py

Factory for voice-cloning backends. New providers are added by
registering a (module_path, class_name) pair; no caller changes needed.
"""
from config import settings as config
from app.voice_cloning.base import BaseVoiceCloner
from app.utils.logger import get_logger

logger = get_logger(__name__)

_CLONER_REGISTRY: dict[str, tuple[str, str]] = {
    "xtts": ("app.voice_cloning.xtts_cloner", "XTTSCloner"),
}


def get_voice_cloner(provider: str | None = None) -> BaseVoiceCloner:
    """
    Return an instance of the configured voice-cloning backend.

    Args:
        provider: Optional override; defaults to config.VOICE_CLONING_PROVIDER.

    Returns:
        A BaseVoiceCloner implementation.
    """
    selected = (provider or getattr(config, "VOICE_CLONING_PROVIDER", "xtts")).lower().strip()

    if selected not in _CLONER_REGISTRY:
        supported = ", ".join(sorted(_CLONER_REGISTRY.keys()))
        raise ValueError(f"Unknown voice cloning provider: '{selected}'. Supported: {supported}")

    module_path, class_name = _CLONER_REGISTRY[selected]
    logger.info(f"Creating voice cloner: provider='{selected}'")

    import importlib
    module = importlib.import_module(module_path)
    cloner_class = getattr(module, class_name)
    return cloner_class()
