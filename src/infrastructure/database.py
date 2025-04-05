from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.models import Base

# Подключение к PostgreSQL
DATABASE_URL = "postgresql+pg8000://postgres:xtsf8dDfr2as@212.109.198.57:5433/space_lords"


engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
