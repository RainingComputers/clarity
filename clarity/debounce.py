import functools
from typing import Callable, Any
from threading import Timer


def debounce(
    timeout: float,
) -> Callable[[Callable], Callable]:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            wrapper.func.cancel()  # type: ignore
            wrapper.func = Timer(timeout, func, args, kwargs)  # type: ignore
            wrapper.func.start()  # type: ignore

        wrapper.func = Timer(timeout, lambda: None)  # type: ignore
        return wrapper

    return decorator
