from fastapi import APIRouter

from app.chains.eli5_chain import run_leaderboard_eli5, run_team_eli5, run_term_eli5
from app.models.cricket import LeaderboardEntry
from app.models.responses import ELI5Response, LeaderboardELI5Response
from app.services.r_client import get_leaderboard, get_team_record

router = APIRouter(prefix="/eli5", tags=["eli5"])


def _to_leaderboard_entries(
    raw_entries: list[dict],
    metric: str,
) -> list[LeaderboardEntry]:
    return [
        LeaderboardEntry(
            rank=entry.get("rank", index + 1),
            name=entry.get("name", "Unknown"),
            value=entry.get(metric, 0.0),
            metric=metric,
        )
        for index, entry in enumerate(raw_entries)
    ]


@router.get(
    "/team/{team}",
    response_model=ELI5Response,
    summary="Explain a team's batting record in plain English",
)
async def explain_team(team: str, format: str = "T20") -> ELI5Response:
    stats = await get_team_record(team)
    explanation = await run_team_eli5(team, format, stats)
    return ELI5Response(explanation=explanation, raw_data=stats)


@router.get(
    "/leaderboard/{format}",
    response_model=LeaderboardELI5Response,
    summary="Explain a leaderboard in plain English",
)
async def explain_leaderboard(
    format: str,
    metric: str = "batting_avg",
    n: int = 10,
) -> LeaderboardELI5Response:
    raw_leaderboard = await get_leaderboard(format, metric, n)
    summary = await run_leaderboard_eli5(format, metric, raw_leaderboard)
    entries = _to_leaderboard_entries(raw_leaderboard, metric)
    return LeaderboardELI5Response(entries=entries, summary=summary)


@router.get(
    "/term/{term}",
    response_model=ELI5Response,
    summary="Explain a cricket term in plain English",
)
async def explain_term(term: str) -> ELI5Response:
    explanation = await run_term_eli5(term)
    return ELI5Response(explanation=explanation, raw_data={"term": term})
