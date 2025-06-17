from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from src.application.config_loader import config
from src.application.player_service import PlayerService
from src.presentation.screens.registry import register
from src.application.ship_service import ShipService
from src.application.arena_service import ArenaService
from src.infrastructure.database import SessionLocal
from datetime import datetime, timezone
from pytz import timezone as pytz_timezone

# Определяем идентификаторы экранов
ARENA = config["screens"]["ARENA"]
ARENA_QUEUE = config["screens"]["ARENA_QUEUE"]

# Функция, возвращающая разметку для арены
@register(ARENA)
def get_arena(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, ARENA)
        service = ShipService(db)
        stats = service.get_ship_stats(player_id)

        keyboard = [
            [InlineKeyboardButton("Встать в очередь", callback_data=ARENA_QUEUE)]
        ]

        text = f"""Арена

                    Характеристики вашего корабля:
                    Скорость: {stats['speed_gun']:.0f}
                    Урон: {stats['damage_gun']:.0f}
                    Шанс крита: {stats['crit_rate_gun']:.2f}%
                    Крит. урон: {stats['crit_damage_gun']:.2f}x
                    Защита: {stats['armor_hull']:.0f}
                    Щиты: {stats['shields_hull']:.0f}
                    Манёвренность: {stats['maneuver_hull']:.2f}
                    
                    Вы можете встать в очередь, система найдёт подходящего оппонента.
                    
                    Бой начнётся автоматически.
                """
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

# Функция, возвращающая разметку для арены
@register(ARENA_QUEUE)
def get_queue(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, ARENA_QUEUE)
        service = ShipService(db)
        arena_service = ArenaService(db)

        data = service.get_active_ship(player_id)
        ship = data["ship"]

        # 🛠 Проверка корабль на ремонте
        if ship.repair_ends_at and ship.repair_ends_at > datetime.now(timezone.utc):
            moscow_time = ship.repair_ends_at.astimezone(pytz_timezone("Europe/Moscow"))
            time_str = moscow_time.strftime('%H:%M:%S')
            text = f"""<b>Ваш корабль сейчас на ремонте!</b>

Вы не можете участвовать в битве, пока ремонт не завершён.

Завершение ремонта: <b>{time_str}</b>
"""
            keyboard = [[InlineKeyboardButton("Назад", callback_data=ARENA)]]
            return InlineKeyboardMarkup(keyboard), text
        
        # 🛠 Проверка HP > 0
        if ship.health <= 0:
            text = """<b>Здоровье вашего корабля равно 0.</b>

Вы не можете участвовать в битве, пока не отремонтируете корабль.
"""
            keyboard = [[InlineKeyboardButton("Назад", callback_data=ARENA)]]
            return InlineKeyboardMarkup(keyboard), text

        # 🧍‍♂️ Проверка уже в очереди
        if arena_service.is_in_queue(player_id):
            stats = service.get_ship_stats(player_id)

            keyboard = [[InlineKeyboardButton("Выйти из очереди", callback_data=ARENA)]]
            text = f"""<b>Арена</b>

<b>Поиск противника...</b>

Вы уже находитесь в очереди.
Ожидаем подходящего соперника...

Характеристики вашего корабля:
Скорость: {stats['speed_gun']:.2f}
Урон: {stats['damage_gun']:.2f}
Шанс крита: {stats['crit_rate_gun']:.2f}%
Крит. урон: {stats['crit_damage_gun']:.2f}x
Защита: {stats['armor_hull']:.2f}
Щиты: {stats['shields_hull']:.2f}
Манёвренность: {stats['maneuver_hull']:.2f}

Мощь: {stats['power_score']:.2f}
"""
            return InlineKeyboardMarkup(keyboard), text

        # ✅ Добавляем в очередь
        arena_service.join_queue(player_id)
        stats = service.get_ship_stats(player_id)

        keyboard = [[InlineKeyboardButton("Выйти из очереди", callback_data=ARENA)]]
        return InlineKeyboardMarkup(keyboard), f"""<b>Арена</b>

<b>Поиск противника...</b>

Вы успешно встали в очередь.
Ожидаем подходящего соперника...

Характеристики вашего корабля:
Скорость: {stats['speed_gun']:.2f}
Урон: {stats['damage_gun']:.2f}
Шанс крита: {stats['crit_rate_gun']:.2f}%
Крит. урон: {stats['crit_damage_gun']:.2f}x
Защита: {stats['armor_hull']:.2f}
Щиты: {stats['shields_hull']:.2f}
Манёвренность: {stats['maneuver_hull']:.2f}

Мощь: {stats['power_score']:.2f}
"""

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()
