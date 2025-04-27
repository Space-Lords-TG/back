from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from src.presentation.screens.registry import register
import src.presentation.screens.mainMenu as mainMenu

# Определяем идентификаторы экранов
MAP = 'КАРТА'

PLANET_1 = 'PLANET_1'
PLANET_2 = 'PLANET_2'
PLANET_3 = 'PLANET_3'
PLANET_4 = 'PLANET_4'
POST_PLANET_1 = 'POST_PLANET_1'
POST_PLANET_2 = 'POST_PLANET_2'
POST_PLANET_3 = 'POST_PLANET_3'
POST_PLANET_4 = 'POST_PLANET_4'

SECTORS = 'SECTORS'
SECTOR_1 = 'SECTOR_1'
SECTOR_2 = 'SECTOR_2'
SECTOR_3 = 'SECTOR_3'
SECTOR_4 = 'SECTOR_4'
POST_SECTOR_1 = 'POST_SECTOR_1'
POST_SECTOR_2 = 'POST_SECTOR_2'
POST_SECTOR_3 = 'POST_SECTOR_3'
POST_SECTOR_4 = 'POST_SECTOR_4'

# Функция, возвращающая разметку для карты
@register(MAP)
def get_map(query: CallbackQuery):
    # Проверка состояние игрока

    # Фетч информации о системе и планетах

    planetNames = ["Альфа 1", "Альфа 2", "Альфа 3", "Альфа 4"]

    keyboard = [
        [InlineKeyboardButton(planetNames[0], callback_data=PLANET_1), InlineKeyboardButton(planetNames[1], callback_data=PLANET_2)],
        [InlineKeyboardButton(planetNames[2], callback_data=PLANET_3), InlineKeyboardButton(planetNames[3], callback_data=PLANET_4)],
        [InlineKeyboardButton("Сектора", callback_data=SECTORS)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Текущая система:
<b>Альфа Центавра</b>

Выберите, к какой планете переместиться:
Альфа 1 (1 пк)
Альфа 2 (1 пк)
Альфа 3 (1 пк)
Альфа 4 (1 пк)
"""



# ПЛАНЕТЫ =====================================================================
def make_planet_text(currentPlanet, planetName):
    return \
f"""Текущая планета:
Пудж 2

Пункт назначения:
{planetName}

Расстояние:
0.1 пк.

Время в пути:
5 минут.

Текущий движок:
1 пк/час.
"""

# Функция, возвращающая разметку для планеты 1
@register(PLANET_1)
def get_planet_1(query: CallbackQuery):
    # Проверка состояния игрока

    # Фетч данных о системе, планете под номером X

    keyboard = [
        [InlineKeyboardButton("В путь", callback_data=POST_PLANET_1)],
        [InlineKeyboardButton("Назад", callback_data=MAP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), make_planet_text(None, "Альфа 1")

# Отправляет запрос на перемещение к планете 1
@register(POST_PLANET_1)
def post_planet_body_1(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('planet 1 flight request')
    
    return mainMenu.get_default_menu(query)

# Функция, возвращающая разметку для планеты 2
@register(PLANET_2)
def get_planet_2(query: CallbackQuery):
    # Проверка состояния игрока

    # Фетч данных о системе, планете под номером X

    keyboard = [
        [InlineKeyboardButton("В путь", callback_data=POST_PLANET_2)],
        [InlineKeyboardButton("Назад", callback_data=MAP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), make_planet_text(None, "Альфа 2")

# Отправляет запрсо на перемещение к планете 2
@register(POST_PLANET_2)
def post_planet_body_2(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('planet 2 flight request')
    
    return mainMenu.get_default_menu(query)

# Функция, возвращающая разметку для планеты 3
@register(PLANET_3)
def get_planet_3(query: CallbackQuery):
    # Проверка состояния игрока

    # Фетч данных о системе, планете под номером X

    keyboard = [
        [InlineKeyboardButton("В путь", callback_data=POST_PLANET_3)],
        [InlineKeyboardButton("Назад", callback_data=MAP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), make_planet_text(None, "Альфа 3")

# Отправляет запрсо на перемещение к планете 3
@register(POST_PLANET_3)
def post_planet_body_3(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('planet 3 flight request')
    
    return mainMenu.get_default_menu(query)

# Функция, возвращающая разметку для планеты 4
@register(PLANET_4)
def get_planet_4(query: CallbackQuery):
    # Проверка состояния игрока

    # Фетч данных о системе, планете под номером X

    keyboard = [
        [InlineKeyboardButton("В путь", callback_data=POST_PLANET_4)],
        [InlineKeyboardButton("Назад", callback_data=MAP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), make_planet_text(None, "Альфа 4")

# Отправляет запрсо на перемещение к планете 4
@register(POST_PLANET_4)
def post_planet_body_4(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('planet 4 flight request')
    
    return mainMenu.get_default_menu(query)



# СЕКТОРА =====================================================================
# Функция, возвращающая разметку для секторов
@register(SECTORS)
def get_sectors(query: CallbackQuery):
    # Проверка состояние игрока

    # Фетч информации о текущем секторе и ближайших секторах

    sectorsNames = ["Абоба", "Амогус", "Чебупель", "Гыча"]

    keyboard = [
        [InlineKeyboardButton(sectorsNames[0], callback_data=SECTOR_1), InlineKeyboardButton(sectorsNames[1], callback_data=SECTOR_2)],
        [InlineKeyboardButton(sectorsNames[2], callback_data=SECTOR_3), InlineKeyboardButton(sectorsNames[3], callback_data=SECTOR_4)],
        [InlineKeyboardButton("Назад", callback_data=MAP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Текущая система:
<b>Альфа Центавра</b>

Выберите, в какую систему переместиться:
Абоба (1 пк)
Амогус (1 пк)
Чебупель (2 пк)
Гыча (4 пк)
"""

def make_sector_text(sectorPlanet, sectorName):
    return \
f"""Текущая система:
Альфа Центавра

Пункт назначения:
{sectorName}

Расстояние:
2 пк.

Время в пути:
2 часа.

Текущий движок:
1 пк/час.
"""

# Функция, возвращающая разметку для секторе 1
@register(SECTOR_1)
def get_sector_1(query: CallbackQuery):
    # Проверка состояния игрока

    # Фетч данных о системе, секторе под номером X

    keyboard = [
        [InlineKeyboardButton("В путь", callback_data=POST_SECTOR_1)],
        [InlineKeyboardButton("Назад", callback_data=MAP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), make_sector_text(None, "Абоба")

# Отправляет запрсо на перемещение к секторе 1
@register(POST_SECTOR_1)
def post_sector_body_1(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('sector 1 flight request')
    
    return mainMenu.get_default_menu(query)

# Функция, возвращающая разметку для секторе 2
@register(SECTOR_2)
def get_sector_2(query: CallbackQuery):
    # Проверка состояния игрока

    # Фетч данных о системе, секторе под номером X

    keyboard = [
        [InlineKeyboardButton("В путь", callback_data=POST_SECTOR_2)],
        [InlineKeyboardButton("Назад", callback_data=MAP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), make_sector_text(None, "Амогус")

# Отправляет запрсо на перемещение к секторе 2
@register(POST_SECTOR_2)
def post_sector_body_2(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('sector 2 flight request')
    
    return mainMenu.get_default_menu(query)

# Функция, возвращающая разметку для секторе 3
@register(SECTOR_3)
def get_sector_3(query: CallbackQuery):
    # Проверка состояния игрока

    # Фетч данных о системе, секторе под номером X

    keyboard = [
        [InlineKeyboardButton("В путь", callback_data=POST_SECTOR_3)],
        [InlineKeyboardButton("Назад", callback_data=MAP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), make_sector_text(None, "Чебупель")

# Отправляет запрсо на перемещение к секторе 3
@register(POST_SECTOR_3)
def post_sector_body_3(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('sector 3 flight request')
    
    return mainMenu.get_default_menu(query)

# Функция, возвращающая разметку для сектора 4
@register(SECTOR_4)
def get_sector_4(query: CallbackQuery):
    # Проверка состояния игрока

    # Фетч данных о системе, секторе под номером X

    keyboard = [
        [InlineKeyboardButton("В путь", callback_data=POST_SECTOR_4)],
        [InlineKeyboardButton("Назад", callback_data=MAP)]
    ]
    
    return InlineKeyboardMarkup(keyboard), make_sector_text(None, "Гыча")

# Отправляет запрсо на перемещение о секторе 4
@register(POST_SECTOR_4)
def post_sector_body_4(query: CallbackQuery):
    # Проверка состояние игрока

    # Отправка запроса
    print('sector 4 flight request')
    
    return mainMenu.get_default_menu(query)
