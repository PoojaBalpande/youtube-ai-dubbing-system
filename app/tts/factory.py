"""
tts/factory.py

Factory registry for Text-to-Speech providers.
"""
from config import settings as config
from app.tts.provider import BaseTTSProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)

_PROVIDER_REGISTRY: dict[str, tuple[str, str]] = {
    "edge": ("app.tts.edge_provider", "EdgeTTSProvider"),
    "xtts": ("app.tts.xtts_provider", "XTTSProvider"),
}

# Cache for the loaded provider instance (singleton pattern)
_provider_instance: BaseTTSProvider | None = None


def get_tts_provider(provider_name: str | None = None) -> BaseTTSProvider:
    """
    Get a Text-to-Speech provider instance. Reuses the active singleton instance if available.

    Args:
        provider_name: Optional provider override (e.g. "edge", "xtts").
                       Defaults to config.VOICE_PROVIDER.

    Returns:
        A BaseTTSProvider instance.
    """
    global _provider_instance
    
    selected = (provider_name or getattr(config, "VOICE_PROVIDER", "edge")).lower().strip()
    
    if selected not in _PROVIDER_REGISTRY:
        supported = ", ".join(sorted(_PROVIDER_REGISTRY.keys()))
        raise ValueError(f"Unknown TTS provider: '{selected}'. Supported: {supported}")
        
    # Reuse the cached singleton instance to avoid reloading models (Objective 1)
    if _provider_instance is not None and _provider_instance.__class__.__name__.lower().startswith(selected):
        return _provider_instance
        
    module_path, class_name = _PROVIDER_REGISTRY[selected]
    logger.info(f"Instantiating TTS provider: {class_name} (module={module_path})...")
    
    import importlib
    module = importlib.import_module(module_path)
    provider_class = getattr(module, class_name)
    
    _provider_instance = provider_class()
    return _provider_instance


def reset_tts_provider() -> None:
    """Reset the singleton provider instance (useful for testing or switching providers)."""
    global _provider_instance
    _provider_instance = None
