from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
    InputMediaPhoto
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from datetime import datetime, date

from info.patterns import make_keyboard, category_message
from log.logger import logger
from DB import database as db
from const import TOKEN, DOTS
from admin.dialoges import STATISTICS, ADMIN
from info.dialoges import START, WELCOME, MENU, GENERAL, OPTION, LIKED
from info.connection import DATA, Option
from stats.handler import TITLES, PERIODS, plot_statistics
from admin.panel import receive_password, admin_cancel, request_password, refresh, news, publish, confirm, statistics, \
    period_statistics


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation"""
    reply_keyboard = [["Согласен с условиями пользования"]]

    user = update.message.from_user
    db.add_user(user.id, user.username)
    db.add_event(user.id, TITLES[0])

    await update.message.reply_text(
        START["greet"], parse_mode='HTML'
    )
    await update.effective_chat.send_photo(photo=START["photo"], caption=START["info"], parse_mode='HTML',
                                           reply_markup=ReplyKeyboardMarkup(
                                               reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                                           ))

    return DOTS["WELCOME_N"]


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Общая информация", "Поиск по категориям", "Избранные заведения"]]

    user = update.message.from_user
    logger.info("Agreement %s: %s", user.first_name, update.message.text)
    db.update_user(update.message.from_user.id, last_timestamp=datetime.now())

    await update.effective_chat.send_photo(photo=WELCOME["photo"], parse_mode='HTML', caption=WELCOME["info"],
                                           reply_markup=ReplyKeyboardMarkup(
                                               reply_keyboard, resize_keyboard=True
                                           ))

    return DOTS["OPTION_N"]


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = {v: k for k, v in DATA.categories_dict.items()}
    keyboard = []
    for i in range(1, len(DATA.categories) + 1):
        if (i - 1) % 3 == 0:
            keyboard.append([InlineKeyboardButton(text=categories[str(i)], callback_data=categories[str(i)])])
        else:
            keyboard[-1].append(InlineKeyboardButton(text=categories[str(i)], callback_data=categories[str(i)]))
    keyboard.append([InlineKeyboardButton(text="В главное меню", callback_data="В главное меню")])

    db.update_user(update.effective_user.id, last_timestamp=datetime.now())

    user = update.effective_user
    logger.info("Categories %s: %s", user.first_name, update.message.text if update.message is not None else None)

    await update.effective_chat.send_photo(photo=MENU["photo"], caption=MENU["info"],
                                           parse_mode='HTML',
                                           reply_markup=InlineKeyboardMarkup(keyboard))

    return DOTS["OPTION_N"]


async def general(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in GENERAL['buttons']]
    db.update_user(update.message.from_user.id, last_timestamp=datetime.now())

    await update.effective_chat.send_photo(
        photo=GENERAL["photo"], caption=GENERAL["info"], parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup.from_column(buttons)
    )

    return DOTS["OPTION_N"]


async def liked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bd_user = db.get_user_by_id(update.message.from_user.id)
    if not bd_user[3]:
        buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in GENERAL["buttons"]]
        await update.message.reply_text(
            text=f"{LIKED['nothing']}", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup.from_row(buttons)
        )
        return DOTS["OPTION_N"]

    db.update_user(update.message.from_user.id, last_timestamp=datetime.now())

    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in LIKED['buttons']]
    likes = "\n".join(bd_user[3].split(';'))
    await update.effective_chat.send_message(
        text=f"{LIKED['info']}\n\n{likes}", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup.from_row(buttons)
    )

    return DOTS["OPTION_N"]


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    logger.info("Category / Place %s: %s", user.first_name, query.data)

    if query.data in DATA.categories:
        category = query.data
        db.add_event(query.from_user.id, TITLES[1], DATA.categories_dict[category])
        db.update_user(query.from_user.id, last_timestamp=datetime.now())

        op = Option(DATA, query.from_user, category)
        Option.list_of_rows.append(op)
        await category_message(query, False)

    elif query.data == "В главное меню":
        for op in Option.list_of_rows:
            if op.from_user.username == query.from_user.username:
                Option.list_of_rows.remove(op)
                break
        reply_keyboard = [["Общая информация", "Поиск по категориям", "Избранные заведения"]]

        db.update_user(query.from_user.id, last_timestamp=datetime.now())
        logger.info("Main menu %s: %s", user.first_name, query.data)

        await query.delete_message()
        await query.message.chat.send_photo(photo=WELCOME["photo"], caption=WELCOME["info"], parse_mode='HTML',
                                            reply_markup=ReplyKeyboardMarkup(
                                                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                                            ))

    elif query.data in OPTION["buttons"]:
        if query.data == OPTION["buttons"][2]:
            await category_message(query, 2)

        if query.data == OPTION["buttons"][3]:
            await category_message(query, 3)

        elif query.data == OPTION["buttons"][-1]:
            db.update_user(query.from_user.id, last_timestamp=datetime.now())
            await category_message(query, 0)

        elif query.data == OPTION["buttons"][1]:
            db.update_user(query.from_user.id, last_timestamp=datetime.now())
            await category_message(query, 1)

    elif query.data in GENERAL["buttons"]:
        await query.delete_message()
        await menu(update, context)

    elif query.data in LIKED["buttons"]:
        if query.data == LIKED["buttons"][0]:
            buttons = [InlineKeyboardButton(text="В главное меню", callback_data="В главное меню")]
            db.reset_likes(query.from_user.id)
            db.add_event(user.id, TITLES[3], ";".join(query.message.text.split("\n\n")[-1].split("\n")))
            logger.info("Reset likes %s", user.first_name)
            db.update_user(query.from_user.id, last_timestamp=datetime.now())

            await query.edit_message_text(LIKED["reset"], parse_mode='HTML',
                                          reply_markup=InlineKeyboardMarkup.from_row(buttons))

    elif query.data in STATISTICS['buttons'][:-1]:
        await period_statistics(query)

    elif query.data == STATISTICS['buttons'][-1]:
        db.update_user(query.from_user.id, last_timestamp=datetime.now())
        keyboard = [["Обновить карточки заведений", "Получить статистику"], ["В главное меню"]]
        await query.delete_message()
        await query.message.chat.send_photo(ADMIN["photo"], caption=f"{user.first_name}, {ADMIN['info']}",
                                            parse_mode="HTML",
                                            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                             resize_keyboard=True))


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    db.add_event(user.id, TITLES[4])
    db.update_user(update.message.from_user.id, last_timestamp=datetime.now())

    await update.message.reply_text(
        "До свидания, приезжайте снова!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), ],
        states={
            DOTS["WELCOME_N"]: [MessageHandler(filters.Regex("^(Согласен с условиями пользования)$"), welcome)],
            DOTS["OPTION_N"]: [MessageHandler(filters.Regex("^(Поиск по категориям)$"), menu),
                               MessageHandler(filters.Regex("^(Общая информация)$"), general),
                               MessageHandler(filters.Regex("^(Избранные заведения)$"), liked),
                               CommandHandler("admin", request_password)],
            DOTS["PASSWORD_N"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(Отмена)$"), receive_password),
                MessageHandler(filters.Regex("^(Отмена)$"), admin_cancel)],
            DOTS["ADMIN_N"]: [MessageHandler(filters.Regex("^(Обновить карточки заведений)$"), refresh),
                              MessageHandler(filters.Regex("^(Написать новость)$"), news),
                              MessageHandler(filters.Regex("^(Получить статистику)$"), statistics),
                              MessageHandler(filters.Regex("^(В главное меню)$"), welcome)],
            DOTS["NEWS_N"]: [MessageHandler(filters.TEXT & ~filters.COMMAND, publish)],
            DOTS["CONFIRM_N"]: [MessageHandler(filters.Regex("^(Опубликовать)$"), confirm),
                                MessageHandler(filters.Regex("^(Отмена)$"), request_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handle_button))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
