from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Tuple

from src.infrastructure.models import (
    Player, Ship,
    PlayerGun, PlayerHull, HullTemplate,
    GunTemplate
)

class ShipService:
    def __init__(self, db: Session):
        self.db = db

    def get_active_ship(self, player_id: int) -> dict:
        ship = self.db.execute(select(Ship).where(Ship.player_id == player_id)).scalar_one_or_none()
        if not ship:
            raise ValueError("Активный корабль не найден")

        player_gun = self.db.get(PlayerGun, ship.player_gun_id)
        player_hull = self.db.get(PlayerHull, ship.player_hull_id)

        gun = self.db.get(GunTemplate, player_gun.gun_id)
        hull = self.db.get(HullTemplate, player_hull.hull_id)

        return {
            "ship": ship,
            "player_gun": player_gun,
            "gun": gun,
            "player_hull": player_hull,
            "hull": hull
        }

    def get_active_ship(self, player_id: int) -> dict:
        ship = self.db.execute(select(Ship).where(Ship.player_id == player_id)).scalar_one_or_none()
        if not ship:
            raise ValueError("Активный корабль не найден")

        player_gun = self.db.get(PlayerGun, ship.player_gun_id)
        player_hull = self.db.get(PlayerHull, ship.player_hull_id)

        gun = self.db.get(GunTemplate, player_gun.gun_id)
        hull = self.db.get(HullTemplate, player_hull.hull_id)

        return {
            "ship": ship,
            "player_gun": player_gun,
            "gun": gun,
            "player_hull": player_hull,
            "hull": hull
        }

    def get_ship_stats(self, player_id: int) -> dict:
        data = self.get_active_ship(player_id)
        ship = data["ship"]
        gun = data["gun"]
        hull = data["hull"]
        level_gun = data["player_gun"].current_level
        level_hull = data["player_hull"].current_level

        return {
            "name": gun.name,
            "damage": self.calc(gun.base_damage, gun.gain_damage, level_gun),
            "crit_rate": self.calc(gun.base_crit_rate, gun.gain_crit_rate, level_gun),
            "crit_damage": self.calc(gun.base_crit_damage, gun.gain_crit_damage, level_gun),
            "speed": self.calc(gun.base_speed, gun.gain_speed, level_gun),
            "armor": self.calc(hull.base_armor, hull.gain_armor, level_hull),
            "maneuver": self.calc(hull.base_maneuver, hull.gain_maneuver, level_hull),
            "health": ship.health,
            "max_health": hull.base_max_health,
            "shields": ship.shields,
            "power_score": self.calc_power_score(gun, level_gun) + self.calc_power_score(hull, level_hull)
        }

    def calc(self, base, gain, level):
        return base + gain * (level - 1) if gain else base

    def calc_power_score(self, obj, level):
        if isinstance(obj, GunTemplate):
            return (
                self.calc(obj.base_damage, obj.gain_damage, level) +
                self.calc(obj.base_crit_rate, obj.gain_crit_rate, level) * 10 +
                self.calc(obj.base_crit_damage, obj.gain_crit_damage, level) * 2 +
                self.calc(obj.base_speed, obj.gain_speed, level)
            )
        elif isinstance(obj, HullTemplate):
            return (
                self.calc(obj.base_armor, obj.gain_armor, level) +
                self.calc(obj.base_max_shields, obj.gain_max_shields, level) +
                self.calc(obj.base_max_health, obj.gain_max_health, level) +
                self.calc(obj.base_maneuver, obj.gain_maneuver, level)
            )
        return 0

    def get_available_weapons(self, player_id: int) -> List[Tuple[PlayerGun, GunTemplate]]:
        player_guns = self.db.execute(
            select(PlayerGun).where(PlayerGun.player_id == player_id)
        ).scalars().all()

        return [(pg, self.db.get(GunTemplate, pg.gun_id)) for pg in player_guns]

    def get_available_hulls(self, player_id: int) -> List[HullTemplate]:
        player_hulls = self.db.execute(
            select(PlayerHull).where(PlayerHull.player_id == player_id)
        ).scalars().all()

        return [self.db.get(HullTemplate, ph.hull_id) for ph in player_hulls]

    def upgrade_weapon(self, player_id: int) -> dict:
        ship = self.db.execute(select(Ship).where(Ship.player_id == player_id)).scalar_one_or_none()
        if not ship:
            raise ValueError("Корабль не найден")

        player_gun = self.db.get(PlayerGun, ship.player_gun_id)
        if not player_gun:
            raise ValueError("Оружие игрока не найдено")

        player_gun.current_level += 1
        self.db.commit()

        return self.get_ship_stats(player_id)

    def change_weapon(self, player_id: int, new_gun_id: int) -> dict:
        ship = self.db.execute(select(Ship).where(Ship.player_id == player_id)).scalar_one_or_none()
        if not ship:
            raise ValueError("Корабль не найден")

        # Найдем нужное оружие
        new_pg = self.db.execute(
            select(PlayerGun).where(
                PlayerGun.player_id == player_id,
                PlayerGun.gun_id == new_gun_id
            )
        ).scalar_one_or_none()

        if not new_pg:
            raise ValueError("У игрока нет этого оружия")

        # Снимаем флаг со всех других пушек
        self.db.execute(
            PlayerGun.__table__.update()
            .where(PlayerGun.player_id == player_id)
            .values(is_equipped=False)
        )

        # Помечаем новую как активную
        new_pg.is_equipped = True

        # Обновляем корабль
        ship.player_gun_id = new_pg.id
        self.db.commit()

        return self.get_ship_stats(player_id)


    def change_hull(self, player_id: int, new_hull_id: int) -> dict:
        ship = self.db.execute(select(Ship).where(Ship.player_id == player_id)).scalar_one_or_none()
        if not ship:
            raise ValueError("Корабль не найден")

        new_ph = self.db.execute(
            select(PlayerHull).where(
                PlayerHull.player_id == player_id,
                PlayerHull.hull_id == new_hull_id
            )
        ).scalar_one_or_none()

        if not new_ph:
            raise ValueError("У игрока нет этого корпуса")

        # Снимаем флаг со всех других корпусов
        self.db.execute(
            PlayerHull.__table__.update()
            .where(PlayerHull.player_id == player_id)
            .values(is_equipped=False)
        )

        # Помечаем новый корпус как активный
        new_ph.is_equipped = True

        ship.player_hull_id = new_ph.id
        self.recalculate_stats(ship)
        self.db.commit()

        return self.get_ship_stats(player_id)


    def recalculate_stats(self, ship: Ship):
        player_hull = self.db.get(PlayerHull, ship.player_hull_id)
        hull_template = self.db.get(HullTemplate, player_hull.hull_id)

        ship.health = self.calc(hull_template.base_max_health, hull_template.gain_max_health, player_hull.current_level)
        ship.shields = self.calc(hull_template.base_max_shields, hull_template.gain_max_shields, player_hull.current_level)

    def repair_ship(self, player_id: int) -> dict:
        data = self.get_active_ship(player_id)
        ship = data["ship"]
        hull = data["hull"]
        level = data["player_hull"].current_level

        max_health = self.calc(hull.base_max_health, hull.gain_max_health, level)

        if ship.health >= max_health:
            return None  # Здоровье полное — не лечим

        ship.health = max_health
        self.db.commit()

        return {
            "health": ship.health,
            "max_health": max_health
        }
