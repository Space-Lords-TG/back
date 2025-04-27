import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.models import Base


DRIVER = "postgresql+pg8000"

DB_USERNAME = os.getenv('DB_USERNAME')
if DB_USERNAME is None:
    print('Need DB_USERNAME env var')
    sys.exit()

DB_PASSWORD = os.getenv('DB_PASSWORD')
if DB_PASSWORD is None:
    print('Need DB_PASSWORD env var')
    sys.exit()

DB_IP = os.getenv('DB_IP')
if DB_IP is None:
    print('Need DB_IP env var')
    sys.exit()

DB_PORT = os.getenv('DB_PORT')
if DB_PORT is None:
    print('Need DB_PORT env var')
    sys.exit()

DB_NAME = os.getenv('DB_NAME')
if DB_NAME is None:
    print('Need DB_NAME env var')
    sys.exit()

# Подключение к PostgreSQL
DATABASE_URL = DRIVER + "://" \
    + DB_USERNAME + ":" + DB_PASSWORD + "@" + DB_IP + ":" + DB_PORT + "/" + DB_NAME


engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
