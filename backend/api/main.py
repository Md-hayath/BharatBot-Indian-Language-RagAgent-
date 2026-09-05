from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from api.routes import chat, upload, health, documents
from api.limiter import limiter
from config.settings import FRONTEND_ORIGIN

app = FastAPI(title="BharatBot", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(upload.router, tags=["Documents"])
app.include_router(documents.router, tags=["Documents"])
app.include_router(chat.router, tags=["Chat"])