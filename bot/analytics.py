import os

from chatbase import MessageSet, Message, MessageTypes


class Analytics(MessageSet):

    def __init__(self, user_id):
        super().__init__(api_key=os.getenv("CHATBASE_TOKEN"),
                         platform="Telegram",
                         version="Release",
                         user_id=user_id)

    def new_message(self,
                    intent="",
                    message="",
                    type=MessageTypes.USER,
                    not_handled=False,
                    time_stamp=None):
        """Add a message to the internal messages list and return it"""
        self.messages.append(Message(api_key=self.api_key,
                                     platform=self.platform,
                                     version=self.version,
                                     user_id=self.user_id,
                                     intent=intent,
                                     message=message,
                                     type=type,
                                     not_handled=not_handled,
                                     time_stamp=time_stamp))
        return self.messages[-1]
