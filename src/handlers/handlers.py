""" basic command and error handlers """
import html
import json
import os
import sys
import traceback

from loguru import logger
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.chat import Chat
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from ..db_functions import Action
from ..data import start_keyboard
from ..data import text
from ..db_functions import db_session
from ..states import States


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

    reply_keyboard = ["🦄"]
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

    reply_keyboard = ["✨"]
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
        return greetings(update, context)


def check_username(update: Update, context: CallbackContext):
    """ checks if username exists """
    chat_id = update.message.chat.id
    mssg = update.message.text

    username = mssg.replace("@", "")


def greetings(update: Update, context: CallbackContext):
    """ greets a user individually """
    pass


def start(update: Update, context: CallbackContext):
    """ start command an msg """
    logger.info("start menu")

    chat = update.message.chat
    chat_id = chat.id

    db_session.add_user(chat=chat)

    user = db_session.get_user_data(chat_id)

    db_session.log_action(chat_id=chat_id, action=Action.now)

    context.bot.send_message(
        chat_id=chat_id, text=text["start"], reply_markup=start_markup()
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
        "Нажмите 'получить подарок ⬇'"
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
