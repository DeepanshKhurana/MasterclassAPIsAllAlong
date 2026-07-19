class LLMNotConfiguredError(RuntimeError):
    """Raised when an LLM chain is invoked without an OpenRouter API key set."""


class LLMCallError(RuntimeError):
    """Raised when a configured LLM provider call fails (auth, network, etc.)."""
