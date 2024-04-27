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
from datetime import datetime, date

from log.logger import logger
from DB import database as db
from const import TOKEN, DOTS
from admin.dialoges import STATISTICS, ADMIN
from info.dialoges import START, WELCOME, MENU, GENERAL, OPTION, LIKED
from info.connection import DATA, Option
from stats.handler import TITLES, PERIODS, plot_statistics

from admin.panel import receive_password, admin_cancel, request_password, refresh, news, publish, confirm, statistics


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation"""
    reply_keyboard = [["Согласен с условиями пользования"]]

    user = update.message.from_user
    db.add_user(user.id, user.username)
    db.add_event(user.id, TITLES[0])

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
    bd_user = db.get_user_by_id(update.message.from_user.id)
    if not bd_user[3]:
        buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in GENERAL["buttons"]]
        await update.message.reply_text(
            text=f"{LIKED['nothing']}", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup.from_row(buttons)
        )
        return DOTS["OPTION_N"]

    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in LIKED['buttons']]
    likes = "\n".join(bd_user[3].split(';'))
    await update.message.reply_text(
        text=f"{LIKED['info']}\n\n{likes}", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup.from_row(buttons)
    )
    return DOTS["OPTION_N"]


def make_keyboard(buttons):
    button_full_width = InlineKeyboardButton(buttons[0], callback_data=buttons[0])
    button_1 = InlineKeyboardButton(buttons[1], callback_data=buttons[1])
    button_2 = InlineKeyboardButton(buttons[2], callback_data=buttons[2])
    button_3 = InlineKeyboardButton(buttons[3], callback_data=buttons[3])

    return [
        [button_full_width],  # Первая кнопка во всю ширину
        [button_1, button_2, button_3]  # Следующие три кнопки в одном ряду
    ]


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    logger.info("Category / Place %s: %s", user.first_name, query.data)

    if query.data in DATA.categories:
        reply_markup = InlineKeyboardMarkup(make_keyboard(OPTION["buttons"]))
        category = query.data
        op = Option(DATA, query.from_user, category)
        info = op.create_message()

        db.add_event(query.from_user.id, TITLES[1], DATA.categories_dict[category])
        if info[2]:
            await query.edit_message_media(media=InputMediaPhoto(info[1]))
            await query.edit_message_caption(caption=info[0], parse_mode='HTML',
                                             reply_markup=reply_markup)

    elif query.data == "В главное меню":
        for op in Option.list_of_rows:
            if op.from_user.username == query.from_user.username:
                Option.list_of_rows.remove(op)
                break
        reply_keyboard = [["Общая информация", "Поиск по категориям", "Избранные заведения"]]

        logger.info("Agreement %s: %s", user.first_name, query.data)

        await query.delete_message()
        await query.message.chat.send_photo(photo=WELCOME["photo"], caption=WELCOME["info"], parse_mode='HTML',
                                            reply_markup=ReplyKeyboardMarkup(
                                                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                                            ))

    elif query.data in OPTION["buttons"]:
        if query.data == OPTION["buttons"][3]:
            for op in Option.list_of_rows:
                if op.from_user.username == query.from_user.username:
                    info = op.create_message()
                    reply_markup = InlineKeyboardMarkup(make_keyboard(OPTION["buttons"]))

                    if info[2]:
                        await query.edit_message_media(media=InputMediaPhoto(info[1]))
                        await query.edit_message_caption(caption=info[0], parse_mode='HTML',
                                                         reply_markup=reply_markup)

        elif query.data == OPTION["buttons"][2]:
            for op in Option.list_of_rows:
                if op.from_user.username == query.from_user.username:
                    row = op.current
                    db.update_user(query.from_user.id, likes=row[0])
                    db.add_event(user.id, TITLES[2], row[0])
                    break

        elif query.data == OPTION["buttons"][1]:
            for op in Option.list_of_rows:
                if op.from_user.username == query.from_user.username:
                    info = op.create_message(reverse=True)
                    reply_markup = InlineKeyboardMarkup(make_keyboard(OPTION["buttons"]))

                    if info[2]:
                        await query.edit_message_media(media=InputMediaPhoto(media=info[1]))
                        await query.edit_message_caption(caption=info[0], parse_mode='HTML',
                                                         reply_markup=reply_markup)
                    break

    elif query.data in GENERAL["buttons"]:
        buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in DATA.categories]
        buttons.insert(0, InlineKeyboardButton(text="В главное меню", callback_data="В главное меню"))

        logger.info("Categories %s: %s", user.first_name, query.data)

        if query.message.photo:
            await query.edit_message_media(media=InputMediaPhoto(media=MENU["photo"]))
            await query.edit_message_caption(
                caption=MENU["info"], parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup.from_column(buttons),
            )
        else:
            await query.delete_message()
            await query.message.chat.send_photo(photo=MENU["photo"], caption=MENU["info"], parse_mode='HTML',
                                                reply_markup=InlineKeyboardMarkup.from_column(buttons))

        return DOTS["OPTION_N"]

    elif query.data in LIKED["buttons"]:
        if query.data == LIKED["buttons"][0]:
            db.reset_likes(query.from_user.id)
            db.add_event(user.id, TITLES[3], ";".join(query.message.text.split("\n\n")[-1].split("\n")))
            logger.info("Reset likes %s", user.first_name)

            await query.edit_message_text(LIKED["reset"], parse_mode='HTML', reply_markup=InlineKeyboardMarkup([]))

    elif query.data in STATISTICS['buttons'][:-1]:
        if query.data == "Всё время":
            start_date = date(2024, 4, 25)
        else:
            start_date = datetime.now() - PERIODS[query.data]
        buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in STATISTICS['buttons']]
        end_date = datetime.now()
        path = plot_statistics(start_date, end_date, "stats\\graphics")

        plot = open(f"{path}\\scatter.png", 'rb')
        bar = open(f"{path}\\bar.png", 'rb')
        bar1 = open(f"{path}\\bar1.png", 'rb')
        await query.message.chat.send_media_group(
            media=[InputMediaPhoto(media=plot), InputMediaPhoto(media=bar), InputMediaPhoto(media=bar1)])
        plot.close()
        bar.close()
        bar1.close()

    elif query.data == STATISTICS['buttons'][-1]:
        print(1)
        reply_keyboard = [["Обновить карточки заведений", "Написать новость", "Получить статистику"]]
        await update.message.reply_photo(ADMIN["photo"], caption=f"{user.first_name}, {ADMIN['info']}",
                                         parse_mode="HTML",
                                         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                          resize_keyboard=True))


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    db.add_event(user.id, TITLES[4])

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
                              MessageHandler(filters.Regex("^(Получить статистику)$"), statistics)],
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
