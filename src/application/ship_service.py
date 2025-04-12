from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Tuple
from datetime import datetime, timedelta, timezone
import pytz

from src.infrastructure.models import (
    Player, Ship,
    PlayerGun, PlayerHull, HullTemplate,
    GunTemplate, PlayerResources
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

    def get_ship_stats(self, player_id: int) -> dict:
        data = self.get_active_ship(player_id)
        ship = data["ship"]
        gun = data["gun"]
        hull = data["hull"]
        level_gun = data["player_gun"].current_level
        level_hull = data["player_hull"].current_level

        power_gun = round(self.get_weapon_power(gun, level_gun), 2)
        power_hull = round(self.get_hull_power(hull, level_hull), 2)

        return {
            # Gun
            "name_gun": gun.name,
            "damage_gun": round(self.calc(gun.base_damage, gun.gain_damage, level_gun), 2),
            "crit_rate_gun": round(self.calc(gun.base_crit_rate, gun.gain_crit_rate, level_gun) * 100, 2),
            "crit_damage_gun": round(self.calc(gun.base_crit_damage, gun.gain_crit_damage, level_gun), 2),
            "speed_gun": round(self.calc(gun.base_speed, gun.gain_speed, level_gun), 2),
            "level_gun": level_gun,
            "power_gun": power_gun,

            # Hull
            "name_hull": hull.name,
            "armor_hull": round(self.calc(hull.base_armor, hull.gain_armor, level_hull), 2),
            "maneuver_hull": round(self.calc(hull.base_maneuver, hull.gain_maneuver, level_hull), 2),
            "max_health_hull": round(self.calc(hull.base_max_health, hull.gain_max_health, level_hull), 2),
            "shields_hull": round(self.calc(hull.base_max_shields, hull.gain_max_shields, level_hull), 2),
            "level_hull": level_hull,
            "power_hull": power_hull,

            # Ship
            "health": round(ship.health, 2),
            "power_score": round(power_gun * power_hull, 2)
        }

    def get_weapon_stats(self, player_id: int) -> dict:
        data = self.get_active_ship(player_id)
        gun = data["gun"]
        level = data["player_gun"].current_level

        return {
            "name_gun": gun.name,
            "level_gun": level,
            "damage_gun": round(self.calc(gun.base_damage, gun.gain_damage, level), 2),
            "crit_rate_gun": round(self.calc(gun.base_crit_rate, gun.gain_crit_rate, level) * 100, 2),
            "crit_damage_gun": round(self.calc(gun.base_crit_damage, gun.gain_crit_damage, level), 2),
            "speed_gun": round(self.calc(gun.base_speed, gun.gain_speed, level), 2),
            "power_gun": round(self.get_weapon_power(gun, level), 2)
        }

    def get_hull_stats(self, player_id: int) -> dict:
        data = self.get_active_ship(player_id)
        hull = data["hull"]
        ship = data["ship"]
        level = data["player_hull"].current_level

        return {
            "name_hull": hull.name,
            "level_hull": level,
            "armor_hull": round(self.calc(hull.base_armor, hull.gain_armor, level), 2),
            "maneuver_hull": round(self.calc(hull.base_maneuver, hull.gain_maneuver, level), 2),
            "max_health_hull": round(self.calc(hull.base_max_health, hull.gain_max_health, level), 2),
            "shields_hull": round(self.calc(hull.base_max_shields, hull.gain_max_shields, level), 2),
            "health": round(ship.health, 2),
            "power_hull": round(self.get_hull_power(hull, level), 2)
        }

    def calc(self, base, gain, level):
        base = float(base)
        gain = float(gain) if gain else 0
        return base + gain * (level - 1)

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

        if player_gun.current_level >= 20:
            return {
                "can_upgrade": False,
                "reason": "Максимальный уровень",
                "level": 20
            }

        # Получаем ресурсы игрока
        resources = self.db.execute(
            select(PlayerResources).where(PlayerResources.player_id == player_id)
        ).scalar_one_or_none()
        if not resources:
            raise ValueError("Ресурсы игрока не найдены")

        gun = self.db.get(GunTemplate, player_gun.gun_id)
        current_level = player_gun.current_level
        next_level = current_level + 1

        # Вычисляем мощь сейчас и на следующем уровне
        power_now = self.get_weapon_power(gun, current_level)
        power_next = self.get_weapon_power(gun, next_level)

        cost = int(100 * (power_next ** 1.5 - power_now ** 1.5))

        if resources.crystalls < cost:
            return {
                "can_upgrade": False,
                "required": cost,
                "available": resources.crystalls
            }

        resources.crystalls -= cost
        player_gun.current_level = next_level
        self.db.commit()

        return self.get_weapon_stats(player_id)

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

        return self.get_weapon_stats(player_id)

    def upgrade_hull(self, player_id: int) -> dict:
        data = self.get_active_ship(player_id)
        player_hull = data["player_hull"]
        hull = data["hull"]

        if player_hull.current_level >= 20:
            return {
                "can_upgrade": False,
                "reason": "Корпус уже имеет максимальный уровень (20)."
            }

        current_level = player_hull.current_level
        next_level = current_level + 1

        power_now = self.get_hull_power(hull, current_level)
        power_next = self.get_hull_power(hull, next_level)
        cost = self.get_upgrade_cost(power_now, power_next)

        resources = self.db.execute(
            select(PlayerResources).where(PlayerResources.player_id == player_id)
        ).scalar_one_or_none()

        if not resources:
            raise ValueError("Ресурсы игрока не найдены.")

        if resources.metals < cost:
            return {
                "can_upgrade": False,
                "reason": f"Недостаточно металлов. Нужно: {cost}, у вас: {resources.metals}"
            }

        # списание металлов и апгрейд уровня
        resources.metals -= cost
        player_hull.current_level = next_level

        self.recalculate_stats(data["ship"])
        self.db.commit()

        stats = self.get_hull_stats(player_id)
        stats["can_upgrade"] = True
        return stats

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

        return self.get_hull_stats(player_id)

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

        max_health = float(self.calc(hull.base_max_health, hull.gain_max_health, level))
        current_health = float(ship.health)

        if current_health >= max_health:
            raise ValueError("Корпус уже полностью отремонтирован!")

        damage_percent = (max_health - current_health) / max_health
        cost = int(damage_percent * 100)
        cooldown_minutes = int(damage_percent * 10)

        player_resources = self.db.execute(
            select(PlayerResources).where(PlayerResources.player_id == player_id)
        ).scalar_one_or_none()

        if not player_resources:
            raise ValueError("Ресурсы игрока не найдены.")

        if player_resources.crystalls < cost:
            if player_resources.crystalls < cost:
                return {
                    "can_repair": False,
                    "required": cost,
                    "available": player_resources.crystalls
                }

        player_resources.crystalls -= cost

        # Задаём дату окончания ремонта в UTC с таймзоной
        ship.repair_ends_at = datetime.now(timezone.utc) + timedelta(minutes=cooldown_minutes)

        self.db.commit()

        return {
            "restored_health": round(max_health),
            "max_health": round(max_health),
            "cost": cost,
            "cooldown_minutes": cooldown_minutes,
            "cooldown_seconds": int(damage_percent * 600)
        }

    # Расчет мощностей 
    def get_weapon_power(self, gun: GunTemplate, level: int) -> float: 
        damage = self.calc(gun.base_damage, gun.gain_damage, level)
        crit_rate = self.calc(gun.base_crit_rate, gun.gain_crit_rate, level) / 100
        crit_damage = self.calc(gun.base_crit_damage, gun.gain_crit_damage, level)
        speed = self.calc(gun.base_speed, gun.gain_speed, level)

        return speed / 100 * (damage * (1 + crit_damage * crit_rate)) # Мощь пушки = Скорость / 100 * (Урон * (1 + Крит. урон * Крит. частота))


    def get_hull_power(self, hull: HullTemplate, level: int) -> float:
        health = float(self.calc(hull.base_max_health, hull.gain_max_health, level))
        shields = float(self.calc(hull.base_max_shields, hull.gain_max_shields, level))
        armor = float(self.calc(hull.base_armor, hull.gain_armor, level))
        maneuver = self.calc(hull.base_maneuver, hull.gain_maneuver, level) / 100

        if armor >= 100:
            armor = 99.9  # чтобы не делить на 0

        survivability = (health / (100 - armor)) + (shields / 100)
        return 10 * (1 + maneuver) * survivability

    def get_upgrade_cost(self, old_power: float, new_power: float) -> int:
        return round(100 * (new_power ** 1.5))