from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from src.presentation.screens.registry import register
from src.application.utm_service import UtmService
from src.infrastructure.database import SessionLocal

from src.application.config_loader import config

# Определяем идентификаторы экранов
ADMIN = "ADMIN"
ADMIN_UTM_ALL = "ADMIN_UTM_ALL"
ADMIN_CREATE_UTM = "ADMIN_CREATE_UTM"
ADMIN_REGISTRATION_INFO = "ADMIN_REGISTRSTION_INFO" 
ADMIN_PLAYER_TABLES = "ADMIN_PLAYER_TABLES"
ADMIN_SET_RESOURCES = "ADMIN_SET_RESOURCES"
ADMIN_BROADCAST = "ADMIN_BROADCAST"

def checkAdmin(query: CallbackQuery | Message):
    # Проверка вхождение пользователя в состав админов
    player_id = query.from_user.id
    if (player_id not in config["admins"]["admins_array"]):
        raise ValueError("Неизвестная команда")

# Функция, возвращающая разметку для админки
@register(ADMIN)
def get_admin(query: CallbackQuery | Message):
    db = SessionLocal()
    try:
        checkAdmin(query)

        # Основной интерфейс админки
        keyboard = [[InlineKeyboardButton("Просмотреть UTM метки", callback_data=ADMIN_UTM_ALL), 
                     InlineKeyboardButton("Создать UTM метку", callback_data=ADMIN_CREATE_UTM, switch_inline_query_current_chat="/utm ")],
                    [InlineKeyboardButton("Данные о регистрации", callback_data=ADMIN_REGISTRATION_INFO), 
                     InlineKeyboardButton("Таблицы игрока", callback_data=ADMIN_PLAYER_TABLES)],
                    [InlineKeyboardButton("Редактирование ресурсов", callback_data=ADMIN_SET_RESOURCES), 
                     InlineKeyboardButton("Оповещение игроков", callback_data=ADMIN_BROADCAST)]]
        return InlineKeyboardMarkup(keyboard), \
"""Админка

Вы находитесь на главном экране админки.

Выберите действие:
"""

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


# Функция, возвращающая статистику по UTM меткам
@register(ADMIN_UTM_ALL)
def get_utm_all(query: CallbackQuery | Message):
    db = SessionLocal()
    try:
        checkAdmin(query)
        service = UtmService(db)

        bot_name = config["admins"]["bot_name"]
        utmList = service.get_all_utm()
        lines = "\n".join([f"{utm.tag}: {utm.used}\nСсылка: <code>\
                           https://t.me/{bot_name}?start={utm.tag}</code>\n" for utm in utmList])

        keyboard = [[InlineKeyboardButton("Назад", callback_data=ADMIN)]]
        return InlineKeyboardMarkup(keyboard), \
f"""Админка

Список UTM меток (Название тега: кол-во вызовов start с этой меткой):
{lines}
"""

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()


# Функция, возвращающая статистику по UTM меткам
@register(ADMIN_CREATE_UTM)
def get_create_all(query: CallbackQuery | Message):
    try:
        checkAdmin(query)

        keyboard = [[InlineKeyboardButton("Назад", callback_data=ADMIN)]]
        return InlineKeyboardMarkup(keyboard), \
"""Админка

Введите тег для новой UTM метки:
<code>/utm ТЕГ_МЕТКИ</code>
"""

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        pass


# Функция, возвращающая статистику по UTM меткам
@register(ADMIN_REGISTRATION_INFO)
def registration_info(query: CallbackQuery | Message):
    try:
        checkAdmin(query)

        keyboard = [[InlineKeyboardButton("Назад", callback_data=ADMIN)]]
        return InlineKeyboardMarkup(keyboard), \
"""Админка

Введите команду для просмотра зарегистрированных пользователей:
<code>/get_users day/week/month/year/all</code>
"""

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        pass


@register(ADMIN_PLAYER_TABLES)
def player_tables(query: CallbackQuery | Message):
    try:
        checkAdmin(query)

        keyboard = [[InlineKeyboardButton("Назад", callback_data=ADMIN)]]
        return InlineKeyboardMarkup(keyboard), \
"""Админка

Введите команду для просмотра таблиц игрока:
<code>/get_user_info ИМЯ_ПОЛЬЗОВАТЕЛЯ</code>
"""

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        pass


@register(ADMIN_SET_RESOURCES)
def set_resources(query: CallbackQuery | Message):
    try:
        checkAdmin(query)

        keyboard = [[InlineKeyboardButton("Назад", callback_data=ADMIN)]]
        return InlineKeyboardMarkup(keyboard), \
"""Админка

Введите команду для установки ресурсов игрока:
<code>/set_resources ИМЯ_ПОЛЬЗОВАТЕЛЯ ТИП_РЕСУРСА КОЛИЧЕСТВО</code>

Пример: /set_resources john_doe metals 1000
Доступные типы ресурсов: metals, crystalls, gas
"""

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        pass


@register(ADMIN_BROADCAST)
def broadcast(query: CallbackQuery | Message):
    try:
        checkAdmin(query)

        keyboard = [[InlineKeyboardButton("Назад", callback_data=ADMIN)]]
        return InlineKeyboardMarkup(keyboard), \
"""Админка

Введите команду для оповещения игроков:
<code>/broadcast СООБЩЕНИЕ</code>

"""

    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        pass


