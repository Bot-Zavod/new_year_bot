""" basic command and error handlers """
import html
import json
import os
import sys
import traceback

from loguru import logger
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from .gsheets import get_greeting
from .gsheets import get_available_nums
from .gsheets import sheets_get_gift
from .gsheets import mark_used_gift

# from ..db_functions import Action
from ..data import start_keyboard
from ..data import text
from ..db_functions import db_session
from ..states import States

ADMIN_IDS = db_session.get_admins()


def start_markup() -> ReplyKeyboardMarkup:
    """ markup for start keyboard """
    markup = ReplyKeyboardMarkup(
        keyboard=start_keyboard, resize_keyboard=True, selective=True
    )
    return markup


def start_init(update: Update, context: CallbackContext):
    """ start command an msg """
    logger.info("start init")

    chat = update.message.chat

    chat_id = update.message.chat.id

    # if db_session.user_is_registered(chat_id=chat_id):
    #     return start(update, context)

    db_session.add_user(chat=chat)

    user = db_session.get_user_data(chat_id)

    reply_keyboard = [["🦄"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id,
        text=text["start_init"],
        reply_markup=markup,
    )

    return States.INTRO

def intro(update: Update, context: CallbackContext):
    """ intro """
    
    chat_id = update.message.chat.id

    reply_keyboard = [["✨"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)

    context.bot.send_message(
        chat_id=chat_id,
        text=text["intro"],
        reply_markup=markup,
    )
    
    if update.message.chat.username == None:
        context.bot.send_message(
            chat_id=chat_id,
            text=text["ask_username"],
            reply_markup=start_markup(),
        )
        return States.ASK_USERNAME
    else:
        return States.GREETINGS


def check_username(update: Update, context: CallbackContext):
    """ checks if username exists """
    chat_id = update.message.chat.id
    mssg = update.message.text

    username = mssg.replace("@", "")


def greetings(update: Update, context: CallbackContext):
    """ greets a user individually """
    chat_id = update.message.chat.id
    user = db_session.get_user_data(chat_id)
    
    greeting = get_greeting(user.username)

    reply_keyboard = [
        ["А я всё лично скажу"],
        ["Давай скорее подарки"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)
    
    if greeting != None:
        context.bot.send_message(
            chat_id=chat_id,
            text=greeting,
            reply_markup=markup,
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text="Извините, но Вы не в списке(",
            reply_markup=markup,
        )
        return stop(update, context)
    return States.ASK_GIFT


def ask_gift(update: Update, context: CallbackContext):
    """ pass """
    chat_id = update.message.chat.id
    username = update.message.chat.username

    available_nums = get_available_nums(username)
    av_nums_text = "Доступные числа: "
    for ii in range(len(available_nums)):
        av_nums_text += str(available_nums[ii])
        if ii != len(available_nums)-1:
            av_nums_text += ", "

    is_more_30_days = db_session.check_last_time_gift(chat_id)
    if is_more_30_days == True:
        context.bot.send_message(
            chat_id=chat_id,
            text=f"А теперь — любая цифра от 1 до 12! Что же там?\n{av_nums_text}",
            reply_markup=ReplyKeyboardRemove(),
        )
        return States.GET_GIFT
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Вы уже получали подарок за последние 30 дней)",
        )
        return start(update, context)

def get_gift(update: Update, context: CallbackContext):
    """ pass """
    chat_id = update.message.chat.id
    username = update.message.chat.username
    mssg = update.message.text
    user = db_session.get_user_data(chat_id)

    available_nums = get_available_nums(username)
    print(available_nums)
    if int(mssg) in available_nums:
        context.bot.send_message(
            chat_id=chat_id,
            text="Получаем Ваш подарок...",
            reply_markup=ReplyKeyboardRemove(),
        )
        gift = sheets_get_gift(username, int(mssg))
        mark_used_gift(username, int(mssg))
        db_session.update_last_time_gift(chat_id)

        reply_keyboard = [["Кайф, жду новостей!"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Поздравляем🎉\nВаш подарок:\n{gift}",
            reply_markup=markup,
        )

        for admin in ADMIN_IDS:
            context.bot.send_message(
                chat_id=admin,
                text=f"Пользователь {user.full_name} с юзернеймом @{user.username} получил такой подарок под номером {mssg}:\n{gift}",
                reply_markup=markup,
            )
        return States.GET_GIFT_APPROVE
    else:
        av_nums_text = "Доступные числа: "
        for ii in range(len(available_nums)):
            av_nums_text += str(available_nums[ii])
            if ii != len(available_nums)-1:
                av_nums_text += ", "
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Выберите один из этих вариантов: {av_nums_text}",
            reply_markup=ReplyKeyboardRemove(),
        )
        return States.GET_GIFT


def start(update: Update, context: CallbackContext):
    """ start command an msg """
    logger.info("main menu")

    chat_id = update.message.chat.id

    reply_keyboard = [
        [text["get_gift"]],
        [text["bot_faq"]],
        [text["connect_admin"]]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)
    context.bot.send_message(
        chat_id=chat_id,
        text="Главное меню:",
        reply_markup=markup,
    )

    return States.MENU


def stop(update: Update, context: CallbackContext):
    """ stops conversation handler """
    logger.info("stop command")

    chat_id = update.message.chat.id
    stop_text = text["reload"]
    if update.message.chat.type != Chat.PRIVATE:
        stop_text += "@" + context.bot.username
    context.bot.send_message(
        chat_id=chat_id,
        text=stop_text,
        reply_markup=start_markup(),
        disable_web_page_preview=True,
    )
    db_session.ban_user(chat_id)
    return ConversationHandler.END

def remind_gift(context: CallbackContext):

    users = db_session.get_all_users()
    for user in users:
        chat_id = user.chat_id
        is_more_30_days = db_session.check_last_time_gift(chat_id)
        if is_more_30_days == True:
            reply_keyboard = [
                [text["get_gift"]],
                [text["bot_faq"]],
                [text["connect_admin"]]
            ]
            markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, selective=True)
            context.bot.send_message(
                chat_id=chat_id,
                text="🎉 Уже прошел месяц и Вы можете снова получить подарок!",
                reply_markup=markup,
            )
            return States.MENU


def connect_to_admin(update: Update, context: CallbackContext):
    """ sends user a link to admin """
    logger.info("connect to admin command")

    chat_id = update.message.chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text=("Если возникли проблемы с ботом, нажмите /start или напишите сюда ➡ @khmellevskyi"),
    )


def help(update: Update, context: CallbackContext):
    """ sends user a link to admin """
    logger.info("help command")

    chat_id = update.message.chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text=("Если возникли проблемы с ботом, нажмите /start или напишите сюда ➡ @khmellevskyi"),
    )


def bot_faq(update: Update, context: CallbackContext):
    """ sends a user the instructions how to use the bot """
    logger.info("bot faq command")

    text_instructions = (
        "В этом боте вы можете получить подарок раз в месяц от PR Trust\n\n"
        "Нажмите 'получить подарок' ⬇"
    )

    chat_id = update.message.chat.id
    context.bot.send_message(chat_id=chat_id, text=text_instructions)


def echo(update: Update, context: CallbackContext):
    """ echo all msgs"""

    chat_id = update.message.chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text=(
            "На данный моемент бот на техническом обслуживании ⚠\n"
            + "и временно не работате 💻❌\nСкоро вернемся 🕔"
        ),
    )


def error_handler(update: Update, context: CallbackContext):
    """ Log the error and send a telegram message to notify the developer """
    # we want to notify the user of this problem.
    # This will always work, but not notify users if the update is an
    # callback or inline query, or a poll update.
    # In case you want this, keep in mind that sending the message could fail

    if update and update.effective_message:
        chat_id = update.message.chat.id
        context.bot.send_message(
            chat_id=chat_id,
            text=text["error"],
        )

    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(f"Exception while handling an update: {context.error}")

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    error_tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    bot_username = "@" + context.bot.username + "\n\n"
    if update:
        update_json = json.dumps(update.to_dict(), indent=2, ensure_ascii=False)
    else:
        update_json = ""
    error_message = (
        "{}"
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>context.chat_data = {}</pre>\n\n"
        "<pre>context.user_data = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        bot_username,
        html.escape(update_json),
        html.escape(str(context.chat_data)),
        html.escape(str(context.user_data)),
        html.escape(error_tb),
    )

    # Finally, send the message
    log_channel = "@" + os.environ["LOG_CHANNEL"]

    # dont print to debug channel in case that's not a production server
    if ("--debug" not in sys.argv) and ("-d" not in sys.argv):
        if len(error_message) < 4096:
            context.bot.send_message(chat_id=log_channel, text=error_message)
        else:
            msg_parts = len(error_message) // 4080
            for i in range(msg_parts):
                err_msg_truncated = error_message[i : i + 4080]
                if i == 0:
                    error_message_text = err_msg_truncated + "</pre>"
                elif i < msg_parts:
                    error_message_text = "<pre>" + err_msg_truncated + "</pre>"
                else:
                    error_message_text = "<pre>" + err_msg_truncated
                context.bot.send_message(chat_id=log_channel, text=error_message_text)
