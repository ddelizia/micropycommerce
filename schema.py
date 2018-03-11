import graphene


class Category(graphene.ObjectType):
    id = graphene.String()
    path = graphene.String()