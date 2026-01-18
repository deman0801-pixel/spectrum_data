from asyncio import CancelledError, Semaphore
from aiohttp import ClientSession

from app.exceptions.status_code import StatusCodeException
from app.utils.crawler.managers.html_manager import HTMLManager
from app.utils.crawler.managers.task_manager import TaskManager
from app.utils.crawler.managers.url_manager import URLManager


class RequestManager:
    def __init__(
        self,
        max_depth: int,
        html_manager: HTMLManager,
        task_manager: TaskManager,
        url_manager: URLManager,
        qnt_semafors: int = 1,
        request_timeout: int = 10,
    ):
        self.semaphore = Semaphore(qnt_semafors)
        self.max_depth = max_depth
        self.html_manager = html_manager
        self.request_timeout = request_timeout
        self.task_manager = task_manager
        self.url_manager = url_manager

    async def get(self, url: str, depth: int) -> bool:
        async with self.semaphore:
            try:
                async with ClientSession() as session:
                    async with session.get(
                        url, timeout=self.request_timeout
                    ) as response:
                        (
                            html_content,
                            title,
                            links,
                        ) = await self.html_manager.parse_response(response)
                        await self.task_manager.results_queue.put(
                            (url, title, html_content)
                        )
                        if depth < self.max_depth and links:
                            for link in links:
                                normalized = self.url_manager.normalize_url(url, link)
                                if normalized:
                                    await self.task_manager.add_task_to_queue(
                                        normalized, depth + 1
                                    )
                        return True

            except CancelledError:
                return False
            except StatusCodeException as e:
                print(f"Неверный статус код {url}: {e}")
                return False
            except Exception as e:
                print(f"Непредвиденная ошибка {url}: {e}")
                return False
