import logging
import util

from mindedge import BaseMapperMixin
from mindedge import helper
from mindedge.import_history_data_keys import ImportHistoryDataKeys
from models.course.course import Course
from models.course.course_fee import CourseFee
from mongoengine import DoesNotExist

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class CertificateMapper(BaseMapperMixin):

    def __init__(self, provider):
        self.provider = provider

    def certificate_courses(self, suite_courses):
        courses = []
        for item in suite_courses:
            try:
                logger.info("CourseExternalID: ----> {}".format(item['course_id']))
                course_obj = Course.objects.get(
                    external_id=str(item['course_id']),
                    provider=self.provider
                )
                courses.append(course_obj.id)
            except DoesNotExist:
                logger.info("CourseExternalID: ----> {} does not exist".format(item['course_id']))

        return courses

    def map(self, data_object):
        try:
            external_id = str(data_object.get('suite_id'))
            slug = data_object.get('slug')
            external_url = helper.get_external_url(external_id, slug, ImportHistoryDataKeys.suites)
            title = data_object.get('title')
            description = data_object.get('web_description')
            default_image = {
                'original': data_object.get('icon', None)
            }
            product_info = data_object.get('product_info')
            courses = self.certificate_courses(data_object.get('suite_courses'))

            mapped_item = {
                "code": external_id,
                "provider": self.provider,
                "from_importer": True,
                "external_id": external_id,
                "external_url": external_url,
                "external_version_id": "0",
                "title": title,
                "slug": slug,
                "description": description,
                "default_image": default_image,
                "price": CourseFee(amount=util.to_float(product_info.get('list_price')), currency='USD'),
                "courses": courses,
                "version": 0
            }

            return mapped_item
        except Exception as error:
            logger.error(f"Error in mapping course: {error}")
            raise error
