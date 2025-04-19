from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from src.presentation.screens.registry import register
from src.application.utm_service import UtmService
from src.infrastructure.database import SessionLocal

from src.application.config_loader import config
import src.presentation.screens.mainMenu as mainMenu

# Определяем идентификаторы экранов
ADMIN = "ADMIN"
ADMIN_UTM_ALL = "ADMIN_UTM_ALL"
ADMIN_CREATE_UTM = "ADMIN_CREATE_UTM"

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
                    [InlineKeyboardButton("Данные о регистрации", callback_data=mainMenu.DEFAULT), 
                     InlineKeyboardButton("Таблицы игрока", callback_data=mainMenu.DEFAULT)],
                    [InlineKeyboardButton("Редактирование ресурсов", callback_data=mainMenu.DEFAULT), 
                     InlineKeyboardButton("Оповещение игроков", callback_data=mainMenu.DEFAULT)]]
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
