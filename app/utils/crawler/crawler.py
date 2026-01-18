from asyncio import Queue
from typing import Set

from app.utils.crawler.managers.html_manager import HTMLManager
from app.utils.crawler.managers.rquest_manager import RequestManager
from app.utils.crawler.managers.task_executor import TaskExecutor
from app.utils.crawler.managers.task_manager import TaskManager
from app.utils.crawler.managers.update_manager import UpdateManager
from app.utils.crawler.managers.url_manager import URLManager
from app.utils.crawler.managers.worker_manager import WorkerManager


class Crawler:
    def __init__(self):
        self.visited: Set[str] = set()
        self.results_queue = Queue()

    async def start(
        self,
        url: str,
        max_depth: int = 0,
        requests_limit: int = 1,
        task_timeout: int = 5,
        request_timeout: int = 10,
    ):
        self.max_depth = max_depth
        self.requests_limit = requests_limit
        self.update_manager = UpdateManager()
        self.url_manager = URLManager()
        self.html_manager = HTMLManager()
        self.task_manager = TaskManager()
        self.request_manager = RequestManager(
            self.max_depth,
            self.html_manager,
            self.task_manager,
            self.url_manager,
            qnt_semafors=requests_limit,
            request_timeout=request_timeout,
        )
        self.task_executor = TaskExecutor(self.max_depth, self.request_manager)
        self.worker_manager = WorkerManager(
            self.task_manager,
            self.update_manager,
            self.task_executor,
            task_timeout=task_timeout,
        )

        await self._parse(url)

    async def _parse(self, url: str):
        try:
            print("Начал обход")
            await self.task_manager.create_task_queue(
                url,
                0,
                self.requests_limit,
                self.worker_manager.parse_task_worker,
                self.worker_manager.db_save_worker,
                self.update_manager,
            )
        except Exception as e:
            print("Непредвиденная шибка во время обхода", e)
        finally:    
            print("Закончил обход")
