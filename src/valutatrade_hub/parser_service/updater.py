
import logging

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.api_clients import (
    CoinGeckoClient,
    ExchangeRateApiClient,
)
from valutatrade_hub.parser_service.storage import RatesStorage

logger = logging.getLogger("valutatrade_hub")


class RatesUpdater:
    """Обновляет курсы валют из нескольких источников."""

    def __init__(self):
        self.clients = [
            ExchangeRateApiClient(),
            CoinGeckoClient(),
        ]
        self.storage = RatesStorage()

    def run_update(self) -> dict:
        """Получает курсы и сохраняет объединённые данные."""
        combined_rates = {}
        errors = []

        for client in self.clients:
            try:
                rates = client.fetch_rates()
                combined_rates.update(rates)
                logger.info(
                    "Получено %s курсов от %s",
                    len(rates),
                    type(client).__name__,
                )
            except ApiRequestError as error:
                errors.append(str(error))
                logger.exception("Ошибка обновления курсов")

        if not combined_rates:
            raise ApiRequestError(
                "; ".join(errors) or "Источники не вернули курсы"
            )

        self.storage.save(combined_rates)

        return {
            "updated": len(combined_rates),
            "errors": errors,
        }

