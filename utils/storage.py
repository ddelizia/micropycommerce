from typing import List

import pyrebase

from utils.config import get_config
from utils.log import get_logger

logger = get_logger(__name__)

_firebase_config = get_config()['firebase']
_firebase = pyrebase.initialize_app(_firebase_config)

logger.info("Firebase initialized correctly")


class Storage:

    def _get_db(self):
        return _firebase.database()

    def latest_version(self, resource: str):
        version = self._get_db().child("versions").child(resource).get().val()
        logger.debug('Latest version for resource [%s]: %s' % (resource, version))
        return version

    def get_items_latest_version(self, resource: str) -> List:
        version = self.latest_version(resource)
        response = self.get_items(resource)
        result = []
        if not(response is None):
            for k in response:
                if not(k is None) and k.get('version') == version:
                    result.append(k)
        return result

    def get_items_older_version(self, resource: str) -> List:
        version = self.latest_version(resource)
        response = self.get_items(resource)
        result = []
        if not(response is None):
            for k in response:
                if not(k is None) and k.get('version') != version:
                    result.append(k)
        return result

    def get_items(self, resource: str) -> List:
        logger.debug('Getting items for resource [%s]' % (resource))
        return self._get_db().child('data').child(resource).order_by_child('id').get().val()

    def update_prestashop_id(self, resource: str, id: str, prestashop_id: str):
        logger.debug('Updating resource [%s] id [%s] with prestashop id [%a]' % (resource, id, prestashop_id))
        return self._get_db().child('data').child(resource).child(id).update({
            'prestashopId': prestashop_id
        })

    def delete_item_by_id(self, resource: str, id: str):
        logger.debug('Delete resource [%s] with id [%s]' % (resource, id))
        self._get_db().child('data').child(resource).child(id).remove()

    def get_item_by_id(self, resource, id):
        logger.debug('Get resource [%s] with id [%s]' % (resource, id))
        return self._get_db().child('data').child(resource).child(id).get().val()


storage = Storage()
logger.info("Module [storage] started correctly")


def get_storage():
    return storage
