from emoji import emojize
from functools import wraps

from bot.analytics import Analytics


class Common(object):
    """Class for storing callback commands and constant text."""

    PHOTO, TEXT = range(2)

    START = 'start'
    RESET = 'reset'
    HELP = 'help'

    BOT_NAME = '@MemeGeneratorForkBot'
    BOT_LINK = 't.me/MemeGeneratorForkBot'
    START_TEXT = emojize("Чтобы начать создание мема наберите {name}, "
                         "нажмите пробел и выберите шаблон из результатов поиска.\n"
                         ":magnifying_glass_tilted_right: Для поиска определенных мемов по их названию "
                         "вводите текст (english only)", use_aliases=True).format(name=BOT_NAME)
    SEND_TEXT = emojize("Отправьте текст, который будет добавлен в поле №{num} из {count}\n\n"
                        ":warning:Если текст в поле №{num} не нужен, то отправьте  '0' (ноль):warning:\n\n"
                        ":back:Отправьте /reset чтобы сбросить переданные данные и вернутся к началу",
                        use_aliases=True)
    NOT_VALID_PHOTO = emojize(":prohibited:Необходимо выбирать шаблон из доступных в поиске {name}\n\n" +
                              START_TEXT, use_aliases=True).format(name=BOT_NAME)
    ERROR = emojize(':cry: Во время генерации что-то пошло не так\n'
                    ':crying_cat_face: Либо сервис временно недоступен\n'
                    ':loudly_crying_face: Либо вы отправили некорректные данные', use_aliases=True)
    HELP_TEXT = emojize("Бот для создания мемов с использованием популярных шаблонов.\n\n"
                        "Позволяет:\n"
                        ":magnifying_glass_tilted_right: - вести поиск среди популярных шаблонов\n"
                        ":spiral_notepad: - добавлять на них текст\n"
                        ":speech_balloon: - отправлять их в чаты\n\n"
                        "Кроме этого - может работать в любом чате в режиме поиска\n"
                        "Просто введите {name} затем поставьте пробел.\n"
                        "Откроется панель со списком картинок.\n"
                        "Вводите текст (eng) для поиска определенных мемов по их названию.\n"
                        "Нажмите на картинку чтобы сразу отправить ее в чат.\n\n"
                        "/start - начать работу с ботом\n"
                        "/reset - сбросить переданные данные и вернутся к старту\n"
                        "/help - вызов справки\n", use_aliases=True).format(name=BOT_NAME)

    START_OR_RESET_CMD = 'start or reset cmd'
    HELP_CMD = 'help cmd'
    PHOTO_CMD = 'photo cmd'
    NOT_VALID_PHOTO_EVENT = 'not valid photo event'
    SEND_PHOTO_EVENT = 'send photo event'
    ERROR_EVENT = 'something go wrong'

    @staticmethod
    def capture_text_from_user(text, user_data):
        user_data['index'] = user_data['index'] + 1 if user_data.get('index') is not None else 0
        if user_data['boxes'] is not None:
            user_data['boxes'][user_data['index']] = {'text': text}
        else:
            key = 'text{}'.format(user_data['index'])
            user_data['text'][key] = text

        return user_data

    @staticmethod
    def send_action(action):
        """Sends `action` while processing func command."""

        def decorator(func):
            @wraps(func)
            def command_func(bot, update, *args, **kwargs):
                bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
                return func(bot, update, *args, **kwargs)

            return command_func

        return decorator

    @staticmethod
    def add_analytics(update, user_data, message, intent=None, not_handled=False):
        if user_data.get('analytics') is None:
            user_data['analytics'] = Analytics(user_id=update.effective_user.id)
        user_data['analytics'].new_message(message=message,
                                           not_handled=not_handled,
                                           intent="" if intent is None else intent)

    @staticmethod
    def send_analytics(user_data):
        if user_data.get('analytics') is not None:
            user_data['analytics'].send()
            user_data['analytics'] = None
