from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from info.connection import Option
from info.dialoges import OPTION
from DB import database as db
from stats.handler import TITLES
from asyncio import sleep


def make_keyboard(buttons):
    button_row = [InlineKeyboardButton(buttons[i], callback_data=buttons[i]) for i in range(1, len(buttons))]
    button_full_width = InlineKeyboardButton(buttons[0], callback_data=buttons[0])
    keyboard = [button_row, [button_full_width]]
    return keyboard


async def category_message(query, action):
    for op in Option.list_of_rows:
        if op.from_user.username == query.from_user.username:
            info = op.create_message(action)
            row = op.rows[op.index]
            user = query.from_user
            if action == 3:
                db.update_user(user.id, likes=row[0], last_timestamp=datetime.now())
                db.add_event(user.id, TITLES[3], row[0])
            elif action == 2:
                db.update_user(user.id, likes=row[0], last_timestamp=datetime.now())
                db.add_event(user.id, TITLES[4], row[0])

            user = db.get_user_by_id(query.from_user.id)
            buttons = [item for item in OPTION["buttons"]]
            if not info[2]:
                buttons.remove("Назад")
            if not info[3]:
                buttons.remove("Вперёд")

            if row[0] in user[3].split(";"):
                buttons.remove("В избранные")
            elif row[0] not in user[3].split(";"):
                buttons.remove("Уже в избранных")

            reply_markup = InlineKeyboardMarkup(make_keyboard(buttons))
            if action > 1:
                await query.edit_message_reply_markup(reply_markup=reply_markup)
            else:
                await query.edit_message_media(media=InputMediaPhoto(info[1]))
                await query.edit_message_caption(caption=info[0], parse_mode='HTML',
                                                 reply_markup=reply_markup)
            break

