from utils.log import get_logger
from prestashop.prestashop_service import PrestashopService

logger = get_logger(__name__)


class PrestashopProductService(PrestashopService):

    def __init__(self):
        super().__init__('prestashop_product')

    def request_with_body(self, body):
        self._cache = {}
        return self.search_product(body)

    def request_no_body(self):
        self._cache = {}
        return self.search_product()

    def search_product(self, options=None):
        result = []
        products = self._ps.search('products', options)
        for product in products:
            result.append(self.populate_product(product.id))
        return result


prestashop_product = PrestashopProductService()
logger.info('Prestashop service [product] started')
