import re
import munch

from cbcservice.cbc_service import CbcTypeService
from utils.log import get_logger

from utils.prestashop import PrestashopItemNotFoundException, PrestashopOperationException, PrestashopSearchElement

logger = get_logger(__name__)


class CbcCategoriesService(CbcTypeService):

    def __init__(self):
        super().__init__('categories')

    def delete_all(self):
        logger.info('Starting deletion all resources of type: %s' % (self._resource))
        items = self._ps.search(self._resource)
        for item in items:
            if int(item.id) > 2:
                try:
                    self._ps.delete(self._resource, item.id)
                except PrestashopOperationException as ex:
                    if ex.errors[0].code != 87:
                        raise ex
        firebase_resources = self._ss.get_items(self._resource)
        for firebase_resource in firebase_resources:
            if not(firebase_resource is None):
                self._ss.update_prestashop_id(self._resource, firebase_resource.get('id'), None)
        logger.info('Completed deletion of type: %s' % (self._resource))

    def upload_single(self, model: munch.Munch):
        result = None
        try:
            if (not(model.parent is None) and model.parent != ''):
                category_parent = self.find_by_name(model.parent)
                model.parentId = category_parent.id
            else:
                model.rootCategory = 1
                model.parentId = 1
            try:

                # Search category by name
                category = self.find_by_id_or_name(model)

                # Update the cateogry information
                model.prestashopId = category.id

                result = self._ps.edit(self._resource, model.prestashopId, self._build_xml(model))
                logger.info('%s %s has been edited correctly' % (self._resource, self._ps.find_id(result)))

            except PrestashopItemNotFoundException as e:
                # if category does not exists then create it
                result = self._ps.add(self._resource, self._build_xml(model))
                model.prestashopId = self._ps.find_id(result)
                logger.info('%s %s has been created correctly' % (self._resource, self._ps.find_id(result)))

            # Update prestashop id
            data = self._ps.build_search_element(result, self._resource)
            self._ss.update_prestashop_id(self._resource, model.id, data.id)
        except PrestashopItemNotFoundException as e:
            logger.error(e)
        except PrestashopOperationException as e:
            logger.error(str(e))

        return data

    def transform_from_dict(self, dict: dict) -> munch.Munch:
        base = super().transform_from_dict(dict)
        base.linkRewrite = re.sub('[^0-9a-zA-Z]+', '-', base.name.lower())
        base.description = "Se sei interessato all'aquisto di %s, questo è il sito che fa al caso tuo!<br>Casabagnoclick.com infatti è un negozio on " \
                           "line dove poter acquistare in piena sicurezza, direttamente da internet, %s e tanto altro ancora, a prezzi convenienti e " \
                           "con la comodità di ricevere la merce direttamente a casa tua in pochi giorni.<br>Visita il nostro catalogo e scopri le " \
                           "numerose offerte di %s, per acquistare in base alle tue esigenze. Infatti tra le tantissime offerte di %s trovi " \
                           "professionali o economici delle migliori marche, suddivisi per fascia di prezzo e corredati da una dettagliata scheda " \
                           "tecnica.<br>Per la vendita avvitatori on line, affidati all'esperienza di chi è nel settore da tanti anni, affidati a " \
                           "casabagnoclick.com!<br>Per informazioni circa %s in offerta o le condizioni di spedizione e vendita %s, non esitare a " \
                           "contattarci, i nostri operatori sono tua disposizione..." % \
                           (base.name, 'Pavimenti, Rivestimenti, Parquet, Laminati, Docce e Vasche, Sanitari, Rubinetteria, Arredobagno, Arredo e '
                                       'Design, Idraulica e Riscaldamento, Stufe e Camini, Climatizzatori, Ferramenta',
                            base.name, base.name, base.name, base.name)
        base.metaTitle = "Vendita %s, Offerte %s Online | casabagnoclick.com" % (base.name, base.name)
        base.metaDescription = "Vendita %s delle migliori marche, tantissime offerte %s a prezzi davvero imbattibili, con la possibilità di acquistare " \
                               "%s Online. Catalogo Online casabagnoclick.com" % (base.name, base.name, base.name)
        base.metaKeywords = None
        return base

    def find_by_id_or_name(self, model: munch.Munch) -> PrestashopSearchElement:
        if (not(model.get('prestashopId') is None)):
            category = self._ps.get(self._resource, resource_id=model.prestashopId)
            return self._ps.build_search_element(category, self._resource)
        else:
            return self._ps.search_unique(self._resource, {
                'filter[name]': model.name
            })

    def find_by_name(self, name: str):
        return self._ps.search_unique(self._resource, {
            'filter[name]': name
        })


category_service = CbcCategoriesService()
logger.info('Cbc service [categories] started')
