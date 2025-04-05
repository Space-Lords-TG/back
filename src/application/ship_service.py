from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


from src.infrastructure.models import Player, Ship, Gun, Hull  # предполагаемое расположение моделей

class ShipService:
    def __init__(self, db: Session):
        self.db = db

    def get_active_ship(self, player_id: int) -> dict:
        ship = self.db.execute(
            select(Ship).where(Ship.player_id == player_id)
        ).scalar_one_or_none()

        if not ship:
            raise ValueError("Активный корабль не найден")

        gun = self.db.get(Gun, ship.gun_id)
        hull = self.db.get(Hull, ship.hull_id)

        return {
            "ship": ship,
            "gun": gun,
            "hull": hull
        }

    def get_ship_stats(self, player_id: int) -> dict:
        data = self.get_active_ship(player_id)
        ship = data["ship"]
        gun = data["gun"]
        hull = data["hull"]

        return {
            "damage": gun.damage,
            "crit_rate": gun.crit_rate,
            "crit_damage": gun.crit_damage,
            "speed": gun.speed,
            "armor": hull.armor,
            "maneuver": hull.maneuver,
            "health": ship.health,
            "shields": ship.shields,
            "power_score": ship.power_score
        }

    def get_available_weapons(self, player_id: int) -> List[Gun]:
        return self.db.execute(select(Gun)).scalars().all()

    def get_available_hulls(self, player_id: int) -> List[Hull]:
        return self.db.execute(select(Hull)).scalars().all()

    def upgrade_weapon(self, player_id: int) -> dict:
        ship = self.db.execute(select(Ship).where(Ship.player_id == player_id)).scalar_one_or_none()
        if not ship:
            raise ValueError("Корабль не найден")

        gun = self.db.get(Gun, ship.gun_id)
        if not gun:
            raise ValueError("Оружие не найдено")

        # Простейшее улучшение
        gun.damage = int(gun.damage * 1.1)
        gun.crit_damage = int(gun.crit_damage * 1.1)

        self.db.commit()

        return {
            "name": gun.name,
            "damage": gun.damage,
            "crit_rate": gun.crit_rate,
            "crit_damage": gun.crit_damage,
            "speed": gun.speed
        }

    def change_weapon(self, player_id: int, new_gun_id: int) -> dict:
        ship = self.db.execute(
            select(Ship).where(Ship.player_id == player_id)
        ).scalar_one_or_none()

        if not ship:
            raise ValueError("Корабль не найден")

        gun = self.db.get(Gun, new_gun_id)
        if not gun:
            raise ValueError("Оружие не найдено")

        ship.gun_id = new_gun_id
        self.recalculate_stats(ship)
        self.db.commit()
        return self.get_ship_stats(player_id)

    def change_hull(self, player_id: int, new_hull_id: int) -> dict:
        ship = self.db.execute(select(Ship).where(Ship.player_id == player_id)).scalar_one_or_none()
        if not ship:
            raise ValueError("Корабль не найден")

        hull = self.db.get(Hull, new_hull_id)
        if not hull:
            raise ValueError("Корпус не найден")

        ship.hull_id = new_hull_id
        self.recalculate_stats(ship)
        self.db.commit()

        return self.get_ship_stats(player_id)

    def recalculate_stats(self, ship: Ship):
        gun = self.db.get(Gun, ship.gun_id)
        hull = self.db.get(Hull, ship.hull_id)

        if not gun or not hull:
            raise ValueError("Невозможно пересчитать характеристики — отсутствуют компоненты")

        ship.health = int(hull.max_health)
        ship.shields = int(hull.max_shields)
        ship.power_score = int(gun.power_score) + int(hull.power_score)

    def repair_ship(self, player_id: int) -> dict:
        ship = self.db.execute(select(Ship).where(Ship.player_id == player_id)).scalar_one_or_none()
        if not ship:
            raise ValueError("Корабль не найден")

        hull = self.db.get(Hull, ship.hull_id)
        if not hull:
            raise ValueError("Корпус не найден")

        ship.health = int(hull.max_health)
        self.db.commit()

        return {
            "health": ship.health,
            "max_health": hull.max_health
        }