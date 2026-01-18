from urllib.parse import urljoin


class URLManager:
    def __init__(self):
        self.non_html_extensions = (
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".zip",
            ".rar",
            ".7z",
            ".tar",
            ".gz",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".svg",
            ".mp4",
            ".mp3",
            ".avi",
            ".mov",
            ".js",
            ".css",
            ".json",
            ".xml",
            ".exe",
            ".dmg",
            ".deb",
            ".rpm",
            ".tar.lz",
        )

    def normalize_url(self, base_url: str, link: str) -> str:
        try:
            absolute = urljoin(base_url, link)
            normalized = absolute.split("#")[0].split("?")[0]
            if normalized:
                is_http = normalized.startswith("http")
                is_html = not normalized.endswith(self.non_html_extensions)
                if all([is_http, is_html]):
                    return normalized
            return None
        except Exception:
            return None
