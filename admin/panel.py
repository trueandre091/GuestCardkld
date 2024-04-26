from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from log.logger import logger
from info.connection import DATA
from admin.dialoges import REQUEST, ADMIN, REFRESH, NEWS, STATISTICS
from const import PASSWORD, DOTS


async def request_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['Отмена']]
    await update.message.reply_text(
        REQUEST["info"], parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return DOTS["PASSWORD_N"]


async def receive_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text
    if password != PASSWORD:
        reply_keyboard = [["Общая информация", "Поиск по категориям", "Избранные заведения"]]

        await update.message.reply_text("Неверный пароль", parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ))
        return DOTS["WELCOME_N"]

    user = update.message.from_user
    logger.info("Entry admin panel %s", user.first_name)

    reply_keyboard = [["Обновить карточки заведений", "Написать новость", "Получить статистику"]]
    await update.message.reply_text(f"{user.first_name}, {ADMIN['info']}", parse_mode="HTML",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return DOTS["ADMIN_N"]


async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    DATA.refresh()
    await update.message.reply_text(REFRESH["info"], parse_mode="HTML")
    return DOTS["ADMIN_N"]


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['Отмена']]
    await update.message.reply_text(NEWS["info"], parse_mode="HTML",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return DOTS["NEWS_N"]


async def publish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    article = update.message.text
    reply_keyboard = [['Отмена', 'Опубликовать']]
    await update.message.reply_text(f"{article}\n\n{NEWS["reply"]}", parse_mode="HTML",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return DOTS["CONFIRM_N"]


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Обновить карточки заведений", "Написать новость", "Получить статистику"]]
    await update.message.reply_text(NEWS["publish"], parse_mode="HTML",
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return DOTS["ADMIN_N"]


async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['Отмена']]
    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in STATISTICS['buttons']]

    await update.message.reply_photo(
        photo=STATISTICS["photo"],
        caption=STATISTICS["info"], parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup.from_column(buttons)
    )

    return DOTS["STATISTICS_N"]


async def graphics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['Отмена']]
