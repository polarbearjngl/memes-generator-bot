import logging
import os
from telegram.ext import (Updater, InlineQueryHandler, CommandHandler, ConversationHandler, MessageHandler, Filters)
from bot import Common
from bot.handlers import inline_query, start, call_help, photo, text, send_template_with_numbers

TOKEN = os.getenv("TOKEN")
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def error(bot, update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def run(updater_instance):
    updater_instance.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater_instance.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))


if __name__ == '__main__':
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(Common.START, start, pass_user_data=True)],

        states={
            Common.PHOTO: [MessageHandler(filters=Filters.photo, callback=photo, pass_user_data=True)],

            Common.TEXT: [MessageHandler(filters=Filters.text, callback=text, pass_user_data=True)],
        },

        fallbacks=[CommandHandler(Common.RESET, start, pass_user_data=True)]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler(Common.START, start, pass_user_data=True))
    dp.add_handler(CommandHandler(Common.HELP, call_help, pass_user_data=True))
    dp.add_handler(InlineQueryHandler(inline_query))
    dp.add_handler(CommandHandler('template_with_numbers', send_template_with_numbers, pass_user_data=True))

    # log all errors
    dp.add_error_handler(error)
    run(updater)
