import json
from dataclasses import dataclass, asdict, fields
from pathlib import Path


@dataclass
class AppConfig:
    """Application configuration model loaded from and saved to disk."""

    app_theme: str = "catnip"
    editor_theme: str = "match"
    use_llm: bool = True
    llm_on_start: bool = False
    # open and save with the OS file dialog (zenity or Tk) instead of in-terminal
    system_file_picker: bool = False

    CONFIG_DIR = Path.home() / ".config" / "catnip"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from disk or return defaults if missing or invalid."""

        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        if not cls.CONFIG_FILE.exists():
            return cls()

        try:
            with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return cls()

        # ignore keys from older or newer versions instead of failing to start
        known = {field.name for field in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})

    def save(self) -> None:
        """Persist the current configuration to disk."""

        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=4)
