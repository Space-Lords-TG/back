from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from src.application.config_loader import config
from src.application.player_service import PlayerService
from src.infrastructure.database import SessionLocal
from src.presentation.screens.registry import register
import src.presentation.screens.mainMenu as mainMenu
from src.presentation.screens.texts import (PLANET_LIST_ITEM, MAP_TEXT, SECTOR_LIST_ITEM, SECTORS_TEXT, PLANET_TRAVEL_TEXT, SECTOR_TRAVEL_TEXT)

# Определяем идентификаторы экранов
MAP = config["screens"]['MAP']

PLANET_1 = config["screens"]['PLANET_1']
PLANET_2 = config["screens"]['PLANET_2']
PLANET_3 = config["screens"]['PLANET_3']
PLANET_4 = config["screens"]['PLANET_4']
POST_PLANET_1 = config["screens"]['POST_PLANET_1']
POST_PLANET_2 = config["screens"]['POST_PLANET_2']
POST_PLANET_3 = config["screens"]['POST_PLANET_3']
POST_PLANET_4 = config["screens"]['POST_PLANET_4']

SECTORS = config["screens"]['SECTORS']
SECTOR_1 = config["screens"]['SECTOR_1']
SECTOR_2 = config["screens"]['SECTOR_2']
SECTOR_3 = config["screens"]['SECTOR_3']
SECTOR_4 = config["screens"]['SECTOR_4']
POST_SECTOR_1 = config["screens"]['POST_SECTOR_1']
POST_SECTOR_2 = config["screens"]['POST_SECTOR_2']
POST_SECTOR_3 = config["screens"]['POST_SECTOR_3']
POST_SECTOR_4 = config["screens"]['POST_SECTOR_4']


# Общие функции для формирования данных
def get_planet_data():
    return [
        {"id": PLANET_1, "name": "Альфа 1", "distance": 1, "post": POST_PLANET_1},
        {"id": PLANET_2, "name": "Альфа 2", "distance": 1, "post": POST_PLANET_2},
        {"id": PLANET_3, "name": "Альфа 3", "distance": 1, "post": POST_PLANET_3},
        {"id": PLANET_4, "name": "Альфа 4", "distance": 1, "post": POST_PLANET_4}
    ]


def get_sector_data():
    return [
        {"id": SECTOR_1, "name": "Абоба", "distance": 1, "post": POST_SECTOR_1},
        {"id": SECTOR_2, "name": "Амогус", "distance": 1, "post": POST_SECTOR_2},
        {"id": SECTOR_3, "name": "Чебупель", "distance": 2, "post": POST_SECTOR_3},
        {"id": SECTOR_4, "name": "Гыча", "distance": 4, "post": POST_SECTOR_4}
    ]


def create_travel_keyboard(confirm_callback, back_callback):
    return [
        [InlineKeyboardButton("В путь", callback_data=confirm_callback)],
        [InlineKeyboardButton("Назад", callback_data=back_callback)]
    ]


def create_list_keyboard(items, back_callback=None):
    keyboard = []
    for i in range(0, len(items), 2):
        row = items[i:i + 2]
        keyboard.append([
            InlineKeyboardButton(item["name"], callback_data=item["id"])
            for item in row
        ])
    if back_callback:
        keyboard.append([InlineKeyboardButton("Назад", callback_data=back_callback)])
    return keyboard


# Основные экраны
@register(MAP)
def get_map(query: CallbackQuery):
    try:
        db = SessionLocal()
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, MAP)
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

    planets = get_planet_data()
    keyboard = create_list_keyboard(planets, back_callback=None)
    keyboard.append([InlineKeyboardButton("Сектора", callback_data=SECTORS)])

    planet_list = "\n".join(
        PLANET_LIST_ITEM.format(name=p["name"], distance=p["distance"])
        for p in planets
    )

    map_data = {
        "current_system": "Альфа Центавра",
        "planet_list": planet_list
    }

    return InlineKeyboardMarkup(keyboard), MAP_TEXT.format(**map_data)


@register(SECTORS)
def get_sectors(query: CallbackQuery):
    try:
        db = SessionLocal()
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, SECTORS)
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

    sectors = get_sector_data()
    keyboard = create_list_keyboard(sectors, MAP)

    sectors_list = "\n".join(
        SECTOR_LIST_ITEM.format(name=s["name"], distance=s["distance"])
        for s in sectors
    )

    sectors_data = {
        "current_system": "Альфа Центавра",
        "sectors_list": sectors_list
    }

    return InlineKeyboardMarkup(keyboard), SECTORS_TEXT.format(**sectors_data)


# Обработчики планет
@register(PLANET_1)
def get_planet_1(query: CallbackQuery):
    planets = get_planet_data()
    planet = next(p for p in planets if p["id"] == PLANET_1)

    keyboard = create_travel_keyboard(planet["post"], MAP)

    travel_data = {
        "current_planet": "Пудж 2",
        "destination_planet": planet["name"],
        "distance": 0.1,
        "travel_time": "5 минут",
        "engine_speed": 1
    }

    return InlineKeyboardMarkup(keyboard), PLANET_TRAVEL_TEXT.format(**travel_data)


@register(POST_PLANET_1)
def post_planet_1(query: CallbackQuery):
    planets = get_planet_data()
    planet = next(p for p in planets if p["id"] == PLANET_1)

    print(f'planet {planet["name"]} flight request')
    return mainMenu.get_default_menu(query)


@register(PLANET_2)
def get_planet_2(query: CallbackQuery):
    planets = get_planet_data()
    planet = next(p for p in planets if p["id"] == PLANET_2)

    keyboard = create_travel_keyboard(planet["post"], MAP)

    travel_data = {
        "current_planet": "Пудж 2",
        "destination_planet": planet["name"],
        "distance": 0.1,
        "travel_time": "5 минут",
        "engine_speed": 1
    }

    return InlineKeyboardMarkup(keyboard), PLANET_TRAVEL_TEXT.format(**travel_data)


@register(POST_PLANET_2)
def post_planet_2(query: CallbackQuery):
    planets = get_planet_data()
    planet = next(p for p in planets if p["id"] == PLANET_2)

    print(f'planet {planet["name"]} flight request')
    return mainMenu.get_default_menu(query)


@register(PLANET_3)
def get_planet_3(query: CallbackQuery):
    planets = get_planet_data()
    planet = next(p for p in planets if p["id"] == PLANET_3)

    keyboard = create_travel_keyboard(planet["post"], MAP)

    travel_data = {
        "current_planet": "Пудж 2",
        "destination_planet": planet["name"],
        "distance": 0.1,
        "travel_time": "5 минут",
        "engine_speed": 1
    }

    return InlineKeyboardMarkup(keyboard), PLANET_TRAVEL_TEXT.format(**travel_data)


@register(POST_PLANET_3)
def post_planet_3(query: CallbackQuery):
    planets = get_planet_data()
    planet = next(p for p in planets if p["id"] == PLANET_3)

    print(f'planet {planet["name"]} flight request')
    return mainMenu.get_default_menu(query)


@register(PLANET_4)
def get_planet_4(query: CallbackQuery):
    planets = get_planet_data()
    planet = next(p for p in planets if p["id"] == PLANET_4)

    keyboard = create_travel_keyboard(planet["post"], MAP)

    travel_data = {
        "current_planet": "Пудж 2",
        "destination_planet": planet["name"],
        "distance": 0.1,
        "travel_time": "5 минут",
        "engine_speed": 1
    }

    return InlineKeyboardMarkup(keyboard), PLANET_TRAVEL_TEXT.format(**travel_data)


@register(POST_PLANET_4)
def post_planet_4(query: CallbackQuery):
    planets = get_planet_data()
    planet = next(p for p in planets if p["id"] == PLANET_4)

    print(f'planet {planet["name"]} flight request')
    return mainMenu.get_default_menu(query)


# Обработчики секторов
@register(SECTOR_1)
def get_sector_1(query: CallbackQuery):
    sectors = get_sector_data()
    sector = next(s for s in sectors if s["id"] == SECTOR_1)

    keyboard = create_travel_keyboard(sector["post"], SECTORS)

    travel_data = {
        "current_system": "Альфа Центавра",
        "destination_sector": sector["name"],
        "distance": sector["distance"],
        "travel_time": f"{sector['distance']} часа",
        "engine_speed": 1
    }

    return InlineKeyboardMarkup(keyboard), SECTOR_TRAVEL_TEXT.format(**travel_data)


@register(POST_SECTOR_1)
def post_sector_1(query: CallbackQuery):
    sectors = get_sector_data()
    sector = next(s for s in sectors if s["id"] == SECTOR_1)

    print(f'sector {sector["name"]} flight request')
    return mainMenu.get_default_menu(query)


@register(SECTOR_2)
def get_sector_2(query: CallbackQuery):
    sectors = get_sector_data()
    sector = next(s for s in sectors if s["id"] == SECTOR_2)

    keyboard = create_travel_keyboard(sector["post"], SECTORS)

    travel_data = {
        "current_system": "Альфа Центавра",
        "destination_sector": sector["name"],
        "distance": sector["distance"],
        "travel_time": f"{sector['distance']} часа",
        "engine_speed": 1
    }

    return InlineKeyboardMarkup(keyboard), SECTOR_TRAVEL_TEXT.format(**travel_data)


@register(POST_SECTOR_2)
def post_sector_2(query: CallbackQuery):
    sectors = get_sector_data()
    sector = next(s for s in sectors if s["id"] == SECTOR_2)

    print(f'sector {sector["name"]} flight request')
    return mainMenu.get_default_menu(query)


@register(SECTOR_3)
def get_sector_3(query: CallbackQuery):
    sectors = get_sector_data()
    sector = next(s for s in sectors if s["id"] == SECTOR_3)

    keyboard = create_travel_keyboard(sector["post"], SECTORS)

    travel_data = {
        "current_system": "Альфа Центавра",
        "destination_sector": sector["name"],
        "distance": sector["distance"],
        "travel_time": f"{sector['distance']} часа",
        "engine_speed": 1
    }

    return InlineKeyboardMarkup(keyboard), SECTOR_TRAVEL_TEXT.format(**travel_data)


@register(POST_SECTOR_3)
def post_sector_3(query: CallbackQuery):
    sectors = get_sector_data()
    sector = next(s for s in sectors if s["id"] == SECTOR_3)

    print(f'sector {sector["name"]} flight request')
    return mainMenu.get_default_menu(query)


@register(SECTOR_4)
def get_sector_4(query: CallbackQuery):
    sectors = get_sector_data()
    sector = next(s for s in sectors if s["id"] == SECTOR_4)

    keyboard = create_travel_keyboard(sector["post"], SECTORS)

    travel_data = {
        "current_system": "Альфа Центавра",
        "destination_sector": sector["name"],
        "distance": sector["distance"],
        "travel_time": f"{sector['distance']} часа",
        "engine_speed": 1
    }

    return InlineKeyboardMarkup(keyboard), SECTOR_TRAVEL_TEXT.format(**travel_data)


@register(POST_SECTOR_4)
def post_sector_4(query: CallbackQuery):
    sectors = get_sector_data()
    sector = next(s for s in sectors if s["id"] == SECTOR_4)

    print(f'sector {sector["name"]} flight request')
    return mainMenu.get_default_menu(query)
