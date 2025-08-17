from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from settings import settings
from auth_routes import router as auth_router
from transcript_routes import router as transcripts_router

app = FastAPI(title="ASR API")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(transcripts_router)
