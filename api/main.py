from fastapi import FastAPI
from api.routes import chat, upload, health

app = FastAPI(title="BharatBot", version="1.0.0")

app.include_router(health.router, tags=["Health"])
app.include_router(upload.router, tags=["Documents"])
app.include_router(chat.router, tags=["Chat"])