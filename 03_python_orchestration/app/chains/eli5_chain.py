import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from app.chains.errors import LLMCallError, LLMNotConfiguredError
from app.chains.prompt_loader import load_prompt_text
from app.config import settings

TEAM_PROMPT = ChatPromptTemplate.from_template(load_prompt_text("eli5_team.md"))
LEADERBOARD_PROMPT = ChatPromptTemplate.from_template(
    load_prompt_text("eli5_leaderboard.md"),
)
TERM_PROMPT = ChatPromptTemplate.from_template(load_prompt_text("eli5_term.md"))


def _build_model() -> ChatOpenAI:
    if not settings.openrouter_api_key:
        raise LLMNotConfiguredError(
            "OPENROUTER_API_KEY is not set. Add it to your .env file to use "
            "the ELI5 endpoints.",
        )
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
        temperature=0.4,
    )


async def _invoke(chain: Runnable, inputs: dict) -> str:
    try:
        return await chain.ainvoke(inputs)
    except LLMNotConfiguredError:
        raise
    except Exception as exc:
        raise LLMCallError(f"The ELI5 model call failed: {exc}") from exc


async def run_team_eli5(team: str, format: str, stats: dict) -> str:
    chain = TEAM_PROMPT | _build_model() | StrOutputParser()
    return await _invoke(
        chain,
        {
            "team": team,
            "format": format,
            "stats_json": json.dumps(stats, indent=2),
        },
    )


async def run_leaderboard_eli5(format: str, metric: str, leaderboard: list) -> str:
    chain = LEADERBOARD_PROMPT | _build_model() | StrOutputParser()
    return await _invoke(
        chain,
        {
            "format": format,
            "metric": metric,
            "leaderboard_json": json.dumps(leaderboard, indent=2),
        },
    )


async def run_term_eli5(term: str) -> str:
    chain = TERM_PROMPT | _build_model() | StrOutputParser()
    return await _invoke(chain, {"term": term})
