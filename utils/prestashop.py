import requests

from xml.etree import ElementTree
from urllib.parse import urlencode
from typing import List
import mimetypes

from utils.log import get_logger
from utils.config import get_config

logger = get_logger(__name__)


# Exceptions
class PrestashopItemNotFoundException(Exception):
    pass


class PrestashopMultipleItemsFoundException(Exception):
    pass


class PrestashopErrorElement:
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


class PrestashopSearchElement:
    def __init__(self, id: str, ref: str):
        self.id = id
        self.ref = ref


class PrestashopOperationException(Exception):
    def __init__(self, input_message, errors: List[PrestashopErrorElement]):
        message = '%s\nError list: ' % (input_message)
        for error in errors:
            message += "\n%s - %s" % (error.code, error.message)
        super(PrestashopOperationException, self).__init__(message)
        self.errors = errors
        logger.error(message)


class Prestashop:
    def __init__(self, api_url: str, api_key: str):
        self._api_url = api_url
        self._api_key = api_key
        self._session = requests.Session()

        if not self._api_url.endswith('/'):
            self._api_url += '/'

        if not self._api_url.endswith('/api/'):
            self._api_url += 'api/'

    def search_unique(self, resource: str, options: dict=None) -> PrestashopSearchElement:
        logger.debug('Searching unique resource [%s] with following options [%s]' % (resource, options))
        result = self.search(resource, options)
        if (len(result) == 0):
            raise PrestashopItemNotFoundException('No result found')
        if (len(result) > 1):
            raise PrestashopMultipleItemsFoundException('Multiple results found')
        return result[0]

    def search(self, resource: str, options: dict=None) -> List[PrestashopSearchElement]:
        logger.debug('Searching resource [%s] with following options [%s]' % (resource, options))
        xml = self.get(resource, options=options)
        result = []
        for element in xml[0]:
            result.append(PrestashopSearchElement(element.attrib['id'], element.attrib['{http://www.w3.org/1999/xlink}href']))
        return result

    def get(self, resource: str, resource_id: str=None, options: dict=None) -> ElementTree:
        logger.debug('Getting resource [%s] with id [%s]' % (resource, resource_id))
        full_url = self._api_url + resource
        if resource_id is not None:
            full_url += "/%s" % (resource_id,)
        if options is not None:
            full_url += "?%s" % (self._options_to_querystring(options))
        return self.get_with_url(full_url)

    def add(self, resource, xml, optional_headers=None):
        logger.debug('Adding resource [%s]' % (resource))
        return self.add_with_url(self._api_url + resource, xml, optional_headers)

    def delete_image(self, resource, id):
        logger.debug('Deleting image [%s] with id [%s]' % (resource, id))
        full_url = "%simages/%s/%s" % (self._api_url, resource, id)
        headers = {'Content-Type': 'text/xml'}
        r = self._session.delete(full_url, headers=headers, auth=(self._api_key, ''))
        return self._process_response(r, 'Deleting image for %s with id %s' % (resource, id))

    def add_image(self, resource, id, image=None, image_url=None):
        logger.debug('Add image [%s] with id [%s]' % (resource, id))
        full_url = "%simages/%s/%s" % (self._api_url, resource, id)
        headers, body = self.encode_multipart_formdata(image, image_url)
        r = self._session.post(full_url, headers=headers, data=body, auth=(self._api_key, ''))
        return self._process_response(r, 'Adding image for %s with id %s' % (resource, id))

    def edit(self, resource, id, content, optional_headers=None):
        logger.debug('Editing document [%s] with id [%s]' % (resource, id))
        full_url = "%s%s" % (self._api_url, resource)
        return self.edit_with_url(full_url, content, optional_headers)

    def get_with_url(self, url) -> ElementTree:
        r = self._session.get(url, auth=(self._api_key, ''))
        return self._process_response(r, 'Getting data from url %s' % (url))

    def add_with_url(self, url, xml, optional_headers=None):
        if optional_headers is None:
            headers = {'Content-Type': 'text/xml'}
        else:
            headers = optional_headers
            headers['Content-Type'] = 'text/xml'
        r = self._session.post(url, data=xml.encode('utf-8'), headers=headers, auth=(self._api_key, ''))
        return self._process_response(r, 'Adding data to url %s:\n%s' % (url, xml))

    def edit_with_url(self, url, xml, optional_headers=None):
        if optional_headers is None:
            headers = {'Content-Type': 'text/xml'}
        else:
            headers = optional_headers
            headers['Content-Type'] = 'text/xml'
        r = self._session.put(url, data=xml.encode('utf-8'), headers=headers, auth=(self._api_key, ''))
        return self._process_response(r, 'Editing data on url %s:\n%s' % (url, xml))

    def _process_response(self, r: ElementTree, input: str):
        if r.encoding is None:
            encoding = ''
        else:
            encoding = r.encoding
        content = r.content.decode(encoding)
        if get_config()['environmet']['printXml'] is True:
            logger.debug('Response: %s' % (content))
        if content == '':
            return None
        xml = ElementTree.fromstring(content)
        self._validate(input, xml)
        return xml

    def _options_to_querystring(self, options):
        return urlencode(options)

    def _validate(self, message, xml_response: ElementTree):
        result_list = []
        for error in xml_response.iter('error'):
            result_list.append(PrestashopErrorElement(error.find('code').text, error.find('message').text))
        if (len(result_list) > 0):
            raise PrestashopOperationException(message, result_list)

    def encode_multipart_formdata(self, file=None, url=None):
        image = file

        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'.encode('ascii')
        L = []
        L.append('--'.encode('ascii') + BOUNDARY.encode('ascii'))
        L.append(('Content-Disposition: form-data; name="%s"; filename="%s"' % ('image', image.get('name'))).encode('ascii'))
        L.append(('Content-Type: %s' % mimetypes.guess_type(image.get('name'))[0]).encode('ascii'))
        L.append(''.encode('ascii'))
        L.append(image.get('bytes'))
        L.append('--'.encode('ascii') + BOUNDARY.encode('ascii') + '--'.encode('ascii'))
        L.append(''.encode('ascii'))
        body = CRLF.join(L)
        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % BOUNDARY}
        return headers, body

    def find_id(self, xml: ElementTree):
        return xml[0].find('id').text

    def delete(self, resource, id):
        return self.delete_with_url('%s%s/%s' % (self._api_url, resource, id))

    def delete_with_url(self, url) -> ElementTree:
        headers = {'Content-Type': 'text/xml'}
        r = self._session.delete(url, headers=headers, auth=(self._api_key, ''))
        return self._process_response(r, 'Deleting data for url %s' % (url))

    def find_type(self, xml: ElementTree):
        return xml[0].tag

    def build_search_element(self, xml: ElementTree, resource: str):
        return PrestashopSearchElement(self.find_id(xml), '%s%s/%s' % (self._api_url, resource, self.find_id(xml)))


ps = Prestashop(get_config()['prestashop']['url'], get_config()['prestashop']['apiKey'])
logger.info("Module [prestashop] started correctly")


def get_ps():
    return ps
