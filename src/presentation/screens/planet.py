from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from src.application.config_loader import config
from src.application.player_service import PlayerService
from src.infrastructure.database import SessionLocal
from src.presentation.screens.registry import register
import src.presentation.screens.mainMenu as mainMenu
import src.presentation.screens.ship as shipScreens
from texts import PLANET_FREE_TEXT, PLANET_TUTORIAL_TEXT, PLANET_OWNED_TEXT, PLANET_UPGRADE_PREVIEW_TEXT, \
    PLANET_ENEMY_TEXT, PLANET_FIGHT_RESULT_TEXT

# Определяем идентификаторы экранов
PLANET = config["screens"]['PLANET']
POST_PLANET_CLAIM = config["screens"]['POST_PLANET_CLAIM']
POST_PLANET_GATHER = config["screens"]['POST_PLANET_GATHER']
PLANET_UPGRADE = config["screens"]['PLANET_UPGRADE']
POST_PLANET_UPGRADE = config["screens"]['POST_PLANET_UPGRADE']
PLANET_ENEMY = config["screens"]['PLANET_ENEMY']
PLANET_FIGHT = config["screens"]['PLANET_FIGHT']


@register(PLANET)
def get_planet(query: CallbackQuery):
    tutorial = False
    try:
        db = SessionLocal()
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, PLANET)
        if player_service.get_screen_view_count(player_id, PLANET) == 0:
            tutorial = True
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

    # В реальном приложении здесь должна быть логика определения состояния планеты
    return get_free_planet(query, tutorial)


def get_free_planet(query: CallbackQuery, tutorial: bool = False):
    keyboard = [
        [InlineKeyboardButton(
            "Построить аванпост",
            callback_data=POST_PLANET_CLAIM)],
        [InlineKeyboardButton(
            "Назад",
            callback_data=mainMenu.DEFAULT)]
    ]

    planet_data = {
        'name': 'Альфа 1',
        'production_rate': 10,
        'resource_type': 'кристаллов',
        'level': 1,
        'capacity': 500,
        'claim_cost_metal': 10,
        'claim_cost_fuel': 20
    }

    text = PLANET_FREE_TEXT.format(**planet_data)

    if tutorial:
        text = PLANET_TUTORIAL_TEXT + text

    return InlineKeyboardMarkup(keyboard), text


@register(POST_PLANET_CLAIM)
def post_planet_claim(query: CallbackQuery):
    try:
        db = SessionLocal()
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, POST_PLANET_CLAIM)
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

    # Здесь должна быть логика проверки ресурсов и захвата планеты
    return get_owned_planet(query)


def get_owned_planet(query: CallbackQuery):
    keyboard = [
        [InlineKeyboardButton(
            "Собрать ресурсы",
            callback_data=POST_PLANET_GATHER),
            InlineKeyboardButton("Улучшить", callback_data=PLANET_UPGRADE)],
        [InlineKeyboardButton("Назад", callback_data=mainMenu.DEFAULT)]
    ]

    planet_data = {
        'name': 'Альфа 1',
        'level': 2,
        'next_level': 3,
        'production_rate': 15,
        'resource_type': 'кристаллов',
        'stored': 200,
        'capacity': 1000,
        'upgrade_cost_crystals': 50,
        'upgrade_cost_metal': 80
    }

    return InlineKeyboardMarkup(keyboard), PLANET_OWNED_TEXT.format(**planet_data)


@register(POST_PLANET_GATHER)
def post_planet_gather(query: CallbackQuery):
    try:
        db = SessionLocal()
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, POST_PLANET_GATHER)
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

    # Здесь должна быть логика сбора ресурсов
    return get_owned_planet(query)


@register(PLANET_UPGRADE)
def get_planet_upgrade(query: CallbackQuery):
    try:
        db = SessionLocal()
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, PLANET_UPGRADE)
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

    keyboard = [
        [InlineKeyboardButton(
            "Подтвердить",
            callback_data=POST_PLANET_UPGRADE)],
        [InlineKeyboardButton(
            "Назад",
            callback_data=PLANET)]
    ]

    upgrade_data = {
        'name': 'Альфа 1',
        'current_crystal_rate': 10,
        'next_crystal_rate': 15,
        'current_metal_rate': 15,
        'next_metal_rate': 20,
        'current_crystal_capacity': 100,
        'next_crystal_capacity': 150,
        'current_metal_capacity': 500,
        'next_metal_capacity': 800,
        'upgrade_cost_crystals': 50,
        'upgrade_cost_metal': 80
    }

    return InlineKeyboardMarkup(keyboard), PLANET_UPGRADE_PREVIEW_TEXT.format(**upgrade_data)


@register(POST_PLANET_UPGRADE)
def post_planet_upgrade(query: CallbackQuery):
    try:
        db = SessionLocal()
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, POST_PLANET_UPGRADE)
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

    # Здесь должна быть логика улучшения планеты
    return get_owned_planet(query)


@register(PLANET_ENEMY)
def get_enemy_planet(query: CallbackQuery):
    try:
        db = SessionLocal()
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, PLANET_ENEMY)
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

    keyboard = [
        [InlineKeyboardButton(
            "Захватить планету (бой)",
            callback_data=PLANET_FIGHT)],
        [InlineKeyboardButton(
            "Назад",
            callback_data=mainMenu.DEFAULT)]
    ]

    enemy_data = {
        'name': 'Альфа 1',
        'production_rate': 15,
        'resource_type': 'кристаллов',
        'owner_name': 'Aboba1337',
        'owner_speed': 100,
        'owner_damage': 150,
        'owner_crit_rate': 15,
        'owner_crit_damage': 200,
        'owner_armor': 50,
        'owner_shields': 20,
        'owner_maneuver': 100,
        'owner_health': 1200
    }

    return InlineKeyboardMarkup(keyboard), PLANET_ENEMY_TEXT.format(**enemy_data)


@register(PLANET_FIGHT)
def get_planet_fight(query: CallbackQuery):
    try:
        db = SessionLocal()
        player_id = query.from_user.id
        player_service = PlayerService(db)
        player_service.increment_screen_view(player_id, PLANET_FIGHT)
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

    keyboard = [
        [InlineKeyboardButton("Ремонт", callback_data=shipScreens.SHIP_BODY_REPAIR)],
        [InlineKeyboardButton("К планете", callback_data=PLANET)]
    ]

    fight_result = {
        'player_name': 'DeadlyParkur',
        'player_power': 220,
        'enemy_name': 'Aboba1337',
        'enemy_power': 228,
        'damage_dealt': 1337,
        'damage_received': 1231,
        'rounds': 17,
        'health_left': 228,
        'health_percent': 18,
        'result': 'победа',
        'additional_message': 'Вы захватили планету.'
    }

    return InlineKeyboardMarkup(keyboard), PLANET_FIGHT_RESULT_TEXT.format(**fight_result)
