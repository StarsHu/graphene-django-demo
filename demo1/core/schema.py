import account.schema
import graphene
from graphene_django.debug import DjangoDebug


class Query(
    account.schema.Query,
    graphene.ObjectType
):
    debug = graphene.Field(DjangoDebug, name='__debug')


class Mutation(
    account.schema.Mutation,
    graphene.ObjectType
):
    ...


schema = graphene.Schema(query=Query, mutation=Mutation)
