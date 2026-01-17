class StatusCodeException(Exception):
    def __init__(self, code: int):
        super().__init__(f"Ответ с кодом {code}")

