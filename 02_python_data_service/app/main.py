import os
import subprocess

import uvicorn
from fastapi import FastAPI

from app.routers.matches import router as matches_router
from app.routers.matches import teams_router


app = FastAPI(
    title="APIs All Along — Ball-by-Ball Data Service",
    description="Serves cricket match and ball-by-ball data from cricsheet.org.",
    version="0.1.0",
)

app.include_router(matches_router)
app.include_router(teams_router)


@app.get("/health", summary="Liveness check")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


def workbench_root_path(port: int) -> str:
    """Proxied URL prefix inside Posit Workbench; '' anywhere else."""
    rsu = "/usr/lib/rstudio-server/bin/rserver-url"
    if not os.environ.get("RS_SERVER_URL") or not os.path.exists(rsu):
        return ""
    out = subprocess.run([rsu, "-l", str(port)], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


if __name__ == "__main__":
    SVC = 1
    uid = os.getuid() if hasattr(os, "getuid") else 0
    PORT = 10000 + (uid % 6000) * 3 + SVC
    print(f"Docs: http://127.0.0.1:{PORT}/docs")
    uvicorn.run(app, host="127.0.0.1", port=PORT, root_path=workbench_root_path(PORT))
