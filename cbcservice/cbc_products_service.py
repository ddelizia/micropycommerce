import re
from xml.etree import ElementTree

import munch

from cbcservice.cbc_categories_service import category_service
from cbcservice.cbc_manufacturers_service import manufacturers_service
from cbcservice.cbc_features_service import product_feature_values_service
from cbcservice.cbc_service import CbcTypeService
from utils.log import get_logger
from utils.prestashop import PrestashopItemNotFoundException, PrestashopSearchElement
from utils.template import compile

logger = get_logger(__name__)


class ProductUploadException(Exception):
    pass


class CbcProductsService(CbcTypeService):

    def __init__(self):
        super().__init__('products')
        self._cs = category_service
        self._ms = manufacturers_service
        self._fs = product_feature_values_service

    def find_by_reference(self, name: str):
        return self._ps.search_unique(self._resource, {
            'filter[reference]': name
        })

    def upload_single(self, model: munch.Munch):
        try:
            product = self.find_by_id_or_reference(model)
            model.prestashopId = product.id
            result = self._ps.edit(
                self._resource, model.prestashopId, self._build_xml(model))
            logger.info('%s %s has been edited correctly' %
                        (self._resource, self._ps.find_id(result)))

            images = result[0].find('associations').find('images')
            for image in images:
                image_id = image[0].text
                self._ps.delete_image(self._resource, '%s/%s' %
                                      (model.prestashopId, image_id))
        except PrestashopItemNotFoundException as e:
            logger.debug('Resource [%s] id [%s] not found in db' % (
                self._resource, product.id))
            result = self._ps.add(self._resource, self._build_xml(model))
            model.prestashopId = self._ps.find_id(result)
            logger.info('%s %s has been created correctly' %
                        (self._resource, self._ps.find_id(result)))

        data = self._ps.build_search_element(result, self._resource)
        self._ss.update_prestashop_id(self._resource, model.id, data.id)
        self.update_stock(model, result)
        self.update_specific_price(model, result)

        # Upload product image
        images = self._image_service.get_image_for_code(model.id)
        for image in images:
            self._ps.add_image(self._resource, model.prestashopId, image)
        return data

    def transform_from_dict(self, dict: dict) -> munch.Munch:
        base = super().transform_from_dict(dict)
        if not base.get('width') or not base.get('height') or not base.get('depth') or not base.get('weight'):
            raise ProductUploadException(
                'Some dimention is missing for %s' % (base.id))

        if not base.get('priceWithDiscount'):
            raise ProductUploadException(
                'Price with discount missing for %s' % (base.id))

        if not base.get('reference'):
            if base.get('upc') == 0:
                base.reference = None
            elif not(base.get('upc') is None):
                base.reference = str(base.get('upc')).strip()
            else:
                base.reference = None
            base.upc = None

        base.name = base.name.strip()

        base.linkRewrite = re.sub('[^0-9a-zA-Z]+', '-', base.name.lower())
        base.metaTitle = '%s - %s' % (base.name, base.manufacturerName)

        if not base.priceNoDiscount:
            base.priceNoDiscount = base.priceWithDiscount

        base.finalPriceNoDiscount = round(
            (base.priceNoDiscount * 0.03) + base.priceNoDiscount, 2)
        base.finalPriceWithDiscount = round(
            (base.priceWithDiscount * 0.03) + base.priceWithDiscount, 2)

        base.discountPrice = base.finalPriceNoDiscount - base.finalPriceWithDiscount
        base.discountPercentage = round(
            (base.discountPrice / base.finalPriceNoDiscount), 2)
        base.price = round(base.finalPriceNoDiscount / 1.22, 2)

        if base.discountPercentage > 0:
            base.isOnSale = 1
        else:
            base.isOnSale = 0

        # get Category
        categories_split = base.categoryTree.split(';')
        categories = []
        for category in categories_split:
            categories.append(self._cs.find_by_name(category))
        if (len(categories) == 0):
            raise ProductUploadException(
                'No categories available for %s' % (base.id))
        base.categories = categories
        base.mainCategory = categories[0]

        # get Manufacturer
        manufacturer = self._ms.find_by_name(base.manufacturerName)
        if (manufacturer is None):
            raise ProductUploadException(
                'No manufacturer available available %s' % (base.id))
        base.manufacturer = manufacturer

        # features
        features = []
        """
        features_object = parse_feature(base.featureNames)
        for feature in features_object:
            db_feature = self._fs.find_or_create(feature)
            features.append({
                'feature': db_feature[0].id,
                'featureValue': db_feature[1].id
            })
        """
        base.features = features

        return base

    def find_by_id_or_reference(self, model: munch.Munch) -> PrestashopSearchElement:
        if not(model.get('prestashopId' is None)):
            product = self._ps.get(
                self._resource, resource_id=model.prestashopId)
            return self._ps.build_search_element(product, self._resource)
        if not model.reference:
            raise PrestashopItemNotFoundException('No reference found')
        return self._ps.search_unique(self._resource, {
            'filter[reference]': model.reference
        })

    def update_stock(self, model: munch.Munch, product_xml: ElementTree):
        stock_id = product_xml[0].find('associations').find(
            'stock_availables')[0].find('id').text
        data = self.create_model()
        data.quantity = model.quantity
        data.idProduct = product_xml[0].find('id').text
        data.stockId = stock_id

        self._ps.edit('stock_availables', data.stockId, compile(
            'prestashop', 'stock_availables.xml', data.toDict()), {'id': stock_id})

    def update_specific_price(self, model: munch.Munch, product_xml: ElementTree):
        if model.isOnSale != 0:
            data = self.create_model()
            data.idProduct = product_xml[0].find('id').text
            data.discount = model.discountPercentage
            try:
                specific_price = self._ps.search_unique('specific_prices', {
                    'filter[id_product]': data.idProduct
                })
                data.id = specific_price.id
                self._ps.edit('specific_prices', data.id, compile(
                    'prestashop', 'specific_prices.xml', data.toDict()))
            except PrestashopItemNotFoundException as ex:
                self._ps.add('specific_prices', compile(
                    'prestashop', 'specific_prices.xml', data.toDict()))


products_service = CbcProductsService()
logger.info('Cbc service [products] started')
