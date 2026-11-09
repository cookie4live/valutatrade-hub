
import pytest

from valutatrade_hub.core.currencies import (
    CryptoCurrency,
    FiatCurrency,
    get_currency,
)
from valutatrade_hub.core.exceptions import (
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from valutatrade_hub.core.models import User, Wallet


def test_user_password():
    user = User("anna", "password123")
    assert user.verify_password("password123")
    assert not user.verify_password("wrongpass")


def test_wallet_deposit():
    wallet = Wallet("USD")
    wallet.deposit(100)
    assert wallet.balance == 100


def test_wallet_withdraw():
    wallet = Wallet("USD", 100)
    wallet.withdraw(30)
    assert wallet.balance == 70


def test_insufficient_funds():
    wallet = Wallet("USD", 10)
    with pytest.raises(InsufficientFundsError):
        wallet.withdraw(20)


def test_currency_registry():
    assert isinstance(get_currency("USD"), FiatCurrency)
    assert isinstance(get_currency("BTC"), CryptoCurrency)


def test_unknown_currency():
    with pytest.raises(CurrencyNotFoundError):
        get_currency("XXX")

