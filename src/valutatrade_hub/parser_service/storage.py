
import json
from datetime import datetime, timezone
from pathlib import Path


class RatesStorage:
    """Хранилище актуальных курсов и истории."""

    def __init__(self):
        self.rates_path = Path("data/rates.json")
        self.history_path = Path("data/exchange_rates.json")

    def save(self, rates: dict) -> None:
        """Сохраняет актуальные курсы атомарно."""
        self.rates_path.parent.mkdir(exist_ok=True)

        now = datetime.now(timezone.utc).isoformat()

        data = {
            "pairs": rates,
            "last_refresh": now,
        }

        temp_path = self.rates_path.with_suffix(".tmp")

        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        temp_path.replace(self.rates_path)

        history = self.load_history()
        history.append({
            "updated_at": now,
            "pairs": rates,
        })

        temp_history = self.history_path.with_suffix(".tmp")

        with temp_history.open("w", encoding="utf-8") as file:
            json.dump(history, file, ensure_ascii=False, indent=4)

        temp_history.replace(self.history_path)

    def load_history(self) -> list:
        """Загружает историю курсов."""
        if not self.history_path.exists():
            return []

        with self.history_path.open(encoding="utf-8") as file:
            return json.load(file)

    def load(self) -> dict:
        """Загружает актуальные курсы."""
        if not self.rates_path.exists():
            return {"pairs": {}, "last_refresh": None}

        with self.rates_path.open(encoding="utf-8") as file:
            return json.load(file)

