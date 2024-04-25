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

from const import TOKEN
from info.text import START, MAIN


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

AGREEMENT, MENU, OPTION = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [["Согласен с условиями пользования"]]

    await update.message.reply_text(
        START["greet"],
    )
    await update.message.reply_photo(photo=START["photo"])
    await update.message.reply_text(
        START["info"],
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="What?", resize_keyboard=True
        ),
    )

    return MENU


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stores the selected gender and asks for a photo."""
    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in MAIN['buttons']]

    user = update.message.from_user
    logger.info("Agreement %s: %s", user.first_name, update.message.text)
    await update.message.reply_photo(photo=MAIN["photo"])
    await update.message.reply_text(
        MAIN["info"],
        reply_markup=InlineKeyboardMarkup.from_column(buttons),
    )

    return MENU


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")


async def option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("user_photo.jpg")
    logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
    await update.message.reply_text(
        ""
    )

    return MENU


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
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    buttons = "|".join(MAIN['buttons'])
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [MessageHandler(filters.Regex("^(Согласен с условиями пользования)$"), menu)],
            OPTION: [MessageHandler(filters.Regex(f"^({buttons})$"), option)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handle_button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()