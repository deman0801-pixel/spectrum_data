# TODO: добавить запись в логи вместо принтов

import asyncio
from typing import List, Set, Tuple
from urllib.parse import urljoin

from aiohttp import ClientSession
from lxml import html

from app.exceptions.status_code import StatusCodeException


class Parser:
    def __init__(self):
        self.visited: Set[str] = set()
        self.visited_lock = asyncio.Lock()
        self.results_queue = asyncio.Queue()
        self.non_html_extensions = (
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".zip",
            ".rar",
            ".7z",
            ".tar",
            ".gz",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".svg",
            ".mp4",
            ".mp3",
            ".avi",
            ".mov",
            ".js",
            ".css",
            ".json",
            ".xml",
            ".exe",
            ".dmg",
            ".deb",
            ".rpm",
            ".tar.lz",
        )

    def start(
        self,
        url: str,
        max_depth: int = 0,
        requests_limit: int = 1,
        task_timeout: int = 5,
        request_timeout: int = 10,
    ):
        self.requests_limit = requests_limit
        self.max_depth = max_depth
        self.task_queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(requests_limit)
        self.is_run = True
        self.is_saving = True
        self.task_timeout = task_timeout
        self.request_timeout = request_timeout

        asyncio.run(self._parse(url))

    def _get_info(self, html_raw: str) -> Tuple[str, List[str]]:
        dom = html.fromstring(html_raw)
        head_title = dom.xpath("//head/title/text()")
        title = head_title[0].strip() if head_title else None
        links = dom.xpath("//a/@href")
        clean_links = [link.strip() for link in links if link and link.strip()]
        return (title, clean_links)

    async def _add_task_to_queue(self, url: str, depth: int):
        async with self.visited_lock:
            if url in self.visited:
                print(f"Уже был: {url}")
                return
            self.visited.add(url)
            await self.task_queue.put((url, depth))

    # TODO: реализовать после подключение к базе
    async def bulk_insert_to_db():
        """
        Разгружает очередь результатов.
        Массово вставляет результаты в бд при накоплении лимита
        """
        ...

    def _normalize_url(self, base_url: str, link: str) -> str:
        try:
            absolute = urljoin(base_url, link)
            normalized = absolute.split("#")[0].split("?")[0]
            if normalized:
                is_http = normalized.startswith("http")
                is_html = not normalized.endswith(self.non_html_extensions)
                if all([is_http, is_html]):
                    return normalized
            return None
        except Exception:
            return None

    async def _parse_response(self, response) -> Tuple[str, str, List[str]]:
        code: int = response.status
        if 200 <= code < 400:
            html_content = await response.text()
            title, links = self._get_info(html_content)
            return (html_content, title, links)
        else:
            raise StatusCodeException(code)

    async def _process_task(self, url: str, depth: int):
        if depth > self.max_depth:
            return

        async with self.semaphore:
            try:
                async with ClientSession() as session:
                    async with session.get(
                        url, timeout=self.request_timeout
                    ) as response:
                        (html_content, title, links) = await self._parse_response(
                            response
                        )
                        await self.results_queue.put(
                            (url, title, "0")
                        )  # TODO: заменить "0" на html_content
                        print("ссылок в очереди: ", self.results_queue.qsize())
                        if depth < self.max_depth and links:
                            for link in links:
                                normalized = self._normalize_url(url, link)
                                if normalized:
                                    await self._add_task_to_queue(normalized, depth + 1)

            except asyncio.CancelledError:
                ...
            except StatusCodeException as e:
                print(f"Неверный статус код {url}: {e}")
            except Exception as e:
                print(f"Непредвиденная ошибка {url}: {e}")

    async def _db_save_worker(self):
        batch = []
        batch_size = 100

        while self.is_saving or not self.results_queue.empty():
            try:
                url, title, content = await asyncio.wait_for(
                    self.results_queue.get(), timeout=self.task_timeout
                )
                batch.append((url, title, content))

                if len(batch) >= batch_size or (
                    not self.is_saving and self.results_queue.empty()
                ):
                    if batch:
                        await self.bulk_insert_to_db(batch)
                        batch = []

                self.results_queue.task_done()

            except asyncio.TimeoutError:
                if not self.is_saving and self.results_queue.empty():
                    break
                continue
            except asyncio.CancelledError:
                if batch:
                    await self.bulk_insert_to_db(batch)
                break
            except Exception as e:
                print(f"Ошибка в воркере БД: {e}")

        if batch:
            await self.bulk_insert_to_db(batch)

    async def _parse_task_worker(self):
        while self.is_run:
            try:
                url, depth = await asyncio.wait_for(
                    self.task_queue.get(), timeout=self.task_timeout
                )
                await self._process_task(url, depth)
            except asyncio.CancelledError:
                break
            except asyncio.TimeoutError:
                if self.task_queue.empty():
                    break
                continue
            except Exception as e:
                print(f"Неизвестная ошибка: {e}")
            finally:
                self.task_queue.task_done()

    async def _create_task_queue(self, url: str, current_depth: int):
        await self._add_task_to_queue(url, current_depth)
        tasks = []
        for _ in range(self.requests_limit):
            task = asyncio.create_task(self._parse_task_worker())
            tasks.append(task)
            # TODO: вернуть чтение из очереди. Пока не реализована запись в бд
            # db_task = asyncio.create_task(self.())
            # tasks.append(db_task)
        try:
            await self.task_queue.join()
        finally:
            self.is_run = False
            self.is_saving = False
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _parse(self, url: str):
        try:
            await self._create_task_queue(url, 0)
            print(self.results_queue.qsize())
            print(self.results_queue)
        except Exception as e:
            print("🐍 File: spectrum_data/parser.py | Line: 22 | start ~ e", e)

