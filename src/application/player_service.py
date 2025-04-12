from sqlalchemy.orm import Session
from sqlalchemy import select
import datetime

from src.infrastructure.models import (
    Player
)

class PlayerService:
    def __init__(self, db: Session):
        self.db = db

    def player_init(self, id: int, username: str):
        player = self.db.execute(select(Player).where(Player.id == id)).scalar_one_or_none()

        if not player:
            created_at = datetime.datetime.now()
            newPlayer = Player(id=id, username=username, created_at=created_at)
            self.db.add(newPlayer)
            self.db.commit()

            return newPlayer
        else:
            return player
