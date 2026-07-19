import asyncio
import json
import os
import tempfile
import time
import zipfile
from datetime import date
from pathlib import Path

import httpx
import pandas as pd
from cricketstats.cricketstats import search as CricketStatsSearch

from app.models.match import BallEvent, RecentInnings, TeamForm


CRICSHEET_ZIP_URL = "https://cricsheet.org/downloads/t20s_json.zip"
CACHE_DIR = Path(
    os.getenv("CRICKET_DATA_CACHE_DIR")
    or Path(tempfile.gettempdir()) / "apis-all-along-cricket-data"
)
DATABASE_ZIP_PATH = CACHE_DIR / "t20s_json.zip"
CRICKETSTATS_INDEX_DIR = CACHE_DIR / "cricketstats-index"

TEAM_FORM_SEARCH_FROM_DATE = (2002, 1, 1)
TEAM_FORM_MATCH_TYPES = ["T20"]
TEAM_FORM_CACHE_TTL_SECONDS = 600
RECENT_INNINGS_LIMIT = 5


class CricketDataError(Exception):
    pass


class MatchNotFoundError(CricketDataError):
    pass


class TeamNotFoundError(CricketDataError):
    pass


class CricsheetUnavailableError(CricketDataError):
    pass


_match_json_cache: dict[str, dict] = {}
_team_form_cache: dict[str, tuple[float, TeamForm]] = {}
_real_match_id_index: dict[tuple[str, frozenset[str]], str] | None = None
_database_ready = False
_database_ready_lock = asyncio.Lock()


async def ensure_database_ready() -> None:
    global _database_ready, _real_match_id_index

    if _database_ready:
        return

    async with _database_ready_lock:
        if _database_ready:
            return
        await _download_database_if_missing()
        _real_match_id_index = await asyncio.to_thread(_build_real_match_id_index)
        _database_ready = True


def _build_real_match_id_index() -> dict[tuple[str, frozenset[str]], str]:
    index = {}

    with zipfile.ZipFile(DATABASE_ZIP_PATH) as archive:
        for filename in archive.namelist():
            if not filename.endswith(".json"):
                continue
            with archive.open(filename) as match_file:
                match_json = json.load(match_file)
            info = match_json["info"]
            key = (info["dates"][0], frozenset(team.lower() for team in info["teams"]))
            index[key] = filename.removesuffix(".json")

    return index


def _real_match_id(date_str: str | None, batting_team: str | None, bowling_team: str | None) -> str | None:
    if not date_str or not batting_team or not bowling_team or _real_match_id_index is None:
        return None
    key = (date_str, frozenset({batting_team.lower(), bowling_team.lower()}))
    return _real_match_id_index.get(key)


async def _download_database_if_missing() -> None:
    if DATABASE_ZIP_PATH.exists():
        return

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    partial_path = DATABASE_ZIP_PATH.with_suffix(".zip.part")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("GET", CRICSHEET_ZIP_URL) as response:
                response.raise_for_status()
                with open(partial_path, "wb") as database_file:
                    async for chunk in response.aiter_bytes():
                        database_file.write(chunk)
        os.replace(partial_path, DATABASE_ZIP_PATH)
    except httpx.HTTPError as exc:
        partial_path.unlink(missing_ok=True)
        raise CricsheetUnavailableError(
            "Failed to download the cricsheet match database"
        ) from exc


def _load_match_json(match_id: str) -> dict:
    if match_id in _match_json_cache:
        return _match_json_cache[match_id]

    filename = f"{match_id}.json"
    with zipfile.ZipFile(DATABASE_ZIP_PATH) as archive:
        if filename not in archive.namelist():
            raise MatchNotFoundError(f"No match found with id '{match_id}'")
        with archive.open(filename) as match_file:
            match_json = json.load(match_file)

    _match_json_cache[match_id] = match_json
    return match_json


def _build_ball_events(match_json: dict) -> list[BallEvent]:
    ball_events = []

    for innings_number, innings in enumerate(match_json["innings"], start=1):
        for over in innings["overs"]:
            for delivery in over["deliveries"]:
                over_number, ball_number = delivery["actual_delivery"].split(".")
                wickets = delivery.get("wickets", [])
                runs = delivery["runs"]
                ball_events.append(
                    BallEvent(
                        innings=innings_number,
                        over=int(over_number),
                        ball=int(ball_number),
                        batter=delivery["batter"],
                        non_striker=delivery["non_striker"],
                        bowler=delivery["bowler"],
                        runs_batter=runs["batter"],
                        runs_extras=runs["extras"],
                        runs_total=runs["total"],
                        wicket=bool(wickets),
                        wicket_kind=wickets[0]["kind"] if wickets else None,
                        player_dismissed=wickets[0]["player_out"] if wickets else None,
                    )
                )

    return ball_events


async def get_match_balls(match_id: str) -> list[BallEvent]:
    await ensure_database_ready()
    match_json = await asyncio.to_thread(_load_match_json, match_id)
    return _build_ball_events(match_json)


async def get_team_form(team: str, match_type: str = "T20") -> TeamForm:
    await ensure_database_ready()

    cache_key = f"{team.strip().lower()}:{match_type}"
    cached = _team_form_cache.get(cache_key)
    if cached is not None:
        cached_at, form = cached
        if time.monotonic() - cached_at < TEAM_FORM_CACHE_TTL_SECONDS:
            return form

    form = await asyncio.to_thread(_compute_team_form, team, match_type)
    _team_form_cache[cache_key] = (time.monotonic(), form)
    return form


def _compute_team_form(team: str, match_type: str) -> TeamForm:
    CRICKETSTATS_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    search = CricketStatsSearch(teams=[team])
    search.stats(
        str(DATABASE_ZIP_PATH),
        TEAM_FORM_SEARCH_FROM_DATE,
        (date.today().year, 12, 31),
        TEAM_FORM_MATCH_TYPES,
        matchindexfile=str(CRICKETSTATS_INDEX_DIR),
    )

    if search.result is None or team not in search.result.index:
        raise TeamNotFoundError(f"No {match_type} data found for team '{team}'")

    row = search.result.loc[team]
    if not row.get("Games"):
        raise TeamNotFoundError(f"No {match_type} data found for team '{team}'")

    return TeamForm(
        team=team,
        match_type=match_type,
        games=_int_or_none(row.get("Games")),
        won=_int_or_none(row.get("Won")),
        win_percentage=_float_or_none(row.get("Win %")),
        runs=_int_or_none(row.get("Runs")),
        recent_innings=_recent_innings_from(search.inningsresult),
    )


def _recent_innings_from(innings_df: pd.DataFrame) -> list[RecentInnings]:
    if innings_df is None or innings_df.empty:
        return []

    recent = innings_df.sort_values("Date", ascending=False).head(RECENT_INNINGS_LIMIT)
    innings_list = []
    for _, row in recent.iterrows():
        date_str = str(row["Date"].date()) if pd.notna(row["Date"]) else None
        batting_team = _str_or_none(row.get("Batting Team"))
        bowling_team = _str_or_none(row.get("Bowling Team"))
        real_match_id = _real_match_id(date_str, batting_team, bowling_team)
        innings_list.append(
            RecentInnings(
                match_id=real_match_id or str(row["MatchID"]),
                date=date_str,
                venue=_str_or_none(row.get("Venue")),
                batting_team=batting_team,
                bowling_team=bowling_team,
                score=_float_or_none(row.get("Score")),
                overs=_float_or_none(row.get("Overs")),
                match_winner=_str_or_none(row.get("Match Winner")),
            )
        )
    return innings_list


def _int_or_none(value) -> int | None:
    return None if pd.isna(value) else int(value)


def _float_or_none(value) -> float | None:
    return None if pd.isna(value) else float(value)


def _str_or_none(value) -> str | None:
    return None if pd.isna(value) else str(value)
