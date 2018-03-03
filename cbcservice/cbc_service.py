import munch

from utils.prestashop import get_ps
from utils.log import get_logger
from utils.config import get_config
from utils.storage import get_storage
from utils.template import compile
from utils.ws import Ws
from shipment import shipment_calculator

logger = get_logger(__name__)


class UploadResult:
    def __init__(self, result):
        self.result = result

    def serialize(self):
        return self.result


class CbcTypeService(Ws):
    def __init__(self, resource: str):
        super().__init__("sync_cbc_%s" % (resource))
        self._ps = get_ps()
        self._ss = get_storage()
        self._resource = resource
        self._iso_lang = get_config()['prestashop']['mainLanguage']
        self._current_lang = self.get_language(self._iso_lang)

    def request_with_body(self, body):
        shipment_calculator.clean_cache()
        return self.upload_one_from_firebase(body.get('id')).result

    def request_no_body(self):
        shipment_calculator.clean_cache()
        return self.upload_all_from_firebase().result

    def get_language(self, iso_code):
        logger.debug('Getting language [%s]' % (iso_code))
        return self._ps.search_unique('languages', {
            'filter[iso_code]': iso_code
        })

    def create_model(self, dict: (str, dict) = None) -> munch.Munch:
        logger.info('Creating model [%s] [%s]' % (self._resource, dict))
        model = munch.Munch()
        model.basepath = self._ps._api_url
        model.language = self._current_lang.id
        if not(dict is None):
            model.update(dict)
        return model

    def _build_xml(self, model: munch.Munch):
        return compile('./handlebars/%s.xml' % (self._resource), model.toDict())

    def upload_single(self, model: munch.Munch):
        raise NotImplementedError('Method upload_single not implemented')

    def transform_from_dict(self, dict: dict) -> munch.Munch:
        return self.create_model(dict)

    def delete_all(self):
        logger.info('Starting deletion all resources of type: %s' % (self._resource))
        items = self._ps.search(self._resource)
        for item in items:
            self._ps.delete(self._resource, item.id)
        firebase_resources = self._ss.get_items(self._resource)
        for firebase_resource in firebase_resources:
            if not(firebase_resource is None):
                self._ss.update_prestashop_id(self._resource, firebase_resource.get('id'), None)
        logger.info('Completed deletion of type: %s' % (self._resource))

    def upload(self, items_to_update) -> UploadResult:
        count_ok = 0
        count_ko = 0
        count_delete = 0
        message_result = []
        for item in items_to_update:
            try:
                model = self.transform_from_dict(item)
                self.upload_single(model)
                count_ok += 1
                message = 'Resource [%s] id [%s] Processed correctly' % (self._resource, model.id)
                logger.debug(message)
            except Exception as ex:
                message = 'Resource [%s] id [%s] Error during processing [%s]' % (self._resource, item.get('id'), ex)
                logger.error(message)
                count_ko += 1
                message_result.append(message)
        items_to_delete = self._ss.get_items_older_version(self._resource)
        if not(items_to_delete is None):
            for item in items_to_delete:
                if not(item.get('prestashopId') is None):
                    logger.info('delete item')
                self._ss.delete_item_by_id(self._resource, item.get('id'))
                count_delete += 1

        logger.info('Resource %s: Success %s - Errors %s - Deletions %s' % (self._resource, count_ok, count_ko, count_delete))
        result = {
            'ok': count_ok,
            'error': {
                'count': count_ko,
                'messages': message_result
            },
            'delete': count_delete
        }
        return UploadResult(result)

    def upload_all_from_firebase(self) -> UploadResult:
        items_to_update = self._ss.get_items_latest_version(self._resource)
        return self.upload(items_to_update)

    def upload_one_from_firebase(self, id) -> UploadResult:
        items_to_update = [self._ss.get_item_by_id(self._resource, id)]
        return self.upload(items_to_update)
