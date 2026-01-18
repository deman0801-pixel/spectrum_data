from app.utils.crawler.crawler import Crawler


if __name__ == "__main__":
    parser = Crawler()
    
    # cd test/test_server \
    # uvicorn main:app
    parser.start("http://127.0.0.1:8000", 3, 5) # надо запустить сервер для тестирования в папке test
    parser.start("https://example.com/", 2, 5)


