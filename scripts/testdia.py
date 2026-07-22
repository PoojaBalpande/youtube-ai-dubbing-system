from pyannote.audio import Pipeline
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("HUGGINGFACE_TOKEN")
print("Token loaded:", bool(token))

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=token,
)

print("Pipeline loaded successfully")