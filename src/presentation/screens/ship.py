from datetime import datetime, timezone

from pytz import timezone as pytz_timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

from src.application.config_loader import config
from src.application.player_service import PlayerService
from src.application.ship_service import ShipService
from src.infrastructure.database import SessionLocal
from src.presentation.screens.registry import register, register_pattern
from texts import SHIP_MAIN_TEXT, SHIP_TUTORIAL_TEXT, WEAPON_INFO_TEXT, \
    WEAPON_UPGRADE_PREVIEW_TEXT, \
    NOT_ENOUGH_RESOURCES_TEXT, WEAPON_UPGRADE_SUCCESS_TEXT, WEAPON_CHANGE_TEXT, \
    WEAPON_CHANGE_SUCCESS_TEXT, \
    HULL_INFO_TEXT, HULL_CHANGE_TEXT, HULL_CHANGE_SUCCESS_TEXT, \
    HULL_UPGRADE_PREVIEW_TEXT, HULL_UPGRADE_SUCCESS_TEXT, \
    REPAIR_IN_PROGRESS_TEXT, REPAIR_INFO_TEXT, REPAIR_COSTS_TEXT, REPAIR_STARTED_TEXT, \
    REPAIR_COMPLETE_TEXT

# Определяем идентификаторы экранов
# Главные экраны
SHIP = config["screens"]['SHIP']
SHIP_WEAPON = config["screens"]['SHIP_WEAPON']
SHIP_BODY = config["screens"]['SHIP_BODY']

# Улучшения
SHIP_WEAPON_UPGRADE = config["screens"]['SHIP_WEAPON_UPGRADE']
POST_SHIP_WEAPON_UPGRADE = config["screens"]['POST_SHIP_WEAPON_UPGRADE']
SHIP_HULL_UPGRADE = config["screens"]['SHIP_HULL_UPGRADE']
POST_HULL_UPGRADE = config["screens"]['POST_HULL_UPGRADE']

# Замены
SHIP_WEAPON_CHANGE = config["screens"]['SHIP_WEAPON_CHANGE']
POST_SHIP_WEAPON = config["screens"]["POST_SHIP_WEAPON"]  # динамический handler
SHIP_HULL_CHANGE = config["screens"]['SHIP_HULL_CHANGE']
POST_SHIP_BODY = config["screens"]["POST_SHIP_BODY"]  # динамический handler

# Ремонт
SHIP_BODY_REPAIR = config["screens"]['SHIP_BODY_REPAIR']
POST_SHIP_BODY_REPAIR = config["screens"]['POST_SHIP_BODY_REPAIR']


def format_percent(value):
    return f"{int(value * 10000) / 100:.2f}"


@register(SHIP)
def get_ship(message: Message):
    db = SessionLocal()
    try:
        if not message.from_user:
            raise ValueError("Не удалось определить пользователя.")

        player_id = message.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, SHIP)
        service = ShipService(db)
        stats = service.get_ship_stats(player_id)

        keyboard = [
            [InlineKeyboardButton("Оружие", callback_data=SHIP_WEAPON),
             InlineKeyboardButton("Корпус", callback_data=SHIP_BODY)],
            [InlineKeyboardButton("Ремонт", callback_data=SHIP_BODY_REPAIR)]
        ]

        text = SHIP_MAIN_TEXT.format(**stats)
        if player_service.get_screen_view_count(player_id, SHIP) == 0:
            text = SHIP_TUTORIAL_TEXT + text
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register(SHIP_WEAPON)
def get_ship_weapon(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, SHIP_WEAPON)
        service = ShipService(db)

        stats = service.get_weapon_stats(player_id)
        gun = service.get_active_ship(player_id)['gun']
        level = stats['level_gun']

        power_now = service.get_weapon_power(gun, level)
        cost = service.get_upgrade_cost(power_now)

        keyboard = [
            [InlineKeyboardButton("Заменить", callback_data=SHIP_WEAPON_CHANGE),
             InlineKeyboardButton("Улучшить", callback_data=SHIP_WEAPON_UPGRADE)],
            [InlineKeyboardButton("Назад", callback_data=SHIP)]
        ]

        text = WEAPON_INFO_TEXT.format(**stats, cost=cost)
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register(SHIP_WEAPON_UPGRADE)
def get_ship_weapon_upgrade(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, SHIP_WEAPON_UPGRADE)
        service = ShipService(db)

        ship_data = service.get_active_ship(player_id)
        gun = ship_data["gun"]
        player_gun = ship_data["player_gun"]
        level = player_gun.current_level

        power_now = service.get_weapon_power(gun, level)
        power_next = service.get_weapon_power(gun, level + 1)
        cost = service.get_upgrade_cost(power_now)

        current_stats = {
            'current_damage': service.calc(gun.base_damage, gun.gain_damage, level),
            'current_crit_rate': format_percent(
                service.calc(gun.base_crit_rate, gun.gain_crit_rate, level)),
            'current_crit_damage': service.calc(gun.base_crit_damage,
                                                gun.gain_crit_damage, level),
            'current_speed': service.calc(gun.base_speed, gun.gain_speed, level),
            'current_power': power_now,
            'next_damage': service.calc(gun.base_damage, gun.gain_damage, level + 1),
            'next_crit_rate': format_percent(
                service.calc(gun.base_crit_rate, gun.gain_crit_rate, level + 1)),
            'next_crit_damage': service.calc(gun.base_crit_damage, gun.gain_crit_damage,
                                             level + 1),
            'next_speed': service.calc(gun.base_speed, gun.gain_speed, level + 1),
            'next_power': power_next,
            'name_gun': gun.name,
            'current_level': level,
            'next_level': level + 1,
            'cost': cost
        }

        keyboard = [
            [InlineKeyboardButton("Подтвердить",
                                  callback_data=POST_SHIP_WEAPON_UPGRADE)],
            [InlineKeyboardButton("Назад", callback_data=SHIP)]
        ]

        text = WEAPON_UPGRADE_PREVIEW_TEXT.format(**current_stats)
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register(POST_SHIP_WEAPON_UPGRADE)
def post_ship_weapon_upgrade(query: CallbackQuery):
    try:
        db = SessionLocal()
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, POST_SHIP_WEAPON_UPGRADE)

        service = ShipService(db)
        result = service.upgrade_weapon(player_id)

        if not result.get("can_upgrade", True):
            keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP_WEAPON)]]
            text = NOT_ENOUGH_RESOURCES_TEXT.format(
                required=result['required'],
                available=result['available']
            )
            return InlineKeyboardMarkup(keyboard), text

        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP_WEAPON)]]
        text = WEAPON_UPGRADE_SUCCESS_TEXT.format(**result)
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register(SHIP_WEAPON_CHANGE)
def get_ship_weapon_change(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, SHIP_WEAPON_CHANGE)

        service = ShipService(db)
        current_stats = service.get_weapon_stats(player_id)
        available_guns = service.get_available_weapons(player_id)
        current_pg = service.get_active_ship(player_id)["player_gun"]

        keyboard = []
        for pg, gun in available_guns:
            if pg.id != current_pg.id:
                label = f"{gun.name} ({pg.current_level} уровень)"
                keyboard.append([
                    InlineKeyboardButton(label,
                                         callback_data=f"{POST_SHIP_WEAPON}_{gun.id}")
                ])

        keyboard.append([InlineKeyboardButton("Назад", callback_data=SHIP_WEAPON)])

        text = WEAPON_CHANGE_TEXT.format(**current_stats)
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register_pattern(rf"^{POST_SHIP_WEAPON}_(\d+)$")
def post_ship_weapon_change(query: CallbackQuery, match):
    gun_id = int(match.group(1))
    player_id = query.from_user.id
    db = SessionLocal()

    try:
        service = ShipService(db)
        stats = service.change_weapon(player_id, new_gun_id=gun_id)

        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP)]]
        text = WEAPON_CHANGE_SUCCESS_TEXT.format(**stats)
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register(SHIP_BODY)
def get_ship_body(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, SHIP_BODY)
        service = ShipService(db)

        stats = service.get_hull_stats(player_id)
        hull = service.get_active_ship(player_id)["hull"]
        level = stats['level_hull']

        power_now = service.get_hull_power(hull, level)
        cost = service.get_upgrade_cost(power_now)

        keyboard = [
            [InlineKeyboardButton("Заменить", callback_data=SHIP_HULL_CHANGE),
             InlineKeyboardButton("Улучшить", callback_data=SHIP_HULL_UPGRADE)],
            [InlineKeyboardButton("Назад", callback_data=SHIP)]
        ]

        text = HULL_INFO_TEXT.format(**stats, cost=cost)
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register(SHIP_HULL_CHANGE)
def get_ship_hull_change(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, SHIP_HULL_CHANGE)
        service = ShipService(db)

        stats = service.get_hull_stats(player_id)
        current_ph = service.get_active_ship(player_id)["player_hull"]
        available_hulls = service.get_available_hulls(player_id)

        keyboard = []
        for ph, hull in available_hulls:
            if ph.id != current_ph.id:
                label = f"{hull.name} ({ph.current_level} уровень)"
                keyboard.append([
                    InlineKeyboardButton(label,
                                         callback_data=f"{POST_SHIP_BODY}_{hull.id}")
                ])

        keyboard.append([InlineKeyboardButton("Назад", callback_data=SHIP_BODY)])

        text = HULL_CHANGE_TEXT.format(**stats)
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register_pattern(rf"^{POST_SHIP_BODY}_(\d+)$")
def post_ship_body_change(query: CallbackQuery, match):
    db = SessionLocal()
    try:
        hull_id = int(match.group(1))
        player_id = query.from_user.id
        service = ShipService(db)
        stats = service.change_hull(player_id, new_hull_id=hull_id)

        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP)]]
        text = HULL_CHANGE_SUCCESS_TEXT.format(**stats)
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register(SHIP_HULL_UPGRADE)
def get_ship_hull_upgrade(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, SHIP_HULL_UPGRADE)
        service = ShipService(db)

        ship_data = service.get_active_ship(player_id)
        hull = ship_data["hull"]
        level = ship_data["player_hull"].current_level

        if level >= 20:
            return None, "Корпус уже имеет максимальный уровень (20)."

        power_now = service.get_hull_power(hull, level)
        power_next = service.get_hull_power(hull, level + 1)
        cost = service.get_upgrade_cost(power_now)

        upgrade_stats = {
            'name_hull': hull.name,
            'current_level': level,
            'next_level': level + 1,
            'current_health': service.calc(hull.base_max_health, hull.gain_max_health,
                                           level),
            'next_health': service.calc(hull.base_max_health, hull.gain_max_health,
                                        level + 1),
            'current_armor': service.calc(hull.base_armor, hull.gain_armor, level),
            'next_armor': service.calc(hull.base_armor, hull.gain_armor, level + 1),
            'current_shields': service.calc(hull.base_max_shields,
                                            hull.gain_max_shields, level),
            'next_shields': service.calc(hull.base_max_shields, hull.gain_max_shields,
                                         level + 1),
            'current_maneuver': service.calc(hull.base_maneuver, hull.gain_maneuver,
                                             level),
            'next_maneuver': service.calc(hull.base_maneuver, hull.gain_maneuver,
                                          level + 1),
            'current_power': power_now,
            'next_power': power_next,
            'cost': cost
        }

        keyboard = [
            [InlineKeyboardButton("Подтвердить", callback_data=POST_HULL_UPGRADE)],
            [InlineKeyboardButton("Назад", callback_data=SHIP)]
        ]

        text = HULL_UPGRADE_PREVIEW_TEXT.format(**upgrade_stats)
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register(POST_HULL_UPGRADE)
def post_ship_hull_upgrade(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, POST_HULL_UPGRADE)
        service = ShipService(db)

        result = service.upgrade_hull(player_id)
        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP_BODY)]]

        if not result.get("can_upgrade", True):
            return InlineKeyboardMarkup(keyboard), f"<b>{result['reason']}</b>"

        text = HULL_UPGRADE_SUCCESS_TEXT.format(**result)
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register(SHIP_BODY_REPAIR)
def get_ship_repair(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, SHIP_BODY_REPAIR)
        service = ShipService(db)
        data = service.get_active_ship(player_id)

        ship = data["ship"]
        stats = service.get_hull_stats(player_id)
        max_health = stats['max_health_hull']
        current_health = float(ship.health)
        health_percent = (current_health / max_health * 100) if max_health > 0 else 0

        now = datetime.now(timezone.utc)
        is_repairing = False

        if ship.repair_ends_at:
            repair_ends_at = ship.repair_ends_at
            if repair_ends_at <= now:
                ship.repair_ends_at = None
                ship.health = max_health
                db.commit()
                current_health = max_health
                health_percent = 100
            else:
                is_repairing = True

        if is_repairing:
            remaining = repair_ends_at - now
            total_seconds = int(remaining.total_seconds())
            minutes_left = total_seconds // 60
            seconds_left = total_seconds % 60
            moscow_time = repair_ends_at.astimezone(pytz_timezone("Europe/Moscow"))

            keyboard = [
                [InlineKeyboardButton("Обновить", callback_data=SHIP_BODY_REPAIR)],
                [InlineKeyboardButton("Назад", callback_data=SHIP)]
            ]

            repair_status = REPAIR_IN_PROGRESS_TEXT.format(
                minutes_left=minutes_left,
                seconds_left=seconds_left,
                end_time=moscow_time.strftime('%H:%M:%S')
            )

            text = REPAIR_INFO_TEXT.format(
                current_health=current_health,
                max_health=max_health,
                health_percent=health_percent,
                repair_status=repair_status
            )
        else:
            if health_percent >= 100:
                keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP)]]
                text = REPAIR_INFO_TEXT.format(
                    current_health=current_health,
                    max_health=max_health,
                    health_percent=100.0,
                    repair_status=REPAIR_COMPLETE_TEXT
                )
                return InlineKeyboardMarkup(keyboard), text

            preview = service.repair_ship(player_id, simulate=True)
            cooldown_minutes = preview["cooldown_seconds"] // 60
            cooldown_seconds = preview["cooldown_seconds"] % 60

            keyboard = [
                [InlineKeyboardButton("Ремонт", callback_data=POST_SHIP_BODY_REPAIR)],
                [InlineKeyboardButton("Назад", callback_data=SHIP)]
            ]

            costs_text = REPAIR_COSTS_TEXT.format(
                cost_metals=preview["cost_metals"],
                cost_crystalls=preview["cost_crystalls"],
                cooldown_minutes=cooldown_minutes,
                cooldown_seconds=cooldown_seconds
            )

            text = REPAIR_INFO_TEXT.format(
                current_health=current_health,
                max_health=max_health,
                health_percent=health_percent,
                repair_status=costs_text
            )
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register(POST_SHIP_BODY_REPAIR)
def post_ship_repair(query: CallbackQuery):
    player_id = query.from_user.id
    db = SessionLocal()

    try:
        service = ShipService(db)
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, POST_SHIP_BODY_REPAIR)
        result = service.repair_ship(player_id)

        if not result.get("can_repair", True):
            keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP_BODY)]]
            text = NOT_ENOUGH_RESOURCES_TEXT.format(
                required=f"{result['required_metals']} металлов, "
                         f"{result['required_crystalls']} кристаллов",
                available=f"{result['available_metals']} металлов, "
                          f"{result['available_crystalls']} кристаллов"
            )
            return InlineKeyboardMarkup(keyboard), text

        minutes = result['cooldown_seconds'] // 60
        seconds = result['cooldown_seconds'] % 60

        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP)]]
        text = REPAIR_STARTED_TEXT.format(
            restored_health=result['restored_health'],
            max_health=result['max_health'],
            cost_crystalls=result['cost_crystalls'],
            cost_metals=result['cost_metals'],
            cooldown_minutes=minutes,
            cooldown_seconds=seconds
        )
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()
