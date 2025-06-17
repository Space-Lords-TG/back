from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from src.application.config_loader import config
from src.presentation.screens.registry import register
import src.presentation.screens.planet as planetScreens
from src.application.player_service import PlayerService
from src.infrastructure.database import SessionLocal

# Определяем идентификаторы экранов
DEFAULT = config["screens"]["DEFAULT"]

# Функция, возвращающая разметку для стандартного экрана
@register(DEFAULT)
def get_default_menu(query: CallbackQuery):
    player_id = query.from_user.id
    db = SessionLocal()

    try:
        service = PlayerService(db)
        service.increment_screen_view(player_id, DEFAULT)
        resources = service.get_resources(player_id)
    except Exception as e:
        return None, f"Ошибка: {str(e)}"
    finally:
        db.close()

    # Если находится на орбите планеты
    keyboard = [
        [InlineKeyboardButton("Просмотр планеты", callback_data=planetScreens.PLANET)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
f"""Главный экран
<b>Добро пожаловать!</b>

Вы можете настроить свой корабль воспользовавшись кнопками ниже.
Разделы "карта" и "просмотр планеты" in development.
Так же вы можете сразиться с другими игроками на арене,
система найдёт вам подходящего оппонента.

<b>Ваши ресурсы</b>
Кристаллы: {resources.crystalls}
Металлы: {resources.metals}
Газы: {resources.gas}
"""
