import os
import logging
import traceback
from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, \
    CommandHandler, ContextTypes, MessageHandler, filters

from src.application.config_loader import config

from src.presentation.utils.getImage import getImage
import src.presentation.screens.mainMenu as mainMenu
import src.presentation.screens.map as mapScreens
import src.presentation.screens.ship as shipScreens
import src.presentation.screens.arena as arenaScreens
import src.presentation.screens.admin as adminScreens
import src.presentation.screens.registry as registry

from src.infrastructure.database import SessionLocal
from src.application.player_service import PlayerService
from src.application.utm_service import UtmService


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Обработчик команды /start, выводит главный экран
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        player_id, username = update.message.from_user.id, \
            update.message.from_user.username
        service = PlayerService(db)
        service.player_init(player_id, username)

        utmService = UtmService(db)
        utm_tag = context.args[0]
        utmService.increment_utm_usage(utm_tag)
    except Exception as e:
        await update.message.reply_text(f"Ошибка:\n<code>{str(e)}</code>", \
                                        parse_mode=ParseMode.HTML)
        print(e)
        return
    finally:
        db.close()

    reply_keyboard = [[arenaScreens.ARENA, mapScreens.MAP], \
                      [shipScreens.SHIP, mainMenu.DEFAULT]]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    # Отправляем сообщение со стандартной клавиатурой
    await update.message.reply_text("Добро пожаловать!", \
                                    reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    
    query = update.callback_query
    markup, text = mainMenu.get_default_menu(query)
    imageLink = getImage(mainMenu.DEFAULT)

    await update.message.reply_photo(photo=imageLink, \
                                     caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
    

# Обработчик команды /admin
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_id = update.message.from_user.id
    
    if (player_id not in config["admins"]["admins_array"]):
        await update.message.reply_text("Неизвестная команда")
        return
    
    message = update.message
    markup, text = adminScreens.get_admin(message)
    imageLink = getImage(adminScreens.ADMIN)

    await update.message.reply_photo(photo=imageLink, \
                                    caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
    

# Обработчик команды /utm
async def utm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_id = update.message.from_user.id
    
    if (player_id not in config["admins"]["admins_array"]):
        await update.message.reply_text("Неизвестная команда")
        return
    
    db = SessionLocal()
    try:
        text = update.message.text
        tag = text[len("/utm "):].strip()

        if not tag:
            raise ValueError("Не задано название метки UTM")

        service = UtmService(db)
        service.create_utm(tag)

        bot_name = config["admins"]["bot_name"]
        utm_link = f"https://t.me/{bot_name}?start={tag}"

        await update.message.reply_text(f"Сгенерирован UTM:\n<code>{utm_link}</code>", \
                                        parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"Ошибка:\n<code>{str(e)}</code>", \
                                        parse_mode=ParseMode.HTML)
        print(e)
        return
    finally:
        db.close()


# Обработчик нажатий на inline кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # отвечаем на callback
    screen_id = query.data
    handler, match = registry.resolve_handler(screen_id)

    if not handler:
        await query.edit_message_text("Неизвестный экран.")
        return

    if match:
        markup, text = handler(query, match)
    else:
        markup, text = handler(query)

    await query.edit_message_caption(caption=text, \
                                     reply_markup=markup, parse_mode=ParseMode.HTML)


# Обработчик для стандартных кнопок меню.
# Он обрабатывает входящие сообщения с текстом кнопок 
# и отправляет соответствующие ответы.
async def handle_standard_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commandName = update.message.text
    handler = registry.handlers.get(commandName)

    if not handler:
        update.message.reply_text("Неизвестная команда")
        return

    imageLink = getImage(commandName)
    markup, text = handler(update.message)
    await update.message.reply_photo(photo=imageLink, caption=text, \
                                     reply_markup=markup, parse_mode=ParseMode.HTML)


async def error_handler(update, context):
    tb = ''.join(traceback.format_exception(None, context.error, \
                                            context.error.__traceback__))
    logger.error(f"‼Uncaught exception:\n{tb}")

    if update and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Ошибка:\n<code>{str(context.error)}</code>",
            parse_mode=ParseMode.HTML
        )


def main():

    token = os.getenv('BOT_TOKEN')

    # Создаем приложение
    application = Application.builder().token(token).build()

    # Регистрируем обработчики команд и callback'ов
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("utm", utm))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, \
                                           handle_standard_buttons))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    main()
