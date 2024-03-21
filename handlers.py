from telebot import types
from sqlalchemy import exc
from bot import BOT as bot
from database import DBManager, ENGINE


manager = DBManager(engine=ENGINE)


@bot.message_handler(commands=["start"])
def start(message: types.Message, edit_message = False):
    markup = types.InlineKeyboardMarkup(row_width=1)
    if edit_message:
        reg_user = manager.reg_user(user_id=message.chat.id).fetchall()
    else:
        reg_user = manager.reg_user(user_id=message.from_user.id).fetchall()
    try:
        reg_user[0]
        text = f"{message.chat.username} choose button!"
        buttons = [
            types.InlineKeyboardButton(text="Create a new note", callback_data="create_note"),
            types.InlineKeyboardButton(text="Show my notes", callback_data="show_notes")
        ]
        markup.add(*buttons)
    except:
        text = f"Hello, {message.chat.username}!\nFor start you need to register"
        buttons = [
            types.InlineKeyboardButton(text="Join", callback_data="register"),
        ]
        markup.add(*buttons)
    if edit_message:
        bot.edit_message_text(text=text, chat_id=message.chat.id, message_id=message.id, reply_markup=markup)
    else:
        bot.send_message(text=text, reply_markup=markup, chat_id=message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "register")
def start_registration(call: types.CallbackQuery):
    text = f"Please, write your email and your phone\nExample:\nexample@gmail.com\n+996(550)33-66-99\n\nWrite the datas on different lines!"
    markup = types.InlineKeyboardMarkup(row_width=1)
    button = types.InlineKeyboardButton(text="Back to main menu", callback_data="back://main")
    markup.add(button)
    message = bot.edit_message_text(chat_id=call.message.chat.id, text=text, reply_markup=markup, message_id=call.message.id)
    bot.register_next_step_handler(message=message, callback=register)


def register(message: types.Message):
    data = {}
    data['id'] = str(message.from_user.id)
    data['username'] = message.from_user.username
    data['first_name'] = message.from_user.first_name
    data['last_name'] = message.from_user.last_name
    try:
        message_data = message.text.split("\n")
        data['email'] = message_data[0].strip()
        data['phone_number'] = message_data[1].strip()
        data = {key: f'"{value}"' for key, value in data.items() if value is not None}
        manager.insert_user(data=data)
    except IndexError:
        bot.send_message(chat_id=message.chat.id, text="You have a mistake in the formation of the note!")
    except exc.IntegrityError:
        bot.send_message(chat_id=message.chat.id, text="You already registered or that email is already using!")
    else:
        print(data)
        bot.send_message(chat_id=message.chat.id, text="You have registered!")


@bot.callback_query_handler(func=lambda call: call.data == "create_note")
def create_note(call: types.CallbackQuery):
    text = "Write your new note\nExample:\n\nDo my chores\nI need to finish my chores at home today\n\n\nWrite the datas on different lines!"
    markup = types.InlineKeyboardMarkup(row_width=1)
    button = types.InlineKeyboardButton(text = "Back to main menu", callback_data = "back://main")
    markup.add(button)
    message = bot.edit_message_text(chat_id=call.message.chat.id, text=text, message_id=call.message.id, reply_markup=markup)
    bot.register_next_step_handler(message=message, callback=create_new_note)


def create_new_note(message: types.Message):
    data = {}
    try:
        data['user_id'] = message.from_user.id
        call_data = message.text.split("\n")
        data['name'] = call_data[0].strip()
        data['note'] = call_data[1].strip()
        data = {key: f'"{value}"' for key, value in data.items() if value is not None}
        manager.insert_new_note(data=data)
    except IndexError:
        bot.send_message(chat_id=message.chat.id, text="You have a mistake in the formation of the note!")
    else:
        print(data)
        bot.send_message(chat_id=message.chat.id, text="You created your new note")


@bot.callback_query_handler(func=lambda call: call.data == "show_notes")
def show_notes(call: types.CallbackQuery):
    text = "Choose your notes!"
    markup = types.InlineKeyboardMarkup(row_width=1)
    datas = manager.select_datas("id", "name").fetchall()
    for data in datas:
        button = types.InlineKeyboardButton(text = data[1], callback_data=f"data://{data[0]}")
        markup.add(button)
    back_button = types.InlineKeyboardButton(text="Back to main menu", callback_data="back://main")
    markup.add(back_button)
    bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("data://"))
def show_note(call: types.CallbackQuery):
    data_id = call.data.replace("data://", "")
    data = manager.select_data(data_id=data_id).fetchone()
    if data[4] == 0:
        l_data = "The note wasn't completed"
    text = f"""
    Your note:\n
    {data[2]} - {l_data}
    {data[3]}\n\n\nDid you complete your note?
    """
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text="Yes", callback_data=f"answer_yes_data://{data[0]}"),
        types.InlineKeyboardButton(text="No", callback_data="back://notes")
    ]
    markup.add(*buttons)
    bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup)


@bot.callback_query_handler(func = lambda call: call.data.startswith("answer_yes_data://"))
def call_yes(call: types.CallbackQuery):
    data_id = call.data.replace("answer_yes_data://", "")
    manager.delate_data(data_id=data_id)
    text = "Your note was deleted"
    markup = types.InlineKeyboardMarkup(row_width=1)
    button = types.InlineKeyboardButton(text="Back to notes", callback_data="back://notes")
    markup.add(button)
    bot.edit_message_text(text=text, reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("back://"))
def back_to(call: types.CallbackQuery):
    if call.data.endswith("main"):
        start(message=call.message, edit_message = True)
    elif call.data.endswith("notes"):
        show_notes(call=call)


__all__ = (
    "start",
    "start_registration",
    "register",
    "create_note",
    "create_new_note",
    "show_notes",
    "show_note",
    "call_yes",
    "back_to",
    "manager"
)