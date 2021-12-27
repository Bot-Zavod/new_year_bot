""" conversation handlers of main module """
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler

from .data import text
from .db_functions import db_session
from .handlers import admin
from .handlers import connect_to_admin
from .handlers import start_init
from .handlers import start
from .handlers import stop
from .handlers import help
from .handlers import bot_faq
from .handlers import check_username
from .handlers import intro
from .handlers import greetings
from .handlers import ask_gift
from .handlers import get_gift
from .states import States


ADMIN_IDS = db_session.get_admins()

admin_filters = Filters.user(ADMIN_IDS) & Filters.chat_type.private

admin_handler = CommandHandler(
    "admin",
    admin,
    filters=admin_filters,
)

# push_status_handler = CommandHandler(
#     "push_status", broadcast_status, filters=admin_filters
# )

necessary_handlers = [
    CommandHandler("start", start_init, pass_job_queue=True),
    CommandHandler("help", help),
    admin_handler,
]

conv_handler = ConversationHandler(
    name="conversation",
    persistent=True,
    entry_points=necessary_handlers,
    states={
        # -----------------------------------------------------------
        # Profile
        # -----------------------------------------------------------
        States.MENU: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["get_gift"]]), ask_gift),
            MessageHandler(Filters.text([text["connect_admin"]]), connect_to_admin),
            MessageHandler(Filters.text([text["bot_faq"]]), bot_faq),
        ],
        # -----------------------------------------------------------
        # Registration
        # -----------------------------------------------------------
        States.ASK_USERNAME: [
            *necessary_handlers,
            MessageHandler(Filters.text, check_username)
            # MessageHandler(Filters.text([text["back"]]), profile),
            # MessageHandler(Filters.text, check_notion_username),
        ],
        States.INTRO: [
            *necessary_handlers,
            MessageHandler(Filters.text, intro)
        ],
        States.GREETINGS: [
            *necessary_handlers,
            MessageHandler(Filters.text, greetings)
        ],
        States.ASK_GIFT: [
            *necessary_handlers,
            MessageHandler(Filters.text, ask_gift)
        ],
        States.GET_GIFT: [
            *necessary_handlers,
            MessageHandler(Filters.regex("^(1[0-2]|[1-9])$"), get_gift)
        ],
        States.GET_GIFT_APPROVE: [
            *necessary_handlers,
            MessageHandler(Filters.text, start)
        ],
        # -----------------------------------------------------------
        # Admin
        # -----------------------------------------------------------
        States.ADMIN_MENU: [
            *necessary_handlers,
            MessageHandler(Filters.text([text["back"]]), start),
            # MessageHandler(Filters.text([text["stats"]]), bot_statistics),
            # MessageHandler(Filters.text([text["mailing"]]), push_mssg),
        ],
        # States.PUSH_MSSG_ADD_TEXT: [
        #     *necessary_handlers,
        #     MessageHandler(Filters.text([text["cancel"]]), admin),
        #     MessageHandler(Filters.text, ask_push_text),
        # ],
        # States.PUSH: [
        #     *necessary_handlers,
        #     MessageHandler(Filters.text([text["back"]]), admin),
        #     MessageHandler(Filters.text([text["drop_mailing"]]), admin),
        #     CallbackQueryHandler(ask_url_button, pattern="add_url_button"),
        #     CallbackQueryHandler(delete_url_button, pattern="delete_url_button"),
        #     CallbackQueryHandler(display_push, pattern="back_to_push"),
        #     MessageHandler(Filters.text([text["start_mailing"]]), prepare_broadcast),
        #     MessageHandler(Filters.regex(URL_BUTTON_REGEX), set_url_button),
        #     MessageHandler((Filters.text | Filters.photo), display_push),
        # ],
    },
    fallbacks=[CommandHandler("stop", stop)],
)
