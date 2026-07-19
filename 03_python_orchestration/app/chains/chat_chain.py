import json
import logging
from collections.abc import AsyncIterator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.chains.errors import LLMCallError, LLMNotConfiguredError
from app.chains.prompt_loader import load_prompt_text
from app.config import settings
from app.models.requests import ChatTurn

logger = logging.getLogger(__name__)

HISTORY_WINDOW_TURNS = 10

SYSTEM_PROMPT_TEXT = load_prompt_text("chat_system.md")

CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT_TEXT),
        MessagesPlaceholder("history"),
        ("human", "{message}"),
    ],
)


def _build_model(is_streaming: bool = False) -> ChatOpenAI:
    if not settings.openrouter_api_key:
        raise LLMNotConfiguredError(
            "OPENROUTER_API_KEY is not set. Add it to your .env file to use chat.",
        )
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
        temperature=0.4,
        streaming=is_streaming,
    )


def _to_windowed_messages(history: list[ChatTurn] | None) -> list[BaseMessage]:
    windowed_turns = (history or [])[-HISTORY_WINDOW_TURNS * 2 :]
    messages: list[BaseMessage] = []
    for turn in windowed_turns:
        if turn.role == "assistant":
            messages.append(AIMessage(content=turn.content))
        else:
            messages.append(HumanMessage(content=turn.content))
    return messages


def _build_chain_input(
    message: str,
    context: dict,
    history: list[ChatTurn] | None,
) -> dict:
    return {
        "context_json": json.dumps(context, indent=2),
        "history": _to_windowed_messages(history),
        "message": message,
    }


async def run_chat(
    message: str,
    context: dict,
    history: list[ChatTurn] | None,
) -> str:
    chain = CHAT_PROMPT | _build_model() | StrOutputParser()
    try:
        return await chain.ainvoke(_build_chain_input(message, context, history))
    except LLMNotConfiguredError:
        raise
    except Exception as exc:
        raise LLMCallError(f"The chat model call failed: {exc}") from exc


async def stream_chat(
    message: str,
    context: dict,
    history: list[ChatTurn] | None,
) -> AsyncIterator[str]:
    chain = CHAT_PROMPT | _build_model(is_streaming=True) | StrOutputParser()
    try:
        async for chunk in chain.astream(_build_chain_input(message, context, history)):
            yield chunk
    except LLMNotConfiguredError:
        raise
    except Exception as exc:
        logger.error("Chat stream failed mid-response: %s", exc)
        raise LLMCallError(f"The chat model call failed: {exc}") from exc
