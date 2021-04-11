import logging

from models.course.course import Course
from models.history.import_history import ImportHistory
from models.importer import MindEdgeImporterConfig
from mongoengine import DoesNotExist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_importer_config(importer_id):
    try:
        importer_obj = MindEdgeImporterConfig.objects(id=importer_id).get()
        return importer_obj
    except DoesNotExist as e:
        raise e
    except Exception as e:
        raise e


def update_importer_status(importer_id, importer_status, imp_execution_status):
    try:
        importer_obj = get_importer_config(importer_id=importer_id)
        importer_obj.status = importer_status
        importer_obj.execution_status = imp_execution_status
        importer_obj.save()
    except Exception as error:
        raise error


def update_error(import_history_id, error_msg):
    try:
        importer_history_obj = ImportHistory.objects(id=import_history_id).get()
        importer_history_obj.error = {'msg': error_msg}
        importer_history_obj.save()
        return importer_history_obj
    except DoesNotExist as e:
        raise e
    except Exception as e:
        raise e


def get_transformer_stats():

    stats = {
        'courses': Course.objects.count(),
    }
    return stats


def update_transformer_stats(import_history_id, stats):
    try:
        importer_history_obj = ImportHistory.objects(id=import_history_id).get()
        importer_history_obj.stats['transformer_count'] = stats
        importer_history_obj.save()
        return importer_history_obj
    except DoesNotExist as e:
        raise e
    except Exception as e:
        raise e


if __name__ == '__main__':
    pass
