import os
from pathlib import Path
from typing import Optional

from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.errors import ServerError

from app.config import APP_NAME, GOOGLE_API_KEY, MODEL_NAME

os.environ.setdefault("GOOGLE_API_KEY", GOOGLE_API_KEY)

BASE_DIR = Path(__file__).resolve().parent.parent
SKILL_PATH = BASE_DIR / "skill.md"


def load_skill_instruction() -> str:
    base_instruction = (
        "Bạn là trợ lý game chuyên nghiệp cho tựa game Valorant. "
        "Hãy trả lời ngắn gọn, rõ ràng, sát thực tế và hữu ích cho người chơi. "
        "Tập trung vào: build agent, team composition, map control, economy, hướng dẫn rank, mẹo chơi, lựa chọn agent theo vai trò, chiến thuật giao tranh. "
        "Nếu người dùng hỏi về build, hãy đưa ra gợi ý rõ ràng theo vai trò như Duelist, Controller, Initiator, Sentinel. "
        "Nếu không chắc, nói rõ và đề xuất cách kiểm tra trong game hoặc cách thử nghiệm trong trận. "
        "Tránh trả lời ngoài chủ đề game Valorant."
    )

    try:
        skill_text = SKILL_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return base_instruction

    return f"{base_instruction}\n\nHướng dẫn chi tiết từ file skill.md:\n{skill_text}"


agent = Agent(
    name="valorant_agent",
    model=MODEL_NAME,
    instruction=load_skill_instruction(),
)

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service,
    artifact_service=artifact_service,
)


def _extract_text(event) -> Optional[str]:
    content = getattr(event, "content", None)
    if content is None:
        return None

    parts = getattr(content, "parts", []) or []
    for part in parts:
        text = getattr(part, "text", None)
        if text:
            return text
    return None


async def ask_agent(question: str, user_id: str = "guest") -> str:
    if not question or not question.strip():
        raise ValueError("Câu hỏi không được rỗng.")

    if not GOOGLE_API_KEY:
        raise RuntimeError("Thiếu API key. Hãy thêm GOOGLE_API_KEY hoặc GEMINI_API_KEY vào file .env")

    session = await session_service.create_session(app_name=APP_NAME, user_id=user_id)
    message = types.Content(
        role="user",
        parts=[types.Part(text=question.strip())],
    )

    last_text = "Xin lỗi, tôi chưa nhận được phản hồi từ mô hình."

    for attempt in range(1, 4):
        try:
            for event in runner.run(
                user_id=user_id,
                session_id=session.id,
                new_message=message,
            ):
                text = _extract_text(event)
                if text:
                    last_text = text
            return last_text
        except ServerError as exc:
            if attempt == 3:
                raise RuntimeError(f"Model tạm thời quá tải: {exc}") from exc
            continue

    return last_text
