import httpx
from fastapi import HTTPException

from app.config import settings


async def get_team_form(team: str, match_type: str = "T20") -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.py_data_url}/teams/{team}/form",
                params={"match_type": match_type},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"py-data-service error fetching form for {team}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"py-data-service unreachable while fetching form for {team}",
            ) from exc


async def get_match_balls(match_id: str) -> list:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.py_data_url}/matches/{match_id}/balls",
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"py-data-service error fetching balls for match {match_id}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"py-data-service unreachable while fetching balls "
                f"for match {match_id}",
            ) from exc


async def is_healthy() -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.py_data_url}/health",
                timeout=3.0,
            )
            response.raise_for_status()
            return True
        except httpx.HTTPError:
            return False
