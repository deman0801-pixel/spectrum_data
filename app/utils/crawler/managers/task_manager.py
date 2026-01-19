from asyncio import (
    Lock,
    Queue,
    create_task,
    gather,
)
from typing import Callable, Set

from app.utils.crawler.managers.update_manager import UpdateManager


class TaskManager:
    def __init__(self):
        self.visited: Set[str] = set()
        self.visited_lock = Lock()
        self.task_queue = Queue()
        self.results_queue = Queue()
        self.is_run = True

    async def add_task_to_queue(self, url: str, depth: int):
        async with self.visited_lock:
            if url in self.visited:
                return
            self.visited.add(url)
            await self.task_queue.put((url, depth))

    async def create_task_queue(
        self,
        url: str,
        current_depth: int,
        requests_limit: int,
        parse_task_worker: Callable,
        db_save_worker: Callable,
        update_manager: UpdateManager,
    ):
        await self.add_task_to_queue(url, current_depth)
        tasks = []
        for _ in range(requests_limit):
            task = create_task(parse_task_worker())
            tasks.append(task)
            db_task = create_task(db_save_worker())
            tasks.append(db_task)
        try:
            await self.task_queue.join()
        finally:
            self.is_run = False
            update_manager.is_saving = False
            for task in tasks:
                task.cancel()
            await gather(*tasks, return_exceptions=True)
