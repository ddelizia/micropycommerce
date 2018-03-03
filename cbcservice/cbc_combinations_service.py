from xml.etree.ElementTree import ElementTree

import munch

from cbcservice.cbc_options_service import product_option_value_service
from cbcservice.cbc_options_service import parse_options
from cbcservice.cbc_service import CbcTypeService, UploadResult
from utils.log import get_logger
from utils.prestashop import PrestashopSearchElement, PrestashopItemNotFoundException
from utils.template import compile

logger = get_logger(__name__)


class CombinationsUploadException(Exception):
    pass


class CbcCombinationsService(CbcTypeService):
    _cache = []

    def __init__(self):
        super().__init__('combinations')
        self._os = product_option_value_service

    def upload_all_from_firebase(self) -> UploadResult:
        self._cache = []
        return super().upload_all_from_firebase()

    def transform_from_dict(self, dict: dict) -> munch.Munch:
        base = super().transform_from_dict(dict)
        product_object = self._ss.get_item_by_id('products', base.productId)

        if (base.productId in self._cache):
            base.default = 0
        else:
            base.default = 1
            self._cache.append(base.productId)

        base.priceWithDiscount = product_object.get('priceWithDiscount')
        base.priceNoDiscount = product_object.get('priceNoDiscount')
        if not base.priceNoDiscount:
            base.priceNoDiscount = base.priceWithDiscount

        base.finalPriceNoDiscount = round((base.priceNoDiscount * 0.03) + base.priceNoDiscount, 2)
        base.finalPriceWithDiscount = round((base.priceWithDiscount * 0.03) + base.priceWithDiscount, 2)

        base.discountPrice = base.finalPriceNoDiscount - base.finalPriceWithDiscount
        base.discountPercentage = round((base.discountPrice / base.finalPriceNoDiscount), 2)
        base.price = round(base.finalPriceNoDiscount / 1.22, 2)

        if base.discountPercentage > 0:
            base.isOnSale = 1
        else:
            base.isOnSale = 0

        base.productPrestashopId = product_object.get('prestashopId')
        if (base.productPrestashopId is None):
            raise CombinationsUploadException('Product %s not found' % (base.productPrestashopId))

        base.options = []

        options = parse_options(base.combinationKey, base.combinationValue)
        for option in options:
            option_prestashop = self._os.find_or_create(option)
            base.options.append({
                'optionId': option_prestashop[0].id,
                'optionValueId': option_prestashop[1].id
            })

        return base

    def upload_single(self, model: munch.Munch):
        try:
            combination = self.find_by_id_or_reference(model)
            model.prestashopId = combination.id
            result = self._ps.edit(self._resource, model.prestashopId, self._build_xml(model))
            logger.info('%s %s has been edited correctly' % (self._resource, self._ps.find_id(result)))

        except PrestashopItemNotFoundException as e:
            result = self._ps.add(self._resource, self._build_xml(model))
            model.prestashopId = self._ps.find_id(result)
            logger.info('%s %s has been created correctly' % (self._resource, self._ps.find_id(result)))

        self.update_specific_price(model, result)

        # Upload product image
        images = self._image_service.get_image_for_code(model.reference)
        image_ids = []
        for image in images:
            image_xml = self._ps.add_image('products', model.prestashopId, model.productPrestashopId, image)
            image_ids.append({
                'id': image_xml[0][0].text
            })

        if len(image_ids) > 0:
            model.images = image_ids
            result = self._ps.edit(self._resource, self._build_xml(model))

        data = self._ps.build_search_element(result, self._resource)
        self._ss.update_prestashop_id(self._resource, model.id, data.id)
        return data

    def find_by_id_or_reference(self, model: munch.Munch) -> PrestashopSearchElement:
        if (not(model.get('prestashopId') is None)):
            combination = self._ps.get(self._resource, resource_id=model.prestashopId)
            return self._ps.build_search_element(combination, self._resource)
        else:
            pass
        return self._ps.search_unique(self._resource, {
            'filter[reference]': model.reference
        })

    def update_specific_price(self, model: munch.Munch, combination_xml: ElementTree):
        if model.isOnSale != 0:
            data = self.create_model()
            data.idProduct = combination_xml[0].find('id_product').text
            data.idProductAttribute = combination_xml[0].find('id').text
            data.discount = model.discountPercentage
            try:
                # Delete specific price for products
                specific_price = self._ps.search_unique('specific_prices', {
                    'filter[id_product]': data.idProduct,
                    'filter[id_product_attribute]': "''"
                })
                self._ps.delete('specific_prices', specific_price.id)
            except PrestashopItemNotFoundException as ex:
                logger.debug('No special price found for products attribute')
            try:
                specific_price = self._ps.search_unique('specific_prices', {
                    'filter[id_product]': data.idProduct,
                    'filter[id_product_attribute]': data.idProductAttribute
                })
                data.id = specific_price.id
                self._ps.edit('specific_prices', data.id, compile('./handlebars/%s.xml' % ('specific_prices'), data.toDict()))
            except PrestashopItemNotFoundException as ex:
                self._ps.add('specific_prices', compile('./handlebars/%s.xml' % ('specific_prices'), data.toDict()))


combinations_service = CbcCombinationsService()
logger.info('Cbc service [combinations] started')
