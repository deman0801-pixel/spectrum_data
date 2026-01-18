from asyncio import CancelledError, wait_for

from app.utils.crawler.managers.task_executor import TaskExecutor
from app.utils.crawler.managers.task_manager import TaskManager
from app.utils.crawler.managers.update_manager import UpdateManager


class WorkerManager:
    def __init__(
        self,
        task_manager: TaskManager,
        update_manager: UpdateManager,
        task_executor: TaskExecutor,
        task_timeout: int = 1,
    ):
        self.task_manager = task_manager
        self.update_manager = update_manager
        self.task_timeout = task_timeout
        self.task_executor = task_executor

    async def parse_task_worker(self):
        while self.task_manager.is_run:
            try:
                url, depth = await wait_for(
                    self.task_manager.task_queue.get(), timeout=self.task_timeout
                )
                await self.task_executor.execute(url, depth)
            except CancelledError:
                break
            except TimeoutError:
                if self.task_manager.task_queue.empty():
                    break
                continue
            except Exception as e:
                print(f"Неизвестная ошибка: {e}")
            finally:
                self.task_manager.task_queue.task_done()

    async def db_save_worker(self):
        batch = []
        batch_size = 100

        while self.update_manager.is_saving or not self.task_manager.results_queue.empty():
            try:
                url, title, content = await wait_for(
                    self.task_manager.results_queue.get(), timeout=self.task_timeout
                )
                batch.append((url, title, content))
                if len(batch) >= batch_size or (
                    not self.update_manager.is_saving and self.task_manager.results_queue.empty()
                ):
                    if batch:
                        await self.update_manager.bulk_insert_to_db(batch)
                        batch = []
                self.task_manager.results_queue.task_done()
            except TimeoutError:
                if not self.update_manager.is_saving and self.task_manager.results_queue.empty():
                    break
                continue
            except CancelledError:
                if batch:
                    await self.update_manager.bulk_insert_to_db(batch)
                break
            except Exception as e:
                print(f"Ошибка в воркере БД: {e}")
        if batch:
            await self.update_manager.bulk_insert_to_db(batch)

