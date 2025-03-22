from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from screens.registry import register
import screens.mainMenu as mainMenu
import screens.ship as shipScreens

# Определяем идентификаторы экранов
PLANET = 'PLANET'
POST_PLANET_CLAIM = 'POST_PLANET_CLAIM'
POST_PLANET_GATHER = 'POST_PLANET_GATHER'
PLANET_UPGRADE = 'PLANET_UPGRADE'
POST_PLANET_UPGRADE = 'POST_PLANET_UPGRADE'
PLANET_ENEMY = 'PLANET_ENEMY'

# Функция, возвращающая разметку для планеты
@register(PLANET)
def get_planet(query: CallbackQuery):
    # Проверка состояние игрока

    # Определяем, какой именно экран показывать в зависимости от отношения игрока к планете
    
    return get_free_planet(query)

# Свободная планета
def get_free_planet(query: CallbackQuery):
    # Проверка состояние игрока

    keyboard = [
        [InlineKeyboardButton("Построить аванпост", callback_data=POST_PLANET_CLAIM)],
        [InlineKeyboardButton("Назад", callback_data=mainMenu.DEFAULT)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Планета
Альфа 1

Доступные ресурсы:
10 кристаллов/час

Вместимость (уровень 1):
500 кристаллов

Планета свободна

Стоимость постройки аванпоста:
10 металла
20 топлива
"""

# Отправляет запрос на постройку аванпоста на планете
@register(POST_PLANET_CLAIM)
def post_planet_claim(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('planet claim request')
    
    return get_owned_planet(query)

# Своя планета
def get_owned_planet(query: CallbackQuery):
    # Проверка состояния игрока

    keyboard = [
        [InlineKeyboardButton("Собрать ресурсы", callback_data=POST_PLANET_GATHER), InlineKeyboardButton("Улучшить", callback_data=PLANET_UPGRADE)],
        [InlineKeyboardButton("Назад", callback_data=mainMenu.DEFAULT)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Планета
Альфа 1
Уровень 2

Производство:
15 кристаллов/час

Накоплено ресурсов:
200/1000 кристаллов

Доступно улучшение до уровня 3:
50 кристаллов
80 металлов
Вы владеете этой планетой.
"""

# Отправляет запрос на сбор ресурсов
@register(POST_PLANET_GATHER)
def post_planet_gather(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('planet gether request')
    
    return get_owned_planet(query)

@register(PLANET_UPGRADE)
def get_planet_upgrade(query: CallbackQuery):
    # Проверка состояния игрока

    keyboard = [
        [InlineKeyboardButton("Подтвердить", callback_data=POST_PLANET_UPGRADE)],
        [InlineKeyboardButton("Назад", callback_data=PLANET)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Планета (улучшение)
Вы хотите улучшить:
Альфа 1

Текущие показатели / улучшение:
Кристаллы: 10/час -> 15/час
Металлы: 15/час -> 20/час
Вместимость:
100 (К), 500 (М) -> 150 (К), 800 (М)

Стоимость улучшения:
50 кристаллов
80 металлов
"""

# Отправляет запрос на улучшение планеты
@register(POST_PLANET_UPGRADE)
def post_planet_upgrade(query: CallbackQuery):
    # Проверка состояния игрока

    # Отправка запроса
    print('planet upgrade request')
    
    return get_owned_planet(query)

@register(PLANET_ENEMY)
def get_enemy_planet(query: CallbackQuery):
    # Проверка состояния игрока

    keyboard = [
        [InlineKeyboardButton("Захватить планету (бой)", callback_data=POST_PLANET_UPGRADE)],
        [InlineKeyboardButton("Назад", callback_data=mainMenu.DEFAULT)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Планета
Альфа 1

Производство:
15 кристаллов/час
Планета занята игроков Aboba1337
Скорость: 100
Урон: 150
Шанс крита: 15%
Крит. урон: 200%
Защита: 50
Щиты: 20
Манёвренность: 100
Здоровье: 1200
"""

# Определяем идентификаторы экранов
PLANET_FIGHT = 'PLANET_FIGHT'

# Функция, возвращающая разметку для арены
@register(PLANET_FIGHT)
def get_planet_fight(query: CallbackQuery):
    # Проверка состояние игрока

    # Если игрок уже в очереди, то отправляем соответствующий экран
    # return get_queue(query)

    keyboard = [
        [InlineKeyboardButton("Ремонт", callback_data=shipScreens.SHIP_BODY_REPAIR)]
        [InlineKeyboardButton("К планете", callback_data=PLANET)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Результаты боя

Вы: DeadlyParkur (220 💪)
Противник: Aboba1337 (228 💪)
Статистика боя:Нанесено урона: 1337Получено урона: 1231Раундов: 17Оставшаяся прочность: 228 (18%)
Итог: победа!
Вы захватили планету.
"""
