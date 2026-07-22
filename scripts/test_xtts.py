import os
import sys
from pathlib import Path

# Step 1: Configure Cache Location & Terms of Service programmatically
# TTS_HOME redirects the download cache folder to a local project directory.
# COQUI_TOS_AGREED programmatically accepts the Coqui Public Model License.
os.environ["TTS_HOME"] = os.path.abspath("model_cache")
os.environ["COQUI_TOS_AGREED"] = "1"

try:
    from TTS.api import TTS
except ImportError as error:
    print(f"Error: Coqui TTS is not installed in the active Python environment. Details: {error}")
    sys.exit(1)

def main() -> None:
    # Step 2: Identify a valid reference voice WAV file from the project structure
    reference_wav = Path("temp/tts_wav/segment_0001.wav")
    if not reference_wav.exists():
        print(f"Reference voice path '{reference_wav}' not found. Searching for alternatives...")
        alternative_wavs = list(Path(".").glob("temp/**/*.wav"))
        if alternative_wavs:
            reference_wav = alternative_wavs[0]
            print(f"Found alternative reference WAV: {reference_wav}")
        else:
            print("Error: No WAV file found in the workspace to act as a reference voice.")
            sys.exit(1)

    print(f"Selected reference WAV: {reference_wav.resolve()}")

    # Step 3: Initialize the XTTS-v2 model
    # It will automatically download to 'model_cache' on first run.
    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    print(f"Loading XTTS-v2 model: '{model_name}'...")
    print("If this is the first run, the model (~1.8GB) will download automatically to 'model_cache'.")
    
    try:
        import torch
        use_gpu = torch.cuda.is_available()
        print(f"Hardware Acceleration (CUDA) available: {use_gpu}")
        
        tts = TTS(model_name, gpu=use_gpu)
        print("Model loaded successfully.")

        # Step 4: Synthesize one English sentence using the reference voice
        text = "This is a test of the Coqui XTTS voice cloning system on Windows."
        output_wav = "output.wav"

        print(f"Synthesizing sentence: '{text}'...")
        tts.tts_to_file(
            text=text,
            speaker_wav=str(reference_wav),
            language="en",
            file_path=output_wav
        )
        print(f"[OK] Verification success! Output saved to: {Path(output_wav).resolve()}")

    except Exception as e:
        print(f"Error during XTTS execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
