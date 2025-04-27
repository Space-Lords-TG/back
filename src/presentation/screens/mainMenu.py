from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from src.presentation.screens.registry import register
import src.presentation.screens.planet as planetScreens

# Определяем идентификаторы экранов
DEFAULT = 'ГЛАВНОЕ МЕНЮ'

# Функция, возвращающая разметку для стандартного экрана
@register(DEFAULT)
def get_default_menu(query: CallbackQuery):
    # Проверка состояние игрока

    # Оесли находится на орбите планеты
    keyboard = [
        [InlineKeyboardButton("Просмотр планеты", callback_data=planetScreens.PLANET)]
    ]
    
    return InlineKeyboardMarkup(keyboard), \
"""Главный экран
<b>Добро пожаловать!</b>

Вы можете настроить свой корабль воспользовавшись кнопками ниже.
Раздел "карта" in development.
Так же вы можете сразиться с другими игроками на арене, система найдёт вам подходящего оппонента.
"""
