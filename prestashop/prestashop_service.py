from utils.prestashop import get_ps
from utils.ws import Ws
from utils.log import get_logger

logger = get_logger(__name__)


class PrestashopService(Ws):

    def __init__(self, name):
        super().__init__('prestashop_product')
        self._cache = {}
        self._ps = get_ps()

    def _call_with_cache(self, cache_name, code, method):
        if self._cache.get(cache_name) is None:
            self._cache[cache_name] = {}
        if self._cache[cache_name].get(code) is None:
            result = method(code)
            self._cache[cache_name][code] = result
            return result
        else:
            return self._cache[cache_name].get(code)

    def get_product(self, prestashop_product_code=None, spreadsheet_product_code=None):
        product_code = prestashop_product_code
        return self.populate_product(product_code)

    def populate_product(self, code):
        return self._call_with_cache('languages', code, self._populate_product)

    def _populate_product(self, code):
        prestashop_product = self._ps.get('products', code)
        item = {
            'id': self._get_value(prestashop_product, 'id'),
            'price': self._get_value(prestashop_product, 'price'),
            'name': self._get_localized_value(prestashop_product, 'name'),
            'shortDescription': self._get_localized_value(prestashop_product, 'description_short'),
            'description': self._get_localized_value(prestashop_product, 'description'),
            'manufacturer': self.populate_manufacturer(self._get_value(prestashop_product, 'id_manufacturer')),
            'categories': self._get_association(prestashop_product, 'categories', self.populate_category),
            'images': self._get_association(prestashop_product, 'images', None, is_image=True),
            'combinations': self._get_association(prestashop_product, 'combinations', self.populate_combination),
            'defaultImage': prestashop_product[0].find('id_default_image').attrib['{http://www.w3.org/1999/xlink}href'],
            'defaultCombination': self._get_value(prestashop_product, 'id_default_combination'),
        }
        return item

    def populate_language(self, code):
        return self._call_with_cache('languages', code, self._populate_language)

    def _populate_language(self, code):
        prestashop_language = self._ps.get('languages', code)
        item = {
            'id': self._get_value(prestashop_language, 'id'),
            'iso_code': self._get_value(prestashop_language, 'iso_code'),
        }
        return item

    def populate_manufacturer(self, code):
        return self._call_with_cache('manufacturers', code, self._populate_manufacturer)

    def _populate_manufacturer(self, code):
        prestashop_manufacturer = self._ps.get('manufacturers', code)
        item = {
            'id': self._get_value(prestashop_manufacturer, 'id'),
            'name': self._get_localized_value(prestashop_manufacturer, 'name'),
            'active': self._get_value(prestashop_manufacturer, 'active')
        }
        return item

    def populate_combination(self, code):
        return self._call_with_cache('combinations', code, self._populate_combination)

    def _populate_combination(self, code):
        prestashop_combination = self._ps.get('combinations', code)
        item = {
            'id': self._get_value(prestashop_combination, 'id'),
            'quantity': self._get_value(prestashop_combination, 'quantity'),
            'reference': self._get_value(prestashop_combination, 'reference'),
            'price': self._get_value(prestashop_combination, 'price'),
            'options': self._get_association(prestashop_combination, 'product_option_values', self.populate_product_option_value),
            'images': self._get_association(prestashop_combination, 'images', None, is_image=True)
        }
        return item

    def populate_product_option_value(self, code):
        return self._call_with_cache('product_option_values', code, self._populate_product_option_value)

    def _populate_product_option_value(self, code):
        prestashop_product_option_value = self._ps.get(
            'product_option_values', code)
        item = {
            'id': self._get_value(prestashop_product_option_value, 'id'),
            'value': self._get_localized_value(prestashop_product_option_value, 'name'),
            'option': self.get_product_option(self._get_value(prestashop_product_option_value, 'id_attribute_group')),
        }
        return item

    def populate_product_option(self, code):
        return self._call_with_cache('product_options', code, self._populate_product_option)

    def _populate_product_option(self, code):
        prestashop_product_option = self._ps.get('product_options', code)
        item = {
            'id': self._get_value(prestashop_product_option, 'id'),
            'name': self._get_localized_value(prestashop_product_option, 'name'),
        }
        return item

    def populate_category(self, code):
        return self._call_with_cache('categories', code, self._populate_category)

    def _populate_category(self, code):
        prestashop_manufacturer = self._ps.get('categories', code)
        item = {
            'id': self._get_value(prestashop_manufacturer, 'id'),
            'name': self._get_localized_value(prestashop_manufacturer, 'name')
        }
        return item

    def _get_value(self, result, field):
        return result[0].find(field).text

    def _get_localized_value(self, result, field):
        data = {}
        for field in result[0].find(field):
            language_id = field.attrib.get('id')
            data[self.populate_language(language_id)['iso_code']] = field.text
        return data

    def _get_association(self, result, association_name, mapping_function, is_image=False):
        items = []
        for association in result[0].find('associations').find(association_name):
            if is_image is True:
                item = association.attrib['{http://www.w3.org/1999/xlink}href']
            else:
                item = mapping_function(association[0].text)
            items.append(item)
        return items
