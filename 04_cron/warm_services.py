import os
import sys

import httpx

WARM_TEAM = "India"

SERVICES = {
    "01_r_service": os.environ.get("R_SERVICE_PUBLIC_URL"),
    "02_python_data_service": os.environ.get("PY_DATA_SERVICE_PUBLIC_URL"),
    "03_python_orchestration": os.environ.get("PY_ORCHESTRATION_PUBLIC_URL"),
}

def ping(name: str, base_url: str | None, path: str) -> None:
    if not base_url:
        print(f"{name}: skipped, no URL configured for this service")
        return
    url = f"{base_url.rstrip('/')}{path}"
    try:
        response = httpx.get(url, timeout=240.0)
        print(f"{name} {path} -> {response.status_code}")
    except httpx.HTTPError as exc:
        print(f"{name} {path} -> failed: {exc}")

def main() -> None:
    # First a plain health check on every service, this alone stops Render
    # from spinning a free tier service down for inactivity
    for name, base_url in SERVICES.items():
        ping(name, base_url, "/health")

    # Then a real data call on each data service, this also keeps the
    # cricsheet cache warm so the next real user request is fast
    ping("01_r_service", SERVICES["01_r_service"], f"/teams/{WARM_TEAM}/record")
    ping(
        "02_python_data_service",
        SERVICES["02_python_data_service"],
        f"/teams/{WARM_TEAM}/form",
    )


if __name__ == "__main__":
    main()
    # Best effort job, a single service being down should not fail the cron run
    sys.exit(0)
