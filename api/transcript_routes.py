from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Optional
from firebase import db
from auth_routes import get_current_uid

router = APIRouter(prefix="/transcripts", tags=["transcripts"])

class Word(BaseModel):
    word: str
    start: float
    end: float

class TranscriptIn(BaseModel):
    text: str
    words: Optional[List[Word]] = None
    filename: Optional[str] = None

@router.get("")
async def list_transcripts(uid: str = Depends(get_current_uid)):
    q = db.collection("transcripts").where("uid", "==", uid).order_by("createdAt", direction="DESCENDING").stream()
    results = []
    for d in q:
        doc = d.to_dict()
        doc["id"] = d.id
        results.append(doc)
    return results

@router.post("")
async def create_transcript(payload: TranscriptIn, uid: str = Depends(get_current_uid)):
    data = {
        "uid": uid,
        "text": payload.text,
        "words": [w.dict() for w in (payload.words or [])],
        "filename": payload.filename,
        "createdAt": firestore.SERVER_TIMESTAMP,  # type: ignore
    }
    ref = db.collection("transcripts").add(data)[1]
    return {"id": ref.id, **data}

@router.get("/{tid}")
async def get_transcript(tid: str, uid: str = Depends(get_current_uid)):
    snap = db.collection("transcripts").document(tid).get()
    if not snap.exists:
        raise HTTPException(404, "Not found")
    doc = snap.to_dict()
    if doc.get("uid") != uid:
        raise HTTPException(404, "Not found")
    return {"id": snap.id, **doc}

@router.patch("/{tid}")
async def update_transcript(tid: str, text: str = Body(..., embed=True), uid: str = Depends(get_current_uid)):
    ref = db.collection("transcripts").document(tid)
    snap = ref.get()
    if not snap.exists:
        raise HTTPException(404, "Not found")
    if snap.to_dict().get("uid") != uid:
        raise HTTPException(404, "Not found")
    ref.update({"text": text})
    return {"ok": True}
