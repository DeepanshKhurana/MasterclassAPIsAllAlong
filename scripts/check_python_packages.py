import importlib
import sys

PACKAGES = [
    "fastapi",
    "httpx",
    "pydantic",
    "pydantic_settings",
    "uvicorn",
    "langchain",
    "langchain_openai",
    "langchain_core",
    "cricketstats",
    "pandas",
    "requests",
    "bs4",
]


def check_packages(packages: list[str]) -> bool:
    all_ok = True
    for package in packages:
        try:
            importlib.import_module(package)
            print(f"[OK] {package}")
        except ImportError as exc:
            print(f"[FAILED] {package} - {exc}")
            all_ok = False
    return all_ok


if __name__ == "__main__":
    success = check_packages(PACKAGES)
    if not success:
        print("\nSome Python packages failed to import.")
        sys.exit(1)
    print("\nAll Python packages imported successfully.")
