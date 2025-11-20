import os
import uuid
import tempfile
import os
from faster_whisper import WhisperModel


WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "small")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")         
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")  

print(f"[Whisper] Loading model={WHISPER_MODEL_SIZE}, device={WHISPER_DEVICE}, compute={WHISPER_COMPUTE_TYPE}")
model = WhisperModel(
    WHISPER_MODEL_SIZE,
    device=WHISPER_DEVICE,
    compute_type=WHISPER_COMPUTE_TYPE,
)

def transcribe_audio_bytes(audio_bytes: bytes, language: str = "fr") -> str:
    """
    1. Sauvegarde le chunk audio dans un fichier temporaire
    2. Transcrit avec Whisper (avec VAD activé)
    3. Renvoie le texte
    """
  
    tmp_dir = tempfile.gettempdir()
    tmp_name = os.path.join(tmp_dir, f"{uuid.uuid4()}.mp4")

    with open(tmp_name, "wb") as f:
        f.write(audio_bytes)

    
    segments, info = model.transcribe(
        tmp_name,
        language=language,
        beam_size=5,
        vad_filter=True,
        vad_parameters={
            "min_silence_duration_ms": 500
        },
    )


    text = " ".join(seg.text for seg in segments).strip()

  
    try:
        os.remove(tmp_name)
    except FileNotFoundError:
        pass

    return text
