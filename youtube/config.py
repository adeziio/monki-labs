from pathlib import Path

from core.config_loader import ConfigLoader


def _config_directory():
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "config"


def load_youtube_config():
    loader = ConfigLoader(_config_directory())
    return loader.load("youtube.json")


def get_account(config=None):
    config = config if config is not None else load_youtube_config()
    account = config.get("account") or {}
    return account if isinstance(account, dict) else {}


def get_metadata_defaults(config=None):
    config = config if config is not None else load_youtube_config()
    defaults = (config.get("metadata") or {}).get("defaults") or {}
    return dict(defaults)
