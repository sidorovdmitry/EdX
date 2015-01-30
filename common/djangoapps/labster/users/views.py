from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect

from rest_framework.authtoken.models import Token


def login_by_token(request):
    user_id = request.POST.get('user_id')
    token_key = request.POST.get('token_key')
    next_url = request.POST.get('next', '/')

    try:
        token = Token.objects.get(key=token_key, user_id=user_id)
    except Token.DoesNotExist:
        token = None

    if token:
        user = authenticate(key=token.key)
        if user and user.is_active:
            login(request, user)

    return HttpResponseRedirect(next_url)
