import os

from dotenv import load_dotenv

from config import settings as config
from logging_config import get_logger

# Loaded here (not just in main.py) so this module also picks up GOOGLE_API_KEY when
# imported directly, e.g. by tests or standalone scripts that never boot the FastAPI app.
load_dotenv()

logger = get_logger("gemini_client")

_client = None
_client_init_attempted = False


def _get_client():
    """Lazily builds and caches the Gemini client. Returns None (never raises) if no
    API key is configured or the SDK fails to initialize, so callers can fall back."""
    global _client, _client_init_attempted
    if _client_init_attempted:
        return _client
    _client_init_attempted = True

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.warning("GOOGLE_API_KEY not set; Gemini-backed narratives are disabled.")
        return None

    try:
        from google import genai
        from google.genai import types
        _client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=config.GEMINI_REQUEST_TIMEOUT_MS),
        )
    except Exception:
        logger.exception("Failed to initialize Gemini client")
        _client = None

    return _client


def generate_text(prompt, system_instruction=None):
    """
    Calls Gemini to generate a short piece of text. Returns None on any failure
    (missing key, network error, quota, SDK error) instead of raising, so every caller
    is expected to fall back to a deterministic/template response rather than break.
    """
    client = _get_client()
    if client is None:
        return None

    try:
        from google.genai import types
        response = client.models.generate_content(
            model=config.GEMINI_MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=config.GEMINI_MAX_OUTPUT_TOKENS,
                temperature=0.3,
                # Newer Gemini models "think" before answering by default, and that
                # reasoning eats into max_output_tokens -- for a short grounded summary
                # like this, thinking adds latency/cost without improving the output, and
                # a small token cap combined with default thinking can truncate the
                # response before any real answer text is produced. thinking_budget=0 isn't
                # accepted by every model alias, so ask for the minimal thinking level instead.
                thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.MINIMAL),
            ),
        )
        text = (response.text or "").strip()
        return text or None
    except Exception:
        logger.exception("Gemini generate_text call failed")
        return None
