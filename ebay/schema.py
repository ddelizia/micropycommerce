import graphene
from schema import Category
from utils.helper import cast
from ebay.ebay_service_category import ebay_service_category


class EbayRealCategory(graphene.ObjectType):
    autoPayEnabled = graphene.Boolean()
    bestOfferEnabled = graphene.Boolean()
    categoryId = graphene.String()
    categoryLevel = graphene.Int()
    categoryName = graphene.String()
    categoryParentIs = graphene.String()
    leafCategory = graphene.Boolean()


class EbayCategory(Category):
    ebayCategories = graphene.List(EbayRealCategory)


def convert_dict_EbayRealCategory(o: dict):
    cat = EbayRealCategory()
    cat.autoPayEnabled = cast(o.get('AutoPayEnabled'), bool)
    cat.bestOfferEnabled = cast(o.get('BestOfferEnabled'), bool)
    cat.categoryId = o.get('CategoryID')
    cat.categoryLevel = cast(o.get('CategoryLevel'), int)
    cat.categoryName = o.get('CategoryName')
    cat.categoryParentIs = o.get('CategoryParentID')
    cat.leafCategory = cast(o.get('LeafCategory'), bool)
    return cat


def convert_dict_EbayCategory(o: dict):
    cat = EbayCategory()
    cat.path = o.get('categoryPath')
    cat.id = o.get(
        'categoryResult')[-1].get('CategoryID')
    cat.ebayCategories = map(
        convert_dict_EbayRealCategory, o.get('categoryResult'))
    return cat


class QueryEbay(graphene.ObjectType):

    ebayCategories = graphene.Field(
        graphene.List(EbayCategory), id=graphene.String())

    def resolve_ebayCategories(self, info, id=None):
        categories = ebay_service_category.categories(id)
        result = map(convert_dict_EbayCategory, categories)
        return result
