from app.utils.crawler.crawler import Crawler
from asyncio import run

if __name__ == "__main__":
    crawler = Crawler()

    # cd test/test_server \
    # uvicorn main:app
    # run(crawler.start("http://127.0.0.1:8000", 3, 5)) # надо запустить сервер для тестирования в папке test
    run(crawler.start("https://example.com/", 2, 5))
