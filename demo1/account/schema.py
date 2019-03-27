import django.contrib.auth.models as models
import graphene
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from graphene import Node
from graphene_django import DjangoObjectType


class User(DjangoObjectType):
    class Meta:
        model = models.User
        interfaces = (Node,)
        exclude_fields = ('password', 'is_superuser', 'is_staff')


class UpdateUser(graphene.Mutation):
    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)

    class Arguments:
        id = graphene.String(required=True)
        username = graphene.String()
        password = graphene.String()
        is_active = graphene.Boolean()
        email = graphene.String()

    @staticmethod
    def mutate(root, info, **kwargs):
        _id = kwargs.pop('id')
        _, user_id = Node.from_global_id(_id)

        user = models.User.objects.get(pk=user_id)
        user.__dict__.update(**kwargs)
        if 'password' in kwargs:
            user.set_password(kwargs['password'])
        user.save()

        ok = True

        return UpdateUser(user=user, ok=ok)


class CreateUser(graphene.Mutation):
    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)

    class Arguments:
        username = graphene.String()
        password = graphene.String()
        email = graphene.String()

    @staticmethod
    def mutate(root, info, **kwargs):
        kwargs['is_active'] = True

        user = models.User.objects.create_user(**kwargs)

        ok = True
        return CreateUser(user=user, ok=ok)


class Query(object):
    me = graphene.Field(User)

    @staticmethod
    def resolve_me(root, info):
        if info.context.user.is_authenticated:
            return info.context.user
        else:
            return None

    user = Node.Field(User)
    users = graphene.List(
        User,
        description="用户列表",
        args={
            'username': graphene.String(required=False, description="账号"),
            'is_active': graphene.Boolean(required=False, description="状态，开启或关闭")
        },
    )

    @staticmethod
    def resolve_users(root, info, **kwargs):
        query = Q(is_superuser=False)

        if 'username' in kwargs and kwargs['username']:
            username = kwargs.pop('username')
            query &= Q(username__icontains=username)
        if 'is_active' in kwargs:
            query &= Q(is_active=bool(kwargs['is_active']))

        users = models.User.objects.filter(query)

        return users


class Mutation(object):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
