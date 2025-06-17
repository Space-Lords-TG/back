from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

from src.application.config_loader import config
from src.application.player_service import PlayerService
from src.presentation.screens.registry import register, register_pattern
from src.application.ship_service import ShipService
from src.infrastructure.database import SessionLocal
from datetime import datetime, timezone
from pytz import timezone as pytz_timezone

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
POST_SHIP_BODY = config["screens"]["POST_SHIP_BODY"]      # динамический handler

# Ремонт
SHIP_BODY_REPAIR = config["screens"]['SHIP_BODY_REPAIR']
POST_SHIP_BODY_REPAIR = config["screens"]['POST_SHIP_BODY_REPAIR']

# Функция, возвращающая разметку для корабля
# Кнопка в меню "КОРАБЛЬ"
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

        text = f"""Ваш корабль:

Скорость: {stats['speed_gun']}
Урон: {stats['damage_gun']}
Шанс крита: {stats['crit_rate_gun']}%
Крит. урон: {stats['crit_damage_gun']}x
Защита: {stats['armor_hull']}
Щиты: {stats['shields_hull']}
Манёвренность: {stats['maneuver_hull']}
Здоровье корабля: {stats['health']}/{stats['max_health_hull']}

Установленные модули:
Оружие — <b>{stats['name_gun']}</b>
Корпус — <b>{stats['name_hull']}</b>

Вы можете настроить модули в этом меню.
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# ОРУЖИЕ ======================================================================

# Функция, возвращающая разметку для оружия
# Кнопка в меню "КОРАБЛЬ" -> "Оружие"
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
        # power_next = service.get_weapon_power(gun, level + 1)
        # cost = service.get_upgrade_cost(power_now, power_next)
        cost = service.get_upgrade_cost(power_now)

        keyboard = [
            [InlineKeyboardButton("Заменить", callback_data=SHIP_WEAPON_CHANGE),
             InlineKeyboardButton("Улучшить", callback_data=SHIP_WEAPON_UPGRADE)],
            [InlineKeyboardButton("Назад", callback_data=SHIP)]
        ]

        text = \
f"""<b>Оружие</b>

На данный момент установлено:
<b>{stats['name_gun']}</b>
Уровень: {level}

Характеристики:
Урон: {stats['damage_gun']}
Крит. частота: {stats['crit_rate_gun']}%
Крит. урон: {stats['crit_damage_gun']}x
Скорость: {stats['speed_gun']}

Мощь: {power_now:.2f}

Стоимость улучшения:
{cost:,} кристаллов
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

def format_percent(value):
    return f"{int(value * 10000) / 100:.2f}"

# Отображение информации об оружии перед улучшением
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
        # cost = service.get_upgrade_cost(power_now, power_next)
        cost = service.get_upgrade_cost(power_now)

        # Текущие значения
        damage = service.calc(gun.base_damage, gun.gain_damage, level)
        crit_rate = service.calc(gun.base_crit_rate, gun.gain_crit_rate, level)
        crit_damage = service.calc(gun.base_crit_damage, gun.gain_crit_damage, level)
        speed = service.calc(gun.base_speed, gun.gain_speed, level)

        # Следующие значения
        next_damage = service.calc(gun.base_damage, gun.gain_damage, level + 1)
        next_crit_rate = service.calc(gun.base_crit_rate, gun.gain_crit_rate, level + 1)
        next_crit_damage = service.calc(gun.base_crit_damage, gun.gain_crit_damage, level + 1)
        next_speed = service.calc(gun.base_speed, gun.gain_speed, level + 1)

        crit_rate_percent = format_percent(crit_rate)
        next_crit_rate_percent = format_percent(next_crit_rate)

        keyboard = [
            [InlineKeyboardButton("Подтвердить", callback_data=POST_SHIP_WEAPON_UPGRADE)],
            [InlineKeyboardButton("Назад", callback_data=SHIP)]
        ]

        text = f"""<b>Оружие</b>

Вы хотите улучшить:
<b>{gun.name}</b>
Уровень: {level} ➜ {level + 1}

Урон: {damage:.2f} ➜ {next_damage:.2f}
Крит. частота: {crit_rate_percent}% ➜ {next_crit_rate_percent}%
Крит. урон: {crit_damage:.2f}x ➜ {next_crit_damage:.2f}x
Скорость: {speed:.2f} ➜ {next_speed:.2f}

Мощь: {power_now:.2f} ➜ {power_next:.2f}

Стоимость улучшения:
{cost:,} кристаллов
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# Отображение информации об оружии после улучшения
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
            text = f"""<b>Недостаточно кристаллов</b>

Нужно: {result['required']}
У вас: {result['available']}
"""
            return InlineKeyboardMarkup(keyboard), text

        # если успех, result — это словарь со статистикой
        stats = result

        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP_WEAPON)]]

        text = f"""<b>Оружие улучшено!</b>

<b>{stats['name_gun']}</b> теперь имеет:
Уровень: {stats['level_gun']}
Урон: {stats['damage_gun']:.2f}
Крит. шанс: {stats['crit_rate_gun']:.2f}%
Крит. урон: {stats['crit_damage_gun']:.2f}x
Скорость: {stats['speed_gun']:.2f}

Мощь: {stats['power_gun']:.2f}
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# Функция, возвращающая разметку для замены оружия
# Кнопка в меню "КОРАБЛЬ" -> "Оружие" -> "Заменить"
@register(SHIP_WEAPON_CHANGE)
def get_ship_weapon_change(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, SHIP_WEAPON_CHANGE)

        service = ShipService(db)

        current_stats = service.get_weapon_stats(player_id)
        current_data = service.get_active_ship(player_id)
        current_pg = current_data["player_gun"]

        available_guns = service.get_available_weapons(player_id)
        keyboard = []

        for pg, gun in available_guns:
            if pg.id != current_pg.id:
                label = f"{gun.name} ({pg.current_level} уровень)"
                keyboard.append([
                    InlineKeyboardButton(label, callback_data=f"{POST_SHIP_WEAPON}_{gun.id}")
                ])

        keyboard.append([InlineKeyboardButton("Назад", callback_data=SHIP_WEAPON)])

        text = f"""<b>Оружие</b>

На данный момент установлено:
<b>{current_stats['name_gun']}</b>
Уровень: {current_stats['level_gun']}

Характеристики:
Урон: {current_stats['damage_gun']:.2f}
Крит. частота: {current_stats['crit_rate_gun']:.2f}%
Крит. урон: {current_stats['crit_damage_gun']:.2f}x
Скорость: {current_stats['speed_gun']:.2f}

Мощь: {current_stats['power_gun']:.2f}

Вы можете выбрать оружие для замены:
"""

        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# Отображение информации об оружии после замены оружия
@register_pattern(rf"^{POST_SHIP_WEAPON}_(\d+)$")
def post_ship_weapon_change(query: CallbackQuery, match):
    gun_id = int(match.group(1))
    player_id = query.from_user.id
    db = SessionLocal()

    try:
        service = ShipService(db)
        stats = service.change_weapon(player_id, new_gun_id=gun_id)

        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP)]]

        text = f"""<b>Оружие заменено!</b>

<b>{stats['name_gun']}</b> устновлен.
Уровень: {stats['level_gun']}

Новые характеристики:
Урон: {stats['damage_gun']:.2f}
Крит. шанс: {stats['crit_rate_gun']:.2f}%
Крит. урон: {stats['crit_damage_gun']:.2f}x
Скорость: {stats['speed_gun']:.2f}

Мощь: {stats['power_gun']:.2f}
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()



# КОРПУС =============================================================================

# Функция, возвращающая разметку для корпуса
# Кнопка "Корабль" - > "Корпус"
@register(SHIP_BODY)
def get_ship_body(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, SHIP_BODY)
        service = ShipService(db)

        stats = service.get_hull_stats(player_id)
        ship_data = service.get_active_ship(player_id)
        hull = ship_data["hull"]
        level = ship_data["player_hull"].current_level

        # Текущая и следующая мощь
        power_now = service.get_hull_power(hull, level)
        # power_next = service.get_hull_power(hull, level + 1)

        # Расчёт стоимости
        # cost = service.get_upgrade_cost(power_now, power_next)
        cost = service.get_upgrade_cost(power_now)

        keyboard = [
            [
                InlineKeyboardButton("Заменить", callback_data=SHIP_HULL_CHANGE),
                InlineKeyboardButton("Улучшить", callback_data=SHIP_HULL_UPGRADE)
            ],
            [InlineKeyboardButton("Назад", callback_data=SHIP)]
        ]

        text = f"""<b>Корпус:</b>

На данный момент установлен:
<b>{stats['name_hull']}</b>
Уровень: {stats['level_hull']}

Характеристики:
Здоровье: {stats['max_health_hull']:.0f}
Защита: {stats['armor_hull']:.0f}
Щиты: {stats['shields_hull']:.0f}
Манёвренность: {stats['maneuver_hull']:.2f}

Мощь: {stats['power_hull']:.2f}

Стоимость улучшения:
{cost:,} металлов
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


# Функция, возвращающая разметку для замены корпуса
# Кнопка "Корабль" -> "Корпус" -> "Заменить"
@register(SHIP_HULL_CHANGE)
def get_ship_hull_change(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, SHIP_HULL_CHANGE)
        service = ShipService(db)

        stats = service.get_hull_stats(player_id)
        current_data = service.get_active_ship(player_id)
        current_ph = current_data["player_hull"]

        available_hulls = service.get_available_hulls(player_id)
        keyboard = []

        for ph, hull in available_hulls:
            if ph.id != current_ph.id:
                label = f"{hull.name} ({ph.current_level} уровень)"
                keyboard.append([
                    InlineKeyboardButton(label, callback_data=f"{POST_SHIP_BODY}_{hull.id}")
                ])

        keyboard.append([InlineKeyboardButton("Назад", callback_data=SHIP_BODY)])

        text = f"""<b>Корпус</b>

На данный момент установлен:
<b>{stats['name_hull']}</b>
Уровень: {stats['level_hull']}

Характеристики:
Здоровье: {stats['max_health_hull']:.0f}
Защита: {stats['armor_hull']:.0f}
Щиты: {stats['shields_hull']:.0f}
Манёвренность: {stats['maneuver_hull']:.2f}

Мощь: {stats['power_hull']:.2f}

Вы можете выбрать корпус для замены:
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# Функция, возвращающая разметку после замены корпуса
@register_pattern(rf"^{POST_SHIP_BODY}_(\d+)$")
def post_ship_body_change(query: CallbackQuery, match):
    db = SessionLocal()
    try:
        hull_id = int(match.group(1))
        player_id = query.from_user.id

        service = ShipService(db)
        stats = service.change_hull(player_id, new_hull_id=hull_id)

        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP)]]

        text = f"""<b>Корпус заменён!</b>

<b>{stats['name_hull']}</b>
Уровень: {stats['level_hull']}

Новые характеристики:
Здоровье: {stats['max_health_hull']:.0f}
Защита: {stats['armor_hull']:.0f}
Щиты: {stats['shields_hull']:.0f}
Манёвренность: {stats['maneuver_hull']:.2f}

Мощь: {stats['power_hull']:.2f}
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"

    finally:
        db.close()

# Функция, возвращающая разметку для улучшения корпуса
# Кнопка "Корабль" -> "Корпус" -> "Улучшить"
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
        player_hull = ship_data["player_hull"]
        level = player_hull.current_level

        if level >= 20:
            return None, "Корпус уже имеет максимальный уровень (20)."

        # Текущие параметры
        health = service.calc(hull.base_max_health, hull.gain_max_health, level)
        armor = service.calc(hull.base_armor, hull.gain_armor, level)
        shields = service.calc(hull.base_max_shields, hull.gain_max_shields, level)
        maneuver = service.calc(hull.base_maneuver, hull.gain_maneuver, level)
        power_now = service.get_hull_power(hull, level)

        # Будущие параметры
        next_health = service.calc(hull.base_max_health, hull.gain_max_health, level + 1)
        next_armor = service.calc(hull.base_armor, hull.gain_armor, level + 1)
        next_shields = service.calc(hull.base_max_shields, hull.gain_max_shields, level + 1)
        next_maneuver = service.calc(hull.base_maneuver, hull.gain_maneuver, level + 1)
        power_next = service.get_hull_power(hull, level + 1)

        # cost = service.get_upgrade_cost(power_now, power_next)
        cost = service.get_upgrade_cost(power_now)

        keyboard = [
            [InlineKeyboardButton("Подтвердить", callback_data=POST_HULL_UPGRADE)],
            [InlineKeyboardButton("Назад", callback_data=SHIP)]
        ]

        text = f"""<b>Улучшение корпуса</b>

<b>{hull.name}</b>
Уровень: {level} ➜ {level + 1}

Здоровье: {health:.0f} ➜ {next_health:.0f}
Защита: {armor:.2f} ➜ {next_armor:.2f}
Щиты: {shields:.2f} ➜ {next_shields:.2f}
Манёвренность: {maneuver:.2f} ➜ {next_maneuver:.2f}

Мощь: {power_now:.2f} ➜ {power_next:.2f}

Стоимость улучшения:
{cost:,} металлов
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# Функция, возвращающая разметку после улучшения корпуса
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

        text = f"""<b>Корпус улучшен!</b>

<b>{result['name_hull']}</b>
Уровень: {result['level_hull']}

Новые характеристики:
Здоровье: {result['max_health_hull']:.0f}
Защита: {result['armor_hull']:.0f}
Щиты: {result['shields_hull']:.0f}
Манёвренность: {result['maneuver_hull']:.2f}

Мощь: {result['power_hull']:.2f}
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()



# РЕМОНТ =============================================================================

# Функция, возвращающая разметку для ремонта корабля
# Кнопка "Корабль" -> "Ремонт"
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

        now = datetime.now(timezone.utc)
        is_repairing = False

        if ship.repair_ends_at:
            repair_ends_at = ship.repair_ends_at
            if repair_ends_at <= now:
                ship.repair_ends_at = None
                ship.health = max_health
                db.commit()
                current_health = max_health
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

            text = f"""<b>Ремонт корпуса:</b>

Текущее здоровье корпуса:
{current_health:.0f} / {max_health:.0f} ({(current_health / max_health * 100):.1f}%)

Оставшееся время ремонта:
{minutes_left} мин {seconds_left} сек

<i>Завершение в {moscow_time.strftime('%H:%M:%S')}</i>
"""
        else:
            damage_percent = (max_health - current_health) / max_health

            if damage_percent <= 0:
                keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP)]]
                text = f"""<b>Ремонт корпуса:</b>

Текущее здоровье корпуса:
{current_health:.0f} / {max_health:.0f} (100.0%)

Корпус полностью отремонтирован.
"""
                return InlineKeyboardMarkup(keyboard), text

            preview = service.repair_ship(player_id, simulate=True)

            cost_metals = preview["cost_metals"]
            cost_crystalls = preview["cost_crystalls"]
            cooldown_total_seconds = preview["cooldown_seconds"]
            cooldown_minutes = cooldown_total_seconds // 60
            cooldown_seconds = cooldown_total_seconds % 60

            keyboard = [
                [InlineKeyboardButton("Ремонт", callback_data=POST_SHIP_BODY_REPAIR)],
                [InlineKeyboardButton("Назад", callback_data=SHIP)]
            ]

            text = f"""<b>Ремонт корпуса:</b>

Текущее здоровье корпуса:
{current_health:.0f} / {max_health:.0f} ({(current_health / max_health * 100):.1f}%)

Стоимость ремонта:
{cost_metals} металлов
{cost_crystalls} кристаллов

Время ремонта:
{cooldown_minutes} мин {cooldown_seconds} сек
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# Отображение информации после нажатия на кнопку "Ремонт"
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
            text = f"""<b>Недостаточно ресурсов</b>

Нужно: {result['required_metals']} / Есть: {result['available_metals']}
Нужно: {result['required_crystalls']} / Есть: {result['available_crystalls']}
"""
            return InlineKeyboardMarkup(keyboard), text

        minutes = result['cooldown_seconds'] // 60
        seconds = result['cooldown_seconds'] % 60

        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP)]]

        text = f"""<b>Ремонт запущен!</b>

Восстановится здоровье: {result['restored_health']} / {result['max_health']}
Списано кристаллов: {result['cost_crystalls']}
Списано металлов: {result['cost_metals']}
Завершение через: {minutes} мин {seconds} сек
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()