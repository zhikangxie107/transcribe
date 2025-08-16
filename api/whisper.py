# api/whisper.py
import os
import tempfile
from typing import Optional, Tuple, List, Dict

import torch
from transformers import pipeline


MODEL_ID="openai/whisper-small"
DEVICE = 0 if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32

pipe = pipeline(
    "automatic-speech-recognition",
    model=MODEL_ID,
    device=DEVICE,
    torch_dtype=DTYPE,
    chunk_length_s=30,
)
_CT_EXT = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/opus": ".ogg",
    "audio/mp4": ".m4a",
    "audio/m4a": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
}

def _choose_suffix(filename: Optional[str], content_type: Optional[str]) -> str:
    if filename and os.path.splitext(filename)[1]:
        return os.path.splitext(filename)[1]
    if content_type in _CT_EXT:
        return _CT_EXT[content_type]
    return ".wav"

def _extract_words(result: Dict) -> List[Dict]:
    """
    The HF whisper pipeline returns:
      result["text"]: full text
      result["chunks"]: list of segments; with return_timestamps="word", chunks are words
    Each chunk: {"text": "word", "timestamp": (start, end)}
    """
    out = []
    for ch in result.get("chunks", []):
        w = (ch.get("text") or "").strip()
        ts = ch.get("timestamp") or (None, None)
        if w:
            out.append({"word": w, "start": ts[0], "end": ts[1]})
    return out

async def transcribe_file(
    data: bytes,
    *,
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
    language: Optional[str] = None,
) -> Tuple[str, List[Dict]]:
    # Write to a temp file so the pipeline can let ffmpeg decode it
    suffix = _choose_suffix(filename, content_type)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        generate_kwargs = {"task": "transcribe"}
        if language:
            # Whisper understands language code tokens; passing here hints the decoder
            generate_kwargs["language"] = language

        result = pipe(
            tmp_path,
            return_timestamps="word",
            generate_kwargs=generate_kwargs,
        )
        text = result.get("text", "")
        words = _extract_words(result)
        return text, words
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
