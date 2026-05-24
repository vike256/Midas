import copy

DEFAULT_CONFIG = {
    "site": {
        "url": "https://midas.niila.fi",
        "name": "Midas",
        "description": "Midas Template",
        "copyright": "",
    },
    "languages": {
        "default": "en",
        "additional": [],
    },
    "home": {},
    "postPrefix": "p",
    "recentPosts": 3,
    "rss": {
        "default": "feed.xml",
        "additional": "{lang}/feed.xml",
    },
}


def load_config() -> dict:
    import yaml
    from pathlib import Path

    config_path = Path("midas.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}
    else:
        user_config = {}

    config = copy.deepcopy(DEFAULT_CONFIG)
    _deep_merge(config, user_config)

    if not config["site"].get("name"):
        config["site"]["name"] = config["home"].get("name", "Midas")

    return config


def _deep_merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
