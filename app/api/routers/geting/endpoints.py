from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncConnection
from app.core.database import get_db_connection
from app.shemas.outer_shemas import HtmlView, MainPageView
from app.api.routers.geting.operations import get_pages, get_html_by_id
from app.utils.decorators.catcher_500 import catcher_500

router = APIRouter(prefix="/get", tags=["getting_methods"])


@router.get("/all", response_model=List[MainPageView])
@catcher_500
async def get_all(
    skip: int = Query(0, ge=0, description="Сколько пропустить"),
    limit: int = Query(100, ge=1, le=200, description="Лимит записей"),
    db: AsyncConnection = Depends(get_db_connection),
):
    pages = await get_pages(db, skip=skip, limit=limit)
    return pages


@router.get("/{url}", response_model=HtmlView)
@catcher_500
async def get_html(
    url: str,
    db: AsyncConnection = Depends(get_db_connection),
):
    html = await get_html_by_id(db, url)
    return html
