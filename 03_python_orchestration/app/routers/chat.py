import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.chains.chat_chain import run_chat, stream_chat
from app.chains.errors import LLMNotConfiguredError
from app.config import settings
from app.models.requests import ChatRequest
from app.models.responses import ChatResponse
from app.services.py_client import get_team_form
from app.services.r_client import get_leaderboard, get_team_record

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

KNOWN_TEAMS = [
    "India",
    "Australia",
    "England",
    "Pakistan",
    "New Zealand",
    "South Africa",
    "Afghanistan",
    "Sri Lanka",
]

CRICKET_TERMS = ["googly", "yorker", "maiden over", "duck", "powerplay", "strike rate"]


async def _resolve_context(message: str) -> dict:
    lowered_message = message.lower()
    context: dict = {}

    mentioned_teams = [
        team for team in KNOWN_TEAMS if team.lower() in lowered_message
    ]
    for team in mentioned_teams:
        team_context: dict = {}
        try:
            team_context["official_record"] = await get_team_record(team)
        except Exception as exc:
            logger.warning("Could not fetch r-service record for %s: %s", team, exc)
        try:
            team_context["computed_form"] = await get_team_form(team)
        except Exception as exc:
            logger.warning("Could not fetch py-data-service form for %s: %s", team, exc)
        if team_context:
            context[team] = team_context

    if "leaderboard" in lowered_message or "best" in lowered_message:
        try:
            context["leaderboard"] = await get_leaderboard("T20", "batting_avg", 10)
        except Exception as exc:
            logger.warning("Could not fetch leaderboard: %s", exc)

    mentioned_terms = [term for term in CRICKET_TERMS if term in lowered_message]
    if mentioned_terms:
        context["mentioned_terms"] = mentioned_terms

    return context


@router.post("", response_model=ChatResponse, summary="Chat about cricket stats")
async def chat(payload: ChatRequest) -> ChatResponse:
    context = await _resolve_context(payload.message)
    reply = await run_chat(payload.message, context, payload.history)
    return ChatResponse(reply=reply)


@router.post("/stream", summary="Chat about cricket stats, streamed")
async def chat_stream(payload: ChatRequest) -> StreamingResponse:
    if not settings.openrouter_api_key:
        raise LLMNotConfiguredError(
            "OPENROUTER_API_KEY is not set. Add it to your .env file to use chat.",
        )
    context = await _resolve_context(payload.message)
    return StreamingResponse(
        stream_chat(payload.message, context, payload.history),
        media_type="text/plain",
    )
