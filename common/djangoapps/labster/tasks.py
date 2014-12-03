from celery.task import task

from django.contrib.auth.models import User
from django.conf import settings

from labster.models import Lab
from labster.nutshell import create_new_lead


ENABLE_NUTSHELL = getattr(settings, 'LABSTER_ENABLE_NUTSHELL', False)


def send_nutshell(user_id, lab_id=None):
    if not ENABLE_NUTSHELL:
        return False

    user = lab = None

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        pass

    profile = user.profile
    if profile.user_type != profile.USER_TYPE_TEACHER:
        return (None, None)

    if lab_id:
        try:
            lab = Lab.objects.get(id=lab_id)
        except Lab.DoesNotExist:
            pass

    return (user, lab)


@task()
def create_nutshell_data(user_id):
    user, lab = send_nutshell(user_id)
    if not user:
        return

    name = profile.name
    email = user.email
    phone = ''
    contact_id, lead_id = create_new_lead(name, email, phone)

    NutshellUser.objects.get_or_create(
        user=user,
        contact_id=contact_id,
        lead_id=lead_id)


@task()
def send_play_lab(user_id, lab_id):
    user, lab = send_nutshell(user_id, lab_id)
    if not user or not lab:
        return

    play_lab(user, lab)


@task()
def send_invite_students(user_id, lab_id):
    user, lab = send_nutshell(user_id, lab_id)
    if not user or not lab:
        return

    invite_students(user, lab)


@task()
def send_view_course(user_id, course_name):
    user = send_nutshell(user_id)
    if not user:
        return

    view_course(user, course_name)
