from utils.prestashop import get_ps
from utils.log import get_logger
from prestashop import schema
from utils.helper import cast
import graphene


logger = get_logger(__name__)


class PrestashopService:

    def __init__(self):
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
        return self._call_with_cache('products', code, self._populate_product)

    def _populate_product(self, code):
        prestashop_product = self._ps.get('products', code)
        item = schema.PrestashopProduct()
        item.id = self._get_value(prestashop_product, 'id')
        item.price = cast(self._get_value(prestashop_product, 'price'), float)
        item.name = self._get_localized_value(prestashop_product, 'name')
        item.shortDescription = self._get_localized_value(
            prestashop_product, 'description_short')
        item.description = self._get_localized_value(
            prestashop_product, 'description')
        item.manufacturer = self.populate_manufacturer(
            self._get_value(prestashop_product, 'id_manufacturer'))
        item.categories = self._get_association(
            prestashop_product, 'categories', self.populate_category)
        item.images = self._get_association(
            prestashop_product, 'images', None, is_image=True)
        item.combinations = self._get_association(
            prestashop_product, 'combinations', self.populate_combination)
        item.defaultImage = schema.PrestashopImage
        item.defaultImage.url = prestashop_product[0].find(
            'id_default_image').attrib['{http://www.w3.org/1999/xlink}href']
        item.defaultCombination = self._get_value(
            prestashop_product, 'id_default_combination')
        return item

    def populate_language(self, code):
        return self._call_with_cache('languages', code, self._populate_language)

    def _populate_language(self, code):
        prestashop_language = self._ps.get('languages', code)
        item = schema.PrestashopLanguage()
        item.id = self._get_value(prestashop_language, 'id')
        item.isoCode = self._get_value(prestashop_language, 'iso_code')
        return item

    def populate_manufacturer(self, code):
        return self._call_with_cache('manufacturers', code, self._populate_manufacturer)

    def _populate_manufacturer(self, code):
        prestashop_manufacturer = self._ps.get('manufacturers', code)
        item = schema.PrestashopManufacturer()
        item.id = self._get_value(prestashop_manufacturer, 'id')
        item.name = self._get_value(prestashop_manufacturer, 'name')
        item.active = cast(self._get_value(
            prestashop_manufacturer, 'active'), bool)
        item.shortDescription = self._get_localized_value(
            prestashop_manufacturer, 'short_description')
        item.description = self._get_localized_value(
            prestashop_manufacturer, 'description')
        return item

    def populate_combination(self, code):
        return self._call_with_cache('combinations', code, self._populate_combination)

    def _populate_combination(self, code):
        prestashop_combination = self._ps.get('combinations', code)
        item = schema.PrestashopCombination()
        item.id = self._get_value(prestashop_combination, 'id')
        item.quantity = cast(self._get_value(
            prestashop_combination, 'quantity'), int)
        item.reference = self._get_value(prestashop_combination, 'reference')
        item.price = cast(self._get_value(
            prestashop_combination, 'price'), float)
        item.options = self._get_association(
            prestashop_combination, 'product_option_values', self.populate_product_option_value)
        item.images = self._get_association(
            prestashop_combination, 'images', None, is_image=True)
        return item

    def populate_product_option_value(self, code):
        return self._call_with_cache('product_option_values', code, self._populate_product_option_value)

    def _populate_product_option_value(self, code):
        prestashop_product_option_value = self._ps.get(
            'product_option_values', code)
        item = schema.PrestashopOptionValue()
        item.id = self._get_value(prestashop_product_option_value, 'id')
        item.value = self._get_localized_value(
            prestashop_product_option_value, 'name')
        item.option = self.populate_product_option(self._get_value(
            prestashop_product_option_value, 'id_attribute_group'))
        return item

    def populate_product_option(self, code):
        return self._call_with_cache('product_options', code, self._populate_product_option)

    def _populate_product_option(self, code):
        prestashop_product_option = self._ps.get('product_options', code)
        item = schema.PrestashopOption()
        item.id = self._get_value(prestashop_product_option, 'id'),
        item.name = self._get_localized_value(
            prestashop_product_option, 'name')
        return item

    def populate_category(self, code):
        return self._call_with_cache('categories', code, self._populate_category)

    def _populate_category(self, code):
        prestashop_category = self._ps.get('categories', code)
        item = schema.PrestashopCategory()
        item.id = self._get_value(prestashop_category, 'id')
        item.name = self._get_localized_value(prestashop_category, 'name')
        return item

    def _get_value(self, result, field):
        return result[0].find(field).text

    def _get_localized_value(self, result, field):
        data = []
        for field in result[0].find(field):
            item = schema.PrestashopLocalizedValue()
            item.value = field.text
            language = self.populate_language(field.attrib.get('id'))
            item.isoCode = language.isoCode
            item.id = language.id
            data.append(item)
        return data

    def _get_association(self, result, association_name, mapping_function, is_image=False):
        items = []
        for association in result[0].find('associations').find(association_name):
            if is_image is True:
                item = schema.PrestashopImage()
                item.url = association.attrib['{http://www.w3.org/1999/xlink}href']
            else:
                item = mapping_function(association[0].text)
            items.append(item)
        return items

    def search_products(self, id=None, options=None):
        result = []
        if id is None:
            products = self._ps.search('products', options)
            for product in products:
                result.append(self.populate_product(product.id))
        else:
            result.append(self.populate_product(id))
        return result

    def search_categories(self, id=None, options=None):
        result = []
        if id is None:
            categories = self._ps.search('categories', options)
            for category in categories:
                result.append(self.populate_category(category.id))
        else:
            result.append(self.populate_category(id))
        return result

    def search_manufacturers(self, id=None, options=None):
        result = []
        if id is None:
            manufacturers = self._ps.search('manufacturers', options)
            for manufacturer in manufacturers:
                result.append(self.populate_manufacturer(manufacturer.id))
        else:
            result.append(self.populate_manufacturer(id))
        return result


prestashop_service = PrestashopService()
logger.info('Prestashop service started')


def populate_options(query=None):
    options = None
    if not(query is None):
        options = {}
        for element in query:
            options[element.key] = element.value


class QueryPrestashop(graphene.ObjectType):

    prestashopProducts = graphene.Field(
        graphene.List(schema.PrestashopProduct), id=graphene.String(), query=graphene.List(schema.PrestashopQuery))

    prestashopCategories = graphene.Field(
        graphene.List(schema.PrestashopCategory), id=graphene.String(), query=graphene.List(schema.PrestashopQuery))

    prestashopManufacturers = graphene.Field(
        graphene.List(schema.PrestashopManufacturer), id=graphene.String(), query=graphene.List(schema.PrestashopQuery))

    def resolve_prestashopProducts(self, info, id=None, query=None):
        return prestashop_service.search_products(id=id, options=populate_options(query))

    def resolve_prestashopCategories(self, info, id=None, query=None):
        return prestashop_service.search_categories(id=id, options=populate_options(query))

    def resolve_prestashopManufacturers(self, info, id=None, query=None):
        return prestashop_service.search_manufacturers(id=id, options=populate_options(query))
