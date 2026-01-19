from sqlalchemy import Column, Index, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Page(Base):
    __tablename__ = "pages"

    url = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    html = Column(Text)

    __table_args__ = (
        Index('idx_pages_title', 'title'),
    )