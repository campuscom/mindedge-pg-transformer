import logging

from models.certificate.certificate import Certificate
from models.course.course import Course
from mongoengine import DoesNotExist, NotUniqueError
from copy import copy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_all_course_ids(course_provider):
    try:
        objs = Course.objects(provider=course_provider).timeout(False)
        ids = []
        for data in objs:
            ids.append(data.id)
        return ids
    except Exception as e:
        raise e


def delete_courses(course_list):
    for course_id in course_list:
        try:
            del_obj = Course.objects.get(_id=course_id)
            del_obj.delete()
        except DoesNotExist:
            logger.warning("courseid: {} DoesNotExist for delete!".format(
                str(course_id)))


def upsert_certificate(mapped_certificate, dup_count=0):
    try:
        provider = mapped_certificate.get("provider")
        external_id = mapped_certificate.get("external_id")
        if dup_count > 0:
            slug = mapped_certificate["slug"]
            new_slug = mapped_certificate["slug"] = f"{slug}-{dup_count}"
            logger.info(f"Trying to save again with new slug {new_slug}")

        try:
            logger.info("Certificate ExternalID: ----> {}".format(external_id))
            certificate_obj = Certificate.objects.get(
                external_id=external_id,
                provider=provider
            )
            _old = copy(certificate_obj.__dict__)
            for key, value in mapped_certificate.items():
                certificate_obj.__setattr__(key, value)
            return certificate_obj.save(
                signal_kwargs={
                    "old": _old,
                    "update": mapped_certificate
                })
        except NotUniqueError:
            logger.warning(f"Update! NotUniqueError for certificate_id: {external_id}")
            return upsert_certificate(mapped_certificate, dup_count + 1)
        except DoesNotExist:
            logger.info("Does not exists")
            try:
                new_certificate = Certificate(**mapped_certificate)
                return new_certificate.save()
            except NotUniqueError:
                logger.warning(f"Insert! NotUniqueError for certificate_id: {external_id}")
                return upsert_certificate(mapped_certificate, dup_count + 1)

    except Exception as error:
        raise error


def upsert_course(mapped_course, dup_count=0):
    try:
        provider = mapped_course.get("provider")
        external_id = mapped_course.get("external_id")
        if dup_count > 0:
            slug = mapped_course["slug"]
            new_slug = mapped_course["slug"] = f"{slug}-{dup_count}"
            logger.info(f"Trying to save again with new slug {new_slug}")

        try:
            logger.info("ExternalID: ----> {}".format(external_id))
            course_obj = Course.objects.get(
                external_id=external_id,
                provider=provider
            )
            _old = copy(course_obj.__dict__)
            for key, value in mapped_course.items():
                course_obj.__setattr__(key, value)
            return course_obj.save(
                signal_kwargs={
                    "old": _old,
                    "update": mapped_course
                })
        except NotUniqueError:
            logger.warning(f"Update! NotUniqueError for course_id: {external_id}")
            return upsert_course(mapped_course, dup_count + 1)
        except DoesNotExist:
            logger.info("Does not exists")
            try:
                new_course = Course(**mapped_course)
                return new_course.save()
            except NotUniqueError:
                logger.warning(f"Insert! NotUniqueError for course_id: {external_id}")
                return upsert_course(mapped_course, dup_count + 1)

    except Exception as error:
        raise error
    # try:
    #     external_id = data_dict['external_id']
    #     provider = data_dict['provider']
    #     obj = Course.objects(external_id=external_id, provider=provider)
    #     return upsert(obj, data_dict)
    # except Exception as e:
    #     raise e


# def upsert(obj, data_dict):
#     raw_query = {'$set': data_dict}
#     obj.update_one(__raw__=raw_query, upsert=True)
#     return obj.get()


# ============ updates ================== #
