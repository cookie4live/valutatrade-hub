
import requests

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.config import (
    API_TIMEOUT,
    COINGECKO_URL,
    CRYPTO_CURRENCIES,
    EXCHANGE_RATE_URL,
)


class BaseApiClient:
    """Базовый клиент получения валютных курсов."""

    def fetch_rates(self) -> dict:
        raise NotImplementedError


class ExchangeRateApiClient(BaseApiClient):
    """Клиент получения курсов фиатных валют."""

    def fetch_rates(self) -> dict:
        try:
            response = requests.get(
                EXCHANGE_RATE_URL,
                timeout=API_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("result") != "success":
                raise ApiRequestError("ExchangeRate-API вернул ошибку")

            return {
                f"USD_{code}": float(rate)
                for code, rate in data["rates"].items()
            }

        except (requests.RequestException, ValueError, KeyError) as error:
            raise ApiRequestError(str(error)) from error


class CoinGeckoClient(BaseApiClient):
    """Клиент получения курсов криптовалют."""

    def fetch_rates(self) -> dict:
        try:
            response = requests.get(
                COINGECKO_URL,
                params={
                    "ids": ",".join(CRYPTO_CURRENCIES),
                    "vs_currencies": "usd",
                },
                timeout=API_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            return {
                f"{code}_USD": float(data[coin]["usd"])
                for coin, code in CRYPTO_CURRENCIES.items()
            }

        except (requests.RequestException, ValueError, KeyError) as error:
            raise ApiRequestError(str(error)) from error

