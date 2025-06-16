from sqlalchemy.orm import Session
from sqlalchemy import select
import datetime

from src.application.config_loader import config
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

            self.db.add(newPlayer)
            self.db.add(newPlayerResources)
            self.db.add(newPlayerGun)
            self.db.add(newPlayerHull)
            self.db.commit()

            newShip = Ship(
                player_id=id,
                player_gun_id=newPlayerGun.id,
                player_hull_id=newPlayerHull.id,
                health=0,
                shields=0
            )

            self.db.add(newShip)
            self.db.commit()

            # Добавляем все оставшиеся оружия (неэкипированные)
            guns_count = config["game"]["guns_count"]
            for i in range(2, guns_count):
                anotherPlayerGun = PlayerGun(
                    player_id=id,
                    gun_id=i,
                    is_equipped=False
                )
                self.db.add(anotherPlayerGun)

            # Добавляем все оставшиеся корпуса (неэкипированные)
            hulls_count = config["game"]["hulls_count"]
            for i in range(2, hulls_count):
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
    
    def get_new_users_count(self, interval: datetime.datetime):
        current_time = datetime.datetime.now()
        print(type(interval), type(current_time))
        start_time = current_time - interval
        
        result = self.db.execute(
            select(Player)
            .where(Player.created_at >= start_time)
            .where(Player.created_at <= current_time)
        ).all()

        return len(result)

    def get_id(self, username):
        player = self.db.execute(
            select(Player)
            .where(Player.username == username)
        ).scalar_one_or_none()
        
        return player.id if player else None

    def get_all(self):
        players = self.db.execute(
            select(Player)
        ).scalars().all()
        
        return players
    

    def get_username(self, player_id: int):
        player = self.db.execute(
            select(Player).
            where(Player.id == player_id)
        ).scalar_one_or_none()

        if not player:
            return None
        
        return player.username
    

    def get_resources(self, player_id: int):
        return self.db.execute(
            select(PlayerResources).
            where(PlayerResources.player_id == player_id)
        ).scalar_one()
        
    def set_resources(self, player_id: int, metals: int | None = None, crystalls: int | None = None, gas: int | None = None) -> bool:
        """
        Устанавливает абсолютные значения ресурсов игрока.
        Если значение не указано (None), то оно не изменяется.

        Args:
            player_id (int): ID игрока
            metals (int | None): Новое значение металла
            crystalls (int | None): Новое значение кристаллов
            gas (int | None): Новое значение газа

        Returns:
            bool: True если операция успешна, False если произошла ошибка
        """
        try:
            # Получаем текущие ресурсы игрока
            resources = self.db.execute(
                select(PlayerResources)
                .where(PlayerResources.player_id == player_id)
            ).scalar_one()

            # Обновляем только указанные ресурсы
            if metals is not None:
                if metals < 0:
                    return False
                resources.metals = metals

            if crystalls is not None:
                if crystalls < 0:
                    return False
                resources.crystalls = crystalls

            if gas is not None:
                if gas < 0:
                    return False
                resources.gas = gas

            self.db.commit()
            return True

        except Exception:
            self.db.rollback()
            return False




