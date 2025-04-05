import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from src.presentation.utils.getImage import *
import src.presentation.screens.mainMenu as mainMenu
import src.presentation.screens.map as mapScreens
import src.presentation.screens.ship as shipScreens
import src.presentation.screens.arena as arenaScreens
import src.presentation.screens.registry as registry

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Обработчик команды /start, выводит главный экран
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [[arenaScreens.ARENA, mapScreens.MAP], [shipScreens.SHIP, mainMenu.DEFAULT]]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    # Отправляем сообщение со стандартной клавиатурой
    await update.message.reply_text("Добро пожаловать!", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    
    query = update.callback_query
    markup, text = mainMenu.get_default_menu(query)
    imageLink = getImage(mainMenu.DEFAULT)

    await update.message.reply_photo(photo=imageLink, caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)

# Обработчик нажатий на inline кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # отвечаем на callback
    screen_id = query.data

    handler = registry.handlers.get(screen_id)
    # ID пользователя можно получить из запроса
    print(query.from_user.id)

    # Если экран не найден, можно вернуть сообщение об ошибке
    if not handler:
        await query.edit_message_text("Неизвестный экран.")
        return

    markup, text = handler(query)

    # await query.edit_message_text(text=text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await query.edit_message_caption(caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)

    
# Обработчик для стандартных кнопок меню.
# Он обрабатывает входящие сообщения с текстом кнопок и отправляет соответствующие ответы.
async def handle_standard_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commandName = update.message.text
    handler = registry.handlers.get(commandName)

    if not handler:
        update.message.reply_text("Неизвестная команда")
        return
    
    imageLink = getImage(commandName)
    
    markup, text = handler(commandName)
    await update.message.reply_photo(photo=imageLink, caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
    # if (imageLink):
    #     await update.message.reply_photo(photo=imageLink, caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
    # else:
    #     await update.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)

def main():
    token = os.getenv('BOT_TOKEN')

    # Создаем приложение
    application = Application.builder().token(token).build()

    # Регистрируем обработчики команд и callback'ов
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_standard_buttons))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
