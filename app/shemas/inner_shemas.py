from pydantic import BaseModel, Field


class CrawlRequest(BaseModel):
    url: str = "https://example.com/"
    max_depth: int = Field(ge=1, default=1)
    requests_limit: int = 5
