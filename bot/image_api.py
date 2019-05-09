import enum
import os
import random
import re
import string
import requests
from json import JSONDecodeError
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from requests import HTTPError
from requests_toolbelt.multipart.encoder import MultipartEncoder

from bot import Common


class BaseApi(object):
    """Base API class."""

    @staticmethod
    def _request(method, url, is_decode_to_json=True, params=None, headers=None, data=None, **kwrags):
        resp = requests.request(method=method,
                                url=url,
                                params=params,
                                headers=headers,
                                data=data,
                                **kwrags)
        try:
            resp.raise_for_status()
            if not is_decode_to_json:

                return resp

            content = resp.json()
        except (HTTPError, JSONDecodeError) as error:
            return error

        return content


class ImgFlipApi(BaseApi):
    """Class for imgflip.com API."""

    API_URL = 'https://api.imgflip.com/{path}'
    GET_MEMES = API_URL.format(path='get_memes')
    CAPTION_IMAGE = API_URL.format(path='caption_image')
    URL_REGEXP = r'(http(s?):)([/|.|\w|\s|-])*\.(?:jpg)'
    TYPE = 'boxes[{}][type]'
    TEXT = 'boxes[{}][text]'

    def __init__(self):
        self.__login = os.getenv("LOGIN")
        self.__password = os.getenv("PASSWORD")

    @staticmethod
    def _is_success(response):
        """Check is response success."""
        return True if isinstance(response, dict) and response.get('success') is True else False

    def get_memes(self):
        """Get all top memes."""
        content = self._request(method='GET', url=self.GET_MEMES)

        return [Memes(**kwargs) for kwargs in content['data']['memes']] if self._is_success(content) else str(content)

    def create_memes(self, template_id, **kwargs):
        """Create memes from template."""
        data = {
            'template_id': str(template_id),
            'username': self.__login,
            'password': self.__password
        }

        if kwargs.get('boxes') is not None:
            data = self._multipart_data(data=data, boxes=kwargs.get('boxes'))
            headers = {'Content-Type': data.content_type}
        else:
            headers = None
            data.update(**kwargs)

        content = self._request(method='POST', url=self.CAPTION_IMAGE, data=data, headers=headers)

        url = content['data']['url'] if self._is_success(content) else str(content)

        if re.search(self.URL_REGEXP, url):
            return TextOnImage().create(img_source=url)
        else:
            return None

    def _multipart_data(self, data, boxes, i=0):
        """Creates form-data content for request."""
        for item in boxes:
            d_type = self.TYPE.format(i)
            text = self.TEXT.format(i)
            data.update({d_type: 'text', text: item['text']})
            i += 1

        return MultipartEncoder(fields=data)


class Memes(object):
    """Class for memes object."""

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.url = kwargs.get('url')
        self.box_count = kwargs.get('box_count')


class TextType(enum.Enum):
    """Type of text on Image enumeration."""

    logo = 0
    memes = 1


class TextOnImage(BaseApi):
    """Class representing image with new added text."""

    _letters = string.ascii_lowercase   # letters for generating temp image name
    _format = "JPEG"                    # result image format
    _font = 'bot/impact.ttf'            # path to font file

    TEXT_COLOR = (255, 255, 255)        # white text
    OUTLINE_COLOR = (0, 0, 0)           # black borders
    DELTA_POS = 2                       # for outline draw
    SIZE = 12                           # font size

    @staticmethod
    def _is_success(response):
        """Check is response success."""
        return True if not isinstance(response, HTTPError) else False

    def _generate_name(self):
        return ''.join(random.choice(self._letters) for _ in range(20))

    def _save_image_to_stream(self, image):
        """Save image to object, that can be transferred to telegram chat."""
        bio = BytesIO()
        bio.name = self._generate_name()
        image.save(bio, self._format)
        bio.seek(0)
        return bio

    def _add_outline(self, image_draw_obj, text, text_pos_x, text_pos_y, font):
        """add outline for given text."""
        for x, y in [[text_pos_x - self.DELTA_POS, text_pos_y - self.DELTA_POS],
                     [text_pos_x + self.DELTA_POS, text_pos_y - self.DELTA_POS],
                     [text_pos_x + self.DELTA_POS, text_pos_y + self.DELTA_POS],
                     [text_pos_x - self.DELTA_POS, text_pos_y + self.DELTA_POS]]:
            image_draw_obj.text((x, y), text, self.OUTLINE_COLOR, font=font)

    def create(self, img_source, text=None, text_type=TextType.logo):
        """Add text to image."""
        text = Common.BOT_LINK if text_type == TextType.logo else text
        resp = self._request(method='GET', url=img_source, is_decode_to_json=False)

        if not self._is_success(resp):
            return None

        img = Image.open(BytesIO(resp.content))
        origin_bio = self._save_image_to_stream(image=img)

        try:
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(font=self._font, size=self.SIZE)
            text_size = font.getsize(text)
            t_pos = (img.width - text_size[0], img.height - text_size[1] - self.DELTA_POS)

            # outline
            self._add_outline(image_draw_obj=draw, text=text, text_pos_x=t_pos[0], text_pos_y=t_pos[1], font=font)
            # main text
            draw.text(t_pos, text, self.TEXT_COLOR, font=font)
            # save result
            bio_result = self._save_image_to_stream(image=img)
            img.close()

            return bio_result
        except:
            img.close()
            return origin_bio
