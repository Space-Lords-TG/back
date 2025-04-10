from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from src.presentation.screens.registry import register, register_pattern
import src.presentation.screens.mainMenu as mainMenu
from src.application.ship_service import ShipService
from src.infrastructure.database import SessionLocal

# Определяем идентификаторы экранов
# Главные экраны
SHIP = 'КОРАБЛЬ'
SHIP_WEAPON = 'SHIP_WEAPON'
SHIP_BODY = 'SHIP_BODY'

# Улучшения
SHIP_WEAPON_UPGRADE = 'SHIP_WEAPON_UPGRADE'
POST_SHIP_WEAPON_UPGRADE = 'POST_SHIP_WEAPON_UPGRADE'
SHIP_BODY_UPGRADE = 'SHIP_BODY_UPGRADE'
POST_SHIP_BODY_UPGRADE = 'POST_SHIP_BODY_UPGRADE'

# Замены
SHIP_WEAPON_CHANGE = 'SHIP_WEAPON_CHANGE'
POST_SHIP_WEAPON = "POST_SHIP_WEAPON"  # динамический handler
SHIP_BODY_CHANGE = 'SHIP_BODY_CHANGE'
POST_SHIP_BODY = "POST_SHIP_BODY"      # динамический handler

# Ремонт
SHIP_BODY_REPAIR = 'SHIP_BODY_REPAIR'
POST_SHIP_BODY_REPAIR = 'POST_SHIP_BODY_REPAIR'

# Статические идентификаторы оружия
SHIP_WEAPON_1 = 'SHIP_WEAPON_1'
SHIP_WEAPON_2 = 'SHIP_WEAPON_2'
SHIP_WEAPON_3 = 'SHIP_WEAPON_3'
SHIP_WEAPON_4 = 'SHIP_WEAPON_4'
POST_SHIP_WEAPON_1 = 'POST_SHIP_WEAPON_1'
POST_SHIP_WEAPON_2 = 'POST_SHIP_WEAPON_2'
POST_SHIP_WEAPON_3 = 'POST_SHIP_WEAPON_3'
POST_SHIP_WEAPON_4 = 'POST_SHIP_WEAPON_4'

# Статические идентификаторы корпусов
SHIP_BODY_1 = 'SHIP_BODY_1'
SHIP_BODY_2 = 'SHIP_BODY_2'
SHIP_BODY_3 = 'SHIP_BODY_3'
SHIP_BODY_4 = 'SHIP_BODY_4'
POST_SHIP_BODY_1 = 'POST_SHIP_BODY_1'
POST_SHIP_BODY_2 = 'POST_SHIP_BODY_2'
POST_SHIP_BODY_3 = 'POST_SHIP_BODY_3'
POST_SHIP_BODY_4 = 'POST_SHIP_BODY_4'

# Функция, возвращающая разметку для корабля
# Кнопка в меню "КОРАБЛЬ"
@register(SHIP)
def get_ship(message: Message):
    db = SessionLocal()
    try:
        if not message.from_user:
            raise ValueError("Не удалось определить пользователя.")

        player_id = message.from_user.id
        service = ShipService(db)

        data = service.get_active_ship(player_id)
        stats = service.get_ship_stats(player_id)

        gun = data["gun"]
        hull = data["hull"]

        keyboard = [
            [InlineKeyboardButton("Оружие", callback_data=SHIP_WEAPON),
             InlineKeyboardButton("Корпус", callback_data=SHIP_BODY)],
            [InlineKeyboardButton("Ремонт", callback_data=SHIP_BODY_REPAIR)]
        ]

        text = f"""Ваш корабль:

Скорость: {stats['speed']}
Урон: {stats['damage']}
Шанс крита: {stats['crit_rate']}%
Крит. урон: {stats['crit_damage']}%
Защита: {stats['armor']}
Щиты: {stats['shields']}
Манёвренность: {stats['maneuver']}
Здоровье корабля: {stats['health']}/{stats['max_health']}

Установленные модули:
Оружие — <b>{gun.name}</b>
Корпус — <b>{hull.name}</b>

Вы можете настроить модули в этом меню.
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# ОРУЖИЕ =============================================================================

# Функция, возвращающая разметку для оружия
# Кнопка в меню "КОРАБЛЬ" -> "Оружие"
@register(SHIP_WEAPON)
def get_ship_weapon(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        service = ShipService(db)
        data = service.get_active_ship(player_id)
        gun = data["gun"]
        player_gun = data["player_gun"]
        level = player_gun.current_level

        damage = service.calc(gun.base_damage, gun.gain_damage, level)
        crit_rate = service.calc(gun.base_crit_rate, gun.gain_crit_rate, level)
        crit_damage = service.calc(gun.base_crit_damage, gun.gain_crit_damage, level)

        keyboard = [
            [InlineKeyboardButton("Заменить", callback_data=SHIP_WEAPON_CHANGE),
             InlineKeyboardButton("Улучшить", callback_data=SHIP_WEAPON_UPGRADE)],
            [InlineKeyboardButton("Назад", callback_data=SHIP)]
        ]

        text = f"""Оружие:
На данный момент установлено:
<b>{gun.name}</b>

Характеристики:
Урон: {damage}
Крит. частота: {crit_rate}%
Крит. урон: {crit_damage}%

Стоимость улучшения:
5 кристаллов
10 металлов
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# Функция, возвращающая разметку для улучшения оружия
@register(SHIP_WEAPON_UPGRADE)
def get_ship_weapon_upgrade(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        service = ShipService(db)

        data = service.get_active_ship(player_id)
        gun = data["gun"]

        # Увеличение всех характеристик на 10% !!!!!!!!!!!!!!!!!!
        new_damage = round(gun.damage * 1.1, 1)
        new_crit_rate = round(gun.crit_rate * 1.1, 2)
        new_crit_damage = round(gun.crit_damage * 1.07, 1)

        keyboard = [
            [InlineKeyboardButton("Подтвердить", callback_data=POST_SHIP_WEAPON_UPGRADE)],
            [InlineKeyboardButton("Назад", callback_data=SHIP)]
        ]

        text = f"""Оружие (улучшение)
Вы хотите улучшить:
<b>{gun.name}</b>

Текущие показатели / улучшение:
Урон: {gun.damage} -> {new_damage}
Крит. частота: {gun.crit_rate}% -> {new_crit_rate}%
Крит. урон: {gun.crit_damage}% -> {new_crit_damage}%

Стоимость улучшения:
5 кристаллов
10 металлов
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"

    finally:
        db.close()

# Функция, отправляющая запрос на улучшение
@register(POST_SHIP_WEAPON_UPGRADE)
def post_ship_weapon_upgrade(query: CallbackQuery):
    player_id = query.from_user.id
    db = SessionLocal()

    try:
        service = ShipService(db)
        stats = service.upgrade_weapon(player_id)

        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP_WEAPON)]]

        text = f"""<b>Оружие улучшено!</b>

<b>{stats['name']}</b> теперь имеет:
Урон: {stats['damage']}
Крит. шанс: {stats['crit_rate']}%
Крит. урон: {stats['crit_damage']}%
Скорость: {stats['speed']}
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
        service = ShipService(db)

        current_data = service.get_active_ship(player_id)
        current_gun = current_data["gun"]
        current_pg = current_data["player_gun"]
        current_level = current_pg.current_level

        available_guns = service.get_available_weapons(player_id)
        keyboard = []

        for pg, gun in available_guns:
            if pg.id != current_pg.id:
                keyboard.append([
                    InlineKeyboardButton(gun.name, callback_data=f"{POST_SHIP_WEAPON}_{gun.id}")
                ])

        keyboard.append([InlineKeyboardButton("Назад", callback_data=SHIP_WEAPON)])

        dmg = service.calc(current_gun.base_damage, current_gun.gain_damage, current_level)
        crit_r = service.calc(current_gun.base_crit_rate, current_gun.gain_crit_rate, current_level)
        crit_d = service.calc(current_gun.base_crit_damage, current_gun.gain_crit_damage, current_level)

        text = f"""Оружие (замена)
На данный момент установлено:
<b>{current_gun.name}</b>

Характеристики:
Урон: {dmg}
Крит. частота: {crit_r}%
Крит. урон: {crit_d}%

Вы можете выбрать оружие для замены:
"""

        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

@register_pattern(rf"^{POST_SHIP_WEAPON}_(\d+)$")
def post_ship_weapon_dynamic(query: CallbackQuery, match):
    gun_id = int(match.group(1))
    player_id = query.from_user.id
    db = SessionLocal()

    try:
        service = ShipService(db)
        updated_stats = service.change_weapon(player_id, new_gun_id=gun_id)

        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP)]]
        text = f"""Оружие заменено!

Новые характеристики:
Урон: {updated_stats['damage']}
Крит. шанс: {updated_stats['crit_rate']}%
Крит. урон: {updated_stats['crit_damage']}%
Скорость: {updated_stats['speed']}
"""
        return InlineKeyboardMarkup(keyboard), text
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# Функция, возвращающая разметку для сравнения оружия с оружием 1
@register(POST_SHIP_WEAPON_1)
def post_ship_weapon_1(query: CallbackQuery):
    player_id = query.from_user.id
    db = SessionLocal()

    try:
        service = ShipService(db)
        updated_stats = service.change_weapon(player_id, new_gun_id=1)

        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP)]]
        text = f"""Оружие заменено!

Новые характеристики:
Урон: {updated_stats['damage']}
Крит. шанс: {updated_stats['crit_rate']}%
Крит. урон: {updated_stats['crit_damage']}%
Скорость: {updated_stats['speed']}
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# Функция, возвращающая разметку для сравнения оружия с оружием 2
@register(POST_SHIP_WEAPON_2)
def post_ship_weapon_2(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('weapon_2 change request')
    
    return get_ship_weapon(query)


# КОРПУС =============================================================================

# Функция, возвращающая разметку для корпуса
# Кнопка "Корабль" - > "Корпус"
@register(SHIP_BODY)
def get_ship_body(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        service = ShipService(db)

        data = service.get_active_ship(player_id)
        hull = data["hull"]

        keyboard = [
            [
                InlineKeyboardButton("Заменить", callback_data=SHIP_BODY_CHANGE),
                InlineKeyboardButton("Улучшить", callback_data=SHIP_BODY_UPGRADE)
            ],
            [InlineKeyboardButton("Назад", callback_data=SHIP)]
        ]

        text = f"""Корпус:
На данный момент установлено:
<b>{hull.name}</b>

Характеристики:
Здоровье: {hull.base_max_health}
Защита: {hull.base_armor}
Щиты: {hull.base_max_shields}
Манёвренность: {hull.base_maneuver}

Стоимость улучшения:
5 кристаллов
10 металлов
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"

    finally:
        db.close()

# Функция, возвращающая разметку для ремонта
# Кнопка "Корабль" -> "Ремонт"
@register(SHIP_BODY_REPAIR)
def get_ship_repair(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        service = ShipService(db)
        data = service.get_active_ship(player_id)

        ship = data["ship"]
        hull = data["hull"]

        current = int(ship.health)
        maximum = int(hull.base_max_health)
        percent = round(current / maximum * 100, 1)

        keyboard = [
            [InlineKeyboardButton("Ремонт", callback_data=POST_SHIP_BODY_REPAIR)],
            [InlineKeyboardButton("Назад", callback_data=SHIP_BODY)]
        ]

        text = f"""Ремонт корпуса:

Текущее здоровье корпуса:
{current} / {maximum} ({percent}%)

Стоимость ремонта:
50 кристаллов

Время ремонта:
10 минут
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# Функция, возвращающая разметку для ремонта корабля
# Кнопка "Корабль" -> "Ремонт"
@register(POST_SHIP_BODY_REPAIR)
def post_ship_repair(query: CallbackQuery):
    player_id = query.from_user.id
    db = SessionLocal()

    try:
        service = ShipService(db)
        result = service.repair_ship(player_id)

        if result is None:
            keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP)]]
            return InlineKeyboardMarkup(keyboard), "<b>Корпус уже полностью отремонтирован!</b>"

        keyboard = [[InlineKeyboardButton("Назад", callback_data=SHIP)]]
        text = f"""<b>Корабль отремонтирован!</b>

Здоровье восстановлено: {result['health']} / {result['max_health']}
"""
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


# Функция, возвращающая разметку для улучшения оружия
# Кнопка "Корабль" -> "Корпус" -> "Заменить"
@register(SHIP_BODY_CHANGE)
def get_ship_body_change(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        service = ShipService(db)

        data = service.get_active_ship(player_id)
        current_hull = data["hull"]
        current_ph = data["player_hull"]
        current_level = current_ph.current_level

        available_hulls = service.get_available_hulls(player_id)

        keyboard = []
        for hull in available_hulls:
            if hull.id != current_hull.id:
                keyboard.append([
                    InlineKeyboardButton(hull.name, callback_data=f"{POST_SHIP_BODY}_{hull.id}")
                ])

        keyboard.append([InlineKeyboardButton("Назад", callback_data=SHIP_BODY)])

        health = current_hull.base_max_health
        armor = current_hull.base_armor
        shields = current_hull.base_max_shields
        maneuver = current_hull.base_maneuver

        text = f"""Корпус (замена)
На данный момент установлен:
<b>{current_hull.name}</b>

Характеристики:
Здоровье: {health}
Защита: {armor}
Щиты: {shields}
Манёвренность: {maneuver}

Вы можете выбрать корпус для замены:
"""
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

        text = f"""<b>Корпус заменён!</b>

Новые характеристики:
Здоровье: {stats['health']}
Защита: {stats['armor']}
Щиты: {stats['shields']}
Манёвренность: {stats['maneuver']}
"""

        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"

    finally:
        db.close()