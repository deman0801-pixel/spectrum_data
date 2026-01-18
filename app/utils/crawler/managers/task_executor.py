

from app.utils.crawler.managers.rquest_manager import RequestManager


class TaskExecutor:
    def __init__(self, max_depth: int, request_manager: RequestManager):
        self.request_manager = request_manager
        self.max_depth = max_depth

    async def execute(self, url: str, depth: int):
        if depth > self.max_depth:
            return
        await self.request_manager.get(url, depth)

