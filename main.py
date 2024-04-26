import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from DB import database as db
from const import TOKEN
from info.dialoges import START, WELCOME, MENU, GENERAL, OPTION
from info.connection import Data, Option

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

AGREEMENT_N, WELCOME_N, MENU_N, GENERAL_N = range(4)
DATA = Data()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
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
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="What?", resize_keyboard=True
        ),
    )

    return WELCOME_N


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Общая информация", "Поиск по категориям"]]

    user = update.message.from_user
    logger.info("Agreement %s: %s", user.first_name, update.message.text)

    await update.message.reply_photo(photo=WELCOME["photo"], parse_mode='HTML', )
    await update.message.reply_text(
        WELCOME["info"], parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="What?", resize_keyboard=True
        ),
    )
    return MENU_N


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in DATA.categories]

    user = update.message.from_user
    logger.info("Categories %s: %s", user.first_name, update.message.text)

    user = update.message.from_user
    logger.info("Agreement %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        MENU["info"], parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup.from_column(buttons),
    )

    return MENU_N


async def general(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in GENERAL['buttons']]

    await update.message.reply_text(
        GENERAL["info"], parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup.from_column(buttons),
    )

    return GENERAL_N


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    logger.info("Category / Place %s: %s", user.first_name, query.data)

    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in OPTION['buttons']]
    if query.data in DATA.categories:
        category = query.data
        op = Option(DATA, query.from_user, category)
        text = op.create_message()

        db.update_user(query.from_user.id, categories=f"{DATA.categories_dict[category]} ")

        await query.edit_message_text(text=text, parse_mode='HTML',
                                      reply_markup=InlineKeyboardMarkup.from_column(buttons))

    elif query.data in OPTION["buttons"]:
        if query.data == OPTION["buttons"][2]:

            for obj in Option.list_of_rows:
                if obj.from_user.username != query.from_user.username:
                    continue
                text = obj.create_message()
                await query.edit_message_text(text=text, parse_mode='HTML',
                                              reply_markup=InlineKeyboardMarkup.from_column(buttons))

        elif query.data == OPTION["buttons"][1]:
            for obj in Option.list_of_rows:
                if obj.from_user.username != query.from_user.username:
                    continue
                row = obj.current
                db.update_user(query.from_user.id, likes=f"{row[0]};")

        elif query.data == OPTION["buttons"][0]:
            for obj in Option.list_of_rows:
                if obj.from_user.username != query.from_user.username:
                    continue
                text = obj.create_message(reverse=True)
                await query.edit_message_text(text=text, parse_mode='HTML',
                                              reply_markup=InlineKeyboardMarkup.from_column(buttons))


# async def option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     user = update.message.from_user
#     photo_file = await update.message.photo[-1].get_file()
#     await photo_file.download_to_drive("user_photo.jpg")
#     logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
#     await update.message.reply_text(
#         ""
#     )
#
#     return MENU
#
#
# async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Skips the photo and asks for a location."""
#     user = update.message.from_user
#     logger.info("User %s did not send a photo.", user.first_name)
#     await update.message.reply_text(
#         "I bet you look great! Now, send me your location please, or send /skip."
#     )
#
#     return LOCATION
#
#
#
# async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Stores the location and asks for some info about the user."""
#     user = update.message.from_user
#     user_location = update.message.location
#     logger.info(
#         "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
#     )
#     await update.message.reply_text(
#         "Maybe I can visit you sometime! At last, tell me something about yourself."
#     )
#
#     return BIO
#
#
# async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Skips the location and asks for info about the user."""
#     user = update.message.from_user
#     logger.info("User %s did not send a location.", user.first_name)
#     await update.message.reply_text(
#         "You seem a bit paranoid! At last, tell me something about yourself."
#     )
#
#     return BIO
#
#
# async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Stores the info about the user and ends the conversation."""
#     user = update.message.from_user
#     logger.info("Bio of %s: %s", user.first_name, update.message.text)
#     await update.message.reply_text("Thank you! I hope we can talk again some day.")
#
#     return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WELCOME_N: [MessageHandler(filters.Regex("^(Согласен с условиями пользования)$"), welcome)],
            MENU_N: [MessageHandler(filters.Regex("^(Поиск по категориям)$"), menu)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handle_button))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
