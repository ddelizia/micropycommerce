from ebaysdk.trading import Connection as Trading
from utils.config import get_config
from utils.log import get_logger


logger = get_logger(__name__)


class EbayService:

    """
    0	eBay United States	EBAY-US
    2	eBay Canada (English)	EBAY-ENCA
    3	eBay UK	EBAY-GB
    15	eBay Australia	EBAY-AU
    16	eBay Austria	EBAY-AT
    23	eBay Belgium (French)	EBAY-FRBE
    71	eBay France	EBAY-FR
    77	eBay Germany	EBAY-DE
    100	eBay Motors	EBAY-MOTOR
    101	eBay Italy	EBAY-IT
    123	eBay Belgium (Dutch)	EBAY-NLBE
    146	eBay Netherlands	EBAY-NL
    186	eBay Spain	EBAY-ES
    193	eBay Switzerland	EBAY-CH
    201	eBay Hong Kong	EBAY-HK
    203	eBay India	EBAY-IN
    205	eBay Ireland	EBAY-IE
    207	eBay Malaysia	EBAY-MY
    210	eBay Canada (French)	EBAY-FRCA
    211	eBay Philippines	EBAY-PH
    212	eBay Poland	EBAY-PL
    216	eBay Singapore	EBAY-SG
    """

    # Example from https://github.com/timotheus/ebaysdk-python/blob/master/samples/trading.py
    def __init__(self):
        self._ebay_conf = get_config()['ebay']
        logger.debug('Loading ebay configuration for domain %s' %
                     (self._ebay_conf.get('domain')))
        self._api = Trading(
            debug=self._ebay_conf['debug'],
            config_file=None,
            token=self._ebay_conf['token'],
            devid=self._ebay_conf['devid'],
            appid=self._ebay_conf['appid'],
            certid=self._ebay_conf['certid'],
            domain=self._ebay_conf['domain'],
            warnings=True,
            timeout=20,
            siteid='101')

    def ebayobject_to_dict(self, o) -> dict:
        return dict((name, getattr(o, name)) for name in dir(o) if not (
            name.startswith('_') or
            name == 'get' or
            name == 'has_key'))
