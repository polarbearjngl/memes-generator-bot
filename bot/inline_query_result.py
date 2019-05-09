import random
from uuid import uuid4
from telegram import InlineQueryResultPhoto

from bot.image_api import ImgFlipApi


class InlineQueryResults(object):
    """Class for objects, that represent inline query results."""

    def __init__(self):
        self._imgFlipApi = ImgFlipApi()
        self._all_memes = []

    @staticmethod
    def inline_query_result_photo(memes):
        """Create single InlineQueryResultPhoto."""
        return InlineQueryResultPhoto(id=uuid4(),
                                      photo_url=memes.url,
                                      thumb_url=memes.url,
                                      title=memes.name,
                                      description=memes.name,
                                      caption=memes.name)

    def _get_memes(self):
        """Get all top memes from imgflip.com."""
        self._all_memes = self._imgFlipApi.get_memes() if not self._all_memes else self._all_memes

        return self._all_memes

    def search(self, query, maximum=50):
        """Proceed inline search."""
        query = str(query).lower() if not str(query).isdigit() else str(query)
        answer = [m for m in self._get_memes() if query in str(m.name).lower()]
        inline_answer = [self.inline_query_result_photo(memes=memes) for memes in answer]
        random.shuffle(inline_answer)

        return inline_answer[0:maximum] if len(inline_answer) > maximum else inline_answer
