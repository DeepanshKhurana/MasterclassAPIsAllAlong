import httpx
from fastapi import HTTPException

from app.config import settings


async def get_leaderboard(fmt: str, metric: str, n: int) -> list:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.r_service_url}/leaderboard/{fmt}",
                params={"metric": metric, "n": n},
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()["data"]
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"r-service error fetching {fmt} leaderboard by {metric}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail="r-service unreachable while fetching leaderboard",
            ) from exc


async def get_team_record(team: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.r_service_url}/teams/{team}/record",
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()["data"]
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"r-service error fetching record for {team}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"r-service unreachable while fetching record for {team}",
            ) from exc


async def is_healthy() -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.r_service_url}/health",
                timeout=3.0,
            )
            response.raise_for_status()
            return True
        except httpx.HTTPError:
            return False
