from typing import List

from firebase import firebase

from utils.config import get_config
from utils.log import get_logger

logger = get_logger(__name__)


class Storage:

    def __init__(self):
        self._firebase_config = get_config()['firebase']
        self._firebase = firebase.FirebaseApplication(
            self._firebase_config['databaseURL'], None)
        logger.info("Firebase initialized correctly")

    def _get_db(self):
        return self._firebase

    def latest_version(self, resource: str):
        version = self._get_db().get("/versions/%s" % (resource), None)
        logger.debug(
            'Latest version for resource [%s]: %s' % (resource, version))
        return version

    def get_items_latest_version(self, resource: str) -> List:
        version = self.latest_version(resource)
        all = self.get_items(resource)
        result = filter(lambda x: x.get('version') == version, all)
        return result

    def get_items_older_version(self, resource: str) -> List:
        version = self.latest_version(resource)
        all = self.get_items(resource)
        result = filter(lambda x: x.get('version') != version, all)
        return result

    def get_items(self, resource: str) -> List:
        logger.debug('Getting items for resource [%s]' % (resource))
        all = self._get_db().get('/data/%s' % (resource), None)
        return filter(lambda x: not(x is None), all)

    def update_prestashop_id(self, resource: str, id: str, prestashop_id: str):
        logger.debug('Updating resource [%s] id [%s] with prestashop id [%a]' % (
            resource, id, prestashop_id))
        return self._get_db().patch()('/data/%s/%s', {
            'prestashopId': prestashop_id
        })

    def delete_item_by_id(self, resource: str, id: str):
        logger.debug('Delete resource [%s] with id [%s]' % (resource, id))
        self._get_db().remove('/data/%s/%s' % (resource, id), None)

    def get_item_by_id(self, resource, id):
        logger.debug('Get resource [%s] with id [%s]' % (resource, id))
        return self._get_db().get('/data/%s/%s' % (resource, id), None)


storage = Storage()
logger.info("Module [storage] started correctly")


def get_storage():
    return storage
