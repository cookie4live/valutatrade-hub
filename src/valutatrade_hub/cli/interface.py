
import shlex

from valutatrade_hub.core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from valutatrade_hub.core.usecases import (
    buy,
    get_portfolio,
    get_rate,
    login,
    register,
    sell,
)
from valutatrade_hub.parser_service.storage import RatesStorage
from valutatrade_hub.parser_service.updater import RatesUpdater


def main():
    """Запускает консольный интерфейс приложения."""
    current_user = None

    print("\n=== ValutaTrade Hub ===")
    print("Введите help для просмотра команд.")

    while True:
        try:
            command = input("\nВведите команду: ").strip()
            if not command:
                continue

            parts = shlex.split(command)
            action = parts[0].lower()

            if action == "exit":
                print("До свидания!")
                break

            elif action == "help":
                print(
                    "register <имя> <пароль>\n"
                    "login <имя> <пароль>\n"
                    "show-portfolio\n"
                    "buy <валюта> <сумма>\n"
                    "sell <валюта> <сумма>\n"
                    "get-rate <из> <в>\n"
                    "update-rates\n"
                    "show-rates\n"
                    "logout\n"
                    "exit"
                )

            elif action == "register" and len(parts) == 3:
                register(parts[1], parts[2])
                print("Регистрация прошла успешно!")

            elif action == "login" and len(parts) == 3:
                current_user = login(parts[1], parts[2])
                print(f"Добро пожаловать, {current_user.username}!")

            elif action == "logout":
                current_user = None
                print("Вы вышли из аккаунта.")

            elif action == "show-portfolio":
                if current_user is None:
                    print("Сначала войдите в аккаунт.")
                    continue

                portfolio = get_portfolio(current_user)

                print(f"\nПортфель пользователя {current_user.username}:")
                if not portfolio.wallets:
                    print("Портфель пуст.")
                else:
                    for wallet in portfolio.wallets.values():
                        print(wallet.get_balance_info())

            elif action == "buy" and len(parts) == 3:
                if current_user is None:
                    print("Сначала войдите в аккаунт.")
                    continue

                buy(current_user.username, parts[1], float(parts[2]))
                print("Покупка успешно выполнена!")

            elif action == "sell" and len(parts) == 3:
                if current_user is None:
                    print("Сначала войдите в аккаунт.")
                    continue

                sell(current_user.username, parts[1], float(parts[2]))
                print("Продажа успешно выполнена!")

            elif action == "get-rate" and len(parts) == 3:
                result = get_rate(parts[1], parts[2])
                print(
                    f"Курс {parts[1].upper()}/{parts[2].upper()}: "
                    f"{result['rate']}"
                )
                print(f"Обновлено: {result['updated_at']}")

            elif action == "update-rates":
                result = RatesUpdater().run_update()
                print(f"Обновлено курсов: {result['updated']}")
                if result["errors"]:
                    print("Предупреждения:", result["errors"])

            elif action == "show-rates":
                rates = RatesStorage().load()
                print("Актуальные курсы:")
                for pair, rate in rates["pairs"].items():
                    print(f"{pair}: {rate}")
                print(f"Последнее обновление: {rates['last_refresh']}")

            
            else:
                print("Неизвестная команда или неверные аргументы.")

        except InsufficientFundsError as error:
            print(error)

        except CurrencyNotFoundError as error:
            print(error)
            print("Введите help для просмотра команд и поддерживаемых валют.")

        except ApiRequestError as error:
            print(error)
            print("Попробуйте повторить операцию позже или проверьте интернет.")

        except ValueError as error:
            print(f"Ошибка: {error}")

        except Exception as error:
            print(f"Ошибка выполнения: {error}")



if __name__ == "__main__":
    main()

