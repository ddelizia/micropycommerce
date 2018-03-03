from ebay.ebay_service import EbayService
from utils.log import get_logger
from prestashop.prestashop_product import prestashop_product

logger = get_logger(__name__)


class EbayServiceProduct(EbayService):

    def __init__(self):
        super().__init__('product')
        self._ps_product = prestashop_product

    def request_with_body(self, body):
        return self.categories(body.get('id'))

    def add_product(self, product_code):
        prod = self._ps_product.get_product(product_code)

        # https://stackoverflow.com/questions/38124679/sample-code-for-listing-a-fixedpriceitem-with-ebay
        #
        myitem = {
            'ErrorLanguage': 'en_US',
            'WarningLevel': 'High',
            'Item': {
                'ShipToLocations': 'IT',
                'ReservePrice': '0.0',
                'Title': prod['name']['it'],
                'Description': prod['description']['it'],
                'ProxyItem': 'false',
                'HitCounter': 'NoHitCounter',
                'BuyerRequirementDetails': {
                    'ShipToRegistrationCountry': 'true'
                },
                'Location': 'Calabria',
                'ReturnPolicy': {
                    'ReturnsWithin': '30 giorni',
                    'Description': 'Puoi rendere il prodotto che non ti soddisfa entro e non oltre 30 giorni di calendario dalla data di consegna. Ti invitiamo a provare i prodotti senza rimuovere i cartellini e i sigilli oppure rompere la confezione poichè non potranno essere resi articoli che non siano nelle stesse condizioni in cui li hai ricevuti.\n\nVerranno rimborsati solo ed esclusivamente i prodotti effettivamente ricevuti dal magazzino. Nel caso in cui non venissero rispettate le condizioni appena descritte ed eventualmente accertato il difetto, ti informiamo che il pacco reso ti verrà restituito e il rimborso non verrà accreditato.\n\nPer tutte le richieste di autorizzazione al reso pervenute al nostro Servizio Clienti, il reso è gratuito. Nel caso in cui il pacco venga restituito al magazzino senza autorizzazione al reso e senza il tracking da noi fornito, non sarà effettuato alcun rimborso per le spese di reso sostenute.',
                    'ShippingCostPaidBy': 'Buyer',
                    'ReturnsWithinOption': 'Days_30',
                    'ShippingCostPaidByOption': 'Buyer',
                    'ReturnsAcceptedOption': 'ReturnsAccepted',
                },
                'BusinessSellerDetails': {
                    'LegalInvoice': 'true',
                    'Fax': '0',
                    'Address': {
                        'FirstName': 'Delizia',
                        'LastName': 'Alessandro',
                        'CompanyName': 'Delizia Alessandro',
                        'Street1': 'Via Mazzini 62/66',
                        'CityName': 'Amantea',
                        'CountryName': 'Italia',
                        'Phone': '098268400',
                        'PostalCode': '87032',
                        'StateOrProvince': 'CS'
                    },
                    'Email': 'ebay@xxx.it',
                    'VATDetails': {
                        'VATSite': 'IT',
                        'VATID': '0976543233'
                    }
                },
                'ListingDuration': 'GTC',
                'PictureDetails': {
                    'GalleryType': 'Plus',
                    'PhotoDisplay': 'SuperSize',
                    'ExternalPictureURL': prod['defaultImage']
                },
                'BuyerProtection': 'ItemEligible',
                'StartPrice': prod['price'],
                'eBayPlusEligible': 'false',
                'BuyItNowPrice': '0.0',
                'PrimaryCategory': {
                    'CategoryID': '324'
                },
                'GetItFast': 'false',
                'ListingType': 'FixedPriceItem',
                'Country': 'IT',
                'HideFromSearch': 'true',
                'ConditionID': '1000',
                'PaymentMethods': 'PayPal',
                'PayPalEmailAddress': 'fatture-facilitator@deliziaalessandro.it',
                # 'SecondaryCategory': { 'CategoryID': '324' },
                'AutoPay': 'true',
                'OutOfStockControl': 'true',
                'ReasonHideFromSearch': 'OutOfStock',
                'Quantity': '1',
                'eBayPlus': 'false',
                'DispatchTimeMax': '3',
                'GiftIcon': '0',
                'PostCheckoutExperienceEnabled': 'false',
                'Site': 'Italy',
                'BuyerGuaranteePrice': '20000.0',
                'Currency': 'EUR',
                'HitCount': '8',
                'ConditionDisplayName': 'Nuovo',
                'PrivateListing': 'false',
                'ShippingPackageDetails': {
                    'ShippingIrregular': 'false',
                    'ShippingPackage': 'None',
                    'WeightMajor': '0',
                    'WeightMinor': '0'
                },
                'ShippingDetails': {
                    'InsuranceFee': '5.0',
                    'InternationalShippingDiscountProfileID': '0',
                    'ShippingServiceOptions': {
                        'ShippingTimeMax': '2',
                        'ShippingServiceCost': '0.0',
                        'ShippingServicePriority': '1',
                        'ShippingService': 'IT_ExpressCourier',
                        'ExpeditedService': 'true',
                        'ShippingTimeMin': '1'
                    },
                    'InsuranceDetails': {
                        'InsuranceFee': '5.0',
                        'InsuranceOption': 'Optional'
                    },
                    'InsuranceOption': 'Optional',
                    'ShippingDiscountProfileID': '0',
                    'CalculatedShippingRate': {
                        'WeightMinor': '0',
                        'WeightMajor': '0'
                    },
                    'SellerExcludeShipToLocationsPreference': 'true',
                    'ShippingType': 'Flat',
                    'SalesTax': {
                        'SalesTaxPercent': '0.0',
                        'ShippingIncludedInTax': 'false'
                    },
                    'ApplyShippingDiscount': 'false',
                    'ThirdPartyCheckout': 'false'
                }
            }
        }
        self._api.execute('VerifyAddFixedPriceItem', myitem)


ebay_service_product = EbayServiceProduct()
logger.info('Ebay service [product] started')
