from asyncio import Lock
from typing import List, Tuple, TypeAlias

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.database import AsyncSessionLocal
from app.models.page import Page

Batch: TypeAlias = List[Tuple[str, str, str]]


class UpdateManager:
    def __init__(self):
        self.session = None
        self.is_saving = True
        self._lock = Lock()

    async def bulk_insert_to_db(self, batch: Batch):
        if not batch:
            return 0
        async with self._lock:
            if self.session is None:
                self.session = AsyncSessionLocal()
            try:
                values = [
                    {"url": url, "title": title, "html": html}
                    for url, title, html in batch
                ]
                query = pg_insert(Page).values(values)
                query = query.on_conflict_do_update(
                    index_elements=["url"],
                    set_={"title": query.excluded.title, "html": query.excluded.html},
                )
                await self.session.execute(query)
                await self.session.commit()
            except Exception as e:
                await self.session.rollback()
                print(f"Ошибка при массовой вставке: {e}")
