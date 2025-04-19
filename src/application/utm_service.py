from sqlalchemy.orm import Session
from sqlalchemy import select
import datetime

from src.infrastructure.models import (
    UTMtag
)

class UtmService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_utm(self):
        utmTags = self.db.execute(select(UTMtag)).scalars().all()
        return utmTags

    def create_utm(self, tag: str):
        utmTag = self.db.execute(
            select(UTMtag).
            where(UTMtag.tag == tag)
        ).scalar_one_or_none()

        if utmTag:
            raise ValueError("Такой тег уже существует")
        
        created_at = datetime.datetime.now()
        newUTMtag = UTMtag(
            tag=tag, 
            created_at=created_at,
            used=0
        )

        self.db.add(newUTMtag)
        self.db.commit()

        return tag
    
    def increment_utm_usage(self, tag: str):
        utmTag = self.db.execute(
            select(UTMtag).
            where(UTMtag.tag == tag)
        ).scalar_one_or_none()

        if utmTag:
            # Если есть тег, то увеличиваем счётчик
            utmTag.used += 1

        self.db.commit()

