from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from src.presentation.screens.registry import register
from src.application.ship_service import ShipService
from src.infrastructure.database import SessionLocal
from datetime import datetime, timezone
from pytz import timezone as pytz_timezone

# Определяем идентификаторы экранов
ARENA = 'АРЕНА'
ARENA_QUEUE = 'ARENA_QUEUE'

# Функция, возвращающая разметку для арены
@register(ARENA)
def get_arena(query: CallbackQuery):
    # Проверка состояние игрока

    # Если игрок уже в очереди, то отправляем соответствующий экран
    # return get_queue(query)

    keyboard = [
        [InlineKeyboardButton("Встать в очередь", callback_data=ARENA_QUEUE)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Арена

Характеристики вашего корабля:
Скорость: 100
Урон: 150
Шанс крита: 15%
Крит. урон: 200%
Защита: 50
Щиты: 20
Манёвренность: 100

Вы можете встать в очередь,
система найдёт подходящего
оппонента.
Бой начнётся автоматически.
"""

# Функция, возвращающая разметку для арены
@register(ARENA_QUEUE)
def get_queue(query: CallbackQuery):
    db = SessionLocal()
    try:
        player_id = query.from_user.id
        service = ShipService(db)
        data = service.get_active_ship(player_id)
        ship = data["ship"]

        # Проверка: корабль на ремонте
        if ship.repair_ends_at and ship.repair_ends_at > datetime.now(timezone.utc):
            moscow_time = ship.repair_ends_at.astimezone(pytz_timezone("Europe/Moscow"))
            time_str = moscow_time.strftime('%H:%M:%S')
            text = f"""<b>Ваш корабль сейчас на ремонте!</b>

Вы не можете участвовать в битве, пока ремонт не завершён.

Завершение ремонта: <b>{time_str}</b>
"""
            keyboard = [[InlineKeyboardButton("Назад", callback_data=ARENA)]]
            return InlineKeyboardMarkup(keyboard), text

        # Основной интерфейс арены
        keyboard = [[InlineKeyboardButton("Выйти из очереди", callback_data=ARENA)]]
        return InlineKeyboardMarkup(keyboard), \
"""Арена

<b>Поиск противника...</b>

Характеристики вашего корабля:
Скорость: 100
Урон: 150
Шанс крита: 15%
Крит. урон: 200%
Защита: 50
Щиты: 20
Манёвренность: 100

Вы находитесь в очереди.
"""

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()
