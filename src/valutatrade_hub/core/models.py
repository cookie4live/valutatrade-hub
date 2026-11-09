
import hashlib
import secrets
from datetime import datetime, timezone

from valutatrade_hub.core.exceptions import InsufficientFundsError


class User:
    """Модель пользователя системы."""

    def __init__(self, username: str, password: str):
        if not username.strip():
            raise ValueError("Имя пользователя не может быть пустым")

        if len(password) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")

        self.username = username
        self._salt = secrets.token_hex(16)
        self._password_hash = self._hash_password(password)
        self._registered_at = datetime.now(timezone.utc).isoformat()

    def _hash_password(self, password: str) -> str:
        """Создаёт хеш пароля с солью."""
        return hashlib.sha256(
            (self._salt + password).encode("utf-8")
        ).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Проверяет пароль."""
        return self._password_hash == self._hash_password(password)

    def get_user_info(self) -> dict:
        """Возвращает информацию без пароля и соли."""
        return {
            "username": self.username,
            "registered_at": self._registered_at,
        }

    def to_dict(self) -> dict:
        """Подготавливает пользователя к сохранению."""
        return {
            "username": self.username,
            "salt": self._salt,
            "password_hash": self._password_hash,
            "registered_at": self._registered_at,
        }


class Wallet:
    """Кошелёк для хранения одной валюты."""

    def __init__(self, currency_code: str, balance: float = 0):
        self.currency_code = currency_code.upper()
        self.balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Баланс должен быть числом")

        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")

        self._balance = float(value)

    def deposit(self, amount: float) -> None:
        """Пополняет кошелёк."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValueError("Сумма должна быть числом")
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")

        self.balance += amount

    def withdraw(self, amount: float) -> None:
        """Списывает средства с проверкой остатка."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValueError("Сумма должна быть числом")
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")

        if amount > self.balance:
            raise InsufficientFundsError(
                self.balance, amount, self.currency_code
            )

        self.balance -= amount

    def get_balance_info(self) -> str:
        return f"{self.currency_code}: {self.balance:.4f}"


class Portfolio:
    """Портфель пользователя с несколькими валютными кошельками."""

    def __init__(self, user: User):
        self._user = user
        self._wallets = {}

    @property
    def user(self) -> User:
        return self._user

    @property
    def wallets(self) -> dict:
        return self._wallets.copy()

    def add_currency(self, currency_code: str) -> Wallet:
        """Создаёт кошелёк, если его ещё нет."""
        code = currency_code.upper()

        if code not in self._wallets:
            self._wallets[code] = Wallet(code)

        return self._wallets[code]

    def get_wallet(self, currency_code: str) -> Wallet:
        """Возвращает кошелёк по коду валюты."""
        code = currency_code.upper()

        if code not in self._wallets:
            raise ValueError(f"Кошелёк {code} не найден")

        return self._wallets[code]

    def get_total_value(self, base: str = "USD") -> float:
        """Вычисляет оценочную стоимость портфеля."""
        from valutatrade_hub.core.usecases import get_rate

        total = 0.0

        for code, wallet in self._wallets.items():
            if code == base.upper():
                total += wallet.balance
            else:
                rate = get_rate(code, base)
                total += wallet.balance * rate["rate"]

        return total

