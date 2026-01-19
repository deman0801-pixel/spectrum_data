import logging
from functools import wraps

from fastapi import status

from app.shemas.outer_shemas import ErrorResponse


def catcher_500(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(
                f"Error in function {func.__name__} "
                f"in module {func.__module__}: {str(e)}",
                exc_info=True
            )
            return ErrorResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Что то пошло не так",
            )

    return wrapper
