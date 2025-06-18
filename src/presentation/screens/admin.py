from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from src.presentation.screens.registry import register
from src.application.utm_service import UtmService
from src.infrastructure.database import SessionLocal
from src.application.config_loader import config

from src.presentation.screens.texts import ADMIN_BROADCAST_TEXT, ADMIN_SET_RESOURCES_TEXT, ADMIN_PLAYER_TABLES_TEXT, \
    ADMIN_REGISTRATION_INFO_TEXT, ADMIN_CREATE_UTM_TEXT, ADMIN_UTM_LIST_TEXT, UTM_LINK_TEMPLATE, UTM_ITEM_TEXT, \
    ADMIN_MAIN_TEXT

# Определяем идентификаторы экранов
ADMIN = config["screens"]["ADMIN"]
ADMIN_UTM_ALL = config["screens"]["ADMIN_UTM_ALL"]
ADMIN_CREATE_UTM = config["screens"]["ADMIN_CREATE_UTM"]
ADMIN_REGISTRATION_INFO = config["screens"]["ADMIN_REGISTRATION_INFO"]
ADMIN_PLAYER_TABLES = config["screens"]["ADMIN_PLAYER_TABLES"]
ADMIN_SET_RESOURCES = config["screens"]["ADMIN_SET_RESOURCES"]
ADMIN_BROADCAST = config["screens"]["ADMIN_BROADCAST"]


def check_admin(query: CallbackQuery | Message):
    """Проверка вхождения пользователя в состав админов"""
    player_id = query.from_user.id
    if player_id not in config["admins"]["admins_array"]:
        raise ValueError("Неизвестная команда")


def create_admin_keyboard():
    """Создаёт клавиатуру для главного меню админки"""
    return [
        [
            InlineKeyboardButton("Просмотреть UTM метки", callback_data=ADMIN_UTM_ALL),
            InlineKeyboardButton("Создать UTM метку", callback_data=ADMIN_CREATE_UTM,
                                 switch_inline_query_current_chat="/utm ")
        ],
        [
            InlineKeyboardButton("Данные о регистрации", callback_data=ADMIN_REGISTRATION_INFO),
            InlineKeyboardButton("Таблицы игрока", callback_data=ADMIN_PLAYER_TABLES)
        ],
        [
            InlineKeyboardButton("Редактирование ресурсов", callback_data=ADMIN_SET_RESOURCES),
            InlineKeyboardButton("Оповещение игроков", callback_data=ADMIN_BROADCAST)
        ]
    ]


def create_back_keyboard():
    """Создаёт кнопку 'Назад' для подменю"""
    return [[InlineKeyboardButton("Назад", callback_data=ADMIN)]]


@register(ADMIN)
def get_admin(query: CallbackQuery | Message):
    db = SessionLocal()
    try:
        check_admin(query)
        keyboard = create_admin_keyboard()
        return InlineKeyboardMarkup(keyboard), ADMIN_MAIN_TEXT

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register(ADMIN_UTM_ALL)
def get_utm_all(query: CallbackQuery | Message):
    db = SessionLocal()
    try:
        check_admin(query)
        service = UtmService(db)
        bot_name = config["admins"]["bot_name"]

        utm_list = "\n".join(
            UTM_ITEM_TEXT.format(
                tag=utm.tag,
                used=utm.used,
                link=UTM_LINK_TEMPLATE.format(bot_name=bot_name, tag=utm.tag)
            )
            for utm in service.get_all_utm()
        )

        keyboard = create_back_keyboard()
        return InlineKeyboardMarkup(keyboard), ADMIN_UTM_LIST_TEXT.format(utm_list=utm_list)

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


@register(ADMIN_CREATE_UTM)
def get_create_all(query: CallbackQuery | Message):
    try:
        check_admin(query)
        keyboard = create_back_keyboard()
        return InlineKeyboardMarkup(keyboard), ADMIN_CREATE_UTM_TEXT

    except Exception as e:
        return None, f"Ошибка: {str(e)}"


@register(ADMIN_REGISTRATION_INFO)
def registration_info(query: CallbackQuery | Message):
    try:
        check_admin(query)
        keyboard = create_back_keyboard()
        return InlineKeyboardMarkup(keyboard), ADMIN_REGISTRATION_INFO_TEXT

    except Exception as e:
        return None, f"Ошибка: {str(e)}"


@register(ADMIN_PLAYER_TABLES)
def player_tables(query: CallbackQuery | Message):
    try:
        check_admin(query)
        keyboard = create_back_keyboard()
        return InlineKeyboardMarkup(keyboard), ADMIN_PLAYER_TABLES_TEXT

    except Exception as e:
        return None, f"Ошибка: {str(e)}"


@register(ADMIN_SET_RESOURCES)
def set_resources(query: CallbackQuery | Message):
    try:
        check_admin(query)
        keyboard = create_back_keyboard()
        return InlineKeyboardMarkup(keyboard), ADMIN_SET_RESOURCES_TEXT

    except Exception as e:
        return None, f"Ошибка: {str(e)}"


@register(ADMIN_BROADCAST)
def broadcast(query: CallbackQuery | Message):
    try:
        check_admin(query)
        keyboard = create_back_keyboard()
        return InlineKeyboardMarkup(keyboard), ADMIN_BROADCAST_TEXT

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
