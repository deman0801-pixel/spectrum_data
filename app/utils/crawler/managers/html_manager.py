from typing import List, Tuple
from app.exceptions.status_code import StatusCodeException
from lxml import html

class HTMLManager:
    async def parse_response(self, response) -> Tuple[str, str, List[str]]:
        code: int = response.status
        if 200 <= code < 400:
            html_content = await response.text()
            title, links = self._get_info(html_content)
            return (html_content, title, links)
        else:
            raise StatusCodeException(code)

    def _get_info(self, html_raw: str) -> Tuple[str, List[str]]:
        page = html.fromstring(html_raw)
        head_title = page.xpath("//head/title/text()")
        title = head_title[0].strip() if head_title else None
        links = page.xpath("//a/@href")
        clean_links = [link.strip() for link in links if link and link.strip()]
        return (title, clean_links)