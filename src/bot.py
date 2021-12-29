""" main fuction to launch bot """
import os
import sys

from datetime import time as datetime_time
from dotenv import load_dotenv
from loguru import logger
from telegram import Bot
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import PicklePersistence
from telegram.ext import Updater

from .data import TIME_ZONE
from .conv_handlers import conv_handler
from .handlers import echo
from .handlers import error_handler
from .handlers import remind_gift
from .handlers import update_new_month
from .set_commands import clear_bot
from .set_commands import set_bot_commands

# configure_logger()
load_dotenv()

logger.add(
    "debug.log",
    format="{time} {level} {message}\n",
    level="DEBUG",
    rotation="30 KB",
    compression="zip",
)

logger.debug("-------- succesful import --------")


def setup_bot(bot_token: str):
    """logs data about the bot"""

    bot = Bot(token=bot_token)
    logger.info(f"bot ID: {bot.id}")
    logger.info(f"bot username: {bot.username}")
    logger.info(f"bot link: {bot.link}")

    clear_bot(bot)
    set_bot_commands(bot)


@logger.catch  # catches errors and writes to the debug.log
def main():
    """ inicialise handlers and start the bot """

    storage_file = "storage"
    my_persistence = PicklePersistence(filename=storage_file)

    bot_token = os.getenv("BOT_TOKEN")  # variable, because it is needed on webhook
    setup_bot(bot_token)
    updater = Updater(token=bot_token, use_context=True, persistence=my_persistence)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    if ("--service" in sys.argv) or ("-s" in sys.argv):
        logger.debug("!!!!!!!! bot on service !!!!!!!!")
        dispatcher.add_handler(MessageHandler((Filters.text | Filters.command), echo))
    else:
        # crone jobs
        # ==========

        j = updater.job_queue

        callback_time = datetime_time(hour=6, minute=55, tzinfo=TIME_ZONE)
        # j.run_daily(callback=remind_gift, time=callback_time)
        j.run_monthly(callback=remind_gift, when=callback_time, day=29)

        # j.run_monthly(callback=update_new_month, when=callback_time, day=1)

        # message handlers
        # ================

        dispatcher.add_handler(conv_handler)

    dispatcher.add_error_handler(error_handler)

    if ("--web-hook" in sys.argv) or ("-w" in sys.argv):
        logger.debug("-------- starting webhook --------")
    #     host_port = int(os.getenv("WEBHOOK_PORT"))
    #     host_url = os.getenv("WEBHOOK_URL")
    #     webhook_host_url = f"https://{host_url}:{host_port}/{bot_token}"
    #     logger.debug("started on\n\n" + webhook_host_url)
    #     updater.start_webhook(
    #         listen="0.0.0.0",
    #         port=host_port,
    #         url_path=bot_token,
    #         key="private.key",
    #         cert="cert.pem",
    #         webhook_url=webhook_host_url,
    #     )
    else:
        logger.debug("-------- starting polling --------")
        updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
