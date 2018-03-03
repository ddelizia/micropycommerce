import glob
import re

import munch

from cbcservice.cbc_service import CbcTypeService
from utils.log import get_logger
from utils.prestashop import PrestashopItemNotFoundException, PrestashopSearchElement
from utils.ws import Ws

logger = get_logger(__name__)


class CbcManufacturersService(CbcTypeService, Ws):

    def __init__(self):
        super().__init__('manufacturers')

    def upload_single(self, model: munch.Munch):

        try:
            # Search category by name
            manufacturer = self.find_by_id_or_name(model)

            # Update the cateogry information
            model.prestashopId = manufacturer.id
            model.linkRewrite = None
            self._ps.delete_image(self._resource, model.prestashopId)
            result = self._ps.edit(self._resource, model.prestashopId, self._build_xml(model))
            logger.info('%s %s has been edited correctly' % (self._resource, self._ps.find_id(result)))

        except PrestashopItemNotFoundException as e:
            # if category does not exists then create it
            result = self._ps.add(self._resource, self._build_xml(model))
            model.prestashopId = self._ps.find_id(result)
            logger.info('%s %s has been created correctly' % (self._resource, self._ps.find_id(result)))

        data = self._ps.build_search_element(result, self._resource)
        self._ss.update_prestashop_id(self._resource, model.id, data.id)

        image_paths = glob.glob('/Users/ddelizia/Downloads/produttori/%s.*' % (model.id))
        for image_path in image_paths:
            self._ps.add_image('manufacturers', model.prestashopId, image_path)
        return data

    def transform_from_dict(self, dict: dict) -> munch.Munch:
        base = super().transform_from_dict(dict)
        # chardet.detect(bytes(base.description))
        try:
            base.description = base.description.encode('latin-1').decode('latin-1', 'ignore')
        except UnicodeEncodeError as e:
            base.description = base.description.encode('utf-8').decode('latin-1', 'ignore')

        base.shortDescription = "%s: scopri i prodotti delle migliori marche a prezzi competitivi. Vendita %s con consegna a " \
                                "domicilio in pochi giorni." % (base.name, base.name)
        base.metaDescription = "%s | casabagnoclick.com" % (base.shortDescription)
        base.metaTitle = "%s | casabagnoclick.com" % (base.name)
        base.linkRewrite = re.sub('[^0-9a-zA-Z]+', '-', base.name.lower())

        return base

    def find_by_id_or_name(self, model: munch.Munch) -> PrestashopSearchElement:
        if (not(model.get('prestashopId') is None)):
            manufacturer = self._ps.get(self._resource, resource_id=model.prestashopId)
            return self._ps.build_search_element(manufacturer, self._resource)
        else:
            return self._ps.search_unique(self._resource, {
                'filter[name]': model.name
            })

    def find_by_name(self, name: str):
        return self._ps.search_unique(self._resource, {
            'filter[name]': name
        })


manufacturers_service = CbcManufacturersService()
logger.info('Cbc service [manufacturers] started')
