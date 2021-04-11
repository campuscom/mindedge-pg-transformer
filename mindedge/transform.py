import logging

from mindedge import BaseTransformer, BaseMapperMixin
from mindedge.certificate_mapper import CertificateMapper
from mindedge.course_mapper import CourseMapper
from mindedge.import_history_data_keys import ImportHistoryDataKeys
from mindedge.section_mapper import SectionMapper
from mindedge.catalog_mapper import CatalogMapper
from mindedge.course_catalog_mapper import CourseCatalogMapper
from models.certificate.certificate import Certificate
from services import transformer_service
from services.import_history_data_service import ImportHistoryDataService
from services.django_postgres.postgres_data_service import create_or_update_courses, create_or_update_category,\
    create_or_update_course_category, create_or_update_store_course_sections

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MindEdgeTransformer(BaseTransformer, BaseMapperMixin):

    def __init__(self, importer, import_history_id):
        super().__init__()
        self.importer = importer
        self.history_data_service = ImportHistoryDataService(import_history_id)

    @staticmethod
    def remove_deleted_courses(existing_course_ids, transformed_ids):

        difference_ids = list(set(existing_course_ids).difference(set(transformed_ids)))
        logger.info(f"Total courses to remove: {len(difference_ids)}")

        transformer_service.delete_courses(course_list=difference_ids)
        logger.info(f"deleted course ids from Course collection: {', '.join(str(x) for x in difference_ids)}")

    def transform(self):
        existing_course_ids = transformer_service.get_all_course_ids(self.importer.course_provider.id)
        transformed_ids = self.transform_course()
        self.remove_deleted_courses(existing_course_ids, transformed_ids)

        # save these courses to postgres
        create_or_update_courses(transformed_ids)

    def transform_catalogs(self):
        categories = self.history_data_service.get_all_item(ImportHistoryDataKeys.categories)

        try:
            for category_obj in categories:
                data_object = self.get_value_from_dict(category_obj, "data_object")
                mapped_catalog = CatalogMapper().map(data_object)
                catalog = create_or_update_category(mapped_catalog)

                logger.info(f"catalog transformed: {catalog.title}")

        except Exception as error:
            logger.error(f"Error in transforming categories: {error}")
            raise error

    def transform_course(self):
        try:
            saved_ids = []
            items = self.history_data_service.get_all_item(ImportHistoryDataKeys.courses)
            for item in items:
                data_object = self.get_value_from_dict(item, "data_object")
                mapped_course = CourseMapper(self.importer.course_provider.id).map(data_object)
                mapped_course["sections"] = [SectionMapper().get_section_object(data_object)]
                course = transformer_service.upsert_course(mapped_course)

                if course and course.id:
                    saved_ids.append(course.id)
                    logger.info(f"Course transformed: {mapped_course['code']}")
                else:
                    logger.warning(f"Course could not be transformed: {mapped_course['code']}")

            return saved_ids
        except Exception as error:
            logger.error(f"Error in transforming course: {error}")
            raise error
        pass

    def transform_course_catalogs(self):
        course_categories = self.history_data_service.get_all_item(ImportHistoryDataKeys.courses_category)
        try:
            for course_category_obj in course_categories:
                data_object = self.get_value_from_dict(course_category_obj, "data_object")
                mapped_course_catalog = CourseCatalogMapper().map(data_object)
                course_catalog = create_or_update_course_category(mapped_course_catalog)

                if course_catalog:
                    logger.info(f"course catalog transformed: {course_catalog.catalog.title}")
                else:
                    pass

        except Exception as error:
            logger.error(f"Error in transforming course categories: {error}")
            raise error

    @staticmethod
    def transform_store_course_sections():
        try:
            store_course_sections = create_or_update_store_course_sections()
            return store_course_sections
        except Exception as error:
            logger.error(f"Error in transforming course categories: {error}")
            raise error

    def transform_certificates(self):
        try:
            for item in Certificate.objects:
                print(item.title)
                # mapped_certificate = CertificateMapper(self.importer.course_provider.id).map(item)
                # certificate = transformer_service.upsert_certificate(mapped_certificate)
                #
                # if certificate and certificate.id:
                #     logger.info(f"Certificate transformed: {mapped_certificate['code']}")
                # else:
                #     logger.warning(f"Certificate could not be transformed: {mapped_certificate['code']}")
        except Exception as error:
            logger.error(f"Error in transforming certificate: {error}")
            raise error
