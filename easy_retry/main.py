from asyncio import iscoroutinefunction
from asyncio import sleep as asleep
from functools import wraps
from time import sleep
from typing import (
    Callable,
    Iterable,
    Literal,
    ParamSpec,
    Protocol,
    Type,
    TypeVar,
)

E = TypeVar('E', bound=BaseException)
T = TypeVar('T')
P = ParamSpec('P')


class Handler(Protocol):
    def __call__(self, error: BaseException, attempt: int): ...


def retry(
        exceptions: Iterable[Type[E]] | None = None,
        mode: Literal['handle', 'ignore'] = 'handle',
        handler: Handler | None = None,
        attempts: int | None = None,
        backoff: int | float = 0,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    if attempts is not None:
        attempts += 1

    def handle_exception(error: E, attempt):
        if handler is not None:
            handler(error, attempt)
        if exceptions is None:
            return
        match mode:
            case 'handle':
                handle = type(error) in exceptions
            case 'ignore':
                handle = type(error) not in exceptions
            case _:
                raise ValueError
        if not handle:
            raise error
        return

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            exception = None
            while attempts is None or attempt < attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    exception = error
                    handle_exception(error, attempt)
                    attempt += 1
                    sleep(backoff)
            if exception is not None:
                raise exception

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempt = 1
            exception = None
            while attempts is None or attempt < attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as error:
                    exception = error
                    handle_exception(error, attempt)
                    attempt += 1
                    await asleep(backoff)
            if exception is not None:
                raise exception

        if iscoroutinefunction(func):
            return async_wrapper

        return wrapper

    return decorator
