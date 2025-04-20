import os
import logging
import traceback
import datetime

from telegram import Update, ReplyKeyboardMarkup,  \
    InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, \
    CommandHandler, ContextTypes, MessageHandler, filters, \
        ConversationHandler


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

from threading import Thread
from src.arena_matchmaker import run_arena_matchmaking
import asyncio

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
        if len(context.args):
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


async def get_utm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_id = update.message.from_user.id

    if (player_id not in config["admins"]["admins_array"]):
        await update.message.reply_text("Неизвестная команда")
        return
    
    db = SessionLocal()
    try:
        text = update.message.text
        tag = text[len("/get_utm "):].strip()

        service = UtmService(db)
        used_count = service.get_utm_used_count(tag=tag)
        if used_count == None:
                await update.message.reply_text(f"Метка <code>{tag}</code> еще не создана", \
                                        parse_mode=ParseMode.HTML)
                return

        if not tag:
            raise ValueError("Не задано название метки UTM")

        await update.message.reply_text(f"Количество регистраций в боте по метке:\n<code>{used_count}</code>", \
                                        parse_mode=ParseMode.HTML)

    except Exception as e:
        await update.message.reply_text(f"Ошибка:\n<code>{str(e)}</code>", \
                                        parse_mode=ParseMode.HTML)
        print(e)
        return
    finally:
        db.close()


async def get_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_id = update.message.from_user.id

    if (player_id not in config["admins"]["admins_array"]):
        await update.message.reply_text("Неизвестная команда")
        return
    
    db = SessionLocal()
    try:
        text = update.message.text
        interval = text[len("/get_users "):].strip()

        if not interval:
            raise ValueError("Не указан интервал времени (all/year/month/week/day)")

        match interval:
            case 'all':
                # For 'all', we'll use a very large interval
                delta = datetime.timedelta(days=36500)  # 100 years
                message = "Общее количество пользователей"
            case 'year':
                delta = datetime.timedelta(days=365)
                message = "Количество пользователей за год"
            case 'month':
                delta = datetime.timedelta(days=30)
                message = "Количество пользователей за месяц"
            case 'week':
                delta = datetime.timedelta(weeks=1)
                message = "Количество пользователей за неделю"
            case 'day':
                delta = datetime.timedelta(days=1)
                message = "Количество пользователей за день"
            case _:
                raise ValueError("Неверный интервал. Используйте: all/year/month/week/day")

        service = PlayerService(db=db)
        used_count = service.get_new_users_count(interval=delta)

        await update.message.reply_text(f"Количество регистраций:\n<code>{used_count}</code>", \
                                        parse_mode=ParseMode.HTML)

    except Exception as e:
        await update.message.reply_text(f"Ошибка:\n<code>{str(e)}</code>", \
                                        parse_mode=ParseMode.HTML)
        print(e)
        return
    finally:
        db.close()

async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_id = update.message.from_user.id
    
    if (player_id not in config["admins"]["admins_array"]):
        await update.message.reply_text("Неизвестная команда")
        return
    
    text = update.message.text
    message = text[len("/get_user_info "):].strip()

    if not message:
        raise ValueError("Не указан игрок")
    
    db = SessionLocal()
    try:
        service = PlayerService(db=db)
        # players = service.

    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка при рассылке:\n<code>{str(e)}</code>",
            parse_mode=ParseMode.HTML
        )
        logger.error(f"Broadcast error: {str(e)}")
    finally:
        db.close()

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_id = update.message.from_user.id
    
    if (player_id not in config["admins"]["admins_array"]):
        await update.message.reply_text("Неизвестная команда")
        return
    
    text = update.message.text
    message = text[len("/broadcast "):].strip()

    if not message:
        raise ValueError("Не указано сообщение")

    db = SessionLocal()
    try:
        service = PlayerService(db=db)
        players = service.get_all()
        
        success_count = 0
        error_count = 0
        
        await update.message.reply_text("📤 Отправка сообщений...")
        
        for player in players:
            try:
                await context.bot.send_message(
                    chat_id=player.id,
                    text=message,
                    parse_mode=ParseMode.HTML
                )
                success_count += 1
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to send message to user {player.id}: {str(e)}")
        

        summary = f"""Рассылка завершена:
✅ Успешно отправлено: <code>{success_count}</code>
❌ Ошибок отправки: <code>{error_count}</code>
📝 Текст сообщения:
<code>{message}</code>"""
        
        await update.message.reply_text(summary, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка при рассылке:\n<code>{str(e)}</code>",
            parse_mode=ParseMode.HTML
        )
        logger.error(f"Broadcast error: {str(e)}")
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

    await query.edit_message_caption(
        caption=text, 
        reply_markup=markup, 
        parse_mode=ParseMode.HTML)


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

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("utm", utm))
    application.add_handler(CommandHandler("get_utm", get_utm))
    application.add_handler(CommandHandler("get_users", get_users))
    # application.add_handler(broadcast_handler)
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, \
                                           handle_standard_buttons))
    # application.add_handler(CallbackQueryHandler(broadcast_button))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    # Запуск фонового потока поиска боёв
    asyncio.get_event_loop().create_task(run_arena_matchmaking())
    main()
