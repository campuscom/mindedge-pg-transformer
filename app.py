import argparse
import datetime
import logging

from campuslibs.eventmanager import event_publisher
from campuslibs.eventmanager.event_generator import EventActions
from models.importer.base import ImporterExecutionStatus, ImporterStatus

from client import mongoengine_client
from config.config import Config
from mindedge.transform import MindEdgeTransformer
from services import importer_service

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.propagate = False

parser = argparse.ArgumentParser(description='Mindedge Transformer Runner')
parser.add_argument('--importer-id', type=str, required=True,
                    help='provide importer-id from mongodb(Ref)')
args = parser.parse_args()


EVENT_RESPONSE = {
    "success": False,
    "importer_id": None,
    "import_history_id": None,
    "msg": "Transformer not yet started"
}


def set_response(success=None, msg=None, import_history_id=None, importer_id=None):
    if success:
        EVENT_RESPONSE['success'] = success
    if msg:
        EVENT_RESPONSE['msg'] = msg
    if import_history_id:
        EVENT_RESPONSE['import_history_id'] = import_history_id
    if importer_id:
        EVENT_RESPONSE['importer_id'] = importer_id


class Runner:
    def __init__(self, transformer, config):
        self.transformer = transformer
        self.config = config
        self.transformer_start_time = datetime.datetime.utcnow()

    def run(self):
        # try:
        #     self.transformer.transform()
        # except Exception as error:
        #     raise error
        #
        # try:
        #     self.transformer.transform_catalogs()
        # except Exception as error:
        #     raise error
        #
        # try:
        #     self.transformer.transform_course_catalogs()
        # except Exception as error:
        #     raise error
        #
        # try:
        #     self.transformer.transform_store_course_sections()
        # except Exception as error:
        #     raise error

        try:
            self.transformer.transform_certificates()
        except Exception as error:
            raise error


def main():
    config = Config
    importer_id = args.importer_id
    logger.info(f"Importer Id: {importer_id}")

    mongoengine_client.connect_to_mongodb(config)
    importer = importer_service.get_importer_config(importer_id)
    importer_history_id = importer.last_import_history.id
    logger.info(f"Importer History Id: {importer_history_id}")
    logger.info(f"Course Provider Id: {importer.course_provider.id}")

    try:
        set_response(import_history_id=importer_history_id, importer_id=importer_id)

        mindedge_transformer = MindEdgeTransformer(importer, importer_history_id)

        set_response(success=True, msg="Transforming Started")
        if Config.SEND_EVENT_MESSAGE:
            event_publisher.publish(EventActions.STARTED_TRANSFORMER.value, EVENT_RESPONSE)

        importer_service.update_importer_status(importer_id, ImporterStatus.RUNNING.value,
                                                ImporterExecutionStatus.TRANSFORM_STARTED.value)

        runner = Runner(transformer=mindedge_transformer, config=config)
        runner.run()

        imp_status = ImporterStatus.READY.value if EVENT_RESPONSE.get('success', False) else ImporterStatus.ERROR.value
        importer_service.update_importer_status(importer_id, imp_status, ImporterExecutionStatus.TRANSFORM_DONE.value)

        stats = importer_service.get_transformer_stats()
        importer_service.update_transformer_stats(importer_history_id, stats)

        set_response(success=True, msg="Transforming Completed")

    except Exception as e:
        logger.error('Failed to run transformer! importer_id: %s Error: %s' % (importer_id, e), exc_info=True)
        set_response(success=False, msg=str(e))
        importer_service.update_importer_status(importer_id, ImporterStatus.ERROR.value,
                                                ImporterExecutionStatus.TRANSFORM_DONE.value)
        importer_service.update_error(importer_history_id, str(e))
    finally:
        if Config.SEND_EVENT_MESSAGE:
            event_publisher.publish(EventActions.COMPLETED_TRANSFORMER.value, EVENT_RESPONSE)
        mongoengine_client.disconnect_to_mongodb()
        logger.info("Transforming - Done")


if __name__ == '__main__':
    main()
