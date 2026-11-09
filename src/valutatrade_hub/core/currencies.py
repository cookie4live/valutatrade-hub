
from abc import ABC, abstractmethod

from valutatrade_hub.core.exceptions import CurrencyNotFoundError


class Currency(ABC):
    """Абстрактный базовый класс валюты."""

    def __init__(self, name: str, code: str):
        if not name.strip():
            raise ValueError("Название валюты не может быть пустым")

        if (
            not code.isascii()
            or not code.isalnum()
            or not 2 <= len(code) <= 5
            or code != code.upper()
        ):
            raise ValueError("Некорректный код валюты")

        self.name = name
        self.code = code

    @abstractmethod
    def get_display_info(self) -> str:
        """Возвращает информацию о валюте."""
        pass


class FiatCurrency(Currency):
    """Фиатная валюта."""

    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return (
            f"[FIAT] {self.code} — {self.name} "
            f"(Issuing: {self.issuing_country})"
        )


class CryptoCurrency(Currency):
    """Криптовалюта."""

    def __init__(
        self,
        name: str,
        code: str,
        algorithm: str,
        market_cap: float,
    ):
        super().__init__(name, code)
        if not algorithm.strip() or market_cap < 0:
            raise ValueError("Некорректные данные криптовалюты")

        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        return (
            f"[CRYPTO] {self.code} — {self.name} "
            f"(Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})"
        )


CURRENCIES = {
    "USD": FiatCurrency("US Dollar", "USD", "United States"),
    "EUR": FiatCurrency("Euro", "EUR", "Eurozone"),
    "RUB": FiatCurrency("Russian Ruble", "RUB", "Russia"),
    "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12),
    "ETH": CryptoCurrency("Ethereum", "ETH", "Ethash", 4.0e11),
    "SOL": CryptoCurrency("Solana", "SOL", "Proof of Stake", 1.0e11),
}


def get_currency(code: str) -> Currency:
    """Возвращает валюту по её коду."""
    normalized_code = code.upper()

    if normalized_code not in CURRENCIES:
        raise CurrencyNotFoundError(normalized_code)

    return CURRENCIES[normalized_code]
