from fastapi import APIRouter, HTTPException

from app.models.match import BallEvent, TeamForm
from app.services.cricket_data import (
    CricsheetUnavailableError,
    MatchNotFoundError,
    TeamNotFoundError,
    get_match_balls,
    get_team_form,
)

router = APIRouter(prefix="/matches", tags=["matches"])
teams_router = APIRouter(prefix="/teams", tags=["teams"])

@router.get(
    "/{match_id}/balls",
    response_model=list[BallEvent],
    summary="Get ball-by-ball data for a match",
)
async def read_match_balls(match_id: str) -> list[BallEvent]:
    try:
        return await get_match_balls(match_id)
    except MatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CricsheetUnavailableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@teams_router.get(
    "/{team}/form",
    response_model=TeamForm,
    summary="Get a team's form, computed from raw ball-by-ball data",
)
async def read_team_form(team: str, match_type: str = "T20") -> TeamForm:
    try:
        return await get_team_form(team, match_type)
    except TeamNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CricsheetUnavailableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
