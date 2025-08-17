# api/transcript_routes.py
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List, Dict
from firebase_admin import firestore

from auth_routes import get_current_uid
from firebase import db
from whisper import transcribe_file

router = APIRouter(prefix="/transcripts", tags=["transcripts"])

class Word(BaseModel):
    word: str
    start: float | None = None
    end: float | None = None

class TranscriptCreate(BaseModel):
    text: str
    words: Optional[List[Word]] = None
    filename: Optional[str] = None

class TranscriptUpdate(BaseModel):
    text: Optional[str] = None
    filename: Optional[str] = None

def _serialize_snap(snap):
    """Make Firestore docs JSON-safe (convert Timestamp -> ISO)."""
    doc = snap.to_dict() or {}
    ts = doc.get("createdAt")
    if hasattr(ts, "to_datetime"):
        doc["createdAt"] = ts.to_datetime().isoformat()
    return {"id": snap.id, **doc}

@router.get("")
async def list_transcripts(uid: str = Depends(get_current_uid)):
    q = (
        db.collection("transcripts")
        .where("uid", "==", uid)
        .order_by("createdAt", direction=firestore.Query.DESCENDING)
        .stream()
    )
    return [_serialize_snap(s) for s in q]

@router.get("/{tid}")
async def get_transcript(tid: str, uid: str = Depends(get_current_uid)):
    snap = db.collection("transcripts").document(tid).get()
    if not snap.exists:
        raise HTTPException(404, "Not found")
    doc = snap.to_dict()
    if doc.get("uid") != uid:
        raise HTTPException(404, "Not found")
    return _serialize_snap(snap)

@router.post("")
async def create_transcript(payload: TranscriptCreate, uid: str = Depends(get_current_uid)):
    data = {
        "uid": uid,
        "text": payload.text,
        "words": [w.model_dump() for w in (payload.words or [])],
        "filename": payload.filename,
        "model": "openai/whisper-large-v3",
        "createdAt": firestore.SERVER_TIMESTAMP,
    }
    ref = db.collection("transcripts").add(data)[1]
    return _serialize_snap(ref.get())

@router.patch("/{tid}")
async def update_transcript(
    tid: str,
    payload: TranscriptUpdate = Body(...),
    uid: str = Depends(get_current_uid),
):
    ref = db.collection("transcripts").document(tid)
    snap = ref.get()
    if not snap.exists:
        raise HTTPException(404, "Not found")
    doc = snap.to_dict()
    if doc.get("uid") != uid:
        raise HTTPException(404, "Not found")

    updates: Dict[str, str] = {}
    if payload.text is not None:
        updates["text"] = payload.text
    if payload.filename is not None:
        updates["filename"] = payload.filename
    if updates:
        ref.update(updates)
    return {"ok": True}

@router.delete("/{tid}")
async def delete_transcript(tid: str, uid: str = Depends(get_current_uid)):
    ref = db.collection("transcripts").document(tid)
    snap = ref.get()
    if not snap.exists:
        return {"ok": True}
    doc = snap.to_dict()
    if doc.get("uid") != uid:
        raise HTTPException(404, "Not found")
    ref.delete()
    return {"ok": True}

@router.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None),
    tid: Optional[str] = Form(None),
    uid: str = Depends(get_current_uid),
):
    data = await audio.read()
    if not data:
        raise HTTPException(400, "Empty audio upload")

    text, words = await transcribe_file(
        data,
        filename=audio.filename,
        content_type=audio.content_type,
        language=language,
    )

    if tid:
        ref = db.collection("transcripts").document(tid)
        snap = ref.get()
        if not snap.exists:
            raise HTTPException(404, "Transcript not found")
        doc = snap.to_dict()
        if doc.get("uid") != uid:
            raise HTTPException(404, "Transcript not found")

        ref.update({
            "text": text,
            "words": words,
            "filename": audio.filename,
        })
        return _serialize_snap(ref.get())

    doc = {
        "uid": uid,
        "filename": audio.filename,
        "text": text,
        "words": words,
        "model": "openai/whisper-large-v3",
        "createdAt": firestore.SERVER_TIMESTAMP,
    }
    ref = db.collection("transcripts").add(doc)[1]
    return _serialize_snap(ref.get())
