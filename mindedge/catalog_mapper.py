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


class CatalogMapper(BaseMapperMixin):

    def map(self, data_object):
        try:
            external_id = str(data_object.get('category_id'))
            from_importer = True
            title = data_object.get('category_name')
            store = 'Life Long Campus'
            description = data_object.get('category_description')
            image = data_object.get('category_icon')
            start_date = None
            end_date = None
            is_published = True

            mapped_item = {
                'from_importer': from_importer,
                'external_id': external_id,
                'title': title,
                'store': store,
                'description': description,
                'image': image,
                'start_date': start_date,
                'end_date': end_date,
                'is_published': is_published,
            }

            return mapped_item
        except Exception as error:
            logger.error(f"Error in mapping category: {error}")
            raise error
