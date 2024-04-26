from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, Update, \
    InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from log.logger import logger
from DB import database as db
from const import TOKEN, DOTS
from admin.dialoges import STATISTICS
from info.dialoges import START, WELCOME, MENU, GENERAL, OPTION, LIKED
from info.connection import DATA, Option

from admin.panel import receive_password, request_password, refresh, news, publish, confirm, statistics


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation"""
    reply_keyboard = [["Согласен с условиями пользования"]]

    user = update.message.from_user
    db.add_user(user.id, user.username)

    await update.message.reply_text(
        START["greet"], parse_mode='HTML'
    )
    await update.message.reply_photo(photo=START["photo"])
    await update.message.reply_text(
        START["info"], parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )

    return DOTS["WELCOME_N"]


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Общая информация", "Поиск по категориям", "Избранные заведения"]]

    user = update.message.from_user
    logger.info("Agreement %s: %s", user.first_name, update.message.text)

    await update.message.reply_photo(photo=WELCOME["photo"], parse_mode='HTML', )
    await update.message.reply_text(
        WELCOME["info"], parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return DOTS["OPTION_N"]


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in DATA.categories]
    buttons.insert(0, InlineKeyboardButton(text="В главное меню", callback_data="В главное меню"))

    user = update.message.from_user
    logger.info("Categories %s: %s", user.first_name, update.message.text)

    await update.message.reply_photo(
        photo=MENU["photo"],
        caption=MENU["info"], parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup.from_column(buttons),
    )

    return DOTS["OPTION_N"]


async def general(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in GENERAL['buttons']]

    await update.message.reply_photo(
        photo=GENERAL["photo"], caption=GENERAL["info"], parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup.from_column(buttons)
    )
    return DOTS["OPTION_N"]


async def liked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Общая информация", "Поиск по категориям", "Избранные заведения"]]

    bd_user = db.get_user_by_id(update.message.from_user.id)
    likes = " ".join(bd_user[3].split(';'))

    await update.message.reply_text(
        text=f"{LIKED['info']}\n\n{likes}", parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return DOTS["OPTION_N"]


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    logger.info("Category / Place %s: %s", user.first_name, query.data)

    if query.data in DATA.categories:
        buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in OPTION['buttons']]
        category = query.data
        op = Option(DATA, query.from_user, category)
        info = op.create_message()

        db.update_user(query.from_user.id, categories=f"{DATA.categories_dict[category]} ")

        await query.edit_message_media(media=InputMediaPhoto(info[1]))
        await query.edit_message_caption(caption=info[0], parse_mode='HTML',
                                         reply_markup=InlineKeyboardMarkup.from_column(buttons))

    elif query.data in OPTION["buttons"]:
        if query.data == OPTION["buttons"][3]:
            for op in Option.list_of_rows:
                if op.from_user.username != query.from_user.username:
                    continue
                info = op.create_message()
                buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in OPTION['buttons']]

                await query.edit_message_media(media=InputMediaPhoto(info[1]))
                await query.edit_message_caption(caption=info[0], parse_mode='HTML',
                                                 reply_markup=InlineKeyboardMarkup.from_column(buttons))

        elif query.data == OPTION["buttons"][2]:
            for op in Option.list_of_rows:
                if op.from_user.username == query.from_user.username:
                    row = op.current
                    db.update_user(query.from_user.id, likes=f"{row[0]};")
                    break

        elif query.data == OPTION["buttons"][1]:
            for op in Option.list_of_rows:
                if op.from_user.username == query.from_user.username:
                    info = op.create_message(reverse=True)
                    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in OPTION['buttons']]

                    await query.edit_message_media(media=InputMediaPhoto(media=info[1]))
                    await query.edit_message_caption(caption=info[0], parse_mode='HTML',
                                                     reply_markup=InlineKeyboardMarkup.from_column(buttons))
                    break

        elif query.data == OPTION["buttons"][0]:
            for op in Option.list_of_rows:
                if op.from_user.username == query.from_user.username:
                    Option.list_of_rows.remove(op)
                    break

            reply_keyboard = [["Общая информация", "Поиск по категориям", "Избранные заведения"]]

            user = query.from_user
            logger.info("Agreement %s: %s", user.first_name, query.data)

            await query.delete_message()
            await query.message.chat.send_photo(photo=WELCOME["photo"], caption=WELCOME["info"], parse_mode='HTML',
                                                reply_markup=ReplyKeyboardMarkup(
                                                    reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                                                ))

    elif query.data == "Где можно воспользоваться картой?":
        buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in DATA.categories]
        buttons.insert(0, InlineKeyboardButton(text="В главное меню", callback_data="В главное меню"))

        user = query.from_user
        logger.info("Categories %s: %s", user.first_name, query.data)

        await query.edit_message_media(media=InputMediaPhoto(media=MENU["photo"]))
        await query.edit_message_caption(
            caption=MENU["info"], parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup.from_column(buttons),
        )

        return DOTS["OPTION_N"]

    elif query.data in STATISTICS['buttons']:
        if query.data == STATISTICS['buttons'][0]:
            pass
        elif query.data == STATISTICS['buttons'][1]:
            pass
        elif query.data == STATISTICS['buttons'][2]:
            pass
        elif query.data == STATISTICS['buttons'][3]:
            pass
        elif query.data == STATISTICS['buttons'][4]:
            pass


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    reply_keyboard = [["Общая информация", "Поиск по категориям", "Избранные заведения"]]

    user = query.from_user
    logger.info("Back %s: %s", user.first_name, query.data)

    await query.message.chat.send_photo(photo=WELCOME["photo"], parse_mode='HTML', caption=WELCOME["info"],
                                        reply_markup=ReplyKeyboardMarkup(
                                            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                                        ))
    return DOTS["OPTION_N"]


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "До свидания!", reply_markup=ReplyKeyboardRemove()
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
            DOTS["PASSWORD_N"]: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_password)],
            DOTS["ADMIN_N"]: [MessageHandler(filters.Regex("^(Обновить карточки заведений)$"), refresh),
                              MessageHandler(filters.Regex("^(Написать новость)$"), news),
                              MessageHandler(filters.Regex("^(Получить статистику)$"), statistics)],
            DOTS["NEWS_N"]: [MessageHandler(filters.TEXT & ~filters.COMMAND, publish)],
            DOTS["CONFIRM_N"]: [MessageHandler(filters.Regex("^(Опубликовать)$"), confirm),
                                MessageHandler(filters.Regex("^(Отмена)$"), request_password)],
            DOTS["STATISTICS_N"]: []
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handle_button))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
