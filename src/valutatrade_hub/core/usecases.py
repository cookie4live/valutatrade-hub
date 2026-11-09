

from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.core.exceptions import CurrencyNotFoundError
from valutatrade_hub.core.models import Portfolio, User
from valutatrade_hub.decorators import log_action
from valutatrade_hub.infra.database import DatabaseManager

db = DatabaseManager()


def register(username: str, password: str) -> User:
    """Регистрирует нового пользователя."""
    users = db.load("users.json", [])

    if any(user["username"] == username for user in users):
        raise ValueError("Пользователь уже существует")

    user = User(username, password)
    users.append(user.to_dict())
    db.save("users.json", users)

    portfolios = db.load("portfolios.json", {})
    portfolios[username] = {}
    db.save("portfolios.json", portfolios)

    return user


def login(username: str, password: str) -> User:
    """Авторизует пользователя."""
    users = db.load("users.json", [])

    for item in users:
        if item["username"] == username:
            user = User.__new__(User)
            user.username = item["username"]
            user._salt = item["salt"]
            user._password_hash = item["password_hash"]
            user._registered_at = item["registered_at"]

            if user.verify_password(password):
                return user

            break

    raise ValueError("Неверное имя пользователя или пароль")


def get_portfolio(user: User) -> Portfolio:
    """Загружает портфель пользователя."""
    portfolios = db.load("portfolios.json", {})
    portfolio = Portfolio(user)

    for code, balance in portfolios.get(user.username, {}).items():
        wallet = portfolio.add_currency(code)
        wallet.balance = balance

    return portfolio


def save_portfolio(portfolio: Portfolio) -> None:
    """Сохраняет портфель пользователя."""
    portfolios = db.load("portfolios.json", {})
    portfolios[portfolio.user.username] = {
        code: wallet.balance
        for code, wallet in portfolio.wallets.items()
    }
    db.save("portfolios.json", portfolios)


def get_rate(from_code: str, to_code: str = "USD") -> dict:
    """Получает курс валют из локального хранилища."""
    get_currency(from_code)
    get_currency(to_code)

    rates = db.load("rates.json", {"pairs": {}, "last_refresh": None})
    pair = f"{from_code.upper()}_{to_code.upper()}"
    rate = rates.get("pairs", {}).get(pair)

    if rate is None:
        if from_code.upper() == to_code.upper():
            rate = 1.0
        else:
            raise CurrencyNotFoundError(pair)

    return {
        "rate": float(rate),
        "updated_at": rates.get("last_refresh"),
    }


@log_action("BUY")
def buy(user_id: str, currency_code: str, amount: float) -> Portfolio:
    """Покупает валюту и пополняет кошелёк."""
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")

    get_currency(currency_code)
    users = db.load("users.json", [])

    user_data = next(
        (item for item in users if item["username"] == user_id),
        None,
    )
    if user_data is None:
        raise ValueError("Пользователь не найден")

    user = User.__new__(User)
    user.username = user_data["username"]
    user._salt = user_data["salt"]
    user._password_hash = user_data["password_hash"]
    user._registered_at = user_data["registered_at"]

    portfolio = get_portfolio(user)
    wallet = portfolio.add_currency(currency_code)
    wallet.deposit(amount)
    save_portfolio(portfolio)

    return portfolio


@log_action("SELL")
def sell(user_id: str, currency_code: str, amount: float) -> Portfolio:
    """Продаёт валюту и списывает средства с кошелька."""
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")

    get_currency(currency_code)
    users = db.load("users.json", [])

    user_data = next(
        (item for item in users if item["username"] == user_id),
        None,
    )
    if user_data is None:
        raise ValueError("Пользователь не найден")

    user = User.__new__(User)
    user.username = user_data["username"]
    user._salt = user_data["salt"]
    user._password_hash = user_data["password_hash"]
    user._registered_at = user_data["registered_at"]

    portfolio = get_portfolio(user)
    wallet = portfolio.get_wallet(currency_code)
    wallet.withdraw(amount)
    save_portfolio(portfolio)

    return portfolio

