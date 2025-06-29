from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.application.config_loader import config
from src.presentation.screens.registry import register
import src.presentation.screens.planet as planetScreens
from src.application.player_service import PlayerService
from src.infrastructure.database import SessionLocal
from src.presentation.screens.texts import DEFAULT_TUTORIAL_TEXT, DEFAULT_MENU_TEXT

# Определяем идентификаторы экранов
DEFAULT = config["screens"]["DEFAULT"]


# Функция, возвращающая разметку для стандартного экрана
@register(DEFAULT)
async def get_default_menu(message: Message):
    player_id = message.from_user.id
    db = SessionLocal()
    text = ""

    try:
        service = PlayerService(db)
        service.increment_screen_view(player_id, DEFAULT)
        resources = service.get_resources(player_id)
        if service.get_screen_view_count(player_id, DEFAULT) == 1:
            await message.reply_text(DEFAULT_TUTORIAL_TEXT)
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

    # Если находится на орбите планеты
    keyboard = [
        [InlineKeyboardButton("Просмотр планеты", callback_data=planetScreens.PLANET)]
    ]

    resources_data = {
        'crystalls': resources.crystalls,
        'metals': resources.metals,
        'gas': resources.gas
    }

    text += DEFAULT_MENU_TEXT.format(**resources_data)

    return InlineKeyboardMarkup(keyboard), text
