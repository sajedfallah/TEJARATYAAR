from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.2.0")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "api"}
