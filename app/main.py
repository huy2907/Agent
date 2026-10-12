from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.agent_service import ask_agent
from app.config import APP_NAME

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"

app = FastAPI(
    title="VALORANT Companion API",
    description="Game assistant chuyên về Valorant với giao diện web và chat AI",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class ChatRequest(BaseModel):
    message: str
    user_id: str = "guest"


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "index.html")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app_name": APP_NAME}


@app.post("/chat")
async def chat(request: ChatRequest) -> dict:
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="message không được để trống")

    try:
        answer = await ask_agent(request.message, user_id=request.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Lỗi từ mô hình AI: {exc}") from exc

    return {
        "user_id": request.user_id,
        "question": request.message,
        "answer": answer,
    }
