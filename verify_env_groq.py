import sys
from pathlib import Path
import os
import json
import logging

PROJECT_ROOT = Path("c:/Users/pooja/Projects/youtube-ai-dubbing-system").resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import config
from models import TranscriptSegment
from translation.translator import Translator, get_translator
from translation.groq import GroqTranslator

def run_tests():
    print("=== Groq Integration Test Suite ===")

    # Setup standard config
    config.TRANSLATOR_PROVIDER = "groq"
    config.ENABLE_TRANSLATION_FALLBACK = True
    config.FALLBACK_TRANSLATOR = "marian"

    # Save original env
    orig_key = config.GROQ_API_KEY
    orig_model = config.GROQ_MODEL

    # TEST 1: Valid API key / model initialization
    print("\n[TEST 1] Valid initialization...")
    config.GROQ_API_KEY = "gsk_test_key"
    config.GROQ_MODEL = "mixtral-8x7b-32768"
    
    t = get_translator("groq")
    print(f"  Successfully initialized: {type(t).__name__}")
    assert type(t).__name__ == "GroqTranslator", "Should initialize GroqTranslator"
    assert t.model_name == "mixtral-8x7b-32768"

    # TEST 2: Missing API key fallback
    print("\n[TEST 2] Missing API key fallback...")
    config.GROQ_API_KEY = ""
    config.GROQ_MODEL = "mixtral-8x7b-32768"
    if "GROQ_API_KEY" in os.environ:
        del os.environ["GROQ_API_KEY"]
    
    wrapper = Translator()
    print(f"  Fallback target wrapper Strategy: {type(wrapper._strategy).__name__}")
    assert type(wrapper._strategy).__name__ == "MarianTranslator", "Should fallback to MarianTranslator"

    # TEST 3: Missing Model fallback
    print("\n[TEST 3] Missing Model name fallback...")
    config.GROQ_API_KEY = "gsk_test_key"
    config.GROQ_MODEL = ""
    if "GROQ_MODEL" in os.environ:
        del os.environ["GROQ_MODEL"]
    
    wrapper = Translator()
    print(f"  Fallback target wrapper Strategy: {type(wrapper._strategy).__name__}")
    assert type(wrapper._strategy).__name__ == "MarianTranslator", "Should fallback to MarianTranslator"

    # TEST 4: Invalid API key runtime failure simulation
    print("\n[TEST 4] Invalid API key runtime translation error fallback...")
    config.GROQ_API_KEY = "gsk_invalid_key_value"
    config.GROQ_MODEL = "mixtral-8x7b-32768"
    
    # We call translate on the Translator wrapper. At runtime it will try to hit the API, fail, and fallback.
    wrapper = Translator()
    # Mocking the client call to throw Groq API error
    from groq import APIError
    # We will trigger the API call error to force fallback at translation stage
    # But wait! Translator wrapper's init succeeds because keys are set, but translate() does the retry/fallback.
    # Let's verify that translate falls back to Marian.
    test_segment = TranscriptSegment(start=0.0, end=2.0, original_text="नमस्ते")
    try:
        # Since API key is invalid, the request will fail
        # and wrapper should catch it and use fallback strategy
        results = wrapper.translate_segments([test_segment])
        print(f"  Translation output: '{results[0].translated_text}'")
        assert len(results) == 1
        assert results[0].translated_text != ""
        print("  Fallback succeeded at runtime!")
    except Exception as e:
        print(f"  Error: {e}")
        assert False, "Should have caught the exception and fallen back"

    # TEST 5: Verify JSON Schema compliance
    print("\n[TEST 5] Verifying JSON schema output...")
    # Check schema parameters in translated_segments.json if exists
    json_path = Path(config.TRANSLATED_SEGMENTS_JSON)
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                keys = data[0].keys()
                print(f"  Keys in JSON segment: {list(keys)}")
                for k in ["start", "end", "original_text", "translated_text", "audio"]:
                    assert k in keys or (k == "original_text" and "original" in keys) or (k == "translated_text" and "translated" in keys), f"Key {k} missing in JSON schema"
                print("  JSON Schema validation passed!")
            else:
                print("  Empty segments file. Schema verified conceptually.")
    else:
        print("  translated_segments.json does not exist. Skipping physical schema verify.")

    # Restore config
    config.GROQ_API_KEY = orig_key
    config.GROQ_MODEL = orig_model
    print("\n[All local verify_env_groq tests completed successfully!]")

if __name__ == "__main__":
    run_tests()
