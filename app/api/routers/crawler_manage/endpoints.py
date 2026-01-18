from fastapi import APIRouter, BackgroundTasks

from app.shemas.inner_shemas import CrawlRequest
from app.utils.crawler.crawler import Crawler

router = APIRouter(prefix="/crawler", tags=["Управление обходчиком"])


@router.post("/start", summary="Запустить обходчик")
async def start_crawler(request: CrawlRequest, background_tasks: BackgroundTasks):
    crawler = Crawler()

    background_tasks.add_task(
        crawler.start, request.url, request.max_depth, request.requests_limit
    )

    return {"status": 200, "message": "Обходчик запущен в фоне"}
