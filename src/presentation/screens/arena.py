from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from src.application.player_service import PlayerService
from src.presentation.screens.registry import register
from src.application.ship_service import ShipService
from src.application.arena_service import ArenaService
from src.infrastructure.database import SessionLocal
from datetime import datetime, timezone
from pytz import timezone as pytz_timezone

from src.presentation.screens.texts import *

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

        text = ARENA_STATS_TEXT.format(**stats)
        if player_service.get_screen_view_count(player_id, ARENA) == 0:
            text = ARENA_TUTORIAL_TEXT + text
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
            text = ARENA_QUEUE_REPAIR_TEXT.format(time_str)

            keyboard = [[InlineKeyboardButton("Назад", callback_data=ARENA)]]
            return InlineKeyboardMarkup(keyboard), text

        # 🛠 Проверка HP > 0
        if ship.health <= 0:
            text = ARENA_QUEUE_ZERO_HEALTH_TEXT
            keyboard = [[InlineKeyboardButton("Назад", callback_data=ARENA)]]
            return InlineKeyboardMarkup(keyboard), text

        # 🧍‍♂️ Проверка уже в очереди
        if arena_service.is_in_queue(player_id):
            stats = service.get_ship_stats(player_id)

            keyboard = [[InlineKeyboardButton("Выйти из очереди", callback_data=ARENA)]]
            text = ARENA_IN_QUEUE_TEXT.format(**stats)
            return InlineKeyboardMarkup(keyboard), text

        # ✅ Добавляем в очередь
        arena_service.join_queue(player_id)
        stats = service.get_ship_stats(player_id)
        text = ARENA_IN_QUEUE_TEXT.format(**stats)

        keyboard = [[InlineKeyboardButton("Выйти из очереди", callback_data=ARENA)]]
        return InlineKeyboardMarkup(keyboard), text

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()
