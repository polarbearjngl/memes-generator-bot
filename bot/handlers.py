# coding=utf-8
from telegram import ChatAction
from bot import Common
from bot.image_api import ImgFlipApi
from bot.inline_query_result import InlineQueryResults


def start(bot, update, user_data):
    """Handler that calling when user send /start"""
    Common.add_analytics(update=update, user_data=user_data, message=Common.START_OR_RESET_CMD)
    update.message.reply_html(text=Common.START_TEXT)

    return Common.PHOTO


def call_help(bot, update, user_data):
    """Send a message when the command /help is issued."""
    Common.add_analytics(update=update, user_data=user_data, message=Common.HELP_CMD)
    update.message.reply_text(Common.HELP_TEXT)


def inline_query(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query
    iqr = InlineQueryResults()
    results = iqr.search(query=query)
    update.inline_query.answer(results)


def photo(bot, update, user_data):
    msg = update.effective_message
    caption = msg.to_dict().get('caption')
    if caption is not None:
        template_id = [m for m in ImgFlipApi().get_memes() if m.name == caption]
        if template_id:
            create_template_with_zones(bot=bot, update=update, template_id=template_id, user_data=user_data)

            user_data['text'], user_data['index'] = {}, None
            user_data['template_id'], user_data['start_count'] = template_id[0].id, template_id[0].box_count
            user_data['count'] = [i for i in range(1, template_id[0].box_count + 1)]
            user_data['boxes'] = [{} for _ in range(len(user_data['count']))] if len(user_data['count']) > 2 else None
            update.message.reply_text(text=Common.SEND_TEXT.format(num=user_data['count'].pop(0),
                                                                   count=user_data['start_count']))
            Common.add_analytics(update=update, user_data=user_data, message=Common.PHOTO_CMD)

            return Common.TEXT

    update.message.reply_text(text=Common.NOT_VALID_PHOTO)
    Common.add_analytics(update=update, user_data=user_data, message=Common.NOT_VALID_PHOTO_EVENT)

    return Common.PHOTO


def text(bot, update, user_data):
    _text = update.effective_message.text
    user_data = Common.capture_text_from_user(text=_text, user_data=user_data)

    if user_data['count']:
        update.message.reply_text(text=Common.SEND_TEXT.format(num=user_data['count'].pop(0),
                                                               count=user_data['start_count']))

        return Common.TEXT
    else:
        _send_photo(bot=bot, update=update, user_data=user_data)
        Common.send_analytics(user_data=user_data)

        return start(bot=bot, update=update, user_data=user_data)


@Common.send_action(ChatAction.UPLOAD_PHOTO)
def _send_photo(bot, update, user_data):
    img_flip = ImgFlipApi()
    memes = img_flip.create_memes(template_id=user_data['template_id'],
                                  boxes=user_data['boxes'],
                                  **user_data['text'])
    print("----------------USER DATA TEXT-----------------")
    for key, value in user_data['text'].items():
        print(key, ' : ', value)

    print("----------------USER DATA------------------")
    for key, value in user_data.items():
        print(key, ' : ', value)

    if memes is not None:
        bot.sendPhoto(chat_id=update.message.chat_id, photo=memes)
        Common.add_analytics(update=update, user_data=user_data, message=Common.SEND_PHOTO_EVENT)
    else:
        update.message.reply_text(text=Common.ERROR)
        Common.add_analytics(update=update, user_data=user_data, message=Common.ERROR_EVENT, not_handled=True)

def create_template_with_zones(bot, update, template_id, user_data):
    user_data['template_id'], user_data['start_count'] = template_id[0].id, template_id[0].box_count
    user_data['count'] = [i for i in range(1, template_id[0].box_count + 1)]
    user_data['boxes'] = None
    user_data['text'] = {}

    if len(user_data['count']) > 2:
        user_data['boxes'] = []
        for i in range(1, len(user_data['count']) + 1):
            user_data['boxes'].append(dict(text=str(i)))
    else:
        user_data['text'] = {'text0': '1', 'text1': '2'}

    _send_photo(bot=bot, update=update, user_data=user_data)

    return start(bot=bot, update=update, user_data=user_data)