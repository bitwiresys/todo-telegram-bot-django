import os


def get_settings() -> dict[str, str]:
    """Args: none. Returns: settings dict from env."""
    return {
        "BOT_TOKEN": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        "BACKEND_BASE_URL": os.environ.get("BACKEND_BASE_URL", "http://django:8000"),
    }
