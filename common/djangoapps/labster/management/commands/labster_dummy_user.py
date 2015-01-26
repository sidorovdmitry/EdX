from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from django.db.models import Q


# edx+test0001@labster.com
EMAIL_FORMAT = "edx+test{number}user@labster.com"
USERNAME_FORMAT = "edx_test{number}"


def get_password(number):
    return "edx+test{}".format(str(number).zfill(4))


class Command(BaseCommand):

    def handle(self, *args, **options):
        number = args[0]
        try:
            start = args[1]
        except:
            start = 1

        finished = False
        total = 0
        current = start

        while not finished:
            username = USERNAME_FORMAT.format(number=str(current).zfill(4))
            email = EMAIL_FORMAT.format(number=str(current).zfill(4))
            password = get_password(current)

            try:
                User.objects.filter(Q(username=username) | Q(email=email))[0]
            except:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password)
                total += 1

                self.stdout.write("email: {}, password: {}\n".format(
                    email, password))

            current += 1

            if int(total) == int(number):
                finished = True
