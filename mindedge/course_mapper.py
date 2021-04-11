import logging

from bs4 import BeautifulSoup
from mindedge import BaseMapperMixin
from mindedge import helper
from mindedge.import_history_data_keys import ImportHistoryDataKeys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def render_list_item(item, item_transformer=None):
    item = item_transformer(item) if item_transformer else item
    return f"<li>{item}</li>"


def render_data_item(item, item_transformer=None):
    item = item_transformer(item) if item_transformer else item
    return f'<dt>{item["term"]}</dt><dd>{item["definition"]}</dd>'


def render_list(list, title, h_tag="h3", list_tag="ul", item_renderer=render_list_item, item_transformer=None):
    html = ''
    if title:
        html += f"<{h_tag}>{title}</{h_tag}>"
    html += f'<{list_tag}>' + "".join(map(lambda item: item_renderer(item, item_transformer), list)) + f'</{list_tag}>'
    return html


def transform_certification(certification):
    return render_list(
        certification["credit_values"],
        title=f'{certification["certification_type"]} &mdash; {certification["total"]} credits',
        h_tag="h4",
        item_transformer=(lambda credit: f'{credit["credit_name"]} &mdash; {credit["credit_value"]} credit(s)'))


def html_to_text(html):
    soup = BeautifulSoup(html, features="html.parser")
    return soup.get_text()


# def set_prop_if_not_set(target, prop, value):
#     if getattr(target, prop, None) is None:
#         target.prop = value


class CourseMapper(BaseMapperMixin):

    def __init__(self, provider):
        self.provider = provider

    def map(self, data_object):
        try:
            from_importer = True
            external_id = str(data_object.get('course_id'))
            slug = data_object.get('slug')
            external_url = helper.get_external_url(external_id, slug, ImportHistoryDataKeys.suites)
            external_version_id = '0'
            code = str(data_object.get('course_id'))
            title = html_to_text(data_object.get('title'))
            description = f"<p>{data_object.get('short_description')}</p>" \
                          + render_list(data_object.get('course_features'), "Features") \
                          + render_list(data_object.get('course_topics'), "Topics") \
                          + render_list(data_object.get('course_outcomes'), "Outcomes") \
                          + render_list(data_object.get('course_certifications'), "Certifications",
                                        item_transformer=transform_certification)
            default_image = {
                'original': data_object.get('icon', None)
            }
            # sections = [get_section_object(data_object)]

            mapped_item = {
                "provider": self.provider,
                "from_importer": from_importer,
                "external_id": external_id,
                "external_url": external_url,
                "external_version_id": external_version_id,
                "code": code,
                "title": title,
                "slug": slug,
                "description": description,
                "default_image": default_image,
                # "sections": sections,
            }

            return mapped_item
        except Exception as error:
            logger.error(f"Error in mapping course: {error}")
            raise error
