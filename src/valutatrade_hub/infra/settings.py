
class SettingsLoader:
    """Singleton для хранения настроек приложения."""

    _instance = None

    DEFAULTS = {
        "DATA_DIR": "data",
        "USERS_FILE": "users.json",
        "PORTFOLIOS_FILE": "portfolios.json",
        "RATES_FILE": "rates.json",
        "RATES_TTL_SECONDS": 3600,
        "BASE_CURRENCY": "USD",
        "LOG_FILE": "logs/actions.log",
        "LOG_LEVEL": "INFO",
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = cls.DEFAULTS.copy()
        return cls._instance

    def get(self, key: str, default=None):
        """Возвращает значение настройки."""
        return self._settings.get(key, default)

    def reload(self):
        """Восстанавливает настройки по умолчанию."""
        self._settings = self.DEFAULTS.copy()

