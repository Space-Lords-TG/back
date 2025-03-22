from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from screens.registry import register
import screens.mainMenu as mainMenu

# Определяем идентификаторы экранов
SHIP = 'КОРАБЛЬ'
SHIP_WEAPON = 'SHIP_WEAPON'
SHIP_WEAPON_UPGRADE = 'SHIP_WEAPON_UPGRADE'
POST_SHIP_WEAPON_UPGRADE = 'POST_SHIP_WEAPON_UPGRADE'
SHIP_WEAPON_CHANGE = 'SHIP_WEAPON_CHANGE'
SHIP_BODY = 'SHIP_BODY'
SHIP_BODY_REPAIR = 'SHIP_BODY_REPAIR'
POST_SHIP_BODY_REPAIR = 'POST_SHIP_BODY_REPAIR'
SHIP_BODY_UPGRADE = 'SHIP_BODY_UPGRADE'
POST_SHIP_BODY_UPGRADE = 'POST_SHIP_BODY_UPGRADE'
SHIP_BODY_CHANGE = 'SHIP_BODY_CHANGE'

SHIP_WEAPON_1 = 'SHIP_WEAPON_1'
SHIP_WEAPON_2 = 'SHIP_WEAPON_2'
SHIP_WEAPON_3 = 'SHIP_WEAPON_3'
SHIP_WEAPON_4 = 'SHIP_WEAPON_4'
POST_SHIP_WEAPON_1 = 'POST_SHIP_WEAPON_1'
POST_SHIP_WEAPON_2 = 'POST_SHIP_WEAPON_2'
POST_SHIP_WEAPON_3 = 'POST_SHIP_WEAPON_3'
POST_SHIP_WEAPON_4 = 'POST_SHIP_WEAPON_4'

SHIP_BODY_1 = 'SHIP_BODY_1'
SHIP_BODY_2 = 'SHIP_BODY_2'
SHIP_BODY_3 = 'SHIP_BODY_3'
SHIP_BODY_4 = 'SHIP_BODY_4'
POST_SHIP_BODY_1 = 'POST_SHIP_BODY_1'
POST_SHIP_BODY_2 = 'POST_SHIP_BODY_2'
POST_SHIP_BODY_3 = 'POST_SHIP_BODY_3'
POST_SHIP_BODY_4 = 'POST_SHIP_BODY_4'

# Функция, возвращающая разметку для корабля
@register(SHIP)
def get_ship(query: CallbackQuery):
    # Проверка состояние игрока

    keyboard = [
        [InlineKeyboardButton("Оружие", callback_data=SHIP_WEAPON), InlineKeyboardButton("Корпус", callback_data=SHIP_BODY)],
        [InlineKeyboardButton("Ремонт", callback_data=SHIP_BODY_REPAIR)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Ваш корабль:

Скорость: 100
Урон: 150
Шанс крита: 15%
Крит. урон: 200%
Защита: 50
Щиты: 20
Манёвренность: 100
Здоровье корабля: 200/200

Установленные модули:
Оружие — <b>GIGACHUNGUS_SUPER</b>
Корпус — <b>Millennium Falcon 1000</b>

Вы можете настроить модули в этом меню.
"""


# ОРУЖИЕ =============================================================================

# Функция, возвращающая разметку для оружия
@register(SHIP_WEAPON)
def get_ship_weapon(query: CallbackQuery):
    # Проверка состояние игрока

    keyboard = [
        [InlineKeyboardButton("Заменить", callback_data=SHIP_WEAPON_CHANGE), InlineKeyboardButton("Улучшить", callback_data=SHIP_WEAPON_UPGRADE)],
        [InlineKeyboardButton("Назад", callback_data=SHIP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Оружие:
На данный момент установлено:
GIGACHUNGUS_SUPER_DEVASTATOR7

Характеристики:
Урон: 100
Крит. частота: 15%
Крит. урон: 150%

Стоимость улучшения:
5 кристаллов
10 металлов
"""

# Функция, возвращающая разметку для улучшения оружия
@register(SHIP_WEAPON_UPGRADE)
def get_ship_weapon_upgrade(query: CallbackQuery):
    # Проверка состояние игрока

    keyboard = [
        [InlineKeyboardButton("Подтвердить", callback_data=POST_SHIP_WEAPON_UPGRADE)],
        [InlineKeyboardButton("Назад", callback_data=SHIP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Оружие (улучшение)
Вы хотите улучшить:
GIGACHUNGUS_SUPER_DEVASTATOR7

Текущие показатели / улучшение:
Урон: 100 -> 128
Крит. частота: 15% -> 15%
Крит. урон: 150% -> 160%

Стоимость улучшения:
5 кристаллов
10 металлов
"""

# Функция, отправляющая запрос на улучшение
@register(POST_SHIP_WEAPON_UPGRADE)
def post_ship_weapon_upgrade(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('upgrade request')
    
    return get_ship_weapon(query)

# Функция, возвращающая разметку для замены оружия
@register(SHIP_WEAPON_CHANGE)
def get_ship_weapon_change(query: CallbackQuery):
    # Проверка состояние игрока

    keyboard = [
        [InlineKeyboardButton("Оружие 1", callback_data=SHIP_WEAPON_1), InlineKeyboardButton("Оружие 2", callback_data=SHIP_WEAPON_2)],
        [InlineKeyboardButton("Назад", callback_data=SHIP_WEAPON)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Оружие (замена)
На данный момент установлено:
GIGACHUNGUS_SUPER_DEVASTATOR7

Характеристики:
Урон: 100
Крит. частота: 15%
Крит. урон: 150%

Вы можете выбрать оружие для
замены:
"""

def make_ship_weapon_text(currentWeapon, newWeapon):
    return \
f"""Оружие для замены:
Оружие {newWeapon}
На данный момент установлено:
GIGACHUNGUS_SUPER_DEVASTATOR7

Текущие показатели / замена:
Урон: 100 -> 128
Крит. частота: 15% -> 10%
Крит. урон: 150% -> 130%
"""

# Функция, возвращающая разметку для сравнения оружия с оружием 1
@register(SHIP_WEAPON_1)
def get_ship_weapon_1(query: CallbackQuery):
    # Проверка состояние игрока

    keyboard = [
        [InlineKeyboardButton("Заменить", callback_data=POST_SHIP_WEAPON_1)],
        [InlineKeyboardButton("Назад", callback_data=SHIP_WEAPON)]
    ]
    
    return InlineKeyboardMarkup(keyboard), make_ship_weapon_text(None, 1)

# Функция, возвращающая разметку для сравнения оружия с оружием 1
@register(POST_SHIP_WEAPON_1)
def post_ship_weapon_1(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('weapon_1 change request')
    
    return get_ship_weapon(query)

# Функция, возвращающая разметку для сравнения оружия с оружием 2
@register(SHIP_WEAPON_2)
def get_ship_weapon_2(query: CallbackQuery):
    # Проверка состояние игрока

    keyboard = [
        [InlineKeyboardButton("Заменить", callback_data=POST_SHIP_WEAPON_2)],
        [InlineKeyboardButton("Назад", callback_data=SHIP_WEAPON)]
    ]
    
    return InlineKeyboardMarkup(keyboard), make_ship_weapon_text(None, 2)

# Функция, возвращающая разметку для сравнения оружия с оружием 2
@register(POST_SHIP_WEAPON_2)
def post_ship_weapon_2(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('weapon_2 change request')
    
    return get_ship_weapon(query)


# КОРПУС =============================================================================

# Функция, возвращающая разметку для корпуса
@register(SHIP_BODY)
def get_ship_body(query: CallbackQuery):
    # Проверка состояние игрока

    keyboard = [
        [InlineKeyboardButton("Заменить", callback_data=SHIP_BODY_CHANGE), InlineKeyboardButton("Улучшить", callback_data=SHIP_BODY_UPGRADE)],
        [InlineKeyboardButton("Назад", callback_data=SHIP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Корпус:
На данный момент установлено:
Millennium Falcon 1000

Характеристики:
Здоровье: 1200
Защита: 100
Щиты: 50
Манёвренность: 10

Стоимость улучшения:
5 кристаллов
10 металлов
"""

# Функция, возвращающая разметку для ремонта
@register(SHIP_BODY_REPAIR)
def get_ship_repair(query: CallbackQuery):
    # Проверка состояние игрока

    # fetch стоимости ремонта, здоровья корпуса, времени

    keyboard = [
        [InlineKeyboardButton("Ремонт", callback_data=POST_SHIP_BODY_REPAIR)],
        [InlineKeyboardButton("Назад", callback_data=SHIP_BODY)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Ремонт корпуса:

Текущее здоровье корпуса:
228 / 1000 (22,8%)

Стоимость ремонта:
50 кристаллов

Время ремонта:
10 минут
"""

# Функция, возвращающая разметку для ремонта
@register(POST_SHIP_BODY_REPAIR)
def post_ship_repair(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('repair request')
    
    return mainMenu.get_default_menu(query)

# Функция, возвращающая разметку для улучшения оружия
@register(SHIP_BODY_UPGRADE)
def get_ship_body_upgrade(query: CallbackQuery):
    # Проверка состояние игрока

    keyboard = [
        [InlineKeyboardButton("Подтвердить", callback_data=POST_SHIP_BODY_UPGRADE)],
        [InlineKeyboardButton("Назад", callback_data=SHIP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Корпус (улучшение)
Вы хотите улучшить:
Millennium Falcon 1000

Текущие показатели / улучшение:
Здоровье: 1200 -> 1500
Защита: 100 -> 128
Щиты: 50 -> 80
Манёвренность: 10 -> 20

Стоимость улучшения:
5 кристаллов
10 металлов
"""

# Функция, отправляющая запрос на улучшение
@register(POST_SHIP_BODY_UPGRADE)
def post_ship_body_upgrade(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('body upgrade request')
    
    return get_ship_body(query)

# Функция, возвращающая разметку для улучшения оружия
@register(SHIP_BODY_CHANGE)
def get_ship_body_change(query: CallbackQuery):
    # Проверка состояние игрока

    keyboard = [
        [InlineKeyboardButton("Корпус 1", callback_data=SHIP_BODY_1), InlineKeyboardButton("Корпус 2", callback_data=SHIP_BODY_2)],
        [InlineKeyboardButton("Назад", callback_data=SHIP_BODY)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Корпус (замена)
На данный момент установлено:
Millennium Falcon 1000

Характеристики:
Здоровье: 1200
Защита: 100
Щиты: 50
Манёвренность: 10

Вы можете выбрать корпус для
замены:
"""

def make_ship_body_text(currentBody, newBody):
    return \
f"""Корпус для замены:
Корпус {newBody}
На данный момент установлено:
Millennium Falcon 1000

Текущие показатели / замена:
Здоровье: 1200 -> 1400
Защита: 15% -> 20%
Щиты: 150% -> 100%
Манёвренность: 10 -> 10
"""

# Функция, возвращающая разметку для сравнения оружия с оружием 1
@register(SHIP_BODY_1)
def get_ship_body_1(query: CallbackQuery):
    # Проверка состояние игрока

    keyboard = [
        [InlineKeyboardButton("Заменить", callback_data=POST_SHIP_BODY_1)],
        [InlineKeyboardButton("Назад", callback_data=SHIP_BODY)]
    ]
    
    return InlineKeyboardMarkup(keyboard), make_ship_body_text(None, 1)

# Функция, возвращающая разметку для сравнения оружия с оружием 1
@register(POST_SHIP_BODY_1)
def post_ship_body_1(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('body_1 change request')
    
    return get_ship_body(query)

# Функция, возвращающая разметку для сравнения оружия с оружием 2
@register(SHIP_BODY_2)
def get_ship_body_2(query: CallbackQuery):
    # Проверка состояние игрока

    keyboard = [
        [InlineKeyboardButton("Заменить", callback_data=POST_SHIP_BODY_2)],
        [InlineKeyboardButton("Назад", callback_data=SHIP_BODY)]
    ]
    
    return InlineKeyboardMarkup(keyboard), make_ship_body_text(None, 2)

# Функция, возвращающая разметку для сравнения оружия с оружием 2
@register(POST_SHIP_BODY_2)
def post_ship_body_2(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('body_2 change request')
    
    return get_ship_body(query)
