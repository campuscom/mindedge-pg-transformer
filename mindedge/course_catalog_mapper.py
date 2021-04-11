import logging

from config.config import Config
from mindedge import BaseMapperMixin
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class CourseCatalogMapper(BaseMapperMixin):

    def map(self, data_object):

        try:
            course_id = data_object.get('course_id')
            category_id = data_object.get('category_id')

            mapped_item = {
                'course_id': course_id,
                'category_id': category_id
            }

            return mapped_item
        except Exception as error:
            logger.error(f"Error in mapping course category: {error}")
            raise error
