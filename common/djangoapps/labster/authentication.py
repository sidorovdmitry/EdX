from django.contrib.auth.models import User

from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.authtoken.models import Token


class GetTokenAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        key = request.GET.get('token')
        if key is None:
            return None

        # cleanup key
        key = key.split('?')[0]

        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        return (token.user, token)


class TokenBackend(object):

    def authenticate(self, key=None):
        if key is None:
            return None

        try:
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            return None

        return token.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
