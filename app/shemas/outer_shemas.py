from pydantic import BaseModel


class MainPageView(BaseModel):
    url: str
    title: str


class HtmlView(BaseModel):
    html: str


class ErrorResponse(BaseModel):
    status: int
    message: str
