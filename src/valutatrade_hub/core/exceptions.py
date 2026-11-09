
class InsufficientFundsError(Exception):
    """Ошибка при недостатке средств в кошельке."""

    def __init__(self, available: float, required: float, code: str):
        self.available = available
        self.required = required
        self.code = code
        super().__init__(
            f"Недостаточно средств: доступно {available} {code}, "
            f"требуется {required} {code}"
        )


class CurrencyNotFoundError(Exception):
    """Ошибка при обращении к неизвестной валюте."""

    def __init__(self, code: str):
        super().__init__(f"Неизвестная валюта '{code}'")


class ApiRequestError(Exception):
    """Ошибка при обращении к внешнему API."""

    def __init__(self, reason: str):
        super().__init__(
            f"Ошибка при обращении к внешнему API: {reason}"
        )
