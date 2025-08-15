from fastapi import APIRouter, HTTPException, Body, Depends
from pydantic import BaseModel, EmailStr
import httpx
from settings import settings
from firebase import verify_id_token, set_display_name, get_user_record

router = APIRouter(prefix="/auth", tags=["auth"])

FIREBASE_IDP_BASE = "https://identitytoolkit.googleapis.com/v1"
SECURETOKEN_URL   = "https://securetoken.googleapis.com/v1/token"

class SignUpIn(BaseModel):
    email: EmailStr
    password: str
    display_name: str | None = None

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class RefreshIn(BaseModel):
    refresh_token: str

@router.post("/signup")
async def signup(payload: SignUpIn):
    #Create a Firebase user (email/password) and return ID/refresh tokens.
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            f"{FIREBASE_IDP_BASE}/accounts:signUp?key={settings.FIREBASE_WEB_API_KEY}",
            json={"email": payload.email, "password": payload.password, "returnSecureToken": True}
        )
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail=r.json())

    data = r.json()  # contains idToken, refreshToken, localId (uid)
    uid = data.get("localId")
    try:
        set_display_name(uid, payload.display_name)
    except Exception:
        pass

    return {
        "uid": uid,
        "id_token": data.get("idToken"),
        "refresh_token": data.get("refreshToken"),
        "email": payload.email,
        "display_name": payload.display_name,
    }

@router.post("/login")
async def login(payload: LoginIn):
    #Verify email/password with Firebase, return ID/refresh tokens.
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            f"{FIREBASE_IDP_BASE}/accounts:signInWithPassword?key={settings.FIREBASE_WEB_API_KEY}",
            json={"email": payload.email, "password": payload.password, "returnSecureToken": True}
        )
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail=r.json())

    data = r.json()
    return {
        "uid": data.get("localId"),
        "id_token": data.get("idToken"),
        "refresh_token": data.get("refreshToken"),
        "email": data.get("email"),
        "display_name": data.get("displayName"),
    }

@router.post("/refresh")
async def refresh(payload: RefreshIn):
    #Exchange refresh token for a new ID token.
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            f"{SECURETOKEN_URL}?key={settings.FIREBASE_WEB_API_KEY}",
            data={"grant_type": "refresh_token", "refresh_token": payload.refresh_token},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail=r.json())

    data = r.json()
    return {
        "uid": data.get("user_id"),
        "id_token": data.get("id_token"),
        "refresh_token": data.get("refresh_token"),
        "expires_in": data.get("expires_in"),
    }

# ---- Helpers for auth-protected routes ----
from fastapi import Header

async def get_current_uid(authorization: str = Header(...)):
    #Expect 'Authorization: Bearer <ID_TOKEN>'
    try:
        scheme, token = authorization.split(" ", 1)
        assert scheme.lower() == "bearer"
    except Exception:
        raise HTTPException(401, "Malformed Authorization header")

    try:
        uid = verify_id_token(token)
        return uid
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {e}")

@router.get("/me")
async def me(uid: str = Depends(get_current_uid)):
    user = get_user_record(uid)
    return {
        "uid": uid,
        "email": user.email,
        "display_name": user.display_name,
    }
