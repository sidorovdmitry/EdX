from celery.task import task

from django.contrib.auth.models import User

from labster.nutshell import create_new_lead


@task()
def create_nutshell_data(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    profile = user.profile
    if profile.user_type != profile.USER_TYPE_TEACHER:
        return

    name = profile.name
    email = user.email
    phone = ''
    create_new_lead(name, email, phone)
