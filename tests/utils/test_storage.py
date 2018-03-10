from utils.storage import get_storage
import unittest


class TestStorage(unittest.TestCase):

    _resources = [
        'categories',
        'combinations',
        'manufacturers',
        'products']

    def test_connection(self):
        firebase = get_storage()._firebase
        versions = firebase.get('/versions', None)
        data = firebase.get('/data', None)
        for resource in self._resources:
            self.assertIsNotNone(versions.get(resource))
            self.assertIsNotNone(data.get(resource))

    def test_latest_version(self):
        for resource in self._resources:
            self.assertEqual(type(get_storage().latest_version(resource)), int)

    def test_get_items(self):
        for resource in self._resources:
            results = get_storage().get_items(resource)
            self.assertTrue(type(results), list)
            for result in results:
                self.assertIsNotNone(result)

    def test_get_items_latest_version(self):
        for resource in self._resources:
            results = get_storage().get_items_latest_version(resource)
            latest_version = get_storage().latest_version(resource)
            for result in results:
                self.assertEqual(result.get('version'), latest_version)

    def test_get_items_older_version(self):
        for resource in self._resources:
            results = get_storage().get_items_older_version(resource)
            latest_version = get_storage().latest_version(resource)
            for result in results:
                self.assertNotEqual(result.get('version'), latest_version)

    def test_get_item_by_id(self):
        firebase = get_storage()._firebase
        for resource in self._resources:
            data = firebase.get('/data', None).get(resource)
            not_none_element_id = 0
            for element in data:
                if not(element is None):
                    not_none_element_id = element.get('id')
                    break
            result = get_storage().get_item_by_id(resource, not_none_element_id)
            self.assertIsNotNone(result.get('id'))
