
from typing import List

from cbcservice.cbc_service import CbcTypeService
from utils.log import get_logger
from utils.prestashop import PrestashopSearchElement, PrestashopItemNotFoundException

logger = get_logger(__name__)


class Option:
    def __init__(self, name, value, position, groupType):
        self.name = name
        self.value = value
        self.position = position
        self.groupType = groupType


def parse_options(options_str: str, option_values_str: str) -> List[Option]:
    options = options_str.split(';')
    option_values = option_values_str.split(';')
    result = []
    for idx, item in enumerate(options):
        stripped_options = options[idx].strip()
        stripped_values_options = option_values[idx].strip()
        stripped_options_split = stripped_options.split(':')
        stripped_values_options_split = stripped_values_options.split(':')
        model = Option(stripped_options_split[0], stripped_values_options_split[0], stripped_options_split[2], stripped_options_split[1])
        result.append(model)
    return result


class CbcProductOptionsService(CbcTypeService):

    def __init__(self):
        super().__init__('product_options')

    def find_by_name(self, name: str):
        return self._ps.search_unique(self._resource, {
            'filter[public_name]': name
        })

    def find_or_create(self, model: Option) -> PrestashopSearchElement:
        try:
            result = self.find_by_name(model.name)

        except PrestashopItemNotFoundException as e:
            final_model = self.create_model()
            final_model.name = model.name
            final_model.publicName = model.name
            if (model.groupType == 'Colore'):
                final_model.groupType = 'select'
            else:
                final_model.groupType = model.groupType
            if (model.groupType == 'color'):
                final_model.isColorGroup = 1
            else:
                final_model.isColorGroup = 0
            response = self._ps.add(self._resource, self._build_xml(final_model))
            result = self._ps.build_search_element(response, self._resource)
            logger.info('%s %s has been created correctly' % (self._resource, self._ps.find_id(result)))

        return result


product_options_service = CbcProductOptionsService()
logger.info('Cbc service [product_options] started')


class CbcProductOptionValuesService(CbcTypeService):

    def __init__(self):
        super().__init__('product_option_values')
        self._pos = product_options_service

    def find_by_option_id_and_value(self, option_id: str, value: str):
        return self._ps.search_unique(self._resource, {
            'filter[id_attribute_group]': option_id,
            'filter[name]': value
        })

    def find_or_create(self, model: Option) -> (PrestashopSearchElement, PrestashopSearchElement):
        product_option_model = self._pos.find_or_create(model)
        try:
            result = (product_option_model, self.find_by_option_id_and_value(product_option_model.id, model.value))

        except PrestashopItemNotFoundException as e:
            final_model = self.create_model()
            final_model.name = model.value
            final_model.productOption = product_option_model.id
            response = self._ps.add(self._resource, self._build_xml(final_model))
            result = (product_option_model, self._ps.build_search_element(response, self._resource))
            logger.info('%s %s has been created correctly' % (self._resource, result[1].id))

        return result


product_option_value_service = CbcProductOptionValuesService()
logger.info('Cbc service [product_option_values] started')
