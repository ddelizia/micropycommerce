import unittest
# from mock import Mock, patch
from ebay.ebay_service_category import ebay_service_category


class TestEbayCategories(unittest.TestCase):

    def test_categories_all(self):
        all_categories = ebay_service_category.categories()
        self._test_categories_internal(all_categories)

    def test_category_specific(self):
        all_categories = ebay_service_category.categories(parent_id='8392')
        self._test_categories_internal(all_categories)

    def _test_categories_internal(self, all_categories):
        self.assertIsNotNone(all_categories)
        self.assertEqual(type(all_categories), list)
        self.assertGreater(len(all_categories), 0)
        self.assertEqual(type(all_categories[0]), dict)

        for current_category in all_categories:
            self.assertIsNotNone(current_category['categoryPath'])
            current_category_result = current_category['categoryResult']
            self.assertIsNotNone(current_category_result)
            self.assertEqual(type(current_category_result), list)

            self.assertIsNotNone(current_category_result[len(
                current_category_result) - 1].get('LeafCategory'))
