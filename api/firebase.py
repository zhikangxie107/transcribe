# api/firebase.py
import json, os
import firebase_admin
from firebase_admin import credentials, auth, firestore
from settings import settings

def _load_cred():
    val = settings.GOOGLE_APPLICATION_CREDENTIALS
    if os.path.isfile(val):
        return credentials.Certificate(val)
    return credentials.Certificate(json.loads(val))

if not firebase_admin._apps:
    cred = _load_cred()
    firebase_admin.initialize_app(cred, {
        "projectId": settings.FIREBASE_PROJECT_ID or None,
        # no storageBucket
    })

db = firestore.client()

print("[firebase] Firestore project =", db.project)

def verify_id_token(id_token: str) -> str:
    return auth.verify_id_token(id_token)["uid"]

def set_display_name(uid: str, display_name: str | None):
    if display_name:
        auth.update_user(uid, display_name=display_name)

def get_user_record(uid: str):
    return auth.get_user(uid)
