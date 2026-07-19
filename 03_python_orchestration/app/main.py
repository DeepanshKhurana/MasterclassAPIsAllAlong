import logging
import os
import subprocess
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.chains.errors import LLMCallError, LLMNotConfiguredError
from app.routers.chat import router as chat_router
from app.routers.eli5 import router as eli5_router
from app.services.py_client import is_healthy as is_py_data_service_healthy
from app.services.r_client import is_healthy as is_r_service_healthy

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if not await is_r_service_healthy():
        logger.warning("r-service is not reachable at startup")
    if not await is_py_data_service_healthy():
        logger.warning("py-data-service is not reachable at startup")
    yield


app = FastAPI(title="APIs All Along — Orchestration Service", lifespan=lifespan)

app.include_router(eli5_router)
app.include_router(chat_router)


@app.exception_handler(LLMNotConfiguredError)
async def handle_missing_llm_key(
    request: Request,
    exc: LLMNotConfiguredError,
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(LLMCallError)
async def handle_llm_call_error(request: Request, exc: LLMCallError) -> JSONResponse:
    logger.error("LLM call failed: %s", exc)
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def workbench_root_path(port: int) -> str:
    """Proxied URL prefix inside Posit Workbench; '' anywhere else."""
    rsu = "/usr/lib/rstudio-server/bin/rserver-url"
    if not os.environ.get("RS_SERVER_URL") or not os.path.exists(rsu):
        return ""
    out = subprocess.run([rsu, "-l", str(port)], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


if __name__ == "__main__":
    SVC = 2
    uid = os.getuid() if hasattr(os, "getuid") else 0
    PORT = 10000 + (uid % 6000) * 3 + SVC
    print(f"Docs: http://127.0.0.1:{PORT}/docs")
    uvicorn.run(app, host="127.0.0.1", port=PORT, root_path=workbench_root_path(PORT))
