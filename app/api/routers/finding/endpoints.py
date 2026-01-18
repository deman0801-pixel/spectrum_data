from typing import List, Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncConnection
from app.api.routers.finding.operations import find_pages_by_text
from app.core.database import get_db_connection
from app.shemas.outer_shemas import MainPageView

router = APIRouter(prefix="/find", tags=["Поисковые ендпоинты"])


@router.get("/", response_model=List[MainPageView])
async def get_page_by_title(
    attribute: Literal["url", "title"] = Query(..., description="Имя поля для поиска: url или title"),
    search_str: str = Query(..., description="Строка для поиска"),
    skip: int = Query(0, ge=0, description="Сколько пропустить"),
    limit: int = Query(100, ge=1, le=200, description="Лимит записей"),
    db: AsyncConnection = Depends(get_db_connection),
):
    return await find_pages_by_text(attribute, search_str, skip, limit, db)
