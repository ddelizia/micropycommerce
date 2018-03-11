from schema import Category
from google.google_category import get_google_categories
import graphene


class GoogleCategory(Category):
    pass


def build_google_category(item):
    cat = GoogleCategory()
    cat.id = item.get('id')
    cat.path = item.get('value')
    return cat


class QueryGoogle(graphene.ObjectType):

    googleCategories = graphene.Field(
        graphene.List(GoogleCategory), id=graphene.String())

    def resolve_googleCategories(self, info, id=None):
        data = get_google_categories()
        result = []
        if not(id is None):
            result = map(build_google_category, filter(
                lambda x: x.get('id') == id, data))
        else:
            result = map(build_google_category, data)
        return result
