import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path("c:/Users/pooja/Projects/youtube-ai-dubbing-system").resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import config
from models import TranscriptSegment
from translation.translator import Translator, get_translator
from translation.groq import GroqTranslator

def main():
    print("=== Groq Translator Verification ===")

    # 1. Verify environment loading
    print("\n[1] Verifying environment parameters...")
    print(f"  TRANSLATION_PROVIDER: '{config.TRANSLATOR_PROVIDER}'")
    print(f"  GROQ_MODEL: '{config.GROQ_MODEL}'")
    print(f"  GROQ_API_KEY set: {bool(config.GROQ_API_KEY)}")

    # 2. Verify Factory returns GroqTranslator
    print("\n[2] Verifying factory creation...")
    # Inject a dummy key temporarily to allow instantiation without raising ValueError
    config.GROQ_API_KEY = "test-key"
    translator_instance = get_translator("groq")
    print(f"  get_translator('groq') returned: {type(translator_instance).__name__}")
    assert type(translator_instance).__name__ == "GroqTranslator", "Factory should return GroqTranslator"

    # 3. Verify Fallback Mechanism (no API key -> fallback to Marian)
    print("\n[3] Verifying fallback to MarianMT when Groq API key is empty...")
    config.GROQ_API_KEY = ""
    config.ENABLE_TRANSLATION_FALLBACK = True
    config.FALLBACK_TRANSLATOR = "marian"
    
    print("Instantiating Translator wrapper (expected fallback to Marian)...")
    wrapper = Translator()
    print(f"Wrapper strategy initialized to: {type(wrapper._strategy).__name__}")
    assert type(wrapper._strategy).__name__ == "MarianTranslator", "Wrapper should fallback to MarianMT"

    # 4. Verify Mock GroqTranslator call execution
    print("\n[4] Verifying GroqTranslator with a mock API call...")
    class MockGroqTranslator(GroqTranslator):
        def _call_groq_api(self, prompt: str) -> str:
            return "Good morning friends. Today is a beautiful day."

    config.GROQ_API_KEY = "dummy-key"
    mock_groq = MockGroqTranslator()
    
    segments = [
        TranscriptSegment(start=0.0, end=3.0, original_text="सुप्रभात दोस्तों।"),
        TranscriptSegment(start=3.0, end=6.0, original_text="आज का दिन बहुत खूबसूरत है।")
    ]
    
    translated = mock_groq.translate_segments(segments)
    print("Mock Groq translated segments:")
    for i, seg in enumerate(translated):
        print(f"  Segment {i}: original='{repr(seg.original_text.encode('ascii', 'backslashreplace').decode('ascii'))}' translated='{seg.translated_text}'")
        
    assert translated[0].translated_text == "Good morning", "Mock segment 0 mismatch"
    assert translated[1].translated_text == "friends. Today is a beautiful day.", "Mock segment 1 mismatch"

    print("\n[Verification complete - ALL TESTS PASSED!]")

if __name__ == "__main__":
    main()
