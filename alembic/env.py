from sqlalchemy import create_engine
from alembic import context
from app.core.config import settings
from app.models.page import Base

url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(url)
with engine.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=Base.metadata
    )
    
    with context.begin_transaction():
        context.run_migrations()