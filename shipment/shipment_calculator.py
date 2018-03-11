from utils.log import get_logger
from utils.prestashop import get_ps


logger = get_logger(__name__)


class DataNotFoundException(Exception):
    pass


class ShipmentCalculator:

    def __init__(self):
        self._ps = get_ps()
        self._cache = {}
        self._boundrys = [
            0.0,
            3.0,
            10.0,
            20.0,
            30.0
        ]

        self._mapping_boundryes = {
            '0.0': 5.7,
            '3.0': 7,
            '10.0': 8,
            '20.0': 9,
            '30.0': 12.60,
        }

    def clean_cache(self):
        logger.info('Cleaning cache fired')
        self._cache = {}

    def calculate(self, product_list: list):
        result = 0.0

        weight = 0.0

        for product_map in product_list:
            product_info = self.product_info(product_map['code'])
            real_weight = self.real_weight(product_info)
            weight = weight + (real_weight * product_map['quantity'])

        if weight >= self._boundrys[len(self._boundrys) - 1]:
            result = self._mapping_boundryes[str(
                self._boundrys[len(self._boundrys) - 1])]

            difference = (
                weight - self._boundrys[len(self._boundrys) - 1]) * 0.3

            result = result + difference

        else:
            for idx, boundry in enumerate(self._boundrys):
                if (weight > boundry or weight == boundry) and weight < self._boundrys[idx + 1]:
                    result = self._mapping_boundryes[str(boundry)]
                    break

        return round(result, 2)

    def product_info(self, product_code):
        product_info = self._cache.get(product_code)
        if product_info is None:
            logger.info('Product [%s] not found in cache' % (product_code))
            element_tree = self._ps.get('products', product_code)
            if element_tree is None:
                message_error = 'Product with code {0} not found'.format(
                    product_code)
                logger.error(message_error)
                raise DataNotFoundException(message_error)
            product_info = {
                'weight': float(element_tree[0].find('weight').text),
                'depth': float(element_tree[0].find('depth').text),
                'height': float(element_tree[0].find('height').text),
                'width': float(element_tree[0].find('width').text)
            }
            self._cache[product_code] = product_info
        else:
            logger.debug('Product [%s] found in cache' % (product_code))
        return product_info

    def real_weight(self, product):
        result = (product.get('depth') * product.get('height')
                  * product.get('width')) / 5000.0

        if (result > product.get('weight')):
            return result
        else:
            return product.get('weight')


shipment_calculator = ShipmentCalculator()
logger.info('Cbc service [products] started')
