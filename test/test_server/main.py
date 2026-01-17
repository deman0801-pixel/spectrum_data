# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import random
from typing import Dict, List
import time

app = FastAPI(
    title="Tree Crawler Test Server",
    description="Сервер с древовидной структурой страниц для тестирования веб-краулеров",
    version="1.0.0"
)

# Добавляем CORS для удобства тестирования
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Структура нашего дерева (URL -> [дочерние URL])
TREE_STRUCTURE = {
    "/": ["/level1/a", "/level1/b", "/level1/c"],
    "/level1/a": ["/level1/a/x", "/level1/a/y"],
    "/level1/b": ["/level1/b/x", "/level1/b/y"],
    "/level1/c": ["/level1/c/x", "/level1/c/y"],
    "/level1/a/x": ["/level1/a/x/1", "/level1/a/x/2"],
    "/level1/a/y": ["/level1/a/y/1", "/level1/a/y/2"],
    "/level1/b/x": ["/level1/b/x/1", "/level1/b/x/2"],
    "/level1/b/y": ["/level1/b/y/1", "/level1/b/y/2"],
    "/level1/c/x": ["/level1/c/x/1", "/level1/c/x/2"],
    "/level1/c/y": ["/level1/c/y/1", "/level1/c/y/2"],
    # Листья дерева (без детей)
    "/level1/a/x/1": [],
    "/level1/a/x/2": [],
    "/level1/a/y/1": [],
    "/level1/a/y/2": [],
    "/level1/b/x/1": [],
    "/level1/b/x/2": [],
    "/level1/b/y/1": [],
    "/level1/b/y/2": [],
    "/level1/c/x/1": [],
    "/level1/c/x/2": [],
    "/level1/c/y/1": [],
    "/level1/c/y/2": [],
}

# Специальные тестовые страницы с разными сценариями
SPECIAL_PAGES = {
    "/error/500": {"type": "server_error", "status": 500},
    "/error/404": {"type": "not_found", "status": 404},
    "/timeout": {"type": "timeout", "delay": 5},
    "/redirect": {"type": "redirect", "target": "/level1/a"},
    "/cyclic/a": {"type": "cyclic", "links": ["/cyclic/b"]},
    "/cyclic/b": {"type": "cyclic", "links": ["/cyclic/a"]},
    "/external": {"type": "external", "links": ["https://google.com"]},
    "/large": {"type": "large", "size_kb": 100},  # 100KB страница
    "/malformed": {"type": "malformed"},  # Невалидный HTML
    "/slow": {"type": "slow", "delay": 2},  # Медленная загрузка
}

def generate_html(title: str, links: List[str], current_path: str) -> str:
    """Генерирует HTML страницу с заданными ссылками"""
    
    links_html = ""
    for link in links:
        links_html += f'<li><a href="{link}">{link}</a></li>\n'
    
    # Добавляем случайные "шумовые" ссылки для реалистичности
    noise_links = [
        "/privacy", "/terms", "/about", "/contact",
        "#top", "#main", "javascript:void(0)",
        "mailto:test@example.com",
        "tel:+1234567890"
    ]
    
    for noise in random.sample(noise_links, 2):
        links_html += f'<li><a href="{noise}">{noise} (noise)</a></li>\n'
    
    # Показываем путь в дереве
    breadcrumbs = " → ".join([part for part in current_path.split("/") if part])
    if breadcrumbs:
        breadcrumbs = "Home → " + breadcrumbs
    else:
        breadcrumbs = "Home"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            .tree {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            .links {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; }}
            .breadcrumbs {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
            .current {{ color: #333; font-weight: bold; }}
            .info {{ background-color: #fff3cd; padding: 10px; border-radius: 3px; margin: 10px 0; }}
            li {{ margin: 5px 0; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            h1 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="breadcrumbs">{breadcrumbs}</div>
        <h1>🌳 {title}</h1>
        
        <div class="info">
            <strong>Current URL:</strong> {current_path}<br>
            <strong>Depth in tree:</strong> {len([p for p in current_path.split('/') if p])}<br>
            <strong>Links on page:</strong> {len(links) + 2}
        </div>
        
        <div class="tree">
            <h3>🌍 Navigation Tree</h3>
            <ul>
                <li><a href="/">Home (Root)</a></li>
                <li><a href="/level1/a">Level 1 - Branch A</a></li>
                <li><a href="/level1/b">Level 1 - Branch B</a></li>
                <li><a href="/level1/c">Level 1 - Branch C</a></li>
            </ul>
        </div>
        
        <div class="links">
            <h3>🔗 Links from this page ({len(links)}):</h3>
            <ul>
                {links_html}
            </ul>
        </div>
        
        <div class="info">
            <h3>📊 Page Information</h3>
            <p>This is a test page for web crawler training.</p>
            <p>Tree depth: {current_path.count('/') - 1}</p>
            <p>Server time: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <!-- Скрытый комментарий для теста парсера -->
        <!-- Test comment: page_id={random.randint(1000, 9999)} -->
        
        <!-- Немного динамического контента -->
        <script>
            console.log("Test page loaded: {current_path}");
            document.addEventListener('DOMContentLoaded', function() {{
                console.log("DOM ready for {title}");
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content

def generate_special_html(page_type: str, path: str) -> str:
    """Генерирует специальные страницы для тестирования граничных случаев"""
    
    special_templates = {
        "server_error": """
        <!DOCTYPE html>
        <html>
        <head><title>500 Server Error</title></head>
        <body>
            <h1>500 - Internal Server Error</h1>
            <p>This page simulates a server error for crawler testing.</p>
            <p><a href="/">Back to home</a></p>
        </body>
        </html>
        """,
        
        "not_found": """
        <!DOCTYPE html>
        <html>
        <head><title>404 Not Found</title></head>
        <body>
            <h1>404 - Page Not Found</h1>
            <p>This page doesn't exist. Good crawlers should handle 404s.</p>
            <p><a href="/">Back to home</a></p>
        </body>
        </html>
        """,
        
        "timeout": """
        <!DOCTYPE html>
        <html>
        <head><title>Timeout Test</title></head>
        <body>
            <h1>Timeout Simulation</h1>
            <p>This page has a 5-second delay to test crawler timeouts.</p>
            <p>Loading... (check your crawler's timeout settings)</p>
            <p><a href="/">Back to home</a></p>
        </body>
        </html>
        """,
        
        "redirect": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redirect Page</title>
            <meta http-equiv="refresh" content="2;url=/level1/a">
        </head>
        <body>
            <h1>Redirecting...</h1>
            <p>This page redirects to /level1/a after 2 seconds.</p>
            <p><a href="/level1/a">Go directly</a></p>
        </body>
        </html>
        """,
        
        "cyclic": """
        <!DOCTYPE html>
        <html>
        <head><title>Cyclic Link Test</title></head>
        <body>
            <h1>Cyclic Link Page</h1>
            <p>This page is part of a cycle: A → B → A</p>
            <p><a href="/cyclic/b">Go to cyclic B</a></p>
            <p><a href="/">Back to home</a></p>
        </body>
        </html>
        """,
        
        "external": """
        <!DOCTYPE html>
        <html>
        <head><title>External Links</title></head>
        <body>
            <h1>External Links Test</h1>
            <p>This page contains links to external domains.</p>
            <p><a href="https://google.com">Google (external)</a></p>
            <p><a href="https://github.com">GitHub (external)</a></p>
            <p><a href="/">Internal link</a></p>
        </body>
        </html>
        """,
        
        "large": """
        <!DOCTYPE html>
        <html>
        <head><title>Large Page</title></head>
        <body>
            <h1>Large Page Test</h1>
            <p>This page is intentionally large (~100KB).</p>
            <div id="large-content">
        """ + ("A" * 1024 * 100) + """  <!-- 100KB of content -->
            </div>
            <p><a href="/">Back to home</a></p>
        </body>
        </html>
        """,
        
        "malformed": """
        <!DOCTYPE html>
        <html>
        <head><title>Malformed HTML</title></head>
        <body>
            <h1>Malformed HTML Test</h1>
            <p>This page has intentionally malformed HTML.</p>
            <unclosed_tag>
            <p>Missing closing p tag
            <a href="/">Back to home</a>
            <!-- Unclosed comment
        </body>
        </html>
        """,
        
        "slow": """
        <!DOCTYPE html>
        <html>
        <head><title>Slow Loading</title></head>
        <body>
            <h1>Slow Loading Page</h1>
            <p>This page loads slowly (2-second delay).</p>
            <p>Testing crawler patience...</p>
            <p><a href="/">Back to home</a></p>
            <script>
                // Имитируем медленную загрузку
                setTimeout(() => {{
                    document.getElementById('slow-content').innerHTML = 
                        '<p>Content loaded after delay!</p>';
                }}, 2000);
            </script>
            <div id="slow-content"></div>
        </body>
        </html>
        """
    }
    
    return special_templates.get(page_type, "<h1>Unknown special page</h1>")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Корневая страница с ссылками на первый уровень"""
    title = "Tree Crawler Test - Home Page"
    links = TREE_STRUCTURE.get("/", [])
    return HTMLResponse(content=generate_html(title, links, "/"))

@app.get("/level1/{branch}", response_class=HTMLResponse)
async def level1_branch(branch: str):
    """Страницы первого уровня (A, B, C)"""
    path = f"/level1/{branch}"
    if path not in TREE_STRUCTURE:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    title = f"Level 1 - Branch {branch.upper()}"
    links = TREE_STRUCTURE.get(path, [])
    return HTMLResponse(content=generate_html(title, links, path))

@app.get("/level1/{branch}/{subpage}", response_class=HTMLResponse)
async def level2_page(branch: str, subpage: str):
    """Страницы второго уровня (A/X, A/Y, B/X, etc.)"""
    path = f"/level1/{branch}/{subpage}"
    if path not in TREE_STRUCTURE:
        raise HTTPException(status_code=404, detail="Page not found")
    
    title = f"Level 2 - {branch.upper()}/{subpage.upper()}"
    links = TREE_STRUCTURE.get(path, [])
    return HTMLResponse(content=generate_html(title, links, path))

@app.get("/level1/{branch}/{subpage}/{leaf}", response_class=HTMLResponse)
async def level3_leaf(branch: str, subpage: str, leaf: str):
    """Листья дерева (третий уровень)"""
    path = f"/level1/{branch}/{subpage}/{leaf}"
    if path not in TREE_STRUCTURE:
        raise HTTPException(status_code=404, detail="Leaf not found")
    
    title = f"Level 3 - Leaf {leaf}"
    links = TREE_STRUCTURE.get(path, [])
    return HTMLResponse(content=generate_html(title, links, path))

@app.get("/error/{code}", response_class=HTMLResponse)
async def error_page(code: int):
    """Страницы с ошибками"""
    if code == 500:
        return HTMLResponse(
            content=generate_special_html("server_error", f"/error/{code}"),
            status_code=500
        )
    elif code == 404:
        return HTMLResponse(
            content=generate_special_html("not_found", f"/error/{code}"),
            status_code=404
        )
    else:
        raise HTTPException(status_code=404, detail="Error page not found")

@app.get("/timeout", response_class=HTMLResponse)
async def timeout_page():
    """Страница с задержкой (тест таймаутов)"""
    await asyncio.sleep(5)  # 5-секундная задержка
    return HTMLResponse(content=generate_special_html("timeout", "/timeout"))

@app.get("/redirect", response_class=HTMLResponse)
async def redirect_page():
    """Страница с редиректом"""
    return HTMLResponse(content=generate_special_html("redirect", "/redirect"))

@app.get("/cyclic/{page}", response_class=HTMLResponse)
async def cyclic_page(page: str):
    """Циклические ссылки (A→B→A)"""
    if page in ["a", "b"]:
        return HTMLResponse(content=generate_special_html("cyclic", f"/cyclic/{page}"))
    raise HTTPException(status_code=404, detail="Cyclic page not found")

@app.get("/external", response_class=HTMLResponse)
async def external_links_page():
    """Страница с внешними ссылками"""
    return HTMLResponse(content=generate_special_html("external", "/external"))

@app.get("/large", response_class=HTMLResponse)
async def large_page():
    """Большая страница (~100KB)"""
    return HTMLResponse(content=generate_special_html("large", "/large"))

@app.get("/malformed", response_class=HTMLResponse)
async def malformed_page():
    """Страница с невалидным HTML"""
    return HTMLResponse(content=generate_special_html("malformed", "/malformed"))

@app.get("/slow", response_class=HTMLResponse)
async def slow_page():
    """Медленно загружающаяся страница"""
    await asyncio.sleep(2)  # 2-секундная задержка
    return HTMLResponse(content=generate_special_html("slow", "/slow"))

@app.get("/sitemap", response_class=HTMLResponse)
async def sitemap():
    """Карта сайта для отладки"""
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Site Map</title></head>
    <body>
        <h1>🌳 Site Map for Crawler Testing</h1>
        
        <h2>Main Tree Structure (depth 0-3):</h2>
        <ul>
            <li><a href="/">/ (Root) - Depth 0</a></li>
            <li><a href="/level1/a">/level1/a - Depth 1</a></li>
            <li><a href="/level1/b">/level1/b - Depth 1</a></li>
            <li><a href="/level1/c">/level1/c - Depth 1</a></li>
            <ul>
                <li><a href="/level1/a/x">/level1/a/x - Depth 2</a></li>
                <li><a href="/level1/a/y">/level1/a/y - Depth 2</a></li>
                <li><a href="/level1/b/x">/level1/b/x - Depth 2</a></li>
                <li><a href="/level1/b/y">/level1/b/y - Depth 2</a></li>
                <li><a href="/level1/c/x">/level1/c/x - Depth 2</a></li>
                <li><a href="/level1/c/y">/level1/c/y - Depth 2</a></li>
                <ul>
                    <li><a href="/level1/a/x/1">/level1/a/x/1 - Depth 3</a></li>
                    <li><a href="/level1/a/x/2">/level1/a/x/2 - Depth 3</a></li>
                    <li><a href="/level1/a/y/1">/level1/a/y/1 - Depth 3</a></li>
                    <li>... (12 leaf pages total)</li>
                </ul>
            </ul>
        </ul>
        
        <h2>Special Test Pages:</h2>
        <ul>
            <li><a href="/error/500">/error/500 - Server Error</a></li>
            <li><a href="/error/404">/error/404 - Not Found</a></li>
            <li><a href="/timeout">/timeout - 5-second delay</a></li>
            <li><a href="/redirect">/redirect - Redirect page</a></li>
            <li><a href="/cyclic/a">/cyclic/a - Cyclic links (A→B→A)</a></li>
            <li><a href="/external">/external - External links</a></li>
            <li><a href="/large">/large - 100KB page</a></li>
            <li><a href="/malformed">/malformed - Invalid HTML</a></li>
            <li><a href="/slow">/slow - Slow loading (2s)</a></li>
        </ul>
        
        <h2>API Endpoints:</h2>
        <ul>
            <li><a href="/docs">/docs - Swagger UI</a></li>
            <li><a href="/redoc">/redoc - ReDoc</a></li>
            <li><a href="/openapi.json">/openapi.json - OpenAPI spec</a></li>
        </ul>
        
        <div style="margin-top: 30px; padding: 15px; background: #f0f0f0;">
            <strong>Total pages:</strong> {main_pages} main tree + {special_pages} special = {total_pages} pages
        </div>
    </body>
    </html>
    """.format(
        main_pages=len(TREE_STRUCTURE),
        special_pages=len(SPECIAL_PAGES),
        total_pages=len(TREE_STRUCTURE) + len(SPECIAL_PAGES)
    )
    
    return HTMLResponse(content=html)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tree-crawler-test-server",
        "timestamp": time.time(),
        "pages_available": len(TREE_STRUCTURE) + len(SPECIAL_PAGES),
        "tree_depth": 4
    }

@app.get("/api/tree")
async def get_tree_structure():
    """API endpoint для получения структуры дерева (полезно для тестов)"""
    return {
        "tree": TREE_STRUCTURE,
        "special_pages": list(SPECIAL_PAGES.keys()),
        "max_depth": 4,
        "total_pages": len(TREE_STRUCTURE) + len(SPECIAL_PAGES)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )