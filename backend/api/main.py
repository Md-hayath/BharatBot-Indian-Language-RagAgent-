from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat, upload, health
from config.settings import FRONTEND_ORIGIN

app = FastAPI(title="BharatBot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(upload.router, tags=["Documents"])
app.include_router(chat.router, tags=["Chat"])