import graphene
from schema import Category


class PrestashopQuery(graphene.InputObjectType):
    key = graphene.String(required=True)
    value = graphene.String(required=True)


class PrestashopLanguage(graphene.ObjectType):
    id = graphene.String()
    isoCode = graphene.String()


class PrestashopLocalizedValue(PrestashopLanguage):
    value = graphene.String()


class PrestashopCategory(Category):
    name = graphene.List(PrestashopLocalizedValue)


class PrestashopManufacturer(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    active = graphene.Boolean()
    shortDescription = graphene.List(PrestashopLocalizedValue)
    description = graphene.List(PrestashopLocalizedValue)


class PrestashopImage(graphene.ObjectType):
    url = graphene.String()


class PrestashopOption(graphene.ObjectType):
    id = graphene.String()
    value = graphene.List(PrestashopLocalizedValue)


class PrestashopOptionValue(graphene.ObjectType):
    id = graphene.String()
    value = graphene.List(PrestashopLocalizedValue)
    option = graphene.String()


class PrestashopCombination(graphene.ObjectType):
    id = graphene.String()
    quantity = graphene.Int()
    reference = graphene.String()
    price = graphene.Float()
    images = graphene.List(PrestashopImage)
    options = graphene.List(PrestashopOptionValue)


class PrestashopProduct(graphene.ObjectType):
    id = graphene.String()
    price = graphene.Float()
    name = graphene.List(PrestashopLocalizedValue)
    shortDescription = graphene.List(PrestashopLocalizedValue)
    description = graphene.List(PrestashopLocalizedValue)
    manufacturer = PrestashopManufacturer
    categories = graphene.List(PrestashopManufacturer)
    images = graphene.List(PrestashopImage)
    combinations = graphene.List(PrestashopCombination)
    defaultImage = PrestashopImage
    defaultCombination = PrestashopCombination
