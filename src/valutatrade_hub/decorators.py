
from functools import wraps

from valutatrade_hub.logging_config import logger


def log_action(action: str, verbose: bool = False):
    """Логирует успешные и неуспешные операции."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                logger.info(
                    "%s user=%s currency=%s amount=%s result=OK",
                    action,
                    args[0] if args else "unknown",
                    args[1] if len(args) > 1 else "-",
                    args[2] if len(args) > 2 else "-",
                )

                if verbose:
                    logger.info("Дополнительный контекст: %s", result)

                return result

            except Exception as error:
                logger.exception(
                    "%s result=ERROR error_type=%s error_message=%s",
                    action,
                    type(error).__name__,
                    error,
                )
                raise

        return wrapper

    return decorator

