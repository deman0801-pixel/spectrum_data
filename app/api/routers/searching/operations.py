from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.models.page import Page
from app.shemas.outer_shemas import MainPageView


async def find_pages_by_text(
    attribute: str, search_str: str, skip: int, limit: int, db: AsyncConnection
) -> List[MainPageView]:
    match attribute:
        case "url":
            field_to_search = Page.url
        case "title":
            field_to_search = Page.title
    query = (
        select(Page.url, Page.title)
        .where(field_to_search.ilike(f"%{search_str}%"))
        .offset(skip)
        .limit(limit)
        .order_by(Page.url)
    )
    result = await db.execute(query)
    pages = result.all()
    return pages
