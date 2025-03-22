from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from screens.registry import register

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
    # Проверка состояние игрока

    # Отправка запроса на сервер (чтобы встать в очередь)

    keyboard = [
        [InlineKeyboardButton("Выйти из очереди", callback_data=ARENA)]
    ]
    
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
