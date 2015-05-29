from hashlib import sha1

from django.contrib.auth.models import User


def get_username(external_user_id, provider):
    provider = provider.lower().strip()
    username = 'edx_lti_{}_{}'.format(external_user_id, provider)
    return sha1(username).hexdigest()[:30]


def get_email(external_user_id, provider):
    provider = provider.lower().strip()
    email = 'edx+lti-{}-{}@labster.com'.format(external_user_id, provider)
    return email


def create_user(external_user_id, provider):
    email = get_email(external_user_id, provider)
    username = get_username(external_user_id, provider)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User(username=username, email=email)
        user.set_unusable_password()
        user.save()

    return user
