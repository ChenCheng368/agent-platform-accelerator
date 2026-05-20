from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.agent.orchestrator import AgentOrchestrator
from app.iac_engine.generator import IaCGenerator

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    iac_format: str | None = None  # "bicep" or "terraform"


class ChatResponse(BaseModel):
    reply: str
    iac_code: str | None = None
    pattern_used: str | None = None
    files: list[dict] | None = None


class PatternListResponse(BaseModel):
    patterns: list[dict]


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, settings: Settings = Depends(get_settings)):
    orchestrator = AgentOrchestrator(settings)
    result = await orchestrator.process_message(
        message=request.message,
        session_id=request.session_id,
        iac_format=request.iac_format or settings.default_iac_format,
    )
    return ChatResponse(**result)


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, settings: Settings = Depends(get_settings)):
    orchestrator = AgentOrchestrator(settings)

    async def event_generator():
        async for chunk in orchestrator.process_message_stream(
            message=request.message,
            session_id=request.session_id,
            iac_format=request.iac_format or settings.default_iac_format,
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/patterns", response_model=PatternListResponse)
async def list_patterns():
    generator = IaCGenerator()
    patterns = generator.list_patterns()
    return PatternListResponse(patterns=patterns)


@router.get("/patterns/{pattern_id}")
async def get_pattern(pattern_id: str):
    generator = IaCGenerator()
    return generator.get_pattern_details(pattern_id)
