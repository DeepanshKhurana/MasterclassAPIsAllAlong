import re

from app.config import settings

_DOUBLE_BRACE_VARIABLE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def load_prompt_text(filename: str) -> str:
    raw_text = (settings.prompts_dir / filename).read_text()
    return _DOUBLE_BRACE_VARIABLE.sub(r"{\1}", raw_text)
