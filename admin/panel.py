from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, Update, \
    InputMediaPhoto
from telegram.ext import ContextTypes
from datetime import datetime

from DB import database as db
from log.logger import logger
from info.connection import DATA
from info.dialoges import WELCOME
from admin.dialoges import REQUEST, ADMIN, REFRESH, NEWS, STATISTICS
from const import PASSWORD, DOTS
from stats.handler import plot_statistics, PERIODS


async def request_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['Отмена']]
    db.update_user(update.message.from_user.id, last_timestamp=datetime.now())
    await update.message.reply_text(
        REQUEST["info"], parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return DOTS["PASSWORD_N"]


async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Общая информация", "Поиск по категориям", "Избранные заведения"]]
    db.update_user(update.message.from_user.id, last_timestamp=datetime.now())
    await update.message.reply_photo(
        WELCOME["photo"], caption=WELCOME["info"], parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return DOTS["OPTION_N"]


async def receive_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text
    if password != PASSWORD:
        keyboard = [["Общая информация", "Поиск по категориям", "Избранные заведения"]]

        await update.message.reply_text("Неверный пароль")
        await update.message.reply_photo(WELCOME["photo"], caption=WELCOME["info"], parse_mode="HTML",
                                         reply_markup=ReplyKeyboardMarkup(
                                             keyboard, one_time_keyboard=True, resize_keyboard=True
                                         ))
        return DOTS["OPTION_N"]

    user = update.message.from_user
    logger.info("Entry admin panel %s", user.first_name)
    db.update_user(update.message.from_user.id, last_timestamp=datetime.now())

    keyboard = [
        ["Обновить карточки заведений", "Получить статистику"],  # Первый ряд с тремя кнопками
        ["В главное меню"]  # Второй ряд с одной кнопкой
    ]

    # Создаем объект ReplyKeyboardMarkup с указанием клавиатуры
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_photo(ADMIN["photo"], caption=f"{user.first_name}, {ADMIN['info']}", parse_mode="HTML",
                                     reply_markup=reply_markup)
    return DOTS["ADMIN_N"]


async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    buttons = [InlineKeyboardButton(text="Вернуться в главное меню", callback_data="Вернуться в главное меню")]
    DATA.refresh()
    await update.message.reply_text(REFRESH["info"], parse_mode="HTML", reply_markup=InlineKeyboardMarkup.from_row(buttons))
    db.update_user(update.message.from_user.id, last_timestamp=datetime.now())
    return DOTS["ADMIN_N"]


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['Отмена']]
    db.update_user(update.message.from_user.id, last_timestamp=datetime.now())
    await update.message.reply_text(NEWS["info"], parse_mode="HTML",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return DOTS["NEWS_N"]


async def publish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    article = update.message.text
    reply_keyboard = [['Отмена', 'Опубликовать']]
    db.update_user(update.message.from_user.id, last_timestamp=datetime.now())
    await update.message.reply_text(f"{article}\n\n{NEWS['reply']}", parse_mode="HTML",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return DOTS["CONFIRM_N"]


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Обновить карточки заведений", "Получить статистику"]]
    db.update_user(update.message.from_user.id, last_timestamp=datetime.now())
    await update.message.reply_text(NEWS["publish"], parse_mode="HTML",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return DOTS["ADMIN_N"]


async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in STATISTICS['buttons']]
    db.update_user(update.message.from_user.id, last_timestamp=datetime.now())
    await update.message.reply_photo(
        photo=STATISTICS["photo"],
        caption=STATISTICS["info"], parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup.from_column(buttons)
    )

    return DOTS["ADMIN_N"]


async def period_statistics(query):
    if query.data == "За всё время":
        start_date = datetime(2024, 4, 25, 0, 0, 0)
    else:
        start_date = datetime.now() - PERIODS[query.data]
    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in STATISTICS['buttons']]
    end_date = datetime.now()
    path = plot_statistics(start_date, end_date, "stats\\graphics")

    db.update_user(query.from_user.id, last_timestamp=datetime.now())

    plot = open(f"{path}\\scatter.png", 'rb')
    bar = open(f"{path}\\bar.png", 'rb')
    bar1 = open(f"{path}\\bar1.png", 'rb')
    await query.message.chat.send_media_group(
        media=[InputMediaPhoto(media=plot), InputMediaPhoto(media=bar), InputMediaPhoto(media=bar1)])
    plot.close()
    bar.close()
    bar1.close()
