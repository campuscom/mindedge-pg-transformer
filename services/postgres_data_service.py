import os
import django
from config.config import Config
from django_scopes import scopes_disabled
from models.course.course import Course as CourseModel

DEBUG = True
SECRET_KEY = '4l0ngs3cr3tstr1ngw3lln0ts0l0ngw41tn0w1tsl0ng3n0ugh'
ROOT_URLCONF = __name__
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

urlpatterns = []
PAYMENT_LIB_DIR = BASE_DIR

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'shared_models',
]

config = Config

DATABASES = {
    'default': {
        'ENGINE': config.POSTGRES_ENGINE,
        'NAME': config.DATABASE_NAME,
        'USER': config.DATABASE_USER,
        'PASSWORD': config.DATABASE_PASSWORD,
        'HOST': config.DATABASE_HOST,
        'PORT': config.DATABASE_PORT,
    }
}

os.environ.setdefault('DJANGO_SETTINGS_MODULE', __name__)
django.setup()
from shared_models.models import Certificate, CertificateCourse, CourseProvider, Course, Section, Catalog, Store,\
    StoreCourse, CourseCatalog, StoreCourseSection


def get_course(mongo_course_id):
    try:
        return Course.objects.get(content_db_reference=str(mongo_course_id))
    except Course.DoesNotExist:
        return


def get_provider(mongo_provider_id):
    try:
        return CourseProvider.objects.get(content_db_reference=str(mongo_provider_id))
    except CourseProvider.DoesNotExist as error:
        raise error


def get_store():
    try:
        store = Store.objects.get(url_slug='campus')
    except Store.DoesNotExist:
        store = Store.objects.create(name='Lifelong Campus', url_slug='campus')

    return store


def create_or_update_course_category(data):
    store = get_store()

    catalog = Catalog.objects.get(external_id=data['category_id'], store=store)

    try:
        course_obj = CourseModel.objects.get(external_id=str(data['course_id']))
    except:
        return False

    with scopes_disabled():
        try:
            course = Course.objects.get(content_db_reference=str(course_obj.id))
        except:
            return False

        # we are creating store_course here because without this we can not map course with catalog. because
        # CourseCatalog has two fields: store_course, catalog as foreignid (not course, catalog as foreignid)
        try:
            store_course = StoreCourse.objects.get(course=course, store=store)
        except StoreCourse.DoesNotExist:
            store_course = StoreCourse.objects.create(
                course=course,
                store=store,
                is_published=False,
                is_featured=False
            )

    course_catalogs = CourseCatalog.objects.filter(catalog=catalog, store_course=store_course)

    if course_catalogs.exists():
        # does not make much sense
        course_catalogs.update(catalog=catalog, store_course=store_course)
        return course_catalogs.first()

    else:
        course_catalog = CourseCatalog.objects.create(catalog=catalog, store_course=store_course)
    return course_catalog


def create_or_update_category(data):
    data['store'] = get_store()

    catalogs = Catalog.objects.filter(external_id=data['external_id'], store=data['store'])

    if catalogs.exists():
        catalogs.update(**data)
        return catalogs.first()

    catalog = Catalog.objects.create(**data)
    return catalog


def upsert_certificate(pg_provider, certificate_obj):
    try:
        price = certificate_obj.price['amount']
        external_image_url = certificate_obj.default_image['original']
    except KeyError:
        price = 0
        external_image_url = ''

    with scopes_disabled():
        certificates = Certificate.objects.filter(content_db_reference=str(certificate_obj.id))

        if certificates.exists():
            certificates.update(
                course_provider=pg_provider,
                title=certificate_obj.title,
                slug=certificate_obj.slug,
                content_db_reference=str(certificate_obj.id),
                external_image_url=external_image_url,
                price=price
            )
            certificate = certificates.first()
        else:
            certificate = Certificate.objects.create(
                course_provider=pg_provider,
                title=certificate_obj.title,
                slug=certificate_obj.slug,
                content_db_reference=str(certificate_obj.id),
                external_image_url=external_image_url,
                price=price,
                content_ready=True
            )

        for course_obj in certificate_obj.courses:
            course = get_course(course_obj.id)
            if not course:
                continue

            certificate_courses = CertificateCourse.objects.filter(certificate=certificate, course=course)
            if not certificate_courses.exists():
                CertificateCourse.objects.create(
                    certificate=certificate,
                    course=course
                )

        return certificate


def create_or_update_courses(course_ids):
    for cid in course_ids:
        course_obj = CourseModel.objects.get(id=cid)

        try:
            image_path = course_obj.image['original']
            image_name = image_path.split('/')[-1]
        except KeyError:
            image_name = ''

        try:
            external_image_url = course_obj.default_image['original']
        except KeyError:
            external_image_url = ''

        try:
            course_provider = CourseProvider.objects.get(content_db_reference=str(course_obj.provider.id))
        except CourseProvider.DoesNotExist:
            course_provider = CourseProvider.objects.create(
                name='Mindedge',
                code='001',
                content_db_reference=str(course_obj.provider.id)
            )

        with scopes_disabled():
            courses = Course.objects.filter(content_db_reference=str(course_obj.id))

            if courses.exists():
                courses.update(
                    course_provider=course_provider,
                    title=course_obj.title,
                    slug=course_obj.slug,
                    content_db_reference=str(course_obj.id),
                    # course_image_uri=image_name,
                    external_image_url=external_image_url
                )
                course = courses.first()
            else:
                course = Course.objects.create(
                    course_provider=course_provider,
                    title=course_obj.title,
                    slug=course_obj.slug,
                    content_db_reference=str(course_obj.id),
                    course_image_uri=image_name,
                    external_image_url=external_image_url
                )

            for section_obj in course_obj.sections:
                try:
                    seat_capacity = int(section_obj.num_seats)
                except ValueError:
                    seat_capacity = 0

                if seat_capacity < 0:
                    seat_capacity = 0

                try:
                    available_seat = int(section_obj.available_seats)
                except ValueError:
                    available_seat = 0

                if available_seat < 0:
                    available_seat = 0

                # check if course and name makes it unique
                sections = Section.objects.filter(course=course, name=section_obj.code)

                if sections.exists():
                    sections.update(
                        course=course,
                        name=section_obj.code,
                        fee=section_obj.course_fee.amount,
                        seat_capacity=seat_capacity,
                        available_seat=available_seat,
                        execution_mode=section_obj.execution_mode,
                        registration_deadline=section_obj.registration_deadline,
                        content_db_reference=str(course_obj.id),
                        is_active=section_obj.is_active,
                    )
                    section = sections.first()
                else:
                    section = Section.objects.create(
                        course=course,
                        name=section_obj.code,
                        fee=section_obj.course_fee.amount,
                        seat_capacity=seat_capacity,
                        available_seat=available_seat,
                        execution_mode=section_obj.execution_mode,
                        registration_deadline=section_obj.registration_deadline,
                        content_db_reference=str(course_obj.id),
                        is_active=section_obj.is_active,
                    )


def create_or_update_store_course_sections():
    store_course_section_objects = []
    with scopes_disabled():
        for store_course in StoreCourse.objects.filter(course__course_provider__name='Mindedge'):
            for section in store_course.course.sections.all():
                try:
                    scs = StoreCourseSection.objects.get(store_course=store_course, section=section)
                except StoreCourseSection.DoesNotExist:
                    scs = StoreCourseSection.objects.create(
                        store_course=store_course,
                        section=section,
                        is_published=True,
                        fee=section.fee,
                        seat_capacity=section.seat_capacity
                    )

                store_course_section_objects.append(scs)
    return store_course_section_objects
