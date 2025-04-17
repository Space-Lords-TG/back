from sqlalchemy.orm import Session
from sqlalchemy import select
import datetime

from src.infrastructure.models import (
    Player, PlayerGun, PlayerHull, PlayerResources, Ship, HullTemplate
)


class PlayerService:
    def __init__(self, db: Session):
        self.db = db

    def player_init(self, id: int, username: str):
        player = self.db.execute(
            select(Player).
            where(Player.id == id)
        ).scalar_one_or_none()

        if not player:
            created_at = datetime.datetime.now()
            newPlayer = Player(
                id=id,
                username=username,
                created_at=created_at
                )
            newPlayerResources = PlayerResources(
                player_id=id
                )
            newPlayerGun = PlayerGun(
                player_id=id,
                gun_id=1,
                is_equipped=True
                )
            newPlayerHull = PlayerHull(
                player_id=id,
                hull_id=1,
                is_equipped=True
                )
            newShip = Ship(player_id=id, player_gun_id=1, player_hull_id=1, health=100, shields=100)
            self.db.add(newPlayer)
            self.db.add(newPlayerResources)
            self.db.add(newPlayerGun)
            self.db.add(newPlayerHull)
            self.db.add(newShip)
            # Добавляем все оставшиеся оружия (неэкипированные)
            for i in range(2, 8):
                anotherPlayerGun = PlayerGun(
                    player_id=id,
                    gun_id=i,
                    is_equipped=False
                    )
                self.db.add(anotherPlayerGun)

            # Добавляем все оставшиеся корпуса (неэкипированные)
            for i in range(2, 6):
                anotherPlayerHull = PlayerHull(
                    player_id=id,
                    hull_id=i,
                    is_equipped=False
                    )
                self.db.add(anotherPlayerHull)

            self.db.commit()
            # Пересчитываем параметры корабля
            self.recalculate_stats(newShip)
            self.db.commit()

            return newPlayer
        else:
            return player
        
    def recalculate_stats(self, ship: Ship):
        player_hull = self.db.get(
            PlayerHull,
            ship.player_hull_id
            )
        hull_template = self.db.get(
            HullTemplate,
            player_hull.hull_id
            )

        ship.health = self.calc(
            hull_template.base_max_health,
            hull_template.gain_max_health,
            player_hull.current_level
            )
        ship.shields = self.calc(
            hull_template.base_max_shields,
            hull_template.gain_max_shields,
            player_hull.current_level
            )

    def calc(self, base, gain, level):
        base = float(base)
        gain = float(gain) if gain else 0
        return base + gain * (level - 1)
