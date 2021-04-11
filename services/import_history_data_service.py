import logging

from bson import ObjectId
from models.history.import_history import ImportHistoryDataKeys, ImportHistoryData


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class ImportHistoryDataService:

    def __init__(self, import_history_id):
        self.import_history_id = import_history_id

    def get_all_item(self, history_key_name):
        try:
            pipeline = [
                {"$match": {
                    "$and": [
                        {"history": ObjectId(self.import_history_id)},
                        {"key_name": history_key_name}
                    ]}}
            ]
            for item in ImportHistoryData.objects.timeout(False).aggregate(*pipeline):
                yield item

        except Exception as error:
            raise error

    def get_item(self, history_key_name):
        ImportHistoryData.objects(key_name=history_key_name, history=ObjectId(self.import_history_id)).get()
        pass
