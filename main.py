from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.routers.searching import endpoints as searching
from app.api.routers.geting import endpoints as geting
from app.api.routers.crawler_manage import endpoints as crawler_manage
from app.core.database import engine
from app.models.page import Base


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(title="Pages", version="1.0.0")
for handler in (geting, searching, crawler_manage):
    app.include_router(handler.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")
