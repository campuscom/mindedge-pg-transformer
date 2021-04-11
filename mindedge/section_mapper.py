from datetime import datetime, timedelta

from mindedge import helper
from mindedge.import_history_data_keys import ImportHistoryDataKeys
from models.course.course_fee import CourseFee
from models.course.enums import ExecutionModes
from models.course.registration_form_data import RegistrationFormData
from models.course.section import Section

import util
from config.config import Config


def get_course_fee(price):
    return CourseFee(amount=util.to_float(price['list_price']), currency='USD')


def get_registration_form_data(course_item):
    form_url = Config.REGISTRATION_FROM_URL_TPL.format(identifier=Config.IDENTIFIER)

    reg_form_data = RegistrationFormData()
    reg_form_data.form_url = form_url
    reg_form_data.method = 'POST'
    reg_form_data.fields = {
            "cart_courses": course_item['course_id'],
            "ref": Config.REFERENCE
        }
    return reg_form_data


def convert_string_to_hours(length):
    hour = util.to_float(str(length).replace(' hours', ''))
    return hour


class SectionMapper:

    @staticmethod
    def get_section_object(data_object):
        seat_count = -1
        section = Section()
        section.code = str(data_object['course_id'])
        section.description = data_object['title']
        section.details_url = helper.get_external_url(data_object['course_id'], data_object['slug'],
                                                      ImportHistoryDataKeys.suites)
        section.registration_form_data = get_registration_form_data(data_object)
        section.start_date = None
        section.end_date = None
        section.num_seats = seat_count
        section.available_seats = seat_count
        section.execution_mode = ExecutionModes.SELF_PACED.value
        section.execution_site = None
        section.is_active = True
        section.registration_deadline = datetime.now() + timedelta(days=30)  # ToDo: Find a way to add month
        section.instructors = []
        section.schedules = []
        section.course_fee = get_course_fee(data_object['course_price'])
        section.ceu_hours = util.to_float(data_object['ceu'])
        section.load_hours = convert_string_to_hours(data_object['length'])
        return section
