
import json
from pathlib import Path


class DatabaseManager:
    """Singleton для работы с JSON-хранилищем."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self.base_path = Path("data")
        self.base_path.mkdir(exist_ok=True)
        self._initialized = True

    def load(self, filename, default=None):
        path = self.base_path / filename
        if not path.exists():
            return [] if default is None else default

        try:
            with path.open(encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(f"Ошибка чтения {filename}: {error}") from error

    def save(self, filename, data):
        path = self.base_path / filename
        temp_path = path.with_suffix(".tmp")

        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        temp_path.replace(path)

