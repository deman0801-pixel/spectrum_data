from app.utils.parser import Parser


if __name__ == "__main__":
    parser = Parser()
    # надо запустить сервер для тестирования в папке test
    # cd test/test_server \
    # uvicorn main:app
    parser.start("http://127.0.0.1:8000", 3, 5)


