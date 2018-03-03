from typing import List

from cbcservice.cbc_service import CbcTypeService
from utils.log import get_logger
from utils.prestashop import PrestashopSearchElement, PrestashopItemNotFoundException

logger = get_logger(__name__)


class Feature:
    def __init__(self, name, value, position):
        self.name = name
        self.value = value
        self.position = position


def parse_feature(features: str) -> List[Feature]:
    features = features.split(';')
    result = []
    for feature in features:
        stripped_feature = feature.strip()
        feature_split = stripped_feature.split(':')
        stripped_feature = Feature(feature_split[0], feature_split[1], feature_split[2])
        result.append(stripped_feature)
    return result


class CbcProductFeaturesService(CbcTypeService):

    def __init__(self):
        super().__init__('product_features')

    def find_by_name(self, name: str):
        return self._ps.search_unique(self._resource, {
            'filter[name]': name
        })

    def find_or_create(self, model: Feature) -> PrestashopSearchElement:
        try:
            result = self.find_by_name(model.name)

        except PrestashopItemNotFoundException as e:
            final_model = self.create_model()
            final_model.name = model.name
            response = self._ps.add(self._resource, self._build_xml(final_model))
            result = self._ps.build_search_element(response, self._resource)
            logger.info('%s %s has been created correctly' % (self._resource, self._ps.find_id(result)))

        return result


product_feature_service = CbcProductFeaturesService()
logger.info('Cbc service [product_features] started')


class CbcProductFeatureValuesService(CbcTypeService):

    def __init__(self):
        super().__init__('product_feature_values')
        self._pfs = product_feature_service

    def find_by_feature_id_and_value(self, feature_id: str, value: str):
        return self._ps.search_unique(self._resource, {
            'filter[id_feature]': feature_id,
            'filter[value]': value
        })

    def find_or_create(self, model: Feature) -> (PrestashopSearchElement, PrestashopSearchElement):
        product_feature_model = self._pfs.find_or_create(model)
        try:
            result = (product_feature_model, self.find_by_feature_id_and_value(product_feature_model.id, model.value))

        except PrestashopItemNotFoundException as e:
            final_model = self.create_model()
            final_model.value = model.value
            final_model.feature = product_feature_model.id
            response = self._ps.add(self._resource, self._build_xml(final_model))
            result = (product_feature_model, self._ps.build_search_element(response, self._resource))
            logger.info('%s %s has been created correctly' % (self._resource, self._ps.find_id(result)))

        return result


product_feature_values_service = CbcProductFeatureValuesService()
logger.info('Cbc service [product_feature_values] started')
