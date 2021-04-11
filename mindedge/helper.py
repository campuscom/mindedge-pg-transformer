from config.config import Config


def get_external_url(item_id, item_slug, item_type):
    catalog_url = Config.CATALOG_URL_TPL.format(identifier=Config.IDENTIFIER)
    return f"{catalog_url}/{item_type}/{item_id}/{item_slug}"
