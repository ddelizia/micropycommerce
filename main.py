import graphene
from utils.ws import run, register_service
from ebay.schema import QueryEbay
from prestashop.prestashop_service import QueryPrestashop
from shipment.schema import QueryShipment
from google.schema import QueryGoogle

from cbcservice.cbc_categories_service import category_service
from cbcservice.cbc_manufacturers_service import manufacturers_service
from cbcservice.cbc_products_service import products_service
from cbcservice.cbc_combinations_service import combinations_service

register_service(category_service)
register_service(manufacturers_service)
register_service(products_service)
register_service(combinations_service)


class Query(
        QueryEbay,
        QueryPrestashop,
        QueryShipment,
        QueryGoogle,
        graphene.ObjectType):
    pass


run(Query)
