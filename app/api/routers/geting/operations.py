from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from app.models.page import Page
from app.shemas.outer_shemas import HtmlView, MainPageView


async def get_pages(
    db: AsyncConnection, skip: int = 0, limit: int = 10
) -> List[MainPageView]:
    query = (
        select(Page.url, Page.title)
        .offset(skip)
        .limit(limit)
        .order_by(Page.url)
    )
    result = await db.execute(query)
    pages = result.all()
    return pages


async def get_html_by_url(db: AsyncConnection, url: str) -> HtmlView:
    query = (
        select(Page.html).where(Page.url == url)
    )
    result = await db.execute(query)
    html = result.one()
    return html
