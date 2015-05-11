import re

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse

from django.template.loader import render_to_string


def generate_unique_username(name, model):
    """
    Generate unique username from name by removing spaces, and
    adding numbers if necessary
    """

    index = 0
    while True:
        try:
            username = generate_username(name.strip(), index=index)
            model.objects.get(username__iexact=username)
        except model.DoesNotExist:
            return username
        else:
            index += 1


def generate_username(name, index):
    name = re.sub(r'[^\w+]+', '', name)
    if index > 0:
        name = "{}{}".format(name, index)

    return name


def get_names(name):
    """
    Extract first_name and last_name from name
    """
    first_name = last_name = ''
    try:
        first_name, last_name = name.rsplit(' ', 1)
    except ValueError:
        first_name = name
    return first_name, last_name


def send_activation_email(request, user, labster_user):
    platform_name = settings.PLATFORM_NAME
    activation_url = reverse('labster_activate', args=[labster_user.email_activation_key])

    context = {
        'activation_url': request.build_absolute_uri(activation_url),
        'platform_name': platform_name,
    }

    # composes activation email
    subject = ("Activate Your {} Account").format(platform_name)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    message = render_to_string('emails/activation_email_labster.txt', context)
    from_address = settings.DEFAULT_FROM_EMAIL
    dest_addr = user.email

    mail.send_mail(subject, message, from_address, [dest_addr], fail_silently=False)
