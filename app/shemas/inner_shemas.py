from pydantic import BaseModel


class CrawlRequest(BaseModel):
    url: str
    max_depth: int = 2
    requests_limit: int = 5