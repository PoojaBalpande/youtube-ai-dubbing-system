from transcription.whisper_engine import WhisperEngine
from translation.translator import Translator

translator = Translator()

with open(
    "outputs/transcript.txt",
    "r",
    encoding="utf-8",
) as file:

    text = file.read()

translated = translator.translate(text)

translator.save_translation(translated)

print(translated)