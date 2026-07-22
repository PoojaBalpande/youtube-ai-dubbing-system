from TTS.api import TTS
import torch

print("Import OK")

tts = TTS(
    "tts_models/multilingual/multi-dataset/xtts_v2",
    gpu=torch.cuda.is_available()
)

print("Model loaded OK")