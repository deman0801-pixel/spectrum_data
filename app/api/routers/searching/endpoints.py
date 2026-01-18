from typing import List, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncConnection

from app.api.routers.searching.operations import find_pages_by_text
from app.core.database import get_db_connection
from app.shemas.outer_shemas import MainPageView
from app.utils.decorators.catcher_500 import catcher_500

router = APIRouter(prefix="/search", tags=["Поисковые ендпоинты"])


@router.get(
    "/",
    response_model=List[MainPageView],
    summary="Поиск по частичному совпадению",
    description="Поиск ведется по частичному совпадению без учета регистра. Требуется задать по какому атрибуту искать",
)
@catcher_500
async def get_page_by_title(
    attribute: Literal["url", "title"] = Query(
        ..., description="Имя поля для поиска: url или title"
    ),
    search_str: str = Query(..., description="Строка для поиска"),
    skip: int = Query(0, ge=0, description="Сколько пропустить"),
    limit: int = Query(10, ge=1, le=100, description="Лимит записей"),
    db: AsyncConnection = Depends(get_db_connection),
):
    return await find_pages_by_text(attribute, search_str, skip, limit, db)
