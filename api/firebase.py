import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from settings import settings

if not firebase_admin._apps:
    cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
    firebase_admin.initialize_app(cred, {
        "storageBucket": settings.FIREBASE_STORAGE_BUCKET or None
    })

db = firestore.client()
bucket = storage.bucket() if settings.FIREBASE_STORAGE_BUCKET else None

def verify_id_token(id_token: str) -> str:
    """Verify Firebase ID token and return uid."""
    decoded = auth.verify_id_token(id_token)
    return decoded["uid"]

def set_display_name(uid: str, display_name: str | None):
    if display_name:
        auth.update_user(uid, display_name=display_name)

def get_user_record(uid: str):
    return auth.get_user(uid)
